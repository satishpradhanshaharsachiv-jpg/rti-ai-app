import io
import urllib.parse
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# १. पेज कॉन्फिगरेशन
st.set_page_config(page_title="RTI & तक्रार AI सहाय्यक", page_icon="🏛️", layout="centered")

# CSS स्टाईल
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; display: none;}
h1 { color: #1E3A8A; font-weight: bold; text-align: center; font-size: 26px; }
.stButton>button { width: 100%; border-radius: 12px; height: 50px; font-weight: bold; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# २. PDF तयार करण्याचे फंक्शन (मराठी/युनिकोड सुरक्षित)
def generate_pdf(content_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'NormalMarathi', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14
    )
    elements = []
    for line in content_text.split('\n'):
        clean_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').strip()
        if clean_line:
            elements.append(Paragraph(clean_line, normal_style))
            elements.append(Spacer(1, 4))
        else:
            elements.append(Spacer(1, 6))
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ३. सेशन स्टेट मॅनेजमेंट
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'rti_paid' not in st.session_state:
    st.session_state.rti_paid = False
if 'complaint_paid' not in st.session_state:
    st.session_state.complaint_paid = False

# शीर्ष शीर्षक
st.markdown("<h1>🏛️ RTI व शासकीय तक्रार AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; font-weight: 600; color: #4B5563;'>घरबसल्या १ सेकंदात तयार करा कायदेशीर RTI अर्ज आणि शासकीय तक्रार!</p>", unsafe_allow_html=True)
st.markdown("---")

# ४. मुख्य नेव्हिगेशन बटने
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 मुख्य माहिती"):
        st.session_state.page = "home"
with col2:
    if st.button("📜 RTI अर्ज"):
        st.session_state.page = "rti"
with col3:
    if st.button("📝 तक्रार अर्ज"):
        st.session_state.page = "complaint"

# 🌐 शेअर बटण (WhatsApp वर थेट शेअर आणि लिंक कॉपी)
app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
share_text = urllib.parse.quote(f"🏛️ घरबसल्या RTI अर्ज आणि शासकीय तक्रार १ सेकंदात तयार करा. हे मोफत AI ॲप वापरा: {app_url}")
whatsapp_share_url = f"https://api.whatsapp.com/send?text={share_text}"

st.markdown(f"""
    <div style="margin: 12px 0;">
        <a href="{whatsapp_share_url}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #25D366, #128C7E); color: white; padding: 12px; border-radius: 12px; text-align: center; font-size: 16px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                📲 WhatsApp वर मित्रांना शेअर करा
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ५. साइडबारमध्ये API Key
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")
st.sidebar.markdown("---")
st.sidebar.info("💡 **टीप:** API Key टाकल्यास AI कायदेशीर कलमांसह परिपूर्ण अर्ज तयार करेल.")

# ==================== पान १: मुख्य पान ====================
if st.session_state.page == "home":
    st.markdown("### 📌 ॲप कसे वापरावे?")
    st.markdown("""
    * **RTI अर्ज:** ग्रामपंचायत, महानगरपालिका, महसूल, पोलीस अशा कोणत्याही विभागाकडून माहिती मागवण्यासाठी कायदेशीर अर्ज तयार करा.
    * **शासकीय तक्रार:** रस्ता, पाणी, लाईट, भ्रष्टाचार किंवा प्रशासकीय दिरंगाईविरोधात कडक भाषेत तक्रार मसुदा बनवा.
    * **पारदर्शकता:** मसुदा तयार करणे पूर्णपणे विनामूल्य आहे. अधिकृत PDF डाऊनलोड करण्यासाठी केवळ **₹१०** नाममात्र शुल्क आकारले जाते.
    """)
    st.markdown("---")
    st.markdown("<p style='font-size: 13px; color: #6B7280;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)

# ==================== पान २: RTI अर्ज ====================
elif st.session_state.page == "rti":
    st.markdown("<h3>📜 RTI अर्ज व अपील मसुदा</h3>", unsafe_allow_html=True)

    with st.form("rti_form"):
        doc_type = st.selectbox("अर्जाचा प्रकार निवडा:", [
            "माहिती अधिकार अर्ज (कलम ६(१) - नमुना जोडपत्र अ)",
            "प्रथम अपील अर्ज (कलम १९(१) - नमुना जोडपत्र १)",
            "द्वितीय अपील मसुदा (कलम १९(३))"
        ])
        user_name = st.text_input("अर्जदाराचे पूर्ण नाव:")
        user_address = st.text_area("अर्जदाराचा संपूर्ण पत्ता व मोबाईल:")
        dept_name = st.text_input("सार्वजनिक प्राधिकरणाचे नाव / सरकारी विभाग:")
        query = st.text_area("कोणती माहिती / कागदपत्रे हवी आहेत? (सविस्तर लिहा):")
        submitted = st.form_submit_button("🚀 कायदेशीर RTI अर्ज तयार करा")

    if submitted:
        if not user_name or not query or not dept_name:
            st.warning("कृपया अर्जदाराचे नाव, विभाग आणि मागितलेली माहिती भरा.")
        else:
            with st.spinner("कायदेशीर कलमांसह RTI मसुदा तयार होत आहे..."):
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"""
तुम्ही महाराष्ट्र माहिती अधिकार अधिनियम २००५ चे सर्वोच्च कायदेशीर सल्लागार आहात.
खालील माहितीवरून अत्यंत परिपूर्ण, कायदेशीर आणि शासकीय भाषेत RTI अर्ज तयार करा.

प्रकार: {doc_type}
अर्जदार: {user_name}
पत्ता व संपर्क: {user_address}
संबंधित कार्यालय: {dept_name}
मागितलेली माहिती: {query}

नियम व मसुद्यात पुढील बाबी बंधनकारक असाव्यात:
१. शीर्षभागी: 'माहितीचा अधिकार अधिनियम २००५ चे कलम ६(१) अन्वये अर्ज (नमुना - जोडपत्र अ)'
२. प्रति, जन माहिती अधिकारी / सहाय्यक जन माहिती अधिकारी, {dept_name}
३. मागितलेली माहिती क्रमांकानुसार (१, २, ३...) अत्यंत अचूक व कायदेशीर मुद्द्यांत मागा.
४. कलम ६(३) चा स्पष्ट उल्लेख करा: जर ही माहिती आपल्या अखत्यारीतील नसेल तर ५ दिवसांत संबंधित विभागाकडे वर्ग करावी.
५. कलम ७(१) चा उल्लेख करा: ३० दिवसांच्या विहित मुदतीत माहिती उपलब्ध करून देणे बंधनकारक आहे.
६. कलम २०(१) व २०(२) चे स्मरण द्या: विनाकारण माहिती नाकारल्यास प्रतिदिवस २५० रु. प्रमाणे २५,००० रु. दंडात्मक कारवाई होऊ शकते.
७. १० रुपयांचा कोर्ट फी स्टॅम्प किंवा डिमांड ड्राफ्ट जोडल्याचा उल्लेख असावा.
८. शेवटी अर्जदाराची सही, तारीख आणि ठिकाणाची जागा ठेवा.
"""
                        res = model.generate_content(prompt, generation_config={"temperature": 0.2})
                        st.session_state.rti_result = res.text
                    except Exception as e:
                        st.error(f"AI त्रुटी: {e}")
                else:
                    st.session_state.rti_result = f"""माहितीचा अधिकार अधिनियम २००५ चे कलम ६(१) अन्वये अर्ज
(नमुना - जोडपत्र 'अ')

प्रति,
जन माहिती अधिकारी,
कार्यालय: {dept_name}

१. अर्जदाराचे नाव: {user_name}
२. पत्ता व संपर्क: {user_address}
३. मागितलेल्या माहितीचा तपशील:
{query}

४. माहितीचा कालावधी: चालू वर्ष व मागील अभिलेख
५. माहिती टपालाने / व्यक्तिशः हवी आहे: व्यक्तिशः / प्रमाणित प्रतीसह

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील दाखल करण्यात येईल. तसेच सदर माहिती आपल्या विभागाशी संबंधित नसल्यास कलम ६(३) अन्वये ५ दिवसांत योग्य विभागाकडे वर्ग करावी.

अर् Call फी: ₹१०/- चा कोर्ट फी स्टॅम्प जोडला आहे.

तारीख: ____________
ठिकाण: ____________
अर्जदाराची स्वाक्षरी: {user_name}"""

    if 'rti_result' in st.session_state and st.session_state.rti_result:
        st.success("✅ तुमचा कायदेशीर RTI मसुदा तयार झाला आहे!")
        st.text_area("📄 तयार झालेला मसुदा (येथून कॉपी करू शकता):", value=st.session_state.rti_result, height=350)
        
        # डाऊनलोड व पेमेंट विभाग
        st.markdown("---")
        st.markdown("### 📥 अधिकृत PDF डाऊनलोड करा")
        
        if not st.session_state.rti_paid:
            st.info("📌 **अधिकृत A4 साईझ PDF डाऊनलोड करण्यासाठी नाममात्र ₹१० पेमेंट करा.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करून भरा", width=160)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}`")
                st.markdown("**रक्कम:** ₹१०/-")
                if st.button("✅ मी ₹१० पेमेंट केले आहे (PDF अनलॉक करा)", key="unlock_rti"):
                    st.session_state.rti_paid = True
                    st.rerun()
        else:
            pdf_data = generate_pdf(st.session_state.rti_result)
            st.download_button(
                label="📥 अधिकृत PDF डाऊनलोड करा (A4 Size)",
                data=pdf_data,
                file_name=f"RTI_{user_name if 'user_name' in locals() and user_name else 'Application'}.pdf",
                mime="application/pdf"
            )

# ==================== पान ३: शासकीय तक्रार ====================
elif st.session_state.page == "complaint":
    st.markdown("<h3>📝 शासकीय तक्रार अर्ज</h3>", unsafe_allow_html=True)

    with st.form("complaint_form"):
        c_name = st.text_input("तक्रारदाराचे पूर्ण नाव:")
        c_address = st.text_area("पत्ता व मोबाईल नंबर:")
        c_dept = st.text_input("कार्यालय / अधिकारी ज्यांच्याकडे तक्रार करायची आहे (उदा. आयुक्त, जिल्हाधिकारी, पोलीस अधीक्षक):")
        c_subject = st.text_input("तक्रारीचा मुख्य विषय:")
        c_query = st.text_area("तक्रारीचा सविस्तर तपशील व प्रशासकीय निष्काळजीपणा:")
        c_submitted = st.form_submit_button("🚀 कडक तक्रार मसुदा तयार करा")

    if c_submitted:
        if not c_name or not c_dept or not c_query:
            st.warning("कृपया नाव, विभाग आणि तक्रारीचा तपशील भरा.")
        else:
            with st.spinner("तक्रार मसुदा तयार होत आहे..."):
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"""
तुम्ही प्रशासकीय कायदेतज्ञ आहात. शासकीय अनागोंदी, नागरिकांची गैरसोय किंवा अधिकारांच्या उल्लंघनाविरुद्ध
शासकीय अधिकाऱ्याला सादर करण्यासाठी अत्यंत कडक, आक्रमक आणि कायदेशीर भाषेतील तक्रार अर्ज बनवा.

तक्रारदार: {c_name}
पत्ता: {c_address}
प्रति (अधिकारी): {c_dept}
विषय: {c_subject}
सविस्तर तक्रार: {c_query}

मसुद्यात पुढील मुद्दे असावेत:
१. प्रति: मा. {c_dept} यांना आदरयुक्त पण स्पष्ट संबोधा.
२. विषय: {c_subject} बाबत कठोर कारवाई करण्याबाबत.
३. मुद्द्यांनुसार घडलेला प्रकार, नियमांचे उल्लंघन व नागरिकांना होणारा त्रास स्पष्ट मांडा.
४. विहित मुदतीत (उदा. ७ दिवसांत) निवारण न झाल्यास वरिष्ठ कार्यालय, लोकायुक्त किंवा न्यायालयात दाद मागण्याचा इशारा द्या.
५. प्रतिलिपि (माहितीस्तव): मा. जिल्हाधिकारी / संबंधित वरिष्ठ अधिकारी यांचा समावेश करा.
"""
                        res = model.generate_content(prompt, generation_config={"temperature": 0.2})
                        st.session_state.complaint_result = res.text
                    except Exception as e:
                        st.error(f"AI त्रुटी: {e}")
                else:
                    st.session_state.complaint_result = f"""प्रति,
मा. {c_dept},

विषय: {c_subject} बाबत तातडीने कठोर कारवाई करणेबाबत.
तक्रारदार: {c_name}, रा. {c_address}

महोदय,

मी खालीलप्रमाणे तक्रार नोंदवत आहे:
{c_query}

सदर प्रकरणात संबंधित जबाबदार अधिकाऱ्यांवर/कर्मचाऱ्यांवर प्रशासकीय नियमांनुसार तातडीने कारवाई करण्यात यावी. ७ दिवसांच्या आत यावर योग्य ती कारवाई न झाल्यास मला नाईलाजाने वरिष्ठ पातळीवर व न्यायालयात दाद मागावी लागेल.

तारीख: ____________
आपला नम्र,
{c_name}

प्रत माहितीस्तव सादर:
१. मा. जिल्हाधिकारी महोदय.
२. मा. विभागीय आयुक्त महोदय."""

    if 'complaint_result' in st.session_state and st.session_state.complaint_result:
        st.success("✅ तक्रार अर्ज मसुदा तयार झाला आहे!")
        st.text_area("📄 तयार झालेली तक्रार:", value=st.session_state.complaint_result, height=350)
        
        # डाऊनलोड व पेमेंट विभाग
        st.markdown("---")
        st.markdown("### 📥 अधिकृत PDF डाऊनलोड करा")
        
        if not st.session_state.complaint_paid:
            st.info("📌 **अधिकृत A4 साईझ PDF डाऊनलोड करण्यासाठी नाममात्र ₹१० पेमेंट करा.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करून भरा", width=160)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}`")
                st.markdown("**रक्कम:** ₹१०/-")
                if st.button("✅ मी ₹१० पेमेंट केले आहे (PDF अनलॉक करा)", key="unlock_complaint"):
                    st.session_state.complaint_paid = True
                    st.rerun()
        else:
            c_pdf_data = generate_pdf(st.session_state.complaint_result)
            st.download_button(
                label="📥 अधिकृत तक्रार PDF डाऊनलोड करा",
                data=c_pdf_data,
                file_name=f"Complaint_{c_name if 'c_name' in locals() and c_name else 'Letter'}.pdf",
                mime="application/pdf"
            )
