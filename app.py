import io
import os
import urllib.request
import urllib.parse
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# १. पेज कॉन्फिगरेशन आणि CSS डिझाइन
st.set_page_config(page_title="RTI & तक्रार AI सहाय्यक", page_icon="🏛️", layout="centered")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; display: none;}
h1 { color: #1E3A8A; font-weight: bold; text-align: center; font-size: 24px; }
.stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# २. मराठी फॉन्ट सेट करणे आणि १ पानाची A4 PDF तयार करणे
FONT_NAME = 'MarathiDevanagari'
FONT_FILE = 'NotoSansDevanagari-Regular.ttf'

def setup_marathi_font():
    if not os.path.exists(FONT_FILE):
        url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
        try:
            urllib.request.urlretrieve(url, FONT_FILE)
        except Exception:
            pass
    if os.path.exists(FONT_FILE) and FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
        except Exception:
            pass

def generate_pdf(content_text):
    setup_marathi_font()
    buffer = io.BytesIO()
    
    # एकाच पानात बसवण्यासाठी योग्य मार्जिन (२५ pt)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )
    
    styles = getSampleStyleSheet()
    font_to_use = FONT_NAME if FONT_NAME in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    
    # १ पानाची मर्यादा टिकवण्यासाठी कॉम्पॅक्ट फॉन्ट व साईझ
    marathi_style = ParagraphStyle(
        'MarathiStyle',
        parent=styles['Normal'],
        fontName=font_to_use,
        fontSize=9.5,
        leading=13.5
    )
    
    elements = []
    for line in content_text.split('\n'):
        clean_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').strip()
        if clean_line:
            elements.append(Paragraph(clean_line, marathi_style))
            elements.append(Spacer(1, 2))
        else:
            elements.append(Spacer(1, 4))
            
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

st.markdown("<h1>🏛️ RTI व शासकीय तक्रार AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 13px; font-weight: bold; color: #4B5563;'>घरबसल्या १ सेकंदात तयार करा कायदेशीर RTI अर्ज आणि शासकीय तक्रार!</p>", unsafe_allow_html=True)
st.markdown("---")

# ४. मुख्य नेव्हिगेशन बटने
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏠 मुख्य माहिती"):
        st.session_state.page = "home"
with c2:
    if st.button("📜 RTI अर्ज"):
        st.session_state.page = "rti"
with c3:
    if st.button("📝 तक्रार अर्ज"):
        st.session_state.page = "complaint"

# 🌐 WhatsApp शेअर बटण
app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
share_text = urllib.parse.quote(f"🏛️ घरबसल्या RTI अर्ज व शासकीय तक्रार १ सेकंदात तयार करा: {app_url}")
whatsapp_url = f"https://api.whatsapp.com/send?text={share_text}"

st.markdown(f"""
    <div style="margin: 10px 0;">
        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #25D366, #128C7E); color: white; padding: 10px; border-radius: 10px; text-align: center; font-size: 15px; font-weight: bold;">
                📲 WhatsApp वर मित्रांना शेअर करा
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ५. साइडबारमध्ये API Key
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")
st.sidebar.markdown("---")
st.sidebar.info("💡 **टीप:** API Key टाकल्यास AI कायदेशीर कलमांसह परिपूर्ण अर्ज तयार करतो.")

# ==================== मुख्य पान ====================
if st.session_state.page == "home":
    st.markdown("### 📌 ॲपची वैशिष्ट्ये:")
    st.markdown("""
    * **RTI अर्ज व अपील:** नमुना जोडपत्र अ, प्रथम अपील (कलम १९(१)), द्वितीय अपील (कलम १९(३)) चे कायदेशीर मसुदे.
    * **शासकीय तक्रार अर्ज:** शासकीय कार्यालयातील दिरंगाई व गैरव्यवहाराविरुद्ध कडक तक्रार मसुदा.
    * **१ पान मर्यादा:** डाऊनलोड होणारी PDF थेट प्रिंट काढण्यासाठी एकाच A4 पानावर व्यवस्थित बसते.
    * **मसुदा मोफत:** मजकूर पाहणे पूर्ण मोफत आहे. अधिकृत A4 PDF डाऊनलोड करण्यासाठी केवळ **₹१०** नाममात्र शुल्क आहे.
    """)
    st.markdown("---")
    st.markdown("<p style='font-size: 12px; color: #6B7280;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)

# ==================== RTI अर्ज पान ====================
elif st.session_state.page == "rti":
    st.markdown("<h3>📜 RTI अर्ज व अपील मसुदा तयार करा</h3>", unsafe_allow_html=True)

    with st.form("rti_form"):
        doc_type = st.selectbox("अर्जाचा प्रकार निवडा:", [
            "माहिती अधिकार अर्ज (कलम ६(१) - नमुना जोडपत्र अ)",
            "प्रथम अपील अर्ज (कलम १९(१) - नमुना जोडपत्र १)",
            "द्वितीय अपील मसुदा (कलम १९(३))"
        ])
        user_name = st.text_input("अर्जदाराचे पूर्ण नाव:")
        user_address = st.text_area("अर्जदाराचा संपूर्ण पत्ता व मोबाईल:")
        dept_name = st.text_input("सरकारी विभाग / कार्यालयाचे नाव:")
        query = st.text_area("मागितलेली माहिती / अपीलाचे कारण:")
        submitted = st.form_submit_button("🚀 RTI अर्ज तयार करा")

    if submitted:
        if not user_name or not query or not dept_name:
            st.warning("कृपया सर्व आवश्यक माहिती भरा.")
        else:
            with st.spinner("कायदेशीर कलमांसह १ पानात बसणारा RTI मसुदा तयार होत आहे..."):
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"""
तुम्ही महाराष्ट्र माहिती अधिकार अधिनियम २००५ चे तज्ञ आहात.
खालील माहितीवरून अत्यंत परिपूर्ण आणि A4 साईझच्या एकाच पानात बसेल असा सुटसुटीत RTI मसुदा तयार करा.

प्रकार: {doc_type}
अर्जदार: {user_name}
पत्ता: {user_address}
कार्यालय: {dept_name}
माहिती: {query}

नियम:
१. मसुदा जास्त लांबलचक नसावा जेणेकरून तो एकाच पानात बसेल.
२. कलम ६(१), कलम ६(३) (५ दिवसांत वर्ग करणे), कलम ७(१) (३० दिवसांची मुदत), कलम २०(१) (दंडात्मक कारवाई) आणि ₹१० कोर्ट फी स्टॅम्पचा उल्लेख करा.
३. शेवटी अर्जदाराचे नाव व स्वाक्षरीची जागा ठेवा.
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
५. माहितीचा प्रकार: प्रमाणित सत्यप्रतीसह व्यक्तिशः / टपालाने

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. सदर माहिती आपल्या कार्यालयाशी संबंधित नसल्यास कलम ६(३) अन्वये ५ दिवसांत योग्य विभागाकडे वर्ग करावी.
अर्जासोबत ₹१०/- चा कोर्ट फी स्टॅम्प जोडला आहे.

तारीख: ____________                                अर्जदाराची स्वाक्षरी: {user_name}
ठिकाण: ____________"""

    if 'rti_result' in st.session_state and st.session_state.rti_result:
        st.success("✅ RTI मसुदा यशस्वीपणे तयार झाला आहे!")
        st.text_area("📄 तयार झालेला मसुदा (येथून कॉपी करू शकता):", value=st.session_state.rti_result, height=280)
        
        st.markdown("---")
        st.markdown("### 📥 अधिकृत १-पान PDF डाऊनलोड")
        
        if not st.session_state.rti_paid:
            st.info("📌 **A4 साईझ प्रिंट-रेडी PDF डाऊनलोड करण्यासाठी नाममात्र ₹१० शुल्क भरा.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करा", width=140)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}`")
                st.markdown("**रक्कम:** ₹१०/-")
                if st.button("✅ मी ₹१० पेमेंट केले आहे (PDF अनलॉक करा)", key="unlock_rti"):
                    st.session_state.rti_paid = True
                    st.rerun()
        else:
            pdf_bytes = generate_pdf(st.session_state.rti_result)
            st.download_button(
                label="📥 अधिकृत RTI PDF डाऊनलोड करा (A4 One-Page)",
                data=pdf_bytes,
                file_name="RTI_Application.pdf",
                mime="application/pdf"
            )

# ==================== शासकीय तक्रार पान ====================
elif st.session_state.page == "complaint":
    st.markdown("<h3>📝 शासकीय तक्रार अर्ज तयार करा</h3>", unsafe_allow_html=True)

    with st.form("complaint_form"):
        c_name = st.text_input("तक्रारदाराचे पूर्ण नाव:")
        c_address = st.text_area("पत्ता व मोबाईल नंबर:")
        c_dept = st.text_input("कार्यालय / अधिकारी (उदा. आयुक्त / जिल्हाधिकारी):")
        c_subject = st.text_input("तक्रारीचा मुख्य विषय:")
        c_query = st.text_area("तक्रारीचा सविस्तर तपशील:")
        c_submitted = st.form_submit_button("🚀 तक्रार अर्ज तयार करा")

    if c_submitted:
        if not c_name or not c_dept or not c_query:
            st.warning("कृपया सर्व आवश्यक माहिती भरा.")
        else:
            with st.spinner("१ पानात बसणारा कडक तक्रार मसुदा तयार होत आहे..."):
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"""
तुम्ही प्रशासकीय कायदेतज्ञ आहात. खालील तक्रारीवरून A4 साईझच्या एकाच पानात बसेल असा कडक तक्रार अर्ज बनवा:
तक्रारदार: {c_name}
पत्ता: {c_address}
प्रति: {c_dept}
विषय: {c_subject}
तपशील: {c_query}

मसुद्यात प्रति, विषय, मुद्द्यांनुसार तक्रार, ७ दिवसांत कारवाईचा इशारा आणि प्रतिलिपि (जिल्हाधिकारी) असा सुटसुटीत १-पान फॉरमॅट ठेवा.
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

सदर प्रकरणात संबंधित जबाबदार घटकांवर ७ दिवसांच्या आत प्रशासकीय नियमांनुसार कारवाई करण्यात यावी, अन्यथा वरिष्ठ पातळीवर व न्यायालयात दाद मागावी लागेल.

तारीख: ____________                                तक्रारदाराची स्वाक्षरी: {c_name}
ठिकाण: ____________

प्रत माहितीस्तव: मा. जिल्हाधिकारी महोदय."""

    if 'complaint_result' in st.session_state and st.session_state.complaint_result:
        st.success("✅ तक्रार अर्ज मसुदा तयार झाला आहे!")
        st.text_area("📄 तयार झालेली तक्रार:", value=st.session_state.complaint_result, height=280)
        
        st.markdown("---")
        st.markdown("### 📥 अधिकृत १-पान PDF डाऊनलोड")
        
        if not st.session_state.complaint_paid:
            st.info("📌 **A4 साईझ प्रिंट-रेडी PDF डाऊनलोड करण्यासाठी नाममात्र ₹१० शुल्क भरा.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करा", width=140)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}`")
                st.markdown("**रक्कम:** ₹१०/-")
                if st.button("✅ मी ₹१० पेमेंट केले आहे (PDF अनलॉक करा)", key="unlock_complaint"):
                    st.session_state.complaint_paid = True
                    st.rerun()
        else:
            c_pdf_bytes = generate_pdf(st.session_state.complaint_result)
            st.download_button(
                label="📥 अधिकृत तक्रार PDF डाऊनलोड करा (A4 One-Page)",
                data=c_pdf_bytes,
                file_name="Complaint_Letter.pdf",
                mime="application/pdf"
            )
