import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ================================
# CONFIGURAÇÃO DA CONEXÃO GOOGLE
# ================================
def conectar_google_sheets():
    """
    Faz autenticação com Google Sheets usando credenciais de serviço
    """
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    # Nome da planilha no Google Sheets
    sheet = client.open("Triagem_Clientes").sheet1

    return sheet


# ================================
# CLASSIFICAÇÃO DA DEMANDA
# ================================
def classificar_demanda(tipo):
    """
    Classifica automaticamente a demanda
    """
    tipo = tipo.lower()

    if "aposentadoria" in tipo or "benefício" in tipo or "inss" in tipo:
        return "Previdenciário"
    elif "rescisão" in tipo or "trabalho" in tipo or "fgts" in tipo:
        return "Trabalhista"
    else:
        return "Outros"


# ================================
# INTERFACE STREAMLIT
# ================================
st.title("📋 Triagem Jurídica")
st.write("Preencha as informações abaixo para análise inicial.")

# Formulário
with st.form("form_triagem"):
    nome = st.text_input("Nome completo")

    tipo_de_demanda = st.selectbox(
        "Tipo de demanda",
        [
            "Aposentadoria",
            "Auxílio-doença",
            "Pensão por morte",
            "Rescisão trabalhista",
            "Horas extras",
            "FGTS",
            "Outro"
        ]
    )

    processo_em_andamento = st.radio(
        "Já possui processo em andamento?",
        ["Sim", "Não"]
    )

    urgencia = st.text_area("Descreva a urgência (opcional)")

    documentos_disponiveis = st.multiselect(
        "Documentos disponíveis",
        [
            "RG/CPF",
            "Carteira de Trabalho",
            "CNIS",
            "Contracheques",
            "Sentença",
            "Laudos médicos"
        ]
    )

    contato_preferencial = st.selectbox(
        "Contato preferencial",
        ["WhatsApp", "Telefone", "E-mail"]
    )

    enviar = st.form_submit_button("Enviar")

# ================================
# PROCESSAMENTO DOS DADOS
# ================================
if enviar:
    try:
        # Classificação automática
        classificacao = classificar_demanda(tipo_de_demanda)

        # Conecta na planilha
        sheet = conectar_google_sheets()

        # Prepara dados para envio
        dados = [
            nome,
            tipo_de_demanda,
            classificacao,
            processo_em_andamento,
            urgencia,
            ", ".join(documentos_disponiveis),
            contato_preferencial
        ]

        # Envia para o Google Sheets
        sheet.append_row(dados)

        # Mensagem de sucesso
        st.success("✅ Dados enviados com sucesso! Em breve entraremos em contato.")

    except Exception as e:
        st.error(f"Erro ao enviar dados: {e}")
