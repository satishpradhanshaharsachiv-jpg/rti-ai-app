import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Inches, Pt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="आकांक्षा AI - सतीश अशोक प्रधान",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session State Initialization
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "जोडपत्र 'अ'"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ==========================================
# 2. CUSTOM CSS - DUAL LAYOUT SYSTEM
# ==========================================
st.markdown("""
    <style>
    /* 1. LOCK HORIZONTAL SCROLL (स्क्रीन सरकणे पूर्णपणे बंद) */
    * {
        box-sizing: border-box !important;
    }
    html, body, [data-testid="stAppViewContainer"], .main, .stApp {
        overflow-x: hidden !important;
        max-width: 100vw !important;
        background-color: #FFFFFF;
        color: #0F172A;
    }
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        max-width: 100% !important;
    }

    /* 2. SHINY GOLDEN TOP BANNER */
    .brand-top-banner {
        text-align: center;
        background: linear-gradient(135deg, #0F172A, #1E1B4B, #312E81);
        padding: 10px 4px;
        border-radius: 12px;
        border: 2px solid #FFD700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        margin-bottom: 8px;
    }
    
    .free-dhamaka-tag {
        display: inline-block;
        background: linear-gradient(90deg, #FF0055, #FF5E00);
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 900;
        padding: 2px 12px;
        border-radius: 20px;
        margin-bottom: 4px;
        letter-spacing: 1px;
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.7);
    }

    .brand-title-1 {
        font-size: 18px;
        font-weight: 900;
        background: linear-gradient(90deg, #FFD700, #FFF5A5, #FFA500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 3px;
        text-shadow: 0 0 8px rgba(255, 215, 0, 0.3);
    }

    .brand-title-2 {
        font-size: 13px;
        font-weight: 800;
        background: linear-gradient(90deg, #00FFCC, #FFD700, #FF3366);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    .brand-title-3 {
        color: #FFD700;
        font-size: 12px;
        font-weight: 700;
        border-top: 1px dashed rgba(255, 215, 0, 0.6);
        padding-top: 4px;
        margin-top: 2px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }

    /* 3. BUTTON ZONE (STRICT 4 COLUMNS x 2 ROWS) */
    .button-zone div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        justify-content: space-between !important;
        margin-bottom: 3px !important;
        width: 100% !important;
    }
    
    .button-zone div[data-testid="column"] {
        width: 24.5% !important;
        flex: 1 1 24.5% !important;
        min-width: 0px !important;
        padding: 0px !important;
    }

    .button-zone div.stButton > button {
        width: 100% !important;
        height: 62px !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        padding: 1px !important;
        border-radius: 8px !important;
        margin: 0px !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.3) !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
    }

    /* VIBRANT GRADIENT COLORS FOR BUTTONS */
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(1) button { background: linear-gradient(135deg, #00C853, #00E676) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(2) button { background: linear-gradient(135deg, #FF6D00, #FF9100) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(3) button { background: linear-gradient(135deg, #1A237E, #3F51B5) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(4) button { background: linear-gradient(135deg, #6200EA, #7C4DFF) !important; }

    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(1) button { background: linear-gradient(135deg, #4A148C, #8E24AA) !important; }
    .button-zone div[data-testid="button-zone"]:nth-of-type(2) > div:nth-child(2) button,
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(2) button { background: linear-gradient(135deg, #D50000, #FF1744) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(3) button { background: linear-gradient(135deg, #FFAB00, #FFD600) !important; color: #000000 !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(4) button { background: linear-gradient(135deg, #00B8D4, #00E5FF) !important; color: #000000 !important; }

    /* 4. FORM ZONE (STACKED VERTICALLY FOR ZERO HORIZONTAL SCROLL) */
    div[data-testid="stForm"] {
        border: 1px solid #CBD5E1;
        padding: 8px;
        border-radius: 10px;
        background-color: #F8FAFC;
    }

    div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: column !important; /* सर्व रकाने एकाखाली एक येतील */
        gap: 8px !important;
    }

    div[data-testid="stForm"] div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    .form-title-box {
        background: #0F172A;
        color: #FFD700;
        padding: 8px 10px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 800;
        border-left: 4px solid #FFD700;
        margin-top: 6px;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR CONFIGURATION
# ==========================================
st.sidebar.title("⚙️ आकांक्षा AI सेटिंग्ज")
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password", help="Google AI Studio मधील API Key टाका.")
st.sidebar.markdown("---")
st.sidebar.info("🏢 आकांक्षा एंटरप्रायझेस | RTI व कायदेशीर महा-सहाय्यक")

# ==========================================
# 4. TOP SHINY BRANDING BANNER
# ==========================================
st.markdown("""
    <div class='brand-top-banner'>
        <div><span class='free-dhamaka-tag'>🔥 फ्री धमाका 🔥</span></div>
        <div class='brand-title-1'>✨ आकांक्षा AI - RTI व कायदेशीर महा-सहाय्यक ✨</div>
        <div class='brand-title-2'>⚡ एका सेकंदात अर्ज A4 साईज मध्ये मिळवा ⚡</div>
        <div class='brand-title-3'>👤 सतीश अशोक प्रधान | 📱 मो. ८६६८२३५३९५</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. BUTTON ZONE (4 COLUMNS x 2 ROWS)
# ==========================================
st.markdown("<div class='button-zone'>", unsafe_allow_html=True)

r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1:
    if st.button("📄\nजोडपत्र 'अ'", key="b1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with r1_c2:
    if st.button("⚖️\nप्रथम अपील", key="b2"): st.session_state.active_tab = "प्रथम अपील"
with r1_c3:
    if st.button("🏛️\nमाहिती आयोग", key="b3"): st.session_state.active_tab = "माहिती आयोग"
with r1_c4:
    if st.button("✨\nAI चॅट", key="b4"): st.session_state.active_tab = "AI चॅट"

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
with r2_c1:
    if st.button("📜\nकोर्ट याचिका", key="b5"): st.session_state.active_tab = "कोर्ट याचिका"
with r2_c2:
    if st.button("📢\nशासकीय तक्रार", key="b6"): st.session_state.active_tab = "शासकीय तक्रार"
with r2_c3:
    if st.button("✏️\nप्रतिज्ञापत्र", key="b7"): st.session_state.active_tab = "प्रतिज्ञापत्र"
with r2_c4:
    if st.button("🛒\nग्राहक मंच", key="b8"): st.session_state.active_tab = "ग्राहक मंच"

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 6. A4 EXPORT ENGINES
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
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('A4Body', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.black, spaceAfter=5)
    
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
# 7. FORM ZONE (SELECTED TAB DISPLAY)
# ==========================================
curr = st.session_state.active_tab

if curr == "AI चॅट":
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
            st.error("⚠️ कृपया डाव्या Sidebar मध्ये Gemini API Key टाका!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.chat_message("assistant"):
                    with st.spinner("उत्तर तयार होत आहे..."):
                        response = model.generate_content(f"तुम्ही उच्च कायदेशीर सहाय्यक आहात. मराठीत उत्तर द्या: {user_query}")
                        st.write(response.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"❌ त्रुटी: {str(e)}")

else:
    titles = {
        "जोडपत्र 'अ'": "📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))",
        "प्रथम अपील": "⚖️ जोडपत्र 'ब' (प्रथम अपील अर्ज नियम ५(१))",
        "माहिती आयोग": "🏛️ जोडपत्र 'क' (द्वितीय अपील नियम ७(१))",
        "कोर्ट याचिका": "📜 न्यायालयीन मसुदा / याचिका अर्ज",
        "शासकीय तक्रार": "📢 प्रशासकीय व शासकीय तक्रार अर्ज",
        "प्रतिज्ञापत्र": "✏️ स्व-घोषणापत्र / प्रतिज्ञापत्र (Affidavit)",
        "ग्राहक मंच": "🛒 ग्राहक संरक्षण मंच तक्रार अर्ज"
    }
    
    st.markdown(f"<div class='form-title-box'>{titles.get(curr, curr)}</div>", unsafe_allow_html=True)

    with st.form(key="app_main_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            app_name = st.text_input("१. अर्जदाराचे नाव:", placeholder="अर्जदाराचे नाव प्रविष्ट करा...")
            app_address = st.text_area("२. पूर्ण पत्ता व मोबाईल नंबर:", placeholder="अर्जदाराचा पूर्ण पत्ता व मोबाईल नंबर प्रविष्ट करा...", height=100)
        
        with col2:
            auth_name = st.text_input("३. जन माहिती अधिकारी / विरोधी पक्ष / कार्यालय नाव:", placeholder="उदा. जन माहिती अधिकारी, मुख्य कार्यालय...")
            auth_address = st.text_area("४. कार्यालयाचा पूर्ण पत्ता:", placeholder="कार्यालयीन पत्ता प्रविष्ट करा...", height=100)

        if curr == "जोडपत्र 'अ'":
            subject = st.text_input("५. माहितीचा विषय:", value="माहितीचा अधिकार अधिनियम २००५ च्या कलम ६(१) अन्वये माहिती मिळणेबाबत.")
            info_details = st.text_area("६. मागितलेल्या माहितीचा सुटसुटीत तपशील (१, २, ३ मुद्दे लिहा):", height=120)
            period = st.text_input("७. माहितीचा कालावधी (उदा. २०२४ ते आजपर्यंत):")
            bpl = st.checkbox("अर्जदार दारिद्र्यरेषेखालील (BPL) आहे का?")

        elif curr == "प्रथम अपील":
            subject = st.text_input("५. प्रथम अपील प्राधिकरणाचे पदनाव:")
            info_details = st.text_area("६. अपीलाची मुख्य कारणे (मुद्देनिहाय):", height=120)
            period = st.text_input("७. मूळ जोडपत्र 'अ' सादर केल्याची तारीख:")

        elif curr == "माहिती आयोग":
            subject = st.text_input("५. माहिती आयोग खंडपीठ:", value="राज्य माहिती आयोग, महाराष्ट्र राज्य")
            info_details = st.text_area("६. प्रथम अपीलाचा निर्णय व द्वितीय अपीलाची कारणे:", height=120)
            period = st.text_input("७. प्रथम अपील सादर केल्याची तारीख:")

        else:
            subject = st.text_input("५. अर्ज / प्रकरणाचा विषय:")
            info_details = st.text_area("६. सविस्तर तपशील व मागण्या:", height=120)
            period = "लागू नाही"

        submit = st.form_submit_button(label="🚀 परिपूर्ण मसुदा तयार करा (Generate Draft)")

    if submit:
        if not api_key:
            st.error("⚠️ कृपया डाव्या Sidebar मध्ये Gemini API Key टाका!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                master_prompt = f"""
                तुम्ही महाराष्ट्रातील वरिष्ठ वकील व शासकीय कायदेशीर मसुदा तज्ज्ञ आहात.
                खालील माहितीचा वापर करून महाराष्ट्र शासन नियमांनुसार सुटसुटीत आणि पूर्ण १ पानावर (A4 Size Page Layout) बसणारा कायदेशीर मराठी मसुदा तयार करा:

                सेवा: {curr}
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
                    edited_draft = st.text_area("✏️ तयार झालेला मसुदा (संपादित करा):", value=draft_text, height=400)
                    
                    # Downloads
                    st.markdown("---")
                    st.subheader("📥 A4 Size डाऊनलोड पर्याय")
                    d1, d2 = st.columns(2)
                    
                    docx_bytes = create_a4_docx(edited_draft)
                    pdf_bytes = create_a4_pdf(edited_draft)
                    
                    with d1:
                        st.download_button("📄 Word (.docx) डाऊनलोड", data=docx_bytes, file_name=f"Draft_{curr}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    with d2:
                        st.download_button("📕 PDF (.pdf) डाऊनलोड", data=pdf_bytes, file_name=f"Draft_{curr}.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"❌ त्रुटी: {str(e)}")
