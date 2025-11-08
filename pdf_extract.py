import streamlit as st
import pandas as pd
import pdfplumber
import io
from io import BytesIO

def extract_tables_from_pdf(pdf_file):
    """Extrai todas as tabelas de um arquivo PDF"""
    tables = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Extrair tabelas da página
            page_tables = page.extract_tables()
            for table_num, table in enumerate(page_tables):
                if table and len(table) > 1:  # Ignorar tabelas vazias ou com apenas cabeçalho
                    # Converter para DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df['_page'] = page_num + 1
                    df['_table'] = table_num + 1
                    tables.append(df)
    return tables

def main():
    st.set_page_config(page_title="Extrator de Colunas PDF", page_icon="📄", layout="wide")
    
    st.title("📄 Extrator de Colunas de Tabelas em PDF")
    st.write("Faça upload de um PDF contendo tabelas e selecione as colunas que deseja extrair")
    
    # Upload do arquivo PDF
    uploaded_file = st.file_uploader(
        "Escolha um arquivo PDF", 
        type=['pdf'],
        help="Formatos suportados: PDF"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("🔍 Extraindo tabelas do PDF..."):
                tables = extract_tables_from_pdf(uploaded_file)
            
            if not tables:
                st.error("❌ Nenhuma tabela encontrada no PDF")
                return
            
            st.success(f"✅ {len(tables)} tabela(s) encontrada(s) no PDF")
            
            # Selecionar qual tabela trabalhar (se houver múltiplas)
            if len(tables) > 1:
                st.subheader("📋 Selecione a Tabela")
                table_options = [f"Tabela {i+1} (Página {tables[i]['_page'].iloc[0]})" for i in range(len(tables))]
                selected_table_index = st.selectbox(
                    "Escolha qual tabela trabalhar:",
                    range(len(tables)),
                    format_func=lambda x: table_options[x]
                )
                df = tables[selected_table_index]
            else:
                df = tables[0]
            
            # Remover colunas internas de controle
            df_display = df.drop(['_page', '_table'], axis=1, errors='ignore')
            
            # Mostrar preview da tabela
            st.subheader("👁️ Visualização da Tabela Extraída")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.dataframe(df_display, use_container_width=True, height=300)
            
            with col2:
                st.metric("Linhas", df_display.shape[0])
                st.metric("Colunas", df_display.shape[1])
                st.metric("Página", df['_page'].iloc[0])
            
            # Limpar e preparar dados
            df_clean = df_display.copy()
            
            # Remover linhas completamente vazias
            df_clean = df_clean.dropna(how='all')
            
            # Tentar inferir tipos de dados
            for col in df_clean.columns:
                # Tentar converter para numérico
                df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')
            
            # Seleção de colunas
            st.subheader("🎯 Seleção de Colunas para Extrair")
            
            if len(df_clean.columns) > 0:
                selected_columns = st.multiselect(
                    "Selecione as colunas que deseja extrair:",
                    options=df_clean.columns.tolist(),
                    default=df_clean.columns.tolist()[:min(2, len(df_clean.columns))]
                )
                
                if selected_columns:
                    # Criar novo dataframe com colunas selecionadas
                    extracted_df = df_clean[selected_columns]
                    
                    # Mostrar preview da extração
                    st.subheader("📊 Visualização dos Dados Extraídos")
                    st.dataframe(extracted_df, use_container_width=True, height=250)
                    
                    # Estatísticas
                    st.subheader("📈 Estatísticas da Extração")
                    
                    col3, col4, col5, col6 = st.columns(4)
                    
                    with col3:
                        st.metric("Linhas extraídas", extracted_df.shape[0])
                    
                    with col4:
                        st.metric("Colunas extraídas", extracted_df.shape[1])
                    
                    with col5:
                        non_empty = extracted_df.count().sum()
                        total_cells = extracted_df.shape[0] * extracted_df.shape[1]
                        st.metric("Células preenchidas", f"{non_empty}/{total_cells}")
                    
                    with col6:
                        st.metric("Taxa de preenchimento", f"{(non_empty/total_cells*100):.1f}%")
                    
                    # Download dos dados extraídos
                    st.subheader("💾 Download dos Dados Extraídos")
                    
                    download_format = st.radio(
                        "Formato de download:",
                        ["CSV", "Excel"],
                        horizontal=True
                    )
                    
                    col7, col8 = st.columns(2)
                    
                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M')
                    
                    with col7:
                        if download_format == "CSV":
                            csv = extracted_df.to_csv(index=False, sep=';', decimal=',')
                            st.download_button(
                                label="📥 Baixar CSV",
                                data=csv,
                                file_name=f"colunas_extraidas_pdf_{timestamp}.csv",
                                mime="text/csv"
                            )
                        else:
                            buffer = BytesIO()
                            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                extracted_df.to_excel(writer, index=False, sheet_name='Dados_Extraidos')
                            st.download_button(
                                label="📥 Baixar Excel",
                                data=buffer.getvalue(),
                                file_name=f"colunas_extraidas_pdf_{timestamp}.xlsx",
                                mime="application/vnd.ms-excel"
                            )
                    
                    with col8:
                        # Mostrar dados em formato de texto
                        if st.button("📋 Mostrar Dados em Texto"):
                            st.text_area("Dados extraídos (formato CSV):", 
                                       extracted_df.to_csv(index=False, sep=';'), 
                                       height=200)
                
                else:
                    st.warning("⚠️ Selecione pelo menos uma coluna para extrair")
            else:
                st.error("❌ Nenhuma coluna válida encontrada na tabela")
                
        except Exception as e:
            st.error(f"❌ Erro ao processar o PDF: {str(e)}")
    
    # Instruções na sidebar
    with st.sidebar:
        st.header("ℹ️ Instruções")
        st.markdown("""
        1. **Faça upload** de um arquivo PDF contendo tabelas
        2. **Selecione** a tabela desejada (se houver múltiplas)
        3. **Escolha** as colunas que quer extrair
        4. **Visualize** os dados extraídos
        5. **Baixe** no formato desejado (CSV ou Excel)
        
        **Dica:** Funciona melhor com tabelas bem estruturadas
        """)
        
        st.header("⚙️ Configurações")
        show_raw = st.checkbox("Mostrar dados brutos da extração", value=False)
        
        if show_raw and 'tables' in locals():
            st.subheader("Dados Brutos da Extração")
            for i, table in enumerate(tables):
                st.write(f"Tabela {i+1}: {table.shape}")
                st.dataframe(table.head(3))

if __name__ == "__main__":
    main()
