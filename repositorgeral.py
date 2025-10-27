import streamlit as st

# Configuração inicial
st.set_page_config(page_title="Repósitorio de Links", layout="centered", page_icon="🗄️")

# --- VERIFICAÇÃO DE SENHA ---
SENHA_CORRETA = "23"
senha_digitada = st.text_input("Digite a senha para acessar a lista de links:", type="password")

if senha_digitada != SENHA_CORRETA:
    if senha_digitada:
        st.error("Senha incorreta! Acesso negado.")
    st.stop()

# CSS personalizado mais limpo
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 2.2em;
        font-weight: bold;
        margin-bottom: 30px;
        padding: 15px;
        border-bottom: 2px solid #1f77b4;
    }
    .section-title {
        color: #2c3e50;
        font-size: 1.4em;
        font-weight: bold;
        margin: 25px 0 15px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #3498db;
    }
    .app-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: box-shadow 0.3s ease;
    }
    .app-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .app-title {
        color: #2c3e50;
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .link-button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        font-size: 0.9em;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
        transition: background-color 0.3s ease;
    }
    .link-button:hover {
        background-color: #2980b9;
        text-decoration: none;
        color: white;
    }
    .description-box {
        background-color: #f8f9fa;
        border-left: 3px solid #3498db;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 0 5px 5px 0;
        font-size: 0.9em;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<div class="main-title">🚀 Repositório de Projetos</div>', unsafe_allow_html=True)

# Divisão em colunas
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">📊 Ferramentas Previdenciárias</div>', unsafe_allow_html=True)
    
    # Buscador de Rubricas
    with st.expander("🔍 Buscador de Rubricas no HISCRE", expanded=False):
        st.markdown("""
        <div class="description-box">
        Informe até 4 rubricas específicas para buscar | Organiza em ordem cronológica por competência | Você pode baixar o resultado em CSV
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://07-buscador-de-rubricas.streamlit.app/" target="_blank"><button class="link-button">Acessar Ferramenta</button></a>', unsafe_allow_html=True)
    
    # Cálculo de Multa
    with st.expander("📅 Cálculo de Multa Diária Corrigida", expanded=False):
        st.markdown("""
        <div class="description-box">
        Adicione faixas de multa com valores diferentes. O total por mês será corrigido por índice informado manualmente ou automaticamente pela SELIC.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://02-calculo-da-multa.streamlit.app/" target="_blank"><button class="link-button">Acessar Calculadora</button></a>', unsafe_allow_html=True)
    
    # Cálculo de Multa V2
    with st.expander("📅 Cálculo de Multa Diária (Versão 2)", expanded=False):
        st.markdown("""
        <div class="description-box">
        Versão alternativa da calculadora de multa com funcionalidades adicionais.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://03-calculomulta.streamlit.app/" target="_blank"><button class="link-button">Acessar Calculadora V2</button></a>', unsafe_allow_html=True)
    
    # Benefício Redutor
    with st.expander("📊 Cálculo de Acumulação de Benefícios", expanded=False):
        st.markdown("""
        <div class="description-box">
        Calculadora conforme as regras de redução na acumulação de benefícios (EC 103/2019). Quando uma pessoa tem direito a receber dois benefícios previdenciários ao mesmo tempo.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://01-beneficioredutoracmulacao.streamlit.app/" target="_blank"><button class="link-button">Acessar Calculadora</button></a>', unsafe_allow_html=True)
    
    # Acumulação de Benefícios
    with st.expander("📊 Acumulação de Benefícios (Versão 2)", expanded=False):
        st.markdown("""
        <div class="description-box">
        Calculadora conforme as regras de redução na acumulação de benefícios (EC 103/2019).
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://06-acmulacao-de-beneficios.streamlit.app/" target="_blank"><button class="link-button">Acessar Calculadora V2</button></a>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">⚙️ Ferramentas Técnicas e Produtividade</div>', unsafe_allow_html=True)
    
    # Desbloqueador VBA
    with st.expander("🔓 Desbloqueador de Projetos VBA Excel", expanded=False):
        st.markdown("""
        <div class="description-box">
        Ferramenta para desbloquear e recuperar projetos VBA no Excel.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://04-quebrasenhavba.streamlit.app/" target="_blank"><button class="link-button">Acessar Ferramenta</button></a>', unsafe_allow_html=True)
    
    # Sistema AnaClara 1
    with st.expander("✨ Sistema AnaClara - Cálculo Trabalhista", expanded=False):
        st.markdown("""
        <div class="description-box">
        Sistema com verificação da periculosidade para cálculo de adicionais trabalhistas.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://01-anaclara.streamlit.app/" target="_blank"><button class="link-button">Acessar Sistema</button></a>', unsafe_allow_html=True)
    
    # Sistema AnaClara 2
    with st.expander("⭐ Sistema AnaClara (Versão 2)", expanded=False):
        st.markdown("""
        <div class="description-box">
        Versão alternativa do sistema de cálculo de adicionais trabalhistas.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://02-anaclara.streamlit.app/" target="_blank"><button class="link-button">Acessar Sistema V2</button></a>', unsafe_allow_html=True)
    
    # Sistema AnaClara 3
    with st.expander("🚀 Sistema AnaClara (Versão 3)", expanded=False):
        st.markdown("""
        <div class="description-box">
        Versão mais avançada do sistema de cálculo de adicionais trabalhistas.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://03-anaclara.streamlit.app/" target="_blank"><button class="link-button">Acessar Sistema V3</button></a>', unsafe_allow_html=True)
    
    # Calculadora de IR 2024
    with st.expander("💰 Calculadora de IR 2024", expanded=False):
        st.markdown("""
        <div class="description-box">
        Cálculo de INSS e IR usando métodos tradicional e simplificado | Comparação entre os métodos | Tabelas de referência
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://05-planilhair24.streamlit.app/" target="_blank"><button class="link-button">Acessar Calculadora</button></a>', unsafe_allow_html=True)
    
    # Sistema de Triagem
    with st.expander("⚖️ Sistema de Triagem de Processos", expanded=False):
        st.markdown("""
        <div class="description-box">
        Sistema completo para gestão e triagem de processos judiciais com relatórios PDF e atribuição de servidores.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://08-triagem-27do10-10e49.streamlit.app/" target="_blank"><button class="link-button">Acessar Sistema</button></a>', unsafe_allow_html=True)

# Nova seção para ferramentas de imagem
st.markdown('<div class="section-title">🖼️ Ferramentas de Imagem e PDF</div>', unsafe_allow_html=True)

col3, col4, col5 = st.columns(3)

with col3:
    with st.expander("📄 Imagem para PDF", expanded=False):
        st.markdown("""
        <div class="description-box">
        Converta imagens para formato PDF de maneira rápida e prática.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://01-imagem-para-pdf.streamlit.app/" target="_blank"><button class="link-button">Acessar Conversor</button></a>', unsafe_allow_html=True)

with col4:
    with st.expander("📷 Fotos 3x4 em 10x15", expanded=False):
        st.markdown("""
        <div class="description-box">
        Transforme qualquer foto em 3x4 e num grid de 10x15 cm, prontas para impressão.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://02-fotos3x4em10x15maispola.streamlit.app/" target="_blank"><button class="link-button">Acessar Ferramenta</button></a>', unsafe_allow_html=True)

with col5:
    with st.expander("🖼️ Fotos Multi-Formato", expanded=False):
        st.markdown("""
        <div class="description-box">
        Ferramenta para trabalhar com fotos em múltiplos formatos e tamanhos.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<a href="https://03-fotos-multi-formato.streamlit.app/" target="_blank"><button class="link-button">Acessar Ferramenta</button></a>', unsafe_allow_html=True)

# Rodapé simplificado
st.markdown("---")
col_contact1, col_contact2 = st.columns(2)

with col_contact1:
    st.markdown("**📧 Contato:** carlos.patrick@hotmail.com")
    st.markdown("**🌐 Suporte:** [WhatsApp](https://l1nk.dev/WVtgy)")

with col_contact2:
    st.markdown("**📊 Status:** ✅ Todos operacionais")
    st.markdown("**📦 Total de Projetos:** 14")

# Sidebar minimalista
with st.sidebar:
    st.header("ℹ️ Informações")
    st.markdown("Este repositório contém todas as ferramentas e sistemas desenvolvidos.")
    
    st.header("📈 Estatísticas")
    st.metric("Projetos Ativos", "14")
    st.metric("Categorias", "3")
    
    st.header("🔔 Atualizações")
    st.info("""
    **Novo:**
    - Ferramentas de imagem e PDF
    - Layout redesenhado
    - Navegação simplificada
    """)
    
    st.header("📞 Suporte")
    st.link_button("Reportar Problema", "https://l1nk.dev/WVtgy")
    st.link_button("Sugerir Melhoria", "mailto:carlos.patrick@hotmail.com")

# Informação final
st.markdown("---")
st.caption("© 2024 - Desenvolvido com Streamlit • Atualizado automaticamente")
