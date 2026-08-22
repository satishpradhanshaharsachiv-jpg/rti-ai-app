import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM COLORFUL CSS
# ==========================================
st.set_page_config(
    page_title="RTI AI महा-सहाय्यक",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS for Exact 8 Colorful Buttons & A4 Layout
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #FFFFFF;
        color: #111827;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Title & Badge Styling */
    .main-title {
        text-align: center;
        color: #84CC16;
        font-size: 34px;
        font-weight: 900;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    .badge-sub {
        text-align: center;
        background-color: #FEF3C7;
        color: #D97706;
        border: 2px dashed #F59E0B;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 15px;
        width: fit-content;
        margin: 0 auto 25px auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* General Button Layout */
    div.stButton > button {
        width: 100% !important;
        height: 95px !important;
        font-size: 17px !important;
        font-weight: 800 !important;
        border-radius: 16px !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.2s ease-in-out !important;
        white-space: pre-wrap !important;
        line-height: 1.3 !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2) !important;
    }

    /* Individual Color Codes matching Screenshot 2 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background: linear-gradient(135deg, #10B981, #059669) !important; /* Green - Jodpatra A */
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background: linear-gradient(135deg, #F97316, #EA580C) !important; /* Orange - First Appeal */
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        background: linear-gradient(135deg, #1E293B, #0F172A) !important; /* Dark Navy - Second Appeal */
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {
        background: linear-gradient(135deg, #6366F1, #4F46E5) !important; /* Indigo - AI Chat */
    }

    /* Row 2 Individual Colors */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(1) button {
        background: linear-gradient(135deg, #7C3AED, #6D28D9) !important; /* Purple - Court */
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(2) button {
        background: linear-gradient(135deg, #EF4444, #DC2626) !important; /* Red - Complaint */
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(3) button {
        background: linear-gradient(135deg, #F59E0B, #D97706) !important; /* Amber - Affidavit */
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(4) button {
        background: linear-gradient(135deg, #0284C7, #0369A1) !important; /* Cyan - Consumer */
    }

    /* Form Container Header */
    .form-header-box {
        font-size: 22px;
        font-weight: 800;
        color: #0F172A;
        border-bottom: 3px solid #E2E8F0;
        padding-bottom: 10px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .badge-info-box {
        background-color: #F1F5F9;
        border-left: 5px solid #0284C7;
        padding: 12px;
        border-radius: 6px;
        font-size: 14px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "जोडपत्र 'अ'"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "generated_history" not in st.session_state:
    st.session_state.generated_history = []

# ==========================================
# 2. SIDEBAR - API CONFIGURATION & HISTORY
# ==========================================
st.sidebar.title("⚙️ सेटिंग्ज व पर्याय")
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password", help="Google AI Studio मधील तुमची Gemini API Key येथे प्रविष्ट करा.")

st.sidebar.markdown("---")
st.sidebar.subheader("📜 मसुदा इतिहास")
if st.session_state.generated_history:
    st.sidebar.success(f"एकूण मसुदे: {len(st.session_state.generated_history)}")
    if st.sidebar.button("🗑️ इतिहास साफ करा"):
        st.session_state.generated_history = []
        st.rerun()
else:
    st.sidebar.info("अजून कोणताही मसुदा जनरेट केलेला नाही.")

st.sidebar.markdown("---")
st.sidebar.caption("🏢 **आकांक्षा AI महा-सहाय्यक** | A4 लेआउट व कायदेशीर मानकांसह")

# ==========================================
# 3. HEADER SECTION
# ==========================================
st.markdown("<h1 class='main-title'>⚖️ RTI AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<div class='badge-sub'>⚡ घरबसल्या एका मिनिटात अर्ज तयार करा</div>", unsafe_allow_html=True)

# ==========================================
# 4. COLORFUL GRID BUTTONS (EXACT 8 BUTTONS)
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
# 5. A4 EXPORT HELPER FUNCTIONS (DOCX & PDF)
# ==========================================
def create_a4_docx(text, title="कायदेशीर मसुदा"):
    doc = Document()
    
    # Standard A4 Layout (8.27 x 11.69 inches) with 0.75 inch margin
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    for line in text.split('\n'):
        clean_line = line.strip()
        if clean_line:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(clean_line)
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
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
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
# 6. DYNAMIC SERVICE FORMS & AI LOGIC
# ==========================================
current_tab = st.session_state.active_tab

if current_tab == "AI चॅट":
    st.markdown("<div class='form-header-box'>✨ आकांक्षा AI कायदेशीर चॅट सहाय्यक</div>", unsafe_allow_html=True)
    st.markdown("<div class='badge-info-box'>💡 माहिती अधिकार, शासकीय तक्रारी, किंवा कायदेशीर कलमांबद्दल कोणताही प्रश्न मराठीत विचारा.</div>", unsafe_allow_html=True)
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_query = st.chat_input("तुमचा प्रश्न येथे टाईप करा...")
    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
            
        if not api_key:
            st.error("⚠️ कृपया डाव्या बाजूच्या Sidebar मध्ये Gemini API Key प्रविष्ट करा!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.chat_message("assistant"):
                    with st.spinner("उत्तर शोधत आहे..."):
                        system_context = f"तुम्ही महाराष्ट्रातील वरिष्ठ वकील व कायदेशीर तज्ज्ञ आहात. नागरिकांना अत्यंत सोप्या व अचूक मराठीत मार्गदर्शन करा. प्रश्न: {user_query}"
                        response = model.generate_content(system_context)
                        st.write(response.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"❌ त्रुटी: {str(e)}")

else:
    tab_titles = {
        "जोडपत्र 'अ'": "📄 जोडपत्र 'अ' (माहितीचा अधिकार अर्ज नियम ३)",
        "प्रथम अपील": "⚖️ जोडपत्र 'ब' (प्रथम अपील अर्ज नियम ५(१))",
        "माहिती आयोग": "🏛️ जोडपत्र 'क' (द्वितीय अपील - नियम ७(१))",
        "कोर्ट याचिका": "📜 न्यायालयीन मसुदा / याचिका अर्ज (Court Petition)",
        "शासकीय तक्रार": "📢 प्रशासकीय व शासकीय तक्रार अर्ज",
        "प्रतिज्ञापत्र": "✏️ स्व-घोषणापत्र / प्रतिज्ञापत्र (Affidavit)",
        "ग्राहक मंच": "🛒 ग्राहक संरक्षण मंच तक्रार अर्ज (Consumer Forum)"
    }
    
    st.markdown(f"<div class='form-header-box'>{tab_titles.get(current_tab, current_tab)}</div>", unsafe_allow_html=True)

    with st.form(key="active_form"):
        col_left, col_right = st.columns(2)
        
        with col_left:
            app_name = st.text_input("१. अर्जदाराचे / तक्रारदाराचे पूर्ण नाव:", placeholder="उदा. सतीश अशोक प्रधान")
            app_address = st.text_area("२. अर्जदाराचा पूर्ण पत्ता व संपर्क क्रमांक:", height=110, placeholder="घर क्र., रस्ता, परिसर, शहर, पिनकोड व मोबाईल...")
        
        with col_right:
            auth_name = st.text_input("३. जन माहिती अधिकारी / विरोधी पक्ष / कार्यालय नाव:", placeholder="उदा. जन माहिती अधिकारी, मुख्य कार्यालय...")
            auth_address = st.text_area("४. संबंधित कार्यालयाचा पूर्ण पत्ता:", height=110, placeholder="कार्यालयाचे नाव, विभाग, शहर, पिनकोड...")

        # Specific Inputs per Tab
        if current_tab == "जोडपत्र 'अ'":
            st.markdown("---")
            subject = st.text_input("५. माहितीचा विषय:", value="माहितीचा अधिकार अधिनियम २००५ च्या कलम ६(१) अन्वये माहिती मिळणेबाबत.")
            info_points = st.text_area("६. मागितलेल्या माहितीचा तपशील (मुद्दे क्र. १, २, ३ बनवा):", height=140, placeholder="१. कामाची मंजूर मूळ नस्ती / फाईल प्रत...\n२. ई-निविदा प्रक्रिया व कंत्राटदार करारनामा...\n३. मोजमाप पुस्तिका (MB Book) साक्षांकित प्रत...")
            period = st.text_input("७. माहितीचा कालावधी:", placeholder="उदा. १ जानेवारी २०२४ ते आजपर्यंत")
            post_method = st.selectbox("८. माहिती मिळण्याचा मार्ग:", ["नोंदणीकृत टपालाने (Registered Post)", "प्रत्यक्ष हातोहात (By Hand)", "ईमेलद्वारे (By Email)"])
            bpl_status = st.checkbox("अर्जदार दारिद्र्यरेषेखालील (BPL) आहे का?")
            bpl_no = st.text_input("BPL कार्ड क्रमांक (BPL असल्यास लिहा):") if bpl_status else "लागू नाही"
            
            payload_details = f"माहिती विषय: {subject}\nमाहितीचे मुद्दे:\n{info_points}\nकालावधी: {period}\nमार्ग: {post_method}\nBPL: {bpl_no}"

        elif current_tab == "प्रथम अपील":
            st.markdown("---")
            subject = st.text_input("५. प्रथम अपील प्राधिकरणाचे पदनाव:", placeholder="उदा. मा. प्रथम अपील अधिकारी / उपायुक्त...")
            original_rti_date = st.text_input("६. मूळ RTI अर्ज (जोडपत्र अ) सादर केल्याची तारीख:")
            pio_reply = st.text_area("७. जन माहिती अधिकाऱ्याचे उत्तर / पत्र क्रमांक व तारीख (माहिती न मिळाल्यास 'उत्तर प्राप्त नाही' लिहा):")
            appeal_reasons = st.text_area("८. प्रथम अपीलाची मुख्य कारणे:", height=120, placeholder="१. मुदतीत माहिती न पुरवणे...\n२. चुकीची व अपूर्ण माहिती देणे...")
            
            payload_details = f"प्रथम अपील अधिकारी: {subject}\nमूल RTI अर्ज तारीख: {original_rti_date}\nPIO उत्तर: {pio_reply}\nअपील कारणे:\n{appeal_reasons}"

        elif current_tab == "माहिती आयोग":
            st.markdown("---")
            commission_bench = st.text_input("५. माहिती आयोग खंडपीठ:", value="राज्य माहिती आयोग, महाराष्ट्र राज्य")
            first_appeal_date = st.text_input("६. प्रथम अपील सादर केल्याची तारीख:")
            first_order = st.text_area("७. प्रथम अपील अधिकाऱ्याचा निर्णय / आदेश (तारीख व तपशील):")
            second_grounds = st.text_area("८. द्वितीय अपीलाची मुख्य कारणे व कायदेशीर मुद्दे:", height=120)
            penalty_req = st.checkbox("कलम २० अन्वये दंडात्मक कारवाई व departmental enquiry ची मागणी समाविष्ट करा")
            
            payload_details = f"माहिती आयोग: {commission_bench}\nप्रथम अपील तारीख: {first_appeal_date}\nप्रथम अपील आदेश: {first_order}\nद्वितीय अपील कारणे:\n{second_grounds}\nकलम २० कारवाई: {'होय' if penalty_req else 'नाही'}"

        elif current_tab == "कोर्ट याचिका":
            st.markdown("---")
            court_name = st.text_input("५. न्यायालयाचे नाव:", placeholder="उदा. मा. मुख्य न्यायदंडधिकारी, छत्रपती संभाजीनगर")
            case_type = st.text_input("६. दावा / अर्ज प्रकार व कलमे:")
            facts = st.text_area("७. प्रकरणाची थोडक्यात तथ्ये व कारणे:", height=130)
            prayer = st.text_area("८. अंतिम विनंती / मागणूक (Prayer):", height=100)
            
            payload_details = f"न्यायालय: {court_name}\nदावा/कलम: {case_type}\nतथ्ये:\n{facts}\nविनंती:\n{prayer}"

        elif current_tab == "शासकीय तक्रार":
            st.markdown("---")
            subject = st.text_input("५. तक्रारीचा मुख्य विषय:")
            chronology = st.text_area("६. घटनाक्रम व सविस्तर तक्रार तपशील:", height=140)
            action_required = st.text_area("७. मागितलेली कायदेशीर / प्रशासकीय कारवाई:")
            
            payload_details = f"विषय: {subject}\nघटनाक्रम:\n{chronology}\nमागणी:\n{action_required}"

        elif current_tab == "प्रतिज्ञापत्र":
            st.markdown("---")
            purpose = st.text_input("५. प्रतिज्ञापत्राचे कारण / उद्देश:", placeholder="उदा. नाव बदलणे, कौटुंबिक, वाहन हस्तांतरण...")
            statements = st.text_area("६. प्रतिज्ञापत्रातील मुख्य विधाने (१, २, ३ मुद्द्यांमध्ये):", height=140)
            
            payload_details = f"उद्देश: {purpose}\nविधाने:\n{statements}"

        else: # Consumer
            st.markdown("---")
            product = st.text_input("५. खरेदी केलेली वस्तू / सेवा:")
            purchase_info = st.text_input("६. खरेदी तारीख व भरलेली एकूण रक्कम (रु.):")
            defects = st.text_area("७. वस्तू/सेवेतील त्रुटी व फसवणुकीचा तपशील:", height=130)
            compensation = st.text_input("८. मागितलेली नुकसान भरपाई रक्कम (रु.):")
            
            payload_details = f"वस्तू/सेवा: {product}\nखरेदी तपशील: {purchase_info}\nत्रुटी:\n{defects}\nभरपाई मागणी: {compensation}"

        submit_btn = st.form_submit_button(label="🚀 परिपूर्ण मसुदा तयार करा (Generate Draft)")

    # Processing AI Generation
    if submit_btn:
        if not api_key:
            st.error("⚠️ कृपया आधी Sidebar मध्ये तुमची Gemini API Key प्रविष्ट करा!")
        elif not app_name or not app_address:
            st.warning("⚠️ कृपया अर्जदाराचे नाव आणि पत्ता नक्की भरा!")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                master_prompt = f"""
                तुम्ही महाराष्ट्रातील वरिष्ठ वकील आणि शासकीय कायदेशीर मसुदा तज्ज्ञ आहात.
                खालील माहितीचा वापर करून महाराष्ट्र शासन नियमांनुसार अचूक, सुटसुटीत आणि पूर्ण १ पानावर (A4 Size Page Layout) बसणारा कायदेशीर मराठी मसुदा तयार करा.

                === अर्जाचा प्रकार ===
                {current_tab}

                === पक्षकारांचा तपशील ===
                अर्जदार/तक्रारदार: {app_name}
                अर्जदाराचा पत्ता व संपर्क: {app_address}
                विरोधी पक्ष/अधिकारी/विभाग: {auth_name}
                कार्यालयीन पत्ता: {auth_address}

                === प्रकरणाचा तपशील ===
                {payload_details}

                === कायदेशीर व फॉरमॅटिंग सूचना ===
                १. जर अर्ज माहिती अधिकार (RTI) असेल तर महाराष्ट्र माहितीचा अधिकार नियम २००५ मधील **जोडपत्र 'अ', जोडपत्र 'ब' किंवा जोडपत्र 'क'** चा सर्व अधिकृत सरकारी नमुना हुबेहूब समाविष्ट करा.
                २. परिच्छेद अत्यंत सुटसुटीत, मुदद्देसूद आणि पूर्ण A4 पानावर व्यवस्थित बसणारे असावेत.
                ३. शीर्षक, प्रति, विषय, संदर्भ, मुख्य मजकूर, सत्यप्रतिज्ञा (Verification), तारीख, ठिकाण आणि अर्जदाराची स्वाक्षरी हे सर्व समाविष्ट करा.
                ४. कायदेशीर कलमे (उदा. RTI Act Sec 6(1), Sec 19(1), Sec 19(3), Sec 20) अचूक ठिकाणी वापरा.
                ५. भाषा अत्यंत स्पष्ट, शुद्ध आणि कायदेशीर मराठी असावी.
                """

                with st.spinner("⚡ AI द्वारे परिपूर्ण A4 मसुदा तयार होत आहे..."):
                    response = model.generate_content(master_prompt)
                    generated_draft = response.text
                    
                    st.success("✅ मसुदा यशस्वीरीत्या तयार झाला आहे!")
                    
                    # Editable Draft Text Box
                    edited_draft = st.text_area("✏️ तयार झालेला मसुदा (हवे असल्यास बदल करा):", value=generated_draft, height=450)
                    
                    # Save to History
                    st.session_state.generated_history.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "tab": current_tab,
                        "name": app_name,
                        "content": edited_draft
                    })

                    # Download Buttons
                    st.markdown("---")
                    st.subheader("📥 A4 Size डाऊनलोड पर्याय")
                    d_col1, d_col2 = st.columns(2)
                    
                    docx_bytes = create_a4_docx(edited_draft)
                    pdf_bytes = create_a4_pdf(edited_draft)
                    
                    with d_col1:
                        st.download_button(
                            label="📄 Word (.docx) डाऊनलोड",
                            data=docx_bytes,
                            file_name=f"{app_name}_{current_tab}_Draft.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    
                    with d_col2:
                        st.download_button(
                            label="📕 PDF (.pdf) डाऊनलोड",
                            data=pdf_bytes,
                            file_name=f"{app_name}_{current_tab}_Draft.pdf",
                            mime="application/pdf"
                        )

            except Exception as e:
                st.error(f"❌ त्रुटी आली: {str(e)}")

# History Expander at bottom
if st.session_state.generated_history:
    st.markdown("---")
    with st.expander("📜 या सत्रातील तयार केलेले जुने मसुदे पहा"):
        for idx, item in enumerate(reversed(st.session_state.generated_history)):
            st.markdown(f"**#{len(st.session_state.generated_history)-idx} - {item['tab']} ({item['name']}) - {item['time']}**")
            st.text_area(f"मसुदा {idx+1}", value=item['content'], height=150, key=f"hist_down_{idx}")
