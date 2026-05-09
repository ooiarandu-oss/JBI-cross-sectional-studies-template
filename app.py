import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import tempfile
import datetime

# 1. Configuração de Página e Estilo
st.set_page_config(page_title="JBI Checklist Tool", layout="wide", page_icon="📝")

# Estilo customizado (CSS) para deixar mais bonito
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    div[data-testid="stExpander"] {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 class='main-header'>📝 JBI Critical Appraisal Checklist</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #7f8c8d; margin-top: -20px; margin-bottom: 30px;'>For Analytical Cross Sectional Studies</h4>", unsafe_allow_html=True)

# 2. Cabeçalho Customizado (UI/UX)
with st.expander("ℹ️ Study & Reviewer Information", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        reviewer = st.text_input("Reviewer Name", placeholder="Enter your name")
        article_name = st.text_input("Article Title", placeholder="Title of the study")
        author = st.text_input("Author(s)", placeholder="Authors of the study")
    with col2:
        year = st.text_input("Year of Publication", placeholder="e.g. 2024")
        record_number = st.text_input("Record Number", placeholder="Internal ID or Number")
        doi = st.text_input("DOI", placeholder="Digital Object Identifier")
        date = st.date_input("Appraisal Date", datetime.date.today())

st.divider()

# 3. Definição dos Itens e Explicações Técnicas (Tooltips)
items = [
    {"q": "1. Were the criteria for inclusion in the sample clearly defined?", "help": "Authors should provide clear inclusion and exclusion criteria developed prior to recruitment."},
    {"q": "2. Were the study subjects and the setting described in detail?", "help": "Sample should be described in detail (demographics, location, time period) so others can determine comparability."},
    {"q": "3. Was the exposure measured in a valid and reliable way?", "help": "Description of measurement method required. Validity relates to appropriateness of current or past measures."},
    {"q": "4. Were objective, standard criteria used for measurement of the condition?", "help": "Patients should be included based on a specified diagnosis or definition to decrease bias."},
    {"q": "5. Were confounding factors identified?", "help": "Identify differences between groups (baseline characteristics, prognostic factors) that influence results."},
    {"q": "6. Were strategies to deal with confounding factors stated?", "help": "Strategies include matching or stratifying in design, or multivariate regression in analysis."},
    {"q": "7. Were the outcomes measured in a valid and reliable way?", "help": "Use of validated instruments or existing diagnostic criteria. Trained data collectors increase validity."},
    {"q": "8. Was appropriate statistical analysis used?", "help": "Detailed analytical techniques (regression/stratification) and verification of data assumptions."}
]

# 4. Interface da Checklist
st.markdown("### 📋 Appraisal Questionnaire")
responses = []
options = ["Yes", "No", "Unclear", "Not applicable"]

for i, item in enumerate(items):
    st.markdown(f"**{item['q']}**")
    # Colapsamos o label do rádio já que escrevemos a pergunta no markdown acima
    res = st.radio(f"Answer for Q{i+1}", options, help=item["help"], key=f"q{i}", horizontal=True, label_visibility="collapsed")
    responses.append(res)
    st.write("")

st.divider()

# 5. Overall Appraisal
st.markdown("### 🎯 Overall Appraisal")
col_app1, col_app2 = st.columns(2)
with col_app1:
    overall_decision = st.radio("Decision:", ["Include", "Exclude", "Seek further info"], horizontal=True)
with col_app2:
    comments = st.text_area("Comments", placeholder="Include reasons for exclusion or further info needed...")

# 6. Gráficos e Relatório
st.divider()
st.markdown("### 📊 Results & Report")
col_res1, col_res2 = st.columns(2)

if st.button("Generate Report & Chart", type="primary", use_container_width=True):
    with col_res1:
        # Gráfico de Pizza
        df = pd.DataFrame(responses, columns=["Answer"])
        fig = px.pie(df, names="Answer", title="Score Distribution", 
                     color="Answer", color_discrete_map={"Yes":"#2ecc71", "No":"#e74c3c", "Unclear":"#f1c40f", "Not applicable":"#95a5a6"})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col_res2:
        st.success("Report generated effectively! Preparing PDF for download...")
        
        # Usando fpdf2, que lida com unicode/UTF-8 nativamente
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "JBI Critical Appraisal Report", new_x="LMARGIN", new_y="NEXT", align="C")
        
        pdf.set_font("helvetica", "I", 12)
        pdf.cell(0, 10, "Analytical Cross Sectional Studies", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)
        
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 7, f"Article: {article_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"Reviewer: {reviewer} | Date: {date}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"Author: {author} | Year: {year} | Record: {record_number} | DOI: {doi}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(5)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Summary Table", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 9)
        for idx, r in enumerate(responses):
            question_text = items[idx]['q']
            pdf.multi_cell(0, 7, f"{question_text}\nAnswer: {r}")
            pdf.ln(2)
            
        pdf.ln(3)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"Overall Decision: {overall_decision}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 7, f"Comments: {comments}")
        
        # Rodapé de Referências no PDF
        pdf.ln(10)
        pdf.set_font("helvetica", "I", 8)
        pdf.multi_cell(0, 5, "References:\n- Shortland DL, et al. BMJ Open 2024; 14:e076904.\n- Peters, M. D. J., et al. (2015). JBI reviewers' manual.\n- JBI, 2020. All rights reserved.")

        # Download do PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("📥 Download PDF Report", f, file_name="JBI_Appraisal.pdf", type="primary", use_container_width=True)

# 7. Rodapé Visual (UI)
st.divider()
st.caption("© JBI, 2020. All rights reserved. JBI grants use of these tools for research purposes only.")
st.caption("Shortland DL, et al. BMJ Open 2024; 14:e076904. doi: 10.1136/bmjopen-2023-076904")
st.caption("Peters, M. D. J., et al. (2015). The Joanna Briggs Institute reviewers' manual 2015: methodology for JBI scoping reviews.")
