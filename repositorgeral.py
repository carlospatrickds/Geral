import streamlit as st

# Configuração inicial
st.set_page_config(page_title="Repósitorio de Links", layout="centered",  page_icon="🗄️")



# --- VERIFICAÇÃO DE SENHA ---
SENHA_CORRETA = "23"
senha_digitada = st.text_input("Digite a senha para acessar a lista de links:", type="password")

if senha_digitada != SENHA_CORRETA:
    if senha_digitada:  # Só mostra erro se o usuário já digitou algo
        st.error("Senha incorreta! Acesso negado.")
    st.stop()  # Para aqui se a senha estiver errada ou vazia

# Configuração da página
st.set_page_config(
    page_title="Repositório de Links - Meus Projetos",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .link-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .link-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(255, 0, 0, 0.2);
    }
    .title {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        font-size: 2.5em;
        font-weight: bold;
    }
    .link-button {
        background-color: #ffffff;
        color: #667eea;
        border: none;
        padding: 12px 25px;
        border-radius: 8px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin-top: 15px;
        transition: background-color 0.3s ease;
    }
    .link-button:hover {
        background-color: #f1f2f6;
        text-decoration: none;
        color: #667eea;
    }
    .section-header {
        color: #2c3e50;
        border-left: 5px solid #ff6b6b;
        padding-left: 15px;
        margin: 30px 0 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<div class="title">🚀 Meu Repositório de Projetos</div>', unsafe_allow_html=True)

# Divisão em colunas
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h3 class="section-header">📊 Ferramentas Previdenciárias</h3>', unsafe_allow_html=True)


    # Link 1 - 🔍 Buscador de rubricas do HISCRE
    st.markdown(f"""
    <div class="link-card">
        <h3>🔍 Buscador de Rubricas no HISCRE</h3>
        <p>Informe até 4 rubricas específicas para buscar | Organiza em ordem cronológica por competência | Você pode baixar o resultado em CSV </p>
        <a href="https://04-buscador-de-rubricas.streamlit.app/" target="_blank">
            <button class="link-button">🔗 Acessar: 🔍 Buscador de Rubricas no HISCRE </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Link 2 - Cálculo de Multa
    st.markdown(f"""
    <div class="link-card">
        <h3>📅 Cálculo de Multa Diária Corrigida por Faixa</h3>
        <p>Adicione faixas de multa com valores diferentes. O total por mês será corrigido por índice informado manualmente ou automaticamente pela SELIC.</p>
        <a href="https://05-calculomulta.streamlit.app//" target="_blank">
            <button class="link-button">🔗 Acessar Calculadora de Multa</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

   
    # Link 3 - Benefício Redutor
    st.markdown(f"""
    <div class="link-card">
        <h3>📊 Cálculo de Acumulação de Benefícios Previdenciários</h3>
        <p>Calculadora conforme as regras de redução na acumulação de benefícios (EC 103/2019). Quando uma pessoa tem direito a receber dois benefícios previdenciários ao mesmo tempo, o segundo benefício será reduzido conforme as faixas estabelecidas.</p>
        <a href="https://01-beneficioredutor.streamlit.app/" target="_blank">
            <button class="link-button">🔗 Acessar Calculadora Previdenciária</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # link 4 -CÁLCULO DE ACUMULAÇÃO DE BENEFÍCIOS
    st.markdown(f"""
    <div class="link-card">
        <h3>📊 CÁLCULO DE ACUMULAÇÃO DE BENEFÍCIOS</h3>
        <p>Calculadora conforme as regras de redução na acumulação de benefícios (EC 103/2019).</p>
        <a href="https://14-redutorbenefnovo.streamlit.app////" target="_blank">
            <button class="link-button">🔗 Calculadora de acumulação </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

#COLUNA 2

with col2:
    st.markdown('<h3 class="section-header">⚙️ Ferramentas Técnicas e Produtividade</h3>', unsafe_allow_html=True)
    
    # Link 1 - Desbloqueador VBA
    st.markdown(f"""
    <div class="link-card">
        <h3>🔓 Desbloqueador de Projetos VBA Excel</h3>
        <p>Ferramenta para desbloquear e recuperar projetos VBA no Excel.</p>
        <a href="https://06-quebrasenhavba.streamlit.app/" target="_blank">
            <button class="link-button">🔗 Acessar Desbloqueador VBA</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Link 2 - Sistema AnaClara 2
    st.markdown(f"""
    <div class="link-card">
        <h3>✨ Sistema de Cálculo de Adicionais Trabalhistas - AnaClara (com verificação da periculosidade)</h3>
        <p>Sistema com verificação da periculosidade para cálculo de adicionais trabalhistas.</p>
        <a href="https://03-anaclara2.streamlit.app/" target="_blank">
            <button class="link-button">🔗 Acessar Sistema AnaClara</button>
        </a>
    </div>
    """, unsafe_allow_html=True)


    # Link 3 - Sistema AnaClara 1
    st.markdown(f"""
    <div class="link-card">
        <h3>⭐ Sistema de Cálculo de Adicionais Trabalhistas - AnaClara</h3>
        <p>Versão original do sistema de cálculo de adicionais trabalhistas.</p>
        <a href="https://02-anaclara.streamlit.app/" target="_blank">
            <button class="link-button">🔗 Acessar Sistema AnaClara Original</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Link - 4 - Foto3x4em10x15
    st.markdown(f"""
    <div class="link-card">
        <h3>📷 Transformar qualquer foto em 3x4 e num grid de 10x15</h3>
        <p>Este é um aplicativo web desenvolvido em Streamlit que automatiza a criação de folhas de fotos 3x4 no formato 10x15 cm, prontas para impressão</p>
        <a href="https://10-foto3x4em10x15.streamlit.app/" target="_blank">
            <button class="link-button">🔗 foto em 3x4 e num grid de 10x15</button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Link - 5 - Calculadora de IR 2024 fenomenal com base em planilha
    st.markdown(f"""
    <div class="link-card">
        <h3>Calculadora de IR 2024 fenomenal com base em planilha</h3>
        <p>Cálculo de INSS com base nas faixas da previdência | Cálculo de IR usando both métodos (tradicional e simplificado)| Comparação entre os dois métodos para mostrar qual é mais vantajoso |Tabelas de referência para consulta | Interface amigável com sidebar para entrada de dados</p>
        <a href="https://12-planilhair24.streamlit.app//" target="_blank">
            <button class="link-button">🔗 Calculadora de IR 2024 </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Link - 6 - Unir pdfs
    st.markdown(f"""
    <div class="link-card">
        <h3>📕 Unir e dividir arquivos em pdf</h3>
        <p>Unir e dividir arquivos em pdf, funcionalidades de redução de tamanho em aprimoração.</p>
        <a href="https://14pdffuz.streamlit.app///" target="_blank">
            <button class="link-button">📕 Unir pdf </button>
        </a>
    </div>
    """, unsafe_allow_html=True)


    
    # Espaço para futuros projetos
st.markdown(f"""
    <div class="link-card">
        <h3>🚧 Novo Projeto em Desenvolvimento</h3>
        <p>Em breve uma nova ferramenta estará disponível aqui!</p>
        <button class="link-button" style="background-color: #95a5a6; color: white;" disabled>
            ⏳ Em Breve
        </button>
    </div>
    """, unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.markdown("### 📧 Contato e Suporte")
col_contact1, col_contact2, col_contact3 = st.columns(3)

with col_contact1:
    st.info("**Email:**\carlos.patrick@hotmail.com")

with col_contact2:
    st.info("**W:**\https://l1nk.dev/WVtgy")

with col_contact3:
    st.info("**Status dos Sistemas:**\n✅ Todos operacionais")

# Sidebar com informações
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;">
        <h2>Bem-vindo!</h2>
        <p>Este repositório contém todas as ferramentas e sistemas desenvolvidos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("📊 Estatísticas")
    st.metric("Total de Projetos", "5")
    st.metric("Projetos Ativos", "5")
    st.metric("Última Atualização", "Hoje")
    
    st.header("🔔 Novidades")
    st.success("""
    **Última atualização:**
    - Calculadora de multa com correção SELIC com logo JF
    
    """)
    
   
    st.header("📞 Suporte Rápido")
    st.link_button("🆘 Reportar Problema", "https://l1nk.dev/WVtgy", use_container_width=True)
    st.link_button("💡 Sugerir Melhoria", "carlos.patrick@hotmail.com", use_container_width=True)
    
# Informação adicional
st.markdown("---")
st.caption("© 2024 - Todos os sistemas desenvolvidos com Streamlit • Atualizado automaticamente")
