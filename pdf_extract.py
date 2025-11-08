import streamlit as st
import pandas as pd
import pdfplumber
import io
from io import BytesIO
import re

def clean_column_names(columns):
    """Limpa e corrige nomes de colunas duplicados"""
    seen = {}
    cleaned_columns = []
    
    for i, col in enumerate(columns):
        if col is None or col == '':
            col = f'Coluna_{i+1}'
        elif col in seen:
            seen[col] += 1
            col = f'{col}_{seen[col]}'
        else:
            seen[col] = 1
        cleaned_columns.append(col)
    
    return cleaned_columns

def extract_tables_from_pdf(pdf_file):
    """Extrai todas as tabelas de um arquivo PDF com tratamento de erros"""
    tables = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            try:
                # Extrair tabelas da página
                page_tables = page.extract_tables()
                
                for table_num, table in enumerate(page_tables):
                    if table and len(table) > 1:  # Ignorar tabelas vazias ou com apenas cabeçalho
                        try:
                            # Limpar nomes de colunas
                            headers = table[0]
                            cleaned_headers = clean_column_names(headers)
                            
                            # Converter para DataFrame
                            df = pd.DataFrame(table[1:], columns=cleaned_headers)
                            
                            # Adicionar metadados
                            df['_page'] = page_num + 1
                            df['_table'] = table_num + 1
                            df['_table_id'] = f"p{page_num+1}_t{table_num+1}"
                            
                            # Remover linhas completamente vazias
                            df = df.dropna(how='all')
                            
                            if not df.empty:
                                tables.append(df)
                                
                        except Exception as e:
                            st.warning(f"⚠️ Erro na tabela {table_num+1} da página {page_num+1}: {str(e)}")
                            continue
                            
            except Exception as e:
                st.warning(f"⚠️ Erro na página {page_num+1}: {str(e)}")
                continue
                
    return tables

def main():
    st.set_page_config(page_title="Extrator Multi-Tabelas PDF", page_icon="📄", layout="wide")
    
    st.title("📄 Extrator Multi-Tabelas de PDF")
    st.write("Extraia múltiplas tabelas de PDFs e selecione colunas de cada uma")
    
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
            
            # Seleção múltipla de tabelas
            st.subheader("📋 Selecione as Tabelas")
            
            # Criar opções para seleção
            table_options = []
            for i, table in enumerate(tables):
                page = table['_page'].iloc[0]
                table_num = table['_table'].iloc[0]
                cols = len(table.columns) - 3  # Descontar colunas de metadados
                rows = len(table)
                
                table_options.append({
                    'index': i,
                    'label': f"Tabela {table_num} (Página {page}) - {rows}×{cols}",
                    'page': page,
                    'table_num': table_num,
                    'rows': rows,
                    'cols': cols
                })
            
            # Widget para seleção múltipla
            selected_table_indices = st.multiselect(
                "Selecione as tabelas que deseja trabalhar:",
                options=[i for i in range(len(tables))],
                format_func=lambda x: table_options[x]['label'],
                default=[0] if tables else []
            )
            
            if not selected_table_indices:
                st.warning("⚠️ Selecione pelo menos uma tabela")
                return
            
            # Container para cada tabela selecionada
            all_extracted_data = {}
            
            for table_idx in selected_table_indices:
                df = tables[table_idx]
                table_info = table_options[table_idx]
                
                st.markdown("---")
                st.subheader(f"📊 {table_info['label']}")
                
                # Remover colunas internas de controle para display
                df_display = df.drop(['_page', '_table', '_table_id'], axis=1, errors='ignore')
                
                # Mostrar preview da tabela
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.dataframe(df_display, use_container_width=True, height=250)
                
                with col2:
                    st.metric("Linhas", df_display.shape[0])
                    st.metric("Colunas", df_display.shape[1])
                    st.metric("Página", table_info['page'])
                
                # Preparar dados para seleção
                df_clean = df_display.copy()
                
                # Tentar inferir tipos de dados
                for col in df_clean.columns:
                    try:
                        # Tentar converter para numérico
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')
                    except:
                        pass
                
                # Seleção de colunas para esta tabela
                if len(df_clean.columns) > 0:
                    selected_columns = st.multiselect(
                        f"Selecione colunas para {table_info['label']}:",
                        options=df_clean.columns.tolist(),
                        default=df_clean.columns.tolist()[:min(3, len(df_clean.columns))],
                        key=f"cols_{table_idx}"
                    )
                    
                    if selected_columns:
                        # Criar dataframe com colunas selecionadas
                        extracted_df = df_clean[selected_columns]
                        
                        # Mostrar preview
                        st.write("**Visualização dos dados selecionados:**")
                        st.dataframe(extracted_df, use_container_width=True, height=200)
                        
                        # Armazenar para download conjunto
                        all_extracted_data[table_info['label']] = extracted_df
                        
                        # Estatísticas desta tabela
                        col3, col4, col5 = st.columns(3)
                        with col3:
                            st.metric(f"Linhas {table_info['label']}", extracted_df.shape[0])
                        with col4:
                            st.metric(f"Colunas {table_info['label']}", extracted_df.shape[1])
                        with col5:
                            total_cells = extracted_df.shape[0] * extracted_df.shape[1]
                            filled_cells = extracted_df.count().sum()
                            st.metric(f"Preenchimento {table_info['label']}", f"{(filled_cells/total_cells*100):.1f}%")
            
            # Download de todas as tabelas selecionadas
            if all_extracted_data:
                st.markdown("---")
                st.subheader("💾 Download de Todas as Tabelas Selecionadas")
                
                download_format = st.radio(
                    "Formato de download:",
                    ["Excel (Múltiplas abas)", "CSV Individual"],
                    horizontal=True
                )
                
                timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M')
                
                if download_format == "Excel (Múltiplas abas)":
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        for table_name, table_data in all_extracted_data.items():
                            # Limitar nome da aba para 31 caracteres (limitação do Excel)
                            sheet_name = re.sub(r'[\\/*?:\[\]]', '', table_name)[:31]
                            table_data.to_excel(writer, index=False, sheet_name=sheet_name)
                    
                    st.download_button(
                        label="📥 Baixar Excel com Múltiplas Abas",
                        data=buffer.getvalue(),
                        file_name=f"multiplas_tabelas_{timestamp}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
                
                else:  # CSV Individual
                    st.write("**Download individual de cada tabela:**")
                    for table_name, table_data in all_extracted_data.items():
                        csv_data = table_data.to_csv(index=False, sep=';', decimal=',')
                        safe_name = re.sub(r'[\\/*?:"<>|]', "", table_name)
                        
                        st.download_button(
                            label=f"📥 Baixar {safe_name}.csv",
                            data=csv_data,
                            file_name=f"{safe_name}_{timestamp}.csv",
                            mime="text/csv",
                            key=f"csv_{safe_name}"
                        )
                
                # Resumo final
                st.subheader("📈 Resumo da Extração")
                total_tables = len(all_extracted_data)
                total_rows = sum([df.shape[0] for df in all_extracted_data.values()])
                total_cols = sum([df.shape[1] for df in all_extracted_data.values()])
                
                col6, col7, col8 = st.columns(3)
                with col6:
                    st.metric("Tabelas extraídas", total_tables)
                with col7:
                    st.metric("Total de linhas", total_rows)
                with col8:
                    st.metric("Total de colunas", total_cols)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar o PDF: {str(e)}")
    
    # Instruções na sidebar
    with st.sidebar:
        st.header("ℹ️ Instruções")
        st.markdown("""
        1. **Upload** do PDF com tabelas
        2. **Selecione múltiplas tabelas** na lista
        3. **Para cada tabela:** escolha as colunas
        4. **Visualize** os dados selecionados
        5. **Baixe tudo** em Excel ou CSVs individuais
        
        **Recursos:**
        - ✅ Múltiplas tabelas
        - ✅ Nomes de colunas corrigidos
        - ✅ Download em lote
        - ✅ Tratamento de erros
        """)

if __name__ == "__main__":
    main()
