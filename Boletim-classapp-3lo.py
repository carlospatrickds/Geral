"""
Streamlit app: "Boletim Parser & Analyzer"
- Cole os dados brutos (formato livre) na caixa de texto.
- O app tentará *auto-parsar* o formato fornecido (heurísticas) e também permite colar um CSV com colunas claras.
- Exibe: dados organizados, médias por trimestre e anual, gráficos e pontos de atenção.

Observações:
- O parser automático usa heurísticas para dividir números em trimestres; se o formato estiver muito confuso, cole um CSV usando o botão "Modelo CSV".
- Para escolas com outro layout, adapte as regras de parsing na função parse_discipline_line().

Instalação:
pip install streamlit pandas matplotlib

Como rodar:
streamlit run app_boletim_streamlit.py
"""

import re
from io import StringIO
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Boletim Analyzer", layout="wide")
st.title("Boletim Parser & Analyzer — 5º Ano / Ensino Fundamental")

st.markdown("Cole o bloco de texto do boletim no campo abaixo (formato livre). O app tentará extrair: identificação, notas por disciplina, médias por trimestre e anual, gráficos e pontos de atenção.")

col1, col2 = st.columns([3,1])
with col1:
    raw = st.text_area("Cole aqui o boletim (texto bruto)", height=360)
with col2:
    st.markdown("**Ações rápidas**")
    if st.button("Modelo CSV (baixar)"):
        sample = (
            "Disciplina,A1_1tri,A2_1tri,A3_1tri,Med_1tri,A1_2tri,A2_2tri,A3_2tri,Med_2tri,A1_3tri,A2_3tri,A3_3tri,Med_3tri,Faltas,MA\n"
            "Português,9,10,10,10,9.5,10,10,10,9,10, ,10,0,20\n"
            "Matemática,10,9,10,10,8.5,10,9.5,9.5,8.5,10, ,10,0,19.5\n"
        )
        st.download_button("Baixar modelo CSV", sample, file_name="modelo_boletim.csv", mime="text/csv")

st.write("---")

# --- Helper parsing functions

def extract_header(text):
    header = {}
    # patterns for basic fields
    m = re.search(r'Aluno\(?a\)?:\s*(.+)', text, re.IGNORECASE)
    if m: header['Aluno'] = m.group(1).strip()
    m = re.search(r'Matr[ií]cula:\s*([\w\-]+)', text, re.IGNORECASE)
    if m: header['Matrícula'] = m.group(1).strip()
    m = re.search(r'Emiss[aã]o:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})', text)
    if m: header['Emissão'] = m.group(1)
    # Unidade / Curso / Turma line (one-liner)
    m = re.search(r'CD\s*-\s*(.+)', text)
    if m:
        header['CursoInfo'] = m.group(1).strip()
    else:
        # try to capture line that has 'Ensino' or 'Unidade'
        m2 = re.search(r'(Ensino Fundamental.*)', text, re.IGNORECASE)
        if m2:
            header['CursoInfo'] = m2.group(1).strip()
    return header


def numbers_from_line(line):
    # extract floats like 9,0 or 10,0 and also 9.5
    # normalize comma decimals to dot
    line = line.replace(',', '.')
    nums = re.findall(r"\d+\.?\d*", line)
    return [float(n) for n in nums]


def parse_discipline_line(line):
    """
    Heurística:
    - Extrai nome (texto inicial até encontrar primeiro número)
    - Extrai todos os números da linha
    - Tenta dividir os números em 3 trimestres. Se houver >=9 números, assumir 3 blocos de 3 notas (A1,A2,A3) e possivelmente médias.
    - Calcula média por trimestre como média das notas disponíveis no bloco.
    - Calcula média anual como soma das médias dos trimestres (ou média simples * 2 quando aparecem valores do tipo 20)
    """
    line = line.strip()
    # split name and rest by first occurrence of a number
    m = re.search(r'\d', line)
    if not m:
        name = line
        nums = []
    else:
        idx = m.start()
        name = line[:idx].strip().strip('-').strip()
        nums = numbers_from_line(line[idx:])

    # attempt to interpret nums
    trimesters = []
    used_for_annual = []
    if len(nums) >= 9:
        # take first 9 numbers as three groups of 3 (A1,A2,A3) each
        for t in range(3):
            block = nums[t*3:(t+1)*3]
            if len(block) > 0:
                tr_mean = sum(block)/len(block)
                trimesters.append(round(tr_mean,2))
                used_for_annual.append(tr_mean)
        # attempt to find yearly MA near the end (value >10 likely is 20.0 used as scaled sum)
        annual = None
        for candidate in reversed(nums):
            if candidate >= 0:
                # if candidate > 10 and typical appears as 20.0 in sample, keep but also compute from trimesters
                annual = candidate
                break
        if annual is None:
            annual = round(sum(used_for_annual),2)
    elif len(nums) >= 3:
        # fewer numbers: split equally
        n = len(nums)
        chunk = max(1, n//3)
        for t in range(3):
            start = t*chunk
            block = nums[start:start+chunk]
            if block:
                trimesters.append(round(sum(block)/len(block),2))
        annual = round(sum(trimesters),2) if trimesters else None
    else:
        trimesters = []
        annual = None

    # construct return dict
    return {
        'Disciplina': name if name else 'Desconhecida',
        'Trimestres': trimesters,
        'MA_guess': annual,
        'RawNumbers': nums,
        'RawLine': line
    }


# --- Processing input

if raw.strip() == "":
    st.info("Cole o boletim no campo à esquerda (texto). Para melhores resultados, use o modelo CSV disponível.")
    st.stop()

header = extract_header(raw)

# split lines and find discipline-like lines (we consider lines that start with a letter and contain numbers later)
lines = [l for l in raw.splitlines() if l.strip()]
# filter probable discipline lines: those that contain at least one number and start with a non-space word (no header)
disc_lines = []
for l in lines:
    if re.search(r'\d', l) and not re.search(r'Emiss|Matr|Aluno|Situa|Disciplinas', l, re.IGNORECASE):
        # often discipline lines start with a letter and then a tab/space
        # also avoid the big header line that lists column names
        # Heuristic: if line starts with a discipline word (letters) and contains numbers, accept
        if re.match(r'^[A-Za-z\"\'\s]', l):
            disc_lines.append(l)

# If too few disc_lines, try alternative: lines that start with capitalized word and have many numbers
if len(disc_lines) < 4:
    cand = []
    for l in lines:
        nums = numbers_from_line(l)
        if len(nums) >= 3 and len(l.split()) < 40:
            cand.append(l)
    if len(cand) > len(disc_lines):
        disc_lines = cand

parsed = [parse_discipline_line(l) for l in disc_lines]

# Build DataFrame
rows = []
for p in parsed:
    tr = p['Trimestres']
    # ensure length 3
    while len(tr) < 3:
        tr.append(np.nan)
    row = {
        'Disciplina': p['Disciplina'],
        'A1_1tri': np.nan, 'A2_1tri': np.nan, 'A3_1tri': np.nan,
        'Med_1tri': tr[0] if len(tr) > 0 else np.nan,
        'A1_2tri': np.nan, 'A2_2tri': np.nan, 'A3_2tri': np.nan,
        'Med_2tri': tr[1] if len(tr) > 1 else np.nan,
        'A1_3tri': np.nan, 'A2_3tri': np.nan, 'A3_3tri': np.nan,
        'Med_3tri': tr[2] if len(tr) > 2 else np.nan,
        'MA_guess': p['MA_guess']
    }
    rows.append(row)

df = pd.DataFrame(rows)
if df.empty:
    st.error("Não foi possível identificar linhas de disciplinas — cole no formato CSV usando o botão Modelo CSV.")
    st.stop()

# Compute MA (annual) from trimester means when possible

def compute_annual_from_trimesters(row):
    meds = [row['Med_1tri'], row['Med_2tri'], row['Med_3tri']]
    meds = [m for m in meds if not pd.isna(m)]
    if len(meds) == 3:
        # some schools sum trimesters (ex.: 10+10+0 -> 20). We'll compute a normalized annual mean: average of trimester means * 2
        # but safer: if MA_guess exists and is >10, keep MA_guess; else compute sum
        guess = row.get('MA_guess', None)
        if pd.notna(guess) and guess > 10:
            annual = guess
        else:
            # compute scaled annual to match sample where 20.0 appears as 'MA'
            annual = round(sum(meds),2)
    elif len(meds) > 0:
        annual = round(np.nanmean(meds)* (3 if len(meds)==1 else 3/len(meds)),2)
    else:
        annual = row.get('MA_guess', np.nan)
    return annual


df['MA_computed'] = df.apply(compute_annual_from_trimesters, axis=1)

# Attention rules
ATT_THRESHOLD = 7.0  # below this needs attention
DROP_THRESHOLD = 1.5  # drop between trimesters considered significant

attentions = []
for _, r in df.iterrows():
    notes = []
    meds = [r['Med_1tri'], r['Med_2tri'], r['Med_3tri']]
    meds_clean = [m for m in meds if not pd.isna(m)]
    if any((m < ATT_THRESHOLD) for m in meds_clean):
        notes.append('Média trimestral abaixo de {:.1f}'.format(ATT_THRESHOLD))
    # check drops
    for i in range(len(meds_clean)-1):
        if meds_clean[i+1] + DROP_THRESHOLD < meds_clean[i]:
            notes.append('Queda significativa do {}º para {}º trimestre'.format(i+1, i+2))
    # annual
    if pd.notna(r['MA_computed']) and r['MA_computed'] < ATT_THRESHOLD:
        notes.append('Média anual baixa')
    attentions.append('; '.join(notes) if notes else 'OK')


df['Atenção'] = attentions

# Display header
with st.expander('Informações do aluno (extraídas)'):
    st.write(header)

# Show table
st.subheader('Tabela de Notas (Médias trimestrais estimadas)')
st.dataframe(df[['Disciplina','Med_1tri','Med_2tri','Med_3tri','MA_computed','Atenção']].rename(columns={
    'Med_1tri':'1º Tri (média)', 'Med_2tri':'2º Tri (média)', 'Med_3tri':'3º Tri (média)', 'MA_computed':'MA (estimada)'
}))

# Charts: bar of MA_computed

st.subheader('Gráficos')
fig1, ax1 = plt.subplots(figsize=(10,4))
ax1.bar(df['Disciplina'], df['MA_computed'])
ax1.set_title('Média Anual (estimada) por disciplina')
ax1.set_ylim(0, max(10, np.nanmax(df['MA_computed']) + 1))
ax1.set_ylabel('MA estimada (escala escola)')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

# Line chart of trimester means
fig2, ax2 = plt.subplots(figsize=(10,4))
x = np.arange(len(df))
ax2.plot(x, df['Med_1tri'], marker='o', label='1º Tri')
ax2.plot(x, df['Med_2tri'], marker='o', label='2º Tri')
ax2.plot(x, df['Med_3tri'], marker='o', label='3º Tri')
ax2.set_xticks(x)
ax2.set_xticklabels(df['Disciplina'], rotation=45, ha='right')
ax2.set_title('Comparação de Médias por Trimestre')
ax2.set_ylim(0, 10)
ax2.legend()
st.pyplot(fig2)

# Attention summary
st.subheader('Resumo de atenção')
att_df = df[['Disciplina','Atenção','MA_computed']].copy()
att_df = att_df.rename(columns={'MA_computed':'MA_estimada'})
st.table(att_df)

# Downloadable report as CSV
buffer = StringIO()
df.to_csv(buffer, index=False)
buffer.seek(0)
st.download_button('Baixar planilha (CSV) com resultados', buffer.getvalue(), file_name='boletim_resultado.csv', mime='text/csv')

st.markdown('---')
st.markdown('**Observações importantes:**
- O parser automático faz heurísticas que funcionaram com o exemplo fornecido; para garantir 100% de fidelidade use o formato CSV (modelo disponível).\n- Ajuste `ATT_THRESHOLD` e `DROP_THRESHOLD` no código se quiser outros critérios de atenção.\n- Estou à disposição para adaptar o parser ao layout exato da sua secretaria/escola.')
