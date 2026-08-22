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
    page_title="सतीश अशोक प्रधान - आकांक्षा AI",
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
# 2. RESPONSIVE CSS (PREVENT HORIZONTAL SCROLL)
# ==========================================
st.markdown("""
    <style>
    /* Strict Screen Overflow Lock - Removes Horizontal Scroll */
    html, body, .stApp {
        overflow-x: hidden !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        background-color: #FFFFFF;
        color: #0F172A;
    }

    /* Main Outer Header Banner */
    .brand-banner {
        text-align: center;
        background: linear-gradient(135deg, #0B0F19, #1E1B4B, #312E81);
        padding: 16px 10px;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        margin-bottom: 15px;
        border: 2px solid #FFD700;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    /* 1. Multi-color Animated Golden Title */
    .banner-main-title {
        font-size: 21px;
        font-weight: 900;
        background: linear-gradient(45deg, #FFD700, #FFA500, #FF3366, #00E5FF, #FFD700);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shinyGradient 4s ease infinite;
        margin-bottom: 4px;
        line-height: 1.3;
    }

    @keyframes shinyGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. Colorful Tagline */
    .banner-sub-title {
        font-size: 15px;
        font-weight: 800;
        color: #00FFCC;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.7);
        margin-bottom: 8px;
    }

    /* 3. Shiny Golden Contact Strip */
    .banner-contact-strip {
        background: linear-gradient(90deg, #B8860B, #FFD700, #FFF8DC, #FFD700, #B8860B);
        color: #000000;
        font-weight: 800;
        font-size: 12.5px;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(255, 215, 0, 0.6);
        letter-spacing: 0.3px;
    }

    /* Mobile View CSS (Perfect 2x4 Grid without Horizontal Overflow) */
    @media only screen and (max-width: 768px) {
        .banner-main-title { font-size: 17px; }
        .banner-sub-title { font-size: 13px; }
        .banner-contact-strip { font-size: 11px; padding: 3px 8px; }

        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 3px !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        div[data-testid="column"] {
            width: 24% !important;
            flex: 1 1 24% !important;
            min-width: 0px !important;
            padding: 0px !important;
        }
        div.stButton > button {
            height: 65px !important;
            font-size: 10px !important;
            padding: 2px !important;
            border-radius: 8px !important;
            line-height: 1.1 !important;
        }
    }

    /* Desktop View CSS */
    @media only screen and (min-width: 769px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 10px !important;
        }
        div.stButton > button {
            height: 80px !important;
            font-size: 14px !important;
            border-radius: 12px !important;
        }
    }

    /* Vibrant Buttons Styling */
    div.stButton > button {
        width: 100% !important;
        font-weight: 800 !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        white-space: pre-wrap !important;
    }

    /* Button Gradients */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(1) button { background: linear-gradient(135deg, #00C853, #00E676) !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(2) button { background: linear-gradient(135deg, #FF6D00, #FF9100) !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(3) button { background: linear-gradient(135deg, #1A237E, #3F51B5) !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(4) button { background: linear-gradient(135deg, #6200EA, #7C4DFF) !important; }

    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(1) button { background: linear-gradient(135deg, #4A148C, #8E24AA) !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(2) button { background: linear-gradient(135deg, #D50000, #FF1744) !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(3) button { background: linear-gradient(135deg, #FFAB00, #FFD600) !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(4) button { background: linear-gradient(135deg, #00B8D4, #00E5FF) !important; }

    .form-title {
        font-size: 17px;
        font-weight: 800;
        color: #0F172A;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 6px;
        margin-top: 10px;
        margin-bottom: 12px;
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
# 4. TOP BRANDING BANNER
# ==========================================
st.markdown("""
    <div class='brand-banner'>
        <div class='banner-main-title'>✨ आकांक्षा AI - RTI व कायदेशीर महा-सहाय्यक ✨</div>
        <div class='banner-sub-title'>⚡ एका सेकंदात अर्ज A4 साईज मध्ये मिळवा ⚡</div>
        <div class='banner-contact-strip'>सतीश अशोक प्रधान | मो. ८६६८२३५३९५</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 8 VIBRANT BUTTONS (2x4 GRID)
# ==========================================
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

st.markdown("---")

# ==========================================
# 6. A4 EXPORT ENGINES (DOCX & PDF)
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
# 7. FORM & GENERATION ENGINE
# ==========================================
curr = st.session_state.active_tab

if curr == "AI चॅट":
    st.markdown("<div class='form-title'>✨ आकांक्षा AI कायदेशीर चॅट महा-सहाय्यक</div>", unsafe_allow_html=True)
    
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
    
    st.markdown(f"<div class='form-title'>{titles.get(curr, curr)}</div>", unsafe_allow_html=True)

    with st.form(key="app_main_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            app_name = st.text_input("१. अर्जदाराचे नाव:", placeholder="अर्जदाराचे नाव टाका...")
            app_address = st.text_area("२. पूर्ण पत्ता व मोबाईल नंबर:", placeholder="अर्जदाराचा पत्ता व संपर्क टाका...", height=100)
        
        with col2:
            auth_name = st.text_input("३. जन माहिती अधिकारी / विरोधी पक्ष / कार्यालय नाव:", placeholder="उदा. जन माहिती अधिकारी, मुख्य कार्यालय...")
            auth_address = st.text_area("४. कार्यालयाचा पूर्ण पत्ता:", placeholder="कार्यालयीन पत्ता टाका...", height=100)

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
