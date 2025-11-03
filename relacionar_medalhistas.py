import io
import re
import unicodedata
from collections import defaultdict

import pdfplumber
import pandas as pd
import streamlit as st
from difflib import get_close_matches

st.set_page_config(page_title="Extrator de Lista por Estado", layout="wide")

st.title("Extrair lista do PDF → Excel (Agrupar por Estado)")

st.markdown(
    """
Envie um PDF (texto copiável). O app tentará extrair colunas como **Aluno**, **Data nascimento**, **Estado**, **Nível** e **Medalha**.
Depois você pode colar uma lista de nomes (um por linha) para verificar correspondências.
"""
)

uploaded_file = st.file_uploader("Envie o PDF (texto copiável)", type=["pdf"])

def strip_accents(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text

def parse_table_rows_from_text(text: str):
    """Tenta extrair linhas relevantes a partir do texto cru da página.
    Procura por uma data (ex: 1/28/2016 ou 28/1/2016) e usa isso como divisor entre nome e demais colunas.
    """
    rows = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    date_re = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
    for ln in lines:
        # pular linhas que são títulos ou cabeçalhos
        if re.search(r'MEDALHISTAS|ALUNO|Data nascimento|Nível|Medalha', ln, re.IGNORECASE):
            continue
        m = date_re.search(ln)
        if m:
            name = ln[:m.start()].strip()
            date = m.group().strip()
            rest = ln[m.end():].strip()
            parts = rest.split()
            # normal case: Estado Nível Medalha (3 campos)
            estado = parts[0] if len(parts) >= 1 else ""
            nivel = parts[1] if len(parts) >= 2 else ""
            medalha = parts[2] if len(parts) >= 3 else ""
            rows.append({
                "Aluno": name,
                "Data nascimento": date,
                "Estado": estado,
                "Nível": nivel,
                "Medalha": medalha
            })
        else:
            # Tentativa fallback: se linha longa com 3 colunas separadas por muitos espaços
            # separar por 2+ espaços
            parts = re.split(r'\s{2,}', ln)
            if len(parts) >= 4:
                # supor: Aluno | Data | Estado | Nível/Medalha (tentativa)
                name = parts[0].strip()
                date = parts[1].strip()
                estado = parts[2].strip()
                rest2 = parts[3].split()
                nivel = rest2[0] if rest2 else ""
                medalha = rest2[1] if len(rest2) > 1 else ""
                rows.append({
                    "Aluno": name,
                    "Data nascimento": date,
                    "Estado": estado,
                    "Nível": nivel,
                    "Medalha": medalha
                })
            else:
                # ignorar
                continue
    return rows

def extract_from_pdf(file_stream) -> pd.DataFrame:
    df_rows = []
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            # 1) Tentar extrair tabelas estruturadas
            try:
                tables = page.extract_tables()
            except Exception:
                tables = None

            used_table = False
            if tables:
                for table in tables:
                    if not table:
                        continue
                    # table is list of rows; try detect header row that contains 'Aluno' or 'Data nascimento'
                    header = table[0]
                    header_join = " ".join([str(h) for h in header if h]).lower()
                    if any(k in header_join for k in ["aluno", "data", "estado", "nível", "medalha"]):
                        # assume columns correspond; create dataframe
                        df_tmp = pd.DataFrame(table[1:], columns=table[0])
                        # normalize column names to expected ones if possible
                        colmap = {}
                        for c in df_tmp.columns:
                            c_low = str(c).lower()
                            if "alun" in c_low:
                                colmap[c] = "Aluno"
                            elif "data" in c_low:
                                colmap[c] = "Data nascimento"
                            elif "estado" in c_low:
                                colmap[c] = "Estado"
                            elif "nível" in c_low or "nivel" in c_low:
                                colmap[c] = "Nível"
                            elif "medal" in c_low:
                                colmap[c] = "Medalha"
                        df_tmp = df_tmp.rename(columns=colmap)
                        # keep only expected columns, fill if missing
                        for expected in ["Aluno", "Data nascimento", "Estado", "Nível", "Medalha"]:
                            if expected not in df_tmp.columns:
                                df_tmp[expected] = ""
                        df_rows.extend(df_tmp[["Aluno", "Data nascimento", "Estado", "Nível", "Medalha"]].to_dict(orient="records"))
                        used_table = True
                        break
            if not used_table:
                # fallback: extrair texto e tentar parsear com regex heurística
                text = page.extract_text() or ""
                rows = parse_table_rows_from_text(text)
                df_rows.extend(rows)
    # Montar dataframe final
    df = pd.DataFrame(df_rows)
    # limpar espaços e normalizar
    if not df.empty:
        df = df.astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip()
        # remover linhas em que Aluno está vazio
        df = df[df["Aluno"].str.strip() != ""].reset_index(drop=True)
    else:
        df = pd.DataFrame(columns=["Aluno", "Data nascimento", "Estado", "Nível", "Medalha"])
    return df

if uploaded_file is not None:
    st.info("Extraindo... isso pode demorar alguns segundos dependendo do arquivo.")
    try:
        df = extract_from_pdf(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
        st.stop()

    if df.empty:
        st.warning("Não foi possível extrair dados — verifique se o PDF realmente contém tabelas/texto copiável no formato esperado.")
        st.write("Extração resultou em nada. Tente enviar outra amostra do PDF ou reportar aqui o layout exato.")
    else:
        st.success(f"Extração concluída — {len(df)} registros encontrados.")
        st.dataframe(df.head(200))

        # Normalizar nomes para comparação
        df["Aluno_normalizado"] = df["Aluno"].apply(lambda s: strip_accents(s).upper())

        # Gerar agrupamento por Estado
        grouped = df.groupby("Estado").agg({
            "Aluno": lambda x: "; ".join(x.astype(str)),
            "Aluno_normalizado": lambda x: list(x)
        }).rename(columns={"Aluno": "Lista_nomes", "Aluno_normalizado": "Lista_normalizada"})
        grouped["Contagem"] = df.groupby("Estado")["Aluno"].count()

        # Prepara Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # aba completa
            df.drop(columns=["Aluno_normalizado"]).to_excel(writer, index=False, sheet_name="Completa")
            # aba por estado: criar tabela com contagem e lista
            df_state = grouped.reset_index()[["Estado", "Contagem", "Lista_nomes"]]
            df_state.to_excel(writer, index=False, sheet_name="Por_Estado")
            writer.save()
        output.seek(0)

        st.download_button(
            label="Baixar Excel (Completa + Por_Estado)",
            data=output.getvalue(),
            file_name="medalhistas_por_estado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("---")
        st.header("Comparar com lista colada (um nome por linha)")

        pasted = st.text_area("Cole aqui os nomes (um por linha):", height=200)
        min_similarity = st.slider("Limite de correspondência aproximada (para sugestões)", min_value=50, max_value=100, value=85)

        if st.button("Comparar"):
            if not pasted.strip():
                st.warning("Cole ao menos um nome para comparar.")
            else:
                input_names = [ln.strip() for ln in pasted.splitlines() if ln.strip()]
                # normalizar
                input_norm = [(n, strip_accents(n).upper()) for n in input_names]
                df_names_set = set(df["Aluno_normalizado"].tolist())

                matched = []
                not_matched = []
                suggestions = defaultdict(list)

                # para cada nome, verificar exata, senão fuzzy
                for orig, norm in input_norm:
                    if norm in df_names_set:
                        # encontrar linha(s) exatas
                        rows = df[df["Aluno_normalizado"] == norm]
                        matched.append({
                            "Nome input": orig,
                            "Encontrado?": "Sim",
                            "Quantidade registros": len(rows),
                            "Registro(s)": "; ".join(rows["Aluno"].tolist())
                        })
                    else:
                        # fuzzy suggestions
                        # candidate pool: df["Aluno_normalizado"].tolist()
                        candidates = get_close_matches(norm, df["Aluno_normalizado"].tolist(), n=3, cutoff=min_similarity/100)
                        if candidates:
                            # converter candidatos normalizados para originais
                            sugg = []
                            for c in candidates:
                                rows = df[df["Aluno_normalizado"] == c]
                                sugg.append("; ".join(rows["Aluno"].tolist()))
                            suggestions[orig] = sugg
                            not_matched.append({"Nome input": orig, "Encontrado?": "Não", "Sugestões": " | ".join(sugg)})
                        else:
                            not_matched.append({"Nome input": orig, "Encontrado?": "Não", "Sugestões": ""})

                st.subheader("Encontrados (exatos)")
                if matched:
                    st.table(pd.DataFrame(matched))
                else:
                    st.write("Nenhum nome foi encontrado exatamente.")

                st.subheader("Não encontrados (ou apenas aproximados)")
                if not_matched:
                    st.table(pd.DataFrame(not_matched))
                else:
                    st.write("Todos os nomes colados foram encontrados exatamente.")

        st.markdown("### Observações e dicas")
        st.write(
            """
- O parser tenta detectar datas (formato `d/m/aaaa` ou `m/d/aaaa`) e usa isso para separar o nome do restante das colunas.
- Se o PDF estiver em colunas com espaçamento irregular, a extração pode falhar — nesse caso, envie uma página exemplo e eu ajusto a heurística.
- A correspondência aproximada usa `difflib.get_close_matches`. Para nomes muito parecidos você pode ajustar o *cutoff*.
- Se quiser que a comparação seja insensível a ordem de nomes (ex: "SOBRENOME, Nome") podemos normalizar ainda mais.
"""
        )
