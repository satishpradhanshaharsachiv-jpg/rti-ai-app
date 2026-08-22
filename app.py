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
# 1. PAGE CONFIGURATION & CUSTOM CSS (FAST & RESPONSIVE)
# ==========================================
st.set_page_config(
    page_title="आकांक्षा AI - कायदेशीर व प्रशासकीय महा-सहाय्यक",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Dark Modern Theme and Mobile Optimization
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #00E676;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 26px;
        font-weight: bold;
        padding: 10px;
        background: linear-gradient(90deg, #111827, #1F2937);
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 20px;
    }
    .sub-title {
        text-align: center;
        color: #9CA3AF;
        font-size: 14px;
        margin-top: -10px;
    }
    .stButton>button {
        width: 100%;
        background-color: #10B981;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 17px;
        font-weight: bold;
        padding: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #059669;
        transform: translateY(-1px);
    }
    .badge-info {
        background-color: #1E293B;
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State for History
if "draft_history" not in st.session_state:
    st.session_state.draft_history = []

# Title Section
st.markdown("<div class='main-title'>⚖️ आकांक्षा AI कायदेशीर व प्रशासकीय महा-सहाय्यक<br><p class='sub-title'>माहिती अधिकार (जोडपत्र अ, ब, क), अपील, तक्रार अर्ज व कायदेशीर मसुदा जनरेटर</p></div>", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR - API KEY & NAVIGATION
# ==========================================
st.sidebar.title("⚙️ सेटिंग्ज व सेवा")
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password", help="Google AI Studio मधील API Key टाका.")

service_option = st.sidebar.selectbox(
    "📋 सेवा निवडा (Select Legal Service):",
    [
        "१. माहिती अधिकार अर्ज - जोडपत्र 'अ' (RTI Form A)",
        "२. प्रथम अपील अर्ज - जोडपत्र 'ब' (First Appeal Form B)",
        "३. द्वितीय अपील अर्ज - जोडपत्र 'क' (Second Appeal Form C)",
        "४. प्रशासकीय व शासकीय तक्रार अर्ज",
        "५. ग्राहक मंच तक्रार अर्ज (Consumer Complaint)",
        "६. प्रतिज्ञापत्र मसुदा (Affidavit)",
        "७. कायदेशीर नोटीस (Legal Notice)",
        "८. न्यायालयीन मसुदा / याचिका (Court Application)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📜 मसुदा इतिहास (Draft History)")
if st.session_state.draft_history:
    st.sidebar.success(f"एकूण तयार मसुदे: {len(st.session_state.draft_history)}")
    if st.sidebar.button("🗑️ इतिहास साफ करा"):
        st.session_state.draft_history = []
        st.rerun()
else:
    st.sidebar.info("अजून कोणताही मसुदा तयार केलेला नाही.")

# ==========================================
# 3. A4 EXPORT GENERATORS (DOCX & PDF)
# ==========================================
def create_a4_docx(text, title="कायदेशीर मसुदा"):
    doc = Document()
    
    # Set Exact A4 Page Layout (210mm x 297mm) with 0.75 inch margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    p = doc.add_paragraph()
    p_format = p.paragraph_format
    p_format.space_after = Pt(6)
    p_format.line_spacing = 1.15
    
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
    # Standard A4 Document with precise margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'A4Body',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.black,
        spaceAfter=6
    )
    
    story = []
    for line in text.split('\n'):
        clean_line = line.strip()
        if clean_line:
            # Escape XML special characters for safety in ReportLab
            clean_line = clean_line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(clean_line, normal_style))
            story.append(Spacer(1, 3))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# 4. SERVICE FORM INPUTS
# ==========================================
st.subheader(f"✍️ {service_option}")

prompt_details = ""
applicant_name = ""

with st.form(key="legal_service_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        applicant_name = st.text_input("अर्जदाराचे / तक्रारदाराचे पूर्ण नाव:", placeholder="उदा. सतीश अशोक प्रधान")
        applicant_address = st.text_area("अर्जदाराचा पूर्ण पत्ता व मोबाईल क्र.:", height=100, placeholder="पत्ता, पिनकोड आणि भ्रमणध्वनी क्रमांक...")
    
    with col2:
        authority_name = st.text_input("जन माहिती अधिकारी / विरोधी पक्ष / कार्यालय नाव:", placeholder="उदा. जन माहिती अधिकारी, महानगरपालिका...")
        authority_address = st.text_area("कार्यालयाचा पूर्ण पत्ता:", height=100, placeholder="संबंधित कार्यालयाचा पूर्ण पत्ता...")

    # Dynamic Fields for RTI Jodpatra A, B, C & Legal Services
    if "जोडपत्र 'अ'" in service_option:
        st.markdown("<div class='badge-info'>📌 <b>माहितीचा अधिकार नियम २००५ - जोडपत्र 'अ' (नियम ३)</b></div>", unsafe_allow_html=True)
        subject = st.text_input("माहितीचा विषय:", value="माहितीचा अधिकार अधिनियम २००५ च्या कलम ६(१) अन्वये माहिती मिळणेबाबत.")
        info_points = st.text_area("मागितलेल्या माहितीचा तपशील (सुटसुटीत मुद्दे १, २, ३ लिहा):", height=150, placeholder="१. कामाची मंजूर मूळ नस्ती / फाईल प्रत...\n२. ई-निविदा प्रक्रिया व कंत्राटदार करारनामा...\n३. मोजमाप पुस्तिका (MB Book) साक्षांकित प्रत...")
        period = st.text_input("माहितीचा कालावधी (उदा. १ जानेवारी २०२४ ते आजपर्यंत):")
        post_or_person = st.selectbox("माहिती मिळण्याचा प्रकार:", ["टपालाने (Registered Post)", "प्रत्यक्ष हातोहात (By Hand)", "ईमेलद्वारे (By Email)"])
        bpl_status = st.checkbox("अर्जदार दारिद्र्यरेषेखालील (BPL) आहे का?")
        bpl_card_no = st.text_input("BPL कार्ड क्रमांक (BPL असल्यास लिहा):") if bpl_status else "लागू नाही"
        
        prompt_details = f"फॉर्म प्रकार: जोडपत्र 'अ'\nविषय: {subject}\nमाहितीचे मुद्दे:\n{info_points}\nकालावधी: {period}\nमाहिती मिळण्याचा मार्ग: {post_or_person}\nBPL माहिती: {bpl_card_no}"

    elif "जोडपत्र 'ब'" in service_option:
        st.markdown("<div class='badge-info'>📌 <b>प्रथम अपील - जोडपत्र 'ब' (नियम ५(१))</b></div>", unsafe_allow_html=True)
        first_appellate_auth = st.text_input("प्रथम अपील प्राधिकरणाचे पदनाव व नाव:", placeholder="उदा. मा. प्रथम अपील अधिकारी / उपायुक्त...")
        original_rti_date = st.text_input("मूल RTI अर्ज (जोडपत्र अ) सादर केल्याची तारीख:")
        pio_reply_details = st.text_area("जन माहिती अधिकाऱ्याचे उत्तर / पत्र (मिळाले असल्यास पत्र क्र. व तारीख किंवा न मिळाल्यास 'माहिती मिळालेली नाही' लिहा):")
        appeal_grounds = st.text_area("प्रथम अपीलाची मुख्य कारणे (मुद्देनिहाय):", height=120, placeholder="१. मुदतीत माहिती न पुरवणे...\n२. चुकीची व अपूर्ण माहिती देणे...\n३. बेकायदेशीर शुल्क मागणी करणे...")
        
        prompt_details = f"फॉर्म प्रकार: जोडपत्र 'ब' (प्रथम अपील)\nप्रथम अपील अधिकारी: {first_appellate_auth}\nमूल RTI अर्ज तारीख: {original_rti_date}\nPIO उत्तर तपशील: {pio_reply_details}\nअपीलाची कारणे:\n{appeal_grounds}"

    elif "जोडपत्र 'क'" in service_option:
        st.markdown("<div class='badge-info'>📌 <b>द्वितीय अपील - जोडपत्र 'क' (नियम ७(१))</b></div>", unsafe_allow_html=True)
        commission_bench = st.text_input("माहिती आयोग खंडपीठ:", value="राज्य माहिती आयोग, महाराष्ट्र राज्य")
        first_appeal_date = st.text_input("प्रथम अपील सादर केल्याची तारीख:")
        first_order_details = st.text_area("प्रथम अपील अधिकाऱ्याचा आदेश / निर्णय (तारीख व तपशील):")
        second_appeal_grounds = st.text_area("द्वितीय अपीलाची कारणे व कायदेशीर मुद्दे:", height=120)
        penalty_prayer = st.checkbox("कलम २० अन्वये दंडात्मक कारवाई व विभागीय चौकशीची मागणी करायची आहे का?")
        
        prompt_details = f"फॉर्म प्रकार: जोडपत्र 'क' (द्वितीय अपील)\nमाहिती आयोग: {commission_bench}\nप्रथम अपील तारीख: {first_appeal_date}\nप्रथम अपील आदेश: {first_order_details}\nअपील कारणे:\n{second_appeal_grounds}\nकलम २० कारवाई मागणी: {'होय' if penalty_prayer else 'नाही'}"

    elif "प्रशासकीय व शासकीय तक्रार" in service_option:
        subject = st.text_input("तक्रारीचा मुख्य विषय:")
        incident_details = st.text_area("घटनाक्रम व तक्रारीचा सविस्तर तपशील:", height=140)
        action_demanded = st.text_area("मागितलेली प्रशासकीय / कायदेशीर कारवाई:")
        prompt_details = f"विषय: {subject}\nघटनाक्रम व तपशील:\n{incident_details}\nमागणी:\n{action_demanded}"

    elif "ग्राहक मंच" in service_option:
        product_service = st.text_input("खरेदी केलेली वस्तू / सेवा:")
        purchase_date_cost = st.text_input("खरेदी तारीख व भरलेली एकूण रक्कम (रु.):")
        defect_description = st.text_area("वस्तू/सेवेतील त्रुटी व फसवणुकीचा तपशील:", height=130)
        claim_amount = st.text_input("मागितलेली भरपाई रक्कम (नुकसान भरपाई + मानसिक त्रास):")
        prompt_details = f"वस्तू/सेवा: {product_service}\nखरेदी तारीख/रक्कम: {purchase_date_cost}\nत्रुटी/फसवणूक:\n{defect_description}\nभरपाई मागणी: {claim_amount}"

    elif "प्रतिज्ञापत्र" in service_option:
        purpose = st.text_input("प्रतिज्ञापत्राचे कारण (उदा. नाव बदलणे, कौटुंबिक, वाहन हस्तांतरण):")
        statements = st.text_area("प्रतिज्ञापत्रातील मुख्य विधाने (१, २, ३ असे द्या):", height=140)
        prompt_details = f"उद्देश: {purpose}\nविधाने:\n{statements}"

    elif "कायदेशीर नोटीस" in service_option:
        notice_subject = st.text_input("नोटीसचा विषय:")
        facts = st.text_area("वादाची पार्श्वभूमी व तथ्ये:", height=130)
        notice_time = st.text_input("प्रतिसादाची मुदत (उदा. १५ दिवस):", value="१५ दिवस")
        demand = st.text_area("अंतिम कायदेशीर मागणी:")
        prompt_details = f"विषय: {notice_subject}\nतथ्ये:\n{facts}\nमुदत: {notice_time}\nमागणी:\n{demand}"

    else: # Court Application
        court_name = st.text_input("न्यायालयाचे नाव (उदा. मा. मुख्य न्यायदंडधिकारी, छत्रपती संभाजीनगर):")
        case_section = st.text_input("दावा / कलमाचा प्रकार:")
        facts_court = st.text_area("प्रकरणाची थोडक्यात तथ्ये व कारणे:", height=130)
        prayer = st.text_area("अंतिम विनंती (Prayer):")
        prompt_details = f"न्यायालय: {court_name}\nदावा/कलम: {case_section}\nतथ्ये:\n{facts_court}\nविनंती:\n{prayer}"

    submit_button = st.form_submit_button(label="⚡ परिपूर्ण मसुदा तयार करा (Generate Draft)")

# ==========================================
# 5. AI GENERATION ENGINE (GEMINI 2.5 FLASH)
# ==========================================
if submit_button:
    if not api_key:
        st.error("⚠️ कृपया आधी Sidebar मध्ये तुमची Gemini API Key प्रविष्ट करा!")
    elif not applicant_name or not applicant_address:
        st.warning("⚠️ कृपया अर्जदाराचे नाव आणि पत्ता नक्की भरा!")
    else:
        try:
            genai.configure(api_key=api_key)
            # Ultra Fast Speed with Gemini 2.5 Flash
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            master_prompt = f"""
            तुम्ही एक उच्च विद्याविभूषित वरिष्ठ वकील आणि शासकीय कायदेशीर मसुदा तज्ज्ञ आहात.
            खालील माहितीचा वापर करून महाराष्ट्र शासन नियमांनुसार अचूक, सुटसुटीत आणि पूर्ण A4 पान भरेल असा कायदेशीर मराठी मसुदा तयार करा.

            === सेवेचा प्रकार ===
            {service_option}

            === पक्षकारांचा तपशील ===
            अर्जदार/तक्रारदार: {applicant_name}
            अर्जदाराचा पत्ता व संपर्क: {applicant_address}
            विरोधी पक्ष/अधिकारी/विभाग: {authority_name}
            कार्यालयाचा पत्ता: {authority_address}

            === प्रकरणाचा तपशील ===
            {prompt_details}

            === महत्त्वाच्या कायदेशीर फॉरमॅटिंग सूचना ===
            १. जर अर्ज माहिती अधिकार (RTI) असेल, तर महाराष्ट्र माहितीचा अधिकार नियम २००५ मधील **जोडपत्र 'अ', जोडपत्र 'ब' किंवा जोडपत्र 'क'** चा सर्व अधिकृत सरकारी मसुदा आणि रकाने (Columns/Points) हुबेहूब समाविष्ट करा.
            २. परिच्छेद अत्यंत सुटसुटीत, स्पष्ट आणि पूर्ण A4 साईज पानावर योग्य मार्जिन बसणारे असावेत.
            ३. शीर्षक, प्रति, विषय, संदर्भ, मुख्य मजकूर, सत्यप्रतिज्ञा (Verification/Declaration), तारीख, ठिकाण आणि अर्जदाराची स्वाक्षरी हे सर्व मुद्देसूद मांडलेले असावेत.
            ४. कायदेशीर कलमे (उदा. RTI Act Sec 6(1), Sec 19(1), Sec 19(3), Sec 20, CP Act 2019) अचूक जागी वापरा.
            ५. कोणताही इंग्रजी शब्द न वापरता शुद्ध, स्पष्ट आणि कायदेशीर मराठी भाषा वापरा.
            """

            with st.spinner("🚀 AI द्वारे परिपूर्ण मसुदा तयार होत आहे..."):
                response = model.generate_content(master_prompt)
                generated_draft = response.text
                
                st.success("✅ मसुदा यशस्वीरीत्या तयार झाला आहे!")
                
                # Editable Draft Area
                edited_draft = st.text_area("✏️ तयार झालेला मसुदा (हवे असल्यास बदल करा):", value=generated_draft, height=480)
                
                # Save to Session State History
                st.session_state.draft_history.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "service": service_option,
                    "applicant": applicant_name,
                    "content": edited_draft
                })

                # ==========================================
                # 6. DOWNLOAD BUTTONS (A4 DOCX & A4 PDF)
                # ==========================================
                st.markdown("---")
                st.subheader("📥 A4 Size डाऊनलोड करा")
                d_col1, d_col2 = st.columns(2)
                
                docx_data = create_a4_docx(edited_draft)
                pdf_data = create_a4_pdf(edited_draft)
                
                with d_col1:
                    st.download_button(
                        label="📄 Word (.docx) डाऊनलोड करा",
                        data=docx_data,
                        file_name=f"{applicant_name}_Draft.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
                with d_col2:
                    st.download_button(
                        label="📕 PDF (.pdf) डाऊनलोड करा",
                        data=pdf_data,
                        file_name=f"{applicant_name}_Draft.pdf",
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"❌ त्रुटी आली: {str(e)}")

# ==========================================
# 7. HISTORY VIEWER
# ==========================================
if st.session_state.draft_history:
    st.markdown("---")
    st.subheader("📜 या सत्रातील मसुदा इतिहास")
    for idx, item in enumerate(reversed(st.session_state.draft_history)):
        with st.expander(f"📌 {item['service']} - {item['applicant']} ({item['time']})"):
            st.text_area(f"मसुदा #{len(st.session_state.draft_history)-idx}", value=item['content'], height=200, key=f"hist_{idx}")
