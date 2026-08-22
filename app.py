import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Inches, Pt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# ==========================================
# 1. PAGE CONFIG & EXACT UI STYLING (MATCHING ORIGINAL SCREENSHOT)
# ==========================================
st.set_page_config(
    page_title="RTI AI महा-सहाय्यक",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to replicate original UI colors and Grid Buttons
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
    }
    
    /* Header Styling */
    .main-title {
        text-align: center;
        color: #84CC16;
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .badge-sub {
        text-align: center;
        background-color: #FEF3C7;
        color: #D97706;
        border: 2px dashed #F59E0B;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        width: fit-content;
        margin: 0 auto 25px auto;
    }

    /* Grid Buttons Custom Styling */
    div.stButton > button {
        width: 100%;
        height: 85px;
        font-size: 16px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: transform 0.1s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
    }
    
    /* Form Header */
    .form-title {
        font-size: 22px;
        font-weight: bold;
        color: #111827;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State for Active Tab Management
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "जोडपत्र 'अ'"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ==========================================
# 2. SIDEBAR FOR API KEY & A4 SETTINGS
# ==========================================
st.sidebar.title("⚙️ सेटिंग्ज (Settings)")
api_key = st.sidebar.text_input("🔑 Gemini API Key प्रविष्ट करा:", type="password", help="Google AI Studio मधील API Key टाका.")
st.sidebar.info("💡 टीप: मुख्य स्क्रीनवरील कोणत्याही बटनावर क्लिक करून संबंधित अर्ज तयार करा.")

# ==========================================
# 3. HEADER SECTION
# ==========================================
st.markdown("<h1 class='main-title'>⚖️ RTI AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<div class='badge-sub'>⚡ घरबसल्या एका मिनिटात अर्ज तयार करा</div>", unsafe_allow_html=True)

# ==========================================
# 4. THE 8 GRID BUTTONS (EXACT 2x4 LAYOUT)
# ==========================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄\n\nजोडपत्र 'अ'", key="btn_jod_a"):
        st.session_state.active_tab = "जोडपत्र 'अ'"

with col2:
    if st.button("⚖️\n\nप्रथम अपील", key="btn_first_appeal"):
        st.session_state.active_tab = "प्रथम अपील"

with col3:
    if st.button("🏛️\n\nमाहिती आयोग", key="btn_second_appeal"):
        st.session_state.active_tab = "माहिती आयोग"

with col4:
    if st.button("✨\n\nAI चॅट", key="btn_ai_chat"):
        st.session_state.active_tab = "AI चॅट"

col5, col6, col7, col8 = st.columns(4)

with col5:
    if st.button("📜\n\nकोर्ट याचिका", key="btn_court"):
        st.session_state.active_tab = "कोर्ट याचिका"

with col6:
    if st.button("📢\n\nशासकीय तक्रार", key="btn_gov_complaint"):
        st.session_state.active_tab = "शासकीय तक्रार"

with col7:
    if st.button("✏️\n\nप्रतिज्ञापत्र", key="btn_affidavit"):
        st.session_state.active_tab = "प्रतिज्ञापत्र"

with col8:
    if st.button("🛒\n\nग्राहक मंच", key="btn_consumer"):
        st.session_state.active_tab = "ग्राहक मंच"

st.markdown("---")

# ==========================================
# 5. A4 FORMAT HELPER FUNCTIONS
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
        if line.strip():
            p = doc.add_paragraph(line.strip())
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_a4_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('A4Body', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.black, spaceAfter=6)
    
    story = []
    for line in text.split('\n'):
        clean = line.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if clean:
            story.append(Paragraph(clean, normal_style))
            story.append(Spacer(1, 3))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# 6. DYNAMIC FORM & CONTENT DISPLAY
# ==========================================
current_tab = st.session_state.active_tab

if current_tab == "AI चॅट":
    st.markdown("<div class='form-title'>✨ आकांक्षा AI कायदेशीर चॅट सहाय्यक</div>", unsafe_allow_html=True)
    st.write("कायदेशीर किंवा प्रशासकीय विषयावर प्रश्न विचारा (उदा. 'RTI मध्ये माहिती नाकारल्यास काय करावे?'):")
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_input = st.chat_input("तुमचा प्रश्न इथे टाईप करा...")
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        if not api_key:
            st.error("⚠️ कृपया आधी Sidebar मध्ये Gemini API Key प्रविष्ट करा!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.chat_message("assistant"):
                    with st.spinner("विचार करत आहे..."):
                        res = model.generate_content(f"तुम्ही उच्च कायदेशीर सहाय्यक आहात. मराठीत उत्तर द्या: {user_input}")
                        st.write(res.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"त्रुटी: {str(e)}")

else:
    # Form Headers matching exact labels
    titles_map = {
        "जोडपत्र 'अ'": "📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))",
        "प्रथम अपील": "⚖️ जोडपत्र 'ब' (प्रथम अपील अर्ज कलम १९(१))",
        "माहिती आयोग": "🏛️ जोडपत्र 'क' (द्वितीय अपील - राज्य माहिती आयोग)",
        "कोर्ट याचिका": "📜 न्यायालयीन मसुदा / याचिका अर्ज",
        "शासकीय तक्रार": "📢 प्रशासकीय व शासकीय तक्रार अर्ज",
        "प्रतिज्ञापत्र": "✏️ स्व-घोषणापत्र / प्रतिज्ञापत्र (Affidavit)",
        "ग्राहक मंच": "🛒 ग्राहक संरक्षण मंच तक्रार अर्ज"
    }
    
    st.markdown(f"<div class='form-title'>{titles_map.get(current_tab, current_tab)}</div>", unsafe_allow_html=True)

    with st.form(key="active_service_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            app_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:")
            app_address = st.text_area("२. पूर्ण पत्ता व फोन:", height=100)
        with col_b:
            auth_name = st.text_input("३. सार्वजनिक प्राधिकरण / कार्यालयाचे नाव:")
            auth_address = st.text_area("४. कार्यालयाचा पूर्ण पत्ता:", height=100)

        # Dynamic specific inputs
        if current_tab == "जोडपत्र 'अ'":
            subject = st.text_input("५. माहितीचा विषय:", value="माहितीचा अधिकार अधिनियम २००५ अन्वये माहिती मिळणेबाबत.")
            details = st.text_area("६. मागितलेल्या माहितीचा सुटसुटीत तपशील (१, २, ३ मुद्दे लिहा):", height=130)
            period = st.text_input("७. माहितीचा कालावधी (उदा. २०२३ ते २०२६):")
            bpl = st.checkbox("अर्जदार दारिद्र्यरेषेखालील (BPL) आहे का?")

        elif current_tab == "प्रथम अपील":
            subject = st.text_input("५. अपीलाचा विषय:", value="प्रथम अपील अर्ज माहिती अधिकार कायदा कलम १९(१)")
            details = st.text_area("६. अपीलाची मुख्य कारणे (माहिती न मिळणे / चुकीची मिळणे):", height=130)
            period = st.text_input("७. मूळ जोडपत्र 'अ' सादर केल्याची तारीख:")

        elif current_tab == "माहिती आयोग":
            subject = st.text_input("५. माहिती आयोग खंडपीठ:", value="राज्य माहिती आयोग, महाराष्ट्र राज्य")
            details = st.text_area("६. प्रथम अपील अधिकाऱ्याचा निर्णय व अपीलाचे आधार:", height=130)
            period = st.text_input("७. प्रथम अपील अर्ज केल्याची तारीख:")

        else:
            subject = st.text_input("५. अर्जाचा विषय / मुख्य मुद्दा:")
            details = st.text_area("६. सविस्तर माहिती / घटनाक्रम / मागणी:", height=130)
            period = "लागू नाही"

        submit = st.form_submit_button(label="🚀 परिपूर्ण अर्ज (Draft) तयार करा")

    if submit:
        if not api_key:
            st.error("⚠️ कृपया आधी डाव्या बाजूच्या Sidebar मध्ये Gemini API Key टाका!")
        elif not app_name:
            st.warning("⚠️ कृपया अर्जदाराचे नाव प्रविष्ट करा!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = f"""
                तुम्ही एक उच्च कायदेशीर व प्रशासकीय मसुदा तज्ज्ञ आहात.
                खालील माहितीचा वापर करून महाराष्ट्र शासन नियमांनुसार सुटसुटीत, अचूक आणि पूर्ण १ पानावर (A4 Size) बसणारा कायदेशीर मराठी मसुदा तयार करा:

                प्रकार: {current_tab}
                अर्जदाराचे नाव: {app_name}
                अर्जदाराचा पत्ता: {app_address}
                कार्यालयाचे नाव: {auth_name}
                कार्यालयाचा पत्ता: {auth_address}
                विषय: {subject}
                तपशील व मुद्दे: {details}
                कालावधी/तारीख: {period}

                नियम:
                १. जर जोडपत्र 'अ', 'ब' किंवा 'क' असेल तर महाराष्ट्र RTI नियम २००५ च्या अधिकृत सरकारी मसुद्याप्रमाणे संपूर्ण रकाने व मुद्दे समाविष्ट करा.
                २. मसुदा सुटसुटीत, वाचायला सोपा आणि A4 पानावर व्यवस्थित प्रिंट होईल असा तयार करा.
                """
                
                with st.spinner("⚡ AI द्वारे मसुदा तयार केला जात आहे..."):
                    res = model.generate_content(prompt)
                    draft_text = res.text
                    
                    st.success("✅ मसुदा यशस्वीरीत्या तयार झाला आहे!")
                    final_draft = st.text_area("✏️ मसुदा संपादित करा (Editable):", value=draft_text, height=400)
                    
                    # Downloads
                    st.subheader("📥 A4 Size डाऊनलोड करा")
                    d1, d2 = st.columns(2)
                    
                    docx_bytes = create_a4_docx(final_draft)
                    pdf_bytes = create_a4_pdf(final_draft)
                    
                    with d1:
                        st.download_button("📄 Word (.docx) डाऊनलोड", data=docx_bytes, file_name=f"{app_name}_Draft.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    with d2:
                        st.download_button("📕 PDF (.pdf) डाऊनलोड", data=pdf_bytes, file_name=f"{app_name}_Draft.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"❌ त्रुटी: {str(e)}")
