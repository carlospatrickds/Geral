import io
import re
import unicodedata
from collections import defaultdict
import time

import pdfplumber
import pandas as pd
import streamlit as st
from difflib import get_close_matches

st.set_page_config(page_title="Extrator de Lista por Estado", layout="wide")

st.title("📄 Extrator de Lista de Medalhistas por Estado")

st.markdown(
    """
### 🧩 Passos:
1. Envie o PDF (texto copiável).  
2. O app extrai automaticamente colunas como **Aluno**, **Data nascimento**, **Estado**, **Nível** e **Medalha**.  
3. Gere um Excel com duas abas e compare com uma lista de nomes colada abaixo.
"""
)

uploaded_file = st.file_uploader("Envie o PDF (texto copiável)", type=["pdf"])

# Funções utilitárias
def strip_accents(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text

def parse_table_rows_from_text(text: str):
    """Heurística simples: extrai linhas contendo datas (formato dd/mm/aaaa)."""
    rows = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    date_re = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
    for ln in lines:
        # ignorar cabeçalhos
        if re.search(r'MEDALHISTAS|ALUNO|Data nascimento|Nível|Medalha', ln, re.IGNORECASE):
            continue
        m = date_re.search(ln)
        if m:
            name = ln[:m.start()].strip()
            date = m.group().strip()
            rest = ln[m.end():].strip()
            parts = rest.split()
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
    return rows

def extract_from_pdf(file_stream):
    """Extrai dados de PDF de forma otimizada (para arquivos longos)."""
    df_rows = []
    with pdfplumber.open(file_stream) as pdf:
        total_pages = len(pdf.pages)
        progress = st.progress(0)
        status = st.empty()

        for i, page in enumerate(pdf.pages):
            status.text(f"🔍 Lendo página {i+1}/{total_pages}...")
            try:
                text = page.extract_text() or ""
                rows = parse_table_rows_from_text(text)
                df_rows.extend(rows)
            except Exception as e:
                st.warning(f"Erro na página {i+1}: {e}")
            progress.progress((i + 1) / total_pages)
            time.sleep(0.02)  # pequena pausa para visualização do progresso

        status.text("✅ Extração finalizada.")
        progress.empty()

    df = pd.DataFrame(df_rows)
    if not df.empty:
        df = df.astype(str)
        for col in df.columns:
            df[col] = df[col].str.strip()
        df = df[df["Aluno"].str.strip() != ""].reset_index(drop=True)
    else:
        df = pd.DataFrame(columns=["Aluno", "Data nascimento", "Estado", "Nível", "Medalha"])
    return df

# Execução principal
if uploaded_file is not None:
    st.info("🔧 Processando... isso pode levar alguns segundos dependendo do tamanho do PDF.")
    try:
        df = extract_from_pdf(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
        st.stop()

    if df.empty:
        st.warning("❗Não foi possível extrair dados. Verifique se o PDF contém texto copiável no formato esperado.")
        st.stop()

    st.success(f"✅ Extração concluída — {len(df)} registros encontrados.")
    st.dataframe(df.head(200))

    # Normalizar para comparações
    df["Aluno_normalizado"] = df["Aluno"].apply(lambda s: strip_accents(s).upper())

    # Agrupamento por estado
    grouped = df.groupby("Estado").agg({
        "Aluno": lambda x: "; ".join(x.astype(str)),
        "Aluno_normalizado": lambda x: list(x)
    }).rename(columns={"Aluno": "Lista_nomes", "Aluno_normalizado": "Lista_normalizada"})
    grouped["Contagem"] = df.groupby("Estado")["Aluno"].count()

    # Geração do Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.drop(columns=["Aluno_normalizado"]).to_excel(writer, index=False, sheet_name="Completa")
        df_state = grouped.reset_index()[["Estado", "Contagem", "Lista_nomes"]]
        df_state.to_excel(writer, index=False, sheet_name="Por_Estado")
    output.seek(0)

    st.download_button(
        label="💾 Baixar Excel (Completa + Por_Estado)",
        data=output.getvalue(),
        file_name="medalhistas_por_estado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Comparação de nomes
    st.markdown("---")
    st.header("🔎 Comparar com lista colada (um nome por linha)")

    pasted = st.text_area("Cole aqui os nomes (um por linha):", height=200)
    min_similarity = st.slider(
        "Limite de correspondência aproximada (para sugestões)",
        min_value=50, max_value=100, value=85
    )

    if st.button("Comparar"):
        if not pasted.strip():
            st.warning("⚠️ Cole ao menos um nome para comparar.")
        else:
            input_names = [ln.strip() for ln in pasted.splitlines() if ln.strip()]
            input_norm = [(n, strip_accents(n).upper()) for n in input_names]
            df_names_set = set(df["Aluno_normalizado"].tolist())

            matched = []
            not_matched = []
            for orig, norm in input_norm:
                if norm in df_names_set:
                    rows = df[df["Aluno_normalizado"] == norm]
                    matched.append({
                        "Nome input": orig,
                        "Encontrado?": "Sim",
                        "Quantidade registros": len(rows),
                        "Registro(s)": "; ".join(rows["Aluno"].tolist())
                    })
                else:
                    candidates = get_close_matches(norm, df["Aluno_normalizado"].tolist(), n=3, cutoff=min_similarity/100)
                    if candidates:
                        sugg = []
                        for c in candidates:
                            rows = df[df["Aluno_normalizado"] == c]
                            sugg.append("; ".join(rows["Aluno"].tolist()))
                        not_matched.append({"Nome input": orig, "Encontrado?": "Não", "Sugestões": " | ".join(sugg)})
                    else:
                        not_matched.append({"Nome input": orig, "Encontrado?": "Não", "Sugestões": ""})

            st.subheader("✅ Encontrados (exatos)")
            if matched:
                st.table(pd.DataFrame(matched))
            else:
                st.info("Nenhum nome foi encontrado exatamente.")

            st.subheader("⚠️ Não encontrados (ou apenas aproximados)")
            if not_matched:
                st.table(pd.DataFrame(not_matched))
            else:
                st.success("Todos os nomes colados foram encontrados exatamente.")

    st.markdown("---")
    st.markdown(
        """
**💡 Dicas para PDFs grandes (100+ páginas):**
- O processamento pode levar **1–3 minutos**, dependendo da máquina.  
- Enquanto lê, o app mostra o progresso (%).  
- Evite rodar múltiplas abas Streamlit simultaneamente.  
- O arquivo Excel final contém todas as páginas, já organizadas.
"""
    )
