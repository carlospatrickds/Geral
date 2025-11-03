import streamlit as st
import pandas as pd
import re
from io import StringIO
from PyPDF2 import PdfReader

st.set_page_config(page_title="Medalhistas por Estado", layout="wide")

st.title("🏅 Leitor de Medalhistas por Estado - OBRL 2025")

uploaded_file = st.file_uploader("Envie o PDF (texto copiável)", type=["pdf"])
if uploaded_file:
    st.info("Extraindo texto... isso pode levar alguns segundos dependendo do tamanho do arquivo.")
    
    text = ""
    pdf = PdfReader(uploaded_file)
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    
    # Divide o texto em linhas úteis
    linhas = [l.strip() for l in text.split("\n") if l.strip()]
    
    # Expressão para capturar aluno, data, estado, nível e medalha
    padrao = re.compile(
        r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+)\s+(\d{1,2}/\d{1,2}/\d{4})\s*([A-Z]{2})\s+([A-Z]+)\s+([A-Z]+)$"
    )

    dados = []
    for linha in linhas:
        match = padrao.search(linha)
        if match:
            dados.append(match.groups())

    if dados:
        df = pd.DataFrame(dados, columns=["Aluno", "Data nascimento", "Estado", "Nível", "Medalha"])
        st.success(f"Extração concluída — {len(df)} registros encontrados.")
        st.dataframe(df.head(20), use_container_width=True)
        
        # Agrupamento por estado
        st.subheader("📊 Medalhistas agrupados por estado")
        agrupado = df.groupby("Estado")["Aluno"].apply(list).reset_index()
        st.dataframe(agrupado, use_container_width=True)

        # Comparação com lista de nomes colada
        st.subheader("🔍 Verificar nomes em uma lista")
        nomes_lista = st.text_area("Cole aqui os nomes (um por linha):")

        if nomes_lista:
            nomes_input = [n.strip().upper() for n in nomes_lista.split("\n") if n.strip()]
            encontrados = df[df["Aluno"].isin(nomes_input)]
            nao_encontrados = [n for n in nomes_input if n not in df["Aluno"].values]

            st.write("✅ **Correspondências encontradas:**")
            st.dataframe(encontrados, use_container_width=True)

            st.write("⚠️ **Não encontrados:**")
            st.write(nao_encontrados)
    else:
        st.error("Não foi possível identificar as colunas automaticamente. Verifique se o PDF tem texto copiável.")
        st.code("\n".join(linhas[:20]), language="text")
