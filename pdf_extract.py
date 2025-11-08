import streamlit as st
import pandas as pd
import pdfplumber
import io
from io import BytesIO
import re
from datetime import datetime

def detect_date_column(column_data):
    """Detecta se uma coluna contém datas no formato MM/AAAA"""
    date_pattern = r'^\d{1,2}/\d{4}$'
    date_count = 0
    total_non_empty = 0
    
    for value in column_data:
        if pd.notna(value) and str(value).strip():
            total_non_empty += 1
            if re.match(date_pattern, str(value).strip()):
                date_count += 1
    
    # Se mais de 80% dos valores não vazios são datas, considera como coluna de data
    if total_non_empty > 0 and (date_count / total_non_empty) > 0.8:
        return True
    return False

def detect_header_row(table_data):
    """Detecta automaticamente a linha do cabeçalho"""
    if not table_data or len(table_data) < 2:
        return 0
    
    # Verificar se a primeira linha parece ser cabeçalho
    first_row = table_data[0]
    second_row = table_data[1]
    
    # Critérios para identificar cabeçalho:
    # 1. Se a primeira linha contém principalmente texto e a segunda contém datas/números
    # 2. Se a primeira linha tem muitos valores vazios/nulos (provavelmente não é cabeçalho)
    # 3. Se a segunda linha começa com uma data
    
    first_row_non_empty = sum(1 for cell in first_row if cell and str(cell).strip())
    second_row_non_empty = sum(1 for cell in second_row if cell and str(cell).strip())
    
    # Se a primeira linha tem poucos valores não vazios, provavelmente não é cabeçalho
    if first_row_non_empty < len(first_row) * 0.3:
        return 0  # Não tem cabeçalho
    
    # Verificar se a segunda linha começa com data
    if second_row and second_row[0] and detect_date_column([second_row[0]]):
        return 0  # Não tem cabeçalho, dados começam na primeira linha
    
    # Verificar se a primeira linha parece ter nomes de colunas (texto mais descritivo)
    first_row_has_text = sum(1 for cell in first_row if cell and any(c.isalpha() for c in str(cell)))
    second_row_has_numbers = sum(1 for cell in second_row if cell and any(c.isdigit() for c in str(cell)))
    
    if first_row_has_text > second_row_has_numbers:
        return 0  # Primeira linha é provavelmente cabeçalho
    else:
        return -1  # Não tem cabeçalho claro

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

def generate_column_names(num_columns, first_row_data=None):
    """Gera nomes de colunas baseados no conteúdo ou sequenciais"""
    columns = []
    
    if first_row_data and any(first_row_data):
        # Tentar usar a primeira linha como base para nomes
        for i, cell in enumerate(first_row_data):
            if cell and str(cell).strip():
                # Verificar se é data - se for, usar nome padrão
                if detect_date_column([cell]):
                    columns.append(f'Data')
                else:
                    columns.append(f'Coluna_{i+1}_{str(cell)[:20]}')
            else:
                columns.append(f'Coluna_{i+1}')
    else:
        # Nomes sequenciais
        columns = [f'Coluna_{i+1}' for i in range(num_columns)]
    
    return clean_column_names(columns)

def extract_tables_from_pdf(pdf_file):
    """Extrai todas as tabelas de um arquivo PDF com detecção inteligente de cabeçalhos"""
    tables = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            try:
                # Extrair tabelas da página
                page_tables = page.extract_tables()
                
                for table_num, table in enumerate(page_tables):
                    if table and len(table) > 1:  # Ignorar tabelas vazias ou com apenas uma linha
                        try:
                            # Detectar se tem cabeçalho
                            header_row_index = detect_header_row(table)
                            
                            if header_row_index == 0:
                                # Tem cabeçalho na primeira linha
                                headers = table[0]
                                data_rows = table[1:]
                            else:
                                # Não tem cabeçalho claro - gerar nomes automaticamente
                                headers = generate_column_names(len(table[0]), table[0])
                                data_rows = table
                            
                            # Limpar nomes de colunas
                            cleaned_headers = clean_column_names(headers)
                            
                            # Converter para DataFrame
                            df = pd.DataFrame(data_rows, columns=cleaned_headers)
                            
                            # Adicionar metadados
                            df['_page'] = page_num + 1
                            df['_table'] = table_num + 1
                            df['_table_id'] = f"p{page_num+1}_t{table_num+1}"
                            df['_has_header'] = (header_row_index == 0)
                            
                            # Remover linhas completamente vazias
                            df = df.dropna(how='all')
                            
                            # Remover colunas completamente vazias
                            df = df.dropna(axis=1, how='all')
                            
                            if not df.empty and len(df.columns) > 3:  # Pelo menos uma coluna de dados além dos metadados
                                tables.append(df)
                                
                        except Exception as e:
                            st.warning(f"⚠️ Erro na tabela {table_num+1} da página {page_num+1}: {str(e)}")
                            continue
                            
            except Exception as e:
                st.warning(f"⚠️ Erro na página {page_num+1}: {str(e)}")
                continue
                
    return tables

def combine_all_tables(extracted_data):
    """Combina todas as tabelas em um único DataFrame"""
    combined_dfs = []
    
    for table_name, df in extracted_data.items():
        # Adicionar coluna identificadora
        df_copy = df.copy()
        df_copy['Fonte_Tabela'] = table_name
        combined_dfs.append(df_copy)
    
    if combined_dfs:
        return pd.concat(combined_dfs, ignore_index=True)
    return pd.DataFrame()

def main():
    st.set_page_config(page_title="Extrator Multi-Tabelas PDF", page_icon="📄", layout="wide")
    
    st.title("📄 Extrator Multi-Tabelas de PDF")
    st.write("Extraia múltiplas tabelas de PDFs com detecção automática de cabeçalhos")
    
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
            
            # Mostrar estatísticas de cabeçalhos detectados
            headers_detected = sum(1 for table in tables if table['_has_header'].iloc[0])
            st.info(f"📊 {headers_detected} tabela(s) com cabeçalho detectado | {len(tables) - headers_detected} tabela(s) com cabeçalho gerado automaticamente")
            
            # Seleção múltipla de tabelas
            st.subheader("📋 Selecione as Tabelas")
            
            # Criar opções para seleção
            table_options = []
            for i, table in enumerate(tables):
                page = table['_page'].iloc[0]
                table_num = table['_table'].iloc[0]
                has_header = table['_has_header'].iloc[0]
                cols = len(table.columns) - 4  # Descontar colunas de metadados
                rows = len(table)
                
                header_status = "✅ Com cabeçalho" if has_header else "🤖 Cabeçalho gerado"
                
                table_options.append({
                    'index': i,
                    'label': f"Tabela {table_num} (Página {page}) - {rows}×{cols} - {header_status}",
                    'page': page,
                    'table_num': table_num,
                    'rows': rows,
                    'cols': cols,
                    'has_header': has_header
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
                
                # Ícone indicador de cabeçalho
                header_icon = "✅" if table_info['has_header'] else "🤖"
                st.subheader(f"{header_icon} {table_info['label']}")
                
                # Remover colunas internas de controle para display
                df_display = df.drop(['_page', '_table', '_table_id', '_has_header'], axis=1, errors='ignore')
                
                # Mostrar preview da tabela
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.dataframe(df_display, use_container_width=True, height=250)
                
                with col2:
                    st.metric("Linhas", df_display.shape[0])
                    st.metric("Colunas", df_display.shape[1])
                
                with col3:
                    st.metric("Página", table_info['page'])
                    st.metric("Cabeçalho", "Detectado" if table_info['has_header'] else "Gerado")
                
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
                        f"Selecione colunas para extrair:",
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
                            st.metric(f"Linhas extraídas", extracted_df.shape[0])
                        with col4:
                            st.metric(f"Colunas extraídas", extracted_df.shape[1])
                        with col5:
                            total_cells = extracted_df.shape[0] * extracted_df.shape[1]
                            filled_cells = extracted_df.count().sum()
                            st.metric(f"Preenchimento", f"{(filled_cells/total_cells*100):.1f}%")
            
            # Download de todas as tabelas selecionadas
            if all_extracted_data:
                st.markdown("---")
                st.subheader("💾 Download das Tabelas Selecionadas")
                
                download_format = st.radio(
                    "Formato de download:",
                    ["Excel (Múltiplas abas)", "Excel (Todas juntas)", "CSV Individual"],
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
                        file_name=f"multiplas_tabelas_abas_{timestamp}.xlsx",
                        mime="application/vnd.ms-excel",
                        key="excel_multiple"
                    )
                
                elif download_format == "Excel (Todas juntas)":
                    # Combinar todas as tabelas
                    combined_df = combine_all_tables(all_extracted_data)
                    
                    if not combined_df.empty:
                        buffer = BytesIO()
                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                            combined_df.to_excel(writer, index=False, sheet_name='Todas_Tabelas')
                        
                        st.download_button(
                            label="📥 Baixar Excel com Todas as Tabelas Juntas",
                            data=buffer.getvalue(),
                            file_name=f"todas_tabelas_juntas_{timestamp}.xlsx",
                            mime="application/vnd.ms-excel",
                            key="excel_combined"
                        )
                        
                        # Mostrar preview da tabela combinada
                        st.write("**Preview da tabela combinada:**")
                        st.dataframe(combined_df, use_container_width=True, height=300)
                
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
                st.markdown("---")
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
        5. **Baixe** no formato desejado
        
        **Recursos de detecção:**
        - ✅ Cabeçalhos automáticos
        - ✅ Detecção de colunas de data
        - ✅ Nomes inteligentes para colunas
        - ✅ Tratamento de tabelas sem cabeçalho
        """)
        
        st.header("🔍 Sobre a Detecção")
        st.markdown("""
        **Cabeçalhos detectados automaticamente quando:**
        - Primeira linha contém texto descritivo
        - Segunda linha contém dados (números/datas)
        
        **Cabeçalhos gerados automaticamente quando:**
        - Tabela começa direto com dados
        - Primeira linha contém datas/números
        - Estrutura não parece ter cabeçalho
        """)

if __name__ == "__main__":
    main()
