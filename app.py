import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & SYSTEM SETTINGS
# ==========================================
st.set_page_config(
    page_title="आकांक्षा AI - RTI व कायदेशीर महा-सहाय्यक",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# User Personal Defaults
DEFAULT_USER_NAME = "सतीश अशोक प्रधान"
DEFAULT_USER_ADDRESS = "छत्रपती संभाजीनगर, महाराष्ट्र"
DEFAULT_ENTERPRISE = "आकांक्षा एंटरप्रायझेस"

# Session State Initialization
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "जोडपत्र 'अ'"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "generated_history" not in st.session_state:
    st.session_state.generated_history = []

# ==========================================
# 2. ADVANCED MOBILE 2x4 & DESKTOP RESPONSIVE CSS
# ==========================================
st.markdown("""
    <style>
    /* Global Page Styling */
    .stApp {
        background-color: #FFFFFF;
        color: #0F172A;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Header & Branding Section */
    .header-container {
        text-align: center;
        padding-top: 5px;
        padding-bottom: 15px;
    }
    .brand-header-title {
        color: #84CC16;
        font-size: 30px;
        font-weight: 900;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .brand-sub-badge {
        background-color: #FEF3C7;
        color: #D97706;
        border: 2px dashed #F59E0B;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* CRITICAL MOBILE RESPONSIVE CSS - FORCES 2x4 GRID ON MOBILE */
    @media only screen and (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 6px !important;
        }
        div[data-testid="column"] {
            width: 25% !important;
            flex: 1 1 25% !important;
            min-width: 0px !important;
        }
        div.stButton > button {
            height: 75px !important;
            font-size: 11px !important;
            padding: 2px !important;
            border-radius: 10px !important;
        }
    }

    /* DESKTOP CSS - HORIZONTAL LAYOUT */
    @media only screen and (min-width: 769px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 12px !important;
        }
        div.stButton > button {
            height: 90px !important;
            font-size: 15px !important;
            border-radius: 14px !important;
        }
    }

    /* Vibrant Shiny Button Styling */
    div.stButton > button {
        width: 100% !important;
        font-weight: 800 !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.18) !important;
        transition: all 0.2s ease-in-out !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.03) !important;
        box-shadow: 0 8px 18px rgba(0,0,0,0.25) !important;
    }

    /* Vibrant Gradient Palette for 8 Buttons */
    /* Row 1 Colors */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(1) button {
        background: linear-gradient(135deg, #00C853, #00E676) !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(2) button {
        background: linear-gradient(135deg, #FF6D00, #FF9100) !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(3) button {
        background: linear-gradient(135deg, #1A237E, #3F51B5) !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(4) button {
        background: linear-gradient(135deg, #6200EA, #7C4DFF) !important;
    }

    /* Row 2 Colors */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(1) button {
        background: linear-gradient(135deg, #4A148C, #8E24AA) !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(2) button {
        background: linear-gradient(135deg, #D50000, #FF1744) !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(3) button {
        background: linear-gradient(135deg, #FFAB00, #FFD600) !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(4) button {
        background: linear-gradient(135deg, #00B8D4, #00E5FF) !important;
    }

    /* Section & Form Headers */
    .form-title-box {
        font-size: 20px;
        font-weight: 800;
        color: #0F172A;
        border-bottom: 3px solid #E2E8F0;
        padding-bottom: 8px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.title("⚙️ आकांक्षा AI सेटिंग्ज")
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password", help="Google AI Studio मधील तुमची API Key टाका.")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**अर्जदार:** {DEFAULT_USER_NAME}")
st.sidebar.markdown(f"**पत्ता:** {DEFAULT_USER_ADDRESS}")
st.sidebar.markdown(f"**संस्था:** {DEFAULT_ENTERPRISE}")

if st.session_state.generated_history:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 मसुदा इतिहास")
    if st.sidebar.button("🗑️ इतिहास साफ करा"):
        st.session_state.generated_history = []
        st.rerun()

# ==========================================
# 4. HEADER DASHBOARD
# ==========================================
st.markdown("""
    <div class='header-container'>
        <div class='brand-header-title'>⚖️ RTI AI महा-सहाय्यक</div>
        <div class='brand-sub-badge'>⚡ घरबसल्या एका मिनिटात अर्ज तयार करा</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. THE 8 SHINY APP BUTTONS (2x4 MOBILE GRID)
# ==========================================
row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

with row1_col1:
    if st.button("📄\n\nजोडपत्र 'अ'", key="btn_jod_a"):
        st.session_state.active_tab = "जोडपत्र 'अ'"

with row1_col2:
    if st.button("⚖️\n\nप्रथम अपील", key="btn_first_appeal"):
        st.session_state.active_tab = "प्रथम अपील"

with row1_col3:
    if st.button("🏛️\n\nमाहिती आयोग", key="btn_second_appeal"):
        st.session_state.active_tab = "माहिती आयोग"

with row1_col4:
    if st.button("✨\n\nAI चॅट", key="btn_ai_chat"):
        st.session_state.active_tab = "AI चॅट"

row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

with row2_col1:
    if st.button("📜\n\nकोर्ट याचिका", key="btn_court"):
        st.session_state.active_tab = "कोर्ट याचिका"

with row2_col2:
    if st.button("📢\n\nशासकीय तक्रार", key="btn_gov_complaint"):
        st.session_state.active_tab = "शासकीय तक्रार"

with row2_col3:
    if st.button("✏️\n\nप्रतिज्ञापत्र", key="btn_affidavit"):
        st.session_state.active_tab = "प्रतिज्ञापत्र"

with row2_col4:
    if st.button("🛒\n\nग्राहक मंच", key="btn_consumer"):
        st.session_state.active_tab = "ग्राहक मंच"

st.markdown("---")

# ==========================================
# 6. EXACT A4 EXPORT ENGINES (DOCX & PDF)
# ==========================================
def create_a4_docx(text):
    doc = Document()
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    for line in text.split('\n'):
        clean = line.strip()
        if clean:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(clean)
            run.font.size = Pt(11)
            run.font.name = 'Calibri'
            
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_a4_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        'A4Body',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.black,
        spaceAfter=5
    )
    
    story = []
    for line in text.split('\n'):
        clean = line.strip()
        if clean:
            clean_escaped = clean.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(clean_escaped, body_style))
            story.append(Spacer(1, 2))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# 7. DYNAMIC FORM & GENERATION ENGINE
# ==========================================
current_tab = st.session_state.active_tab

if current_tab == "AI चॅट":
    st.markdown("<div class='form-title-box'>✨ आकांक्षा AI कायदेशीर चॅट महा-सहाय्यक</div>", unsafe_allow_html=True)
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_query = st.chat_input("तुमचा प्रश्न येथे विचारा...")
    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
            
        if not api_key:
            st.error("⚠️ कृपया आधी डाव्या Sidebar मध्ये Gemini API Key प्रविष्ट करा!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.chat_message("assistant"):
                    with st.spinner("उत्तर शोधत आहे..."):
                        response = model.generate_content(f"तुम्ही उच्च कायदेशीर सहाय्यक आहात. मराठीत अचूक उत्तर द्या: {user_query}")
                        st.write(response.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"❌ त्रुटी: {str(e)}")

else:
    titles = {
        "जोडपत्र 'अ'": "📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))",
        "प्रथम अपील": "⚖️ जोडपत्र 'ब' (प्रथम अपील अर्ज नियम ५(१))",
        "माहिती आयोग": "🏛️ जोडपत्र 'क' (द्वितीय अपील नियम ७(१))",
        "कोर्ट याचिका": "📜 न्यायालयीन मसुदा / याचिका अर्ज (Court Petition)",
        "शासकीय तक्रार": "📢 प्रशासकीय व शासकीय तक्रार अर्ज",
        "प्रतिज्ञापत्र": "✏️ स्व-घोषणापत्र / प्रतिज्ञापत्र (Affidavit)",
        "ग्राहक मंच": "🛒 ग्राहक संरक्षण मंच तक्रार अर्ज (Consumer Forum)"
    }
    
    st.markdown(f"<div class='form-title-box'>{titles.get(current_tab, current_tab)}</div>", unsafe_allow_html=True)

    with st.form(key="active_service_form"):
        col_left, col_right = st.columns(2)
        
        with col_left:
            app_name = st.text_input("१. अर्जदाराचे नाव:", value=DEFAULT_USER_NAME)
            app_address = st.text_area("२. पूर्ण पत्ता व फोन:", value=DEFAULT_USER_ADDRESS, height=105)
        
        with col_right:
            auth_name = st.text_input("३. जन माहिती अधिकारी / विरोधी पक्ष / कार्यालय नाव:", placeholder="उदा. जन माहिती अधिकारी, मुख्य कार्यालय...")
            auth_address = st.text_area("४. कार्यालयाचा पूर्ण पत्ता:", height=105, placeholder="कार्यालयाचा सविस्तर पत्ता...")

        # Form Specific Controls
        if current_tab == "जोडपत्र 'अ'":
            subject = st.text_input("५. माहितीचा विषय:", value="माहितीचा अधिकार अधिनियम २००५ च्या कलम ६(१) अन्वये माहिती मिळणेबाबत.")
            info_details = st.text_area("६. मागितलेल्या माहितीचा सुटसुटीत तपशील (१, २, ३ मुद्दे लिहा):", height=130)
            period = st.text_input("७. माहितीचा कालावधी (उदा. २०२४ ते आजपर्यंत):")
            bpl = st.checkbox("अर्जदार दारिद्र्यरेषेखालील (BPL) आहे का?")

        elif current_tab == "प्रथम अपील":
            subject = st.text_input("५. प्रथम अपील प्राधिकरणाचे पदनाव:")
            info_details = st.text_area("६. अपीलाची मुख्य कारणे (मुद्देनिहाय):", height=130)
            period = st.text_input("७. मूळ जोडपत्र 'अ' सादर केल्याची तारीख:")

        elif current_tab == "माहिती आयोग":
            subject = st.text_input("५. माहिती आयोग खंडपीठ:", value="राज्य माहिती आयोग, महाराष्ट्र राज्य")
            info_details = st.text_area("६. प्रथम अपीलाचा निर्णय व द्वितीय अपीलाची कारणे:", height=130)
            period = st.text_input("७. प्रथम अपील सादर केल्याची तारीख:")

        else:
            subject = st.text_input("५. अर्ज / प्रकरणाचा विषय:")
            info_details = st.text_area("६. सविस्तर तपशील व मागण्या:", height=130)
            period = "लागू नाही"

        submit = st.form_submit_button(label="🚀 परिपूर्ण मसुदा तयार करा (Generate Draft)")

    if submit:
        if not api_key:
            st.error("⚠️ कृपया डाव्या Sidebar मध्ये Gemini API Key प्रविष्ट करा!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                master_prompt = f"""
                तुम्ही महाराष्ट्रातील वरिष्ठ वकील व शासकीय कायदेशीर मसुदा तज्ज्ञ आहात.
                खालील माहितीचा वापर करून महाराष्ट्र शासन नियमांनुसार सुटसुटीत आणि पूर्ण १ पानावर (A4 Size Page Layout) बसणारा कायदेशीर मराठी मसुदा तयार करा:

                सेवा: {current_tab}
                अर्जदार: {app_name}
                पत्ता: {app_address}
                कार्यालय/विरोधक: {auth_name}
                कार्यालय पत्ता: {auth_address}
                विषय: {subject}
                तपशील: {info_details}
                कालावधी/तारीख: {period}

                नियम:
                १. जर जोडपत्र 'अ', 'ब' किंवा 'क' असेल तर महाराष्ट्र RTI नियम २००५ च्या अधिकृत सरकारी नमुन्याप्रमाणे सर्व रकाने व मुद्दे हुबेहूब समाविष्ट करा.
                २. मसुदा सुटसुटीत आणि A4 साईज पानावर १ पानावर व्यवस्थित प्रिंट होईल असा तयार करा.
                """
                
                with st.spinner("⚡ AI द्वारे परिपूर्ण मसुदा तयार होत आहे..."):
                    res = model.generate_content(master_prompt)
                    draft_text = res.text
                    
                    st.success("✅ मसुदा यशस्वीरीत्या तयार झाला आहे!")
                    edited_draft = st.text_area("✏️ तयार झालेला मसुदा (संपादित करा):", value=draft_text, height=420)
                    
                    st.session_state.generated_history.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "tab": current_tab,
                        "name": app_name,
                        "content": edited_draft
                    })

                    # Downloads
                    st.markdown("---")
                    st.subheader("📥 A4 Size डाऊनलोड पर्याय")
                    d1, d2 = st.columns(2)
                    
                    docx_bytes = create_a4_docx(edited_draft)
                    pdf_bytes = create_a4_pdf(edited_draft)
                    
                    with d1:
                        st.download_button("📄 Word (.docx) डाऊनलोड", data=docx_bytes, file_name=f"{app_name}_{current_tab}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    with d2:
                        st.download_button("📕 PDF (.pdf) डाऊनलोड", data=pdf_bytes, file_name=f"{app_name}_{current_tab}.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"❌ त्रुटी: {str(e)}")
