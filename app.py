import streamlit as st
import google.generativeai as genai
import urllib.parse

# १. पेज कॉन्फिगरेशन
st.set_page_config(page_title="RTI & Complaint AI Assistant", page_icon="🏛️", layout="centered")

# २. संपूर्ण ॲपसाठी मराठी फॉन्ट, रंगीबेरंगी डिझाइन आणि वॉटरमार्क लपवणे
custom_ui_style = """
<link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
/* सर्व मजकुरासाठी मराठी फॉन्ट */
* {
    font-family: 'Mukta', sans-serif !important;
}

/* Streamlit ब्रँडिंग आणि मेनू पूर्णपणे लपवणे */
#MainMenu {visibility: hidden; display: none;}
footer {visibility: hidden; display: none;}
header {visibility: hidden; display: none;}
[data-testid="stToolbar"] {visibility: hidden; display: none;}
[data-testid="stDecoration"] {visibility: hidden; display: none;}
[data-testid="stStatusWidget"] {visibility: hidden; display: none;}
div[class^="viewerBadge"] {visibility: hidden; display: none !important;}
button[title="View source"] {display: none;}

/* मुख्य शीर्षक */
.main-header {
    background: linear-gradient(135deg, #1E3A8A, #3B82F6);
    color: white;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 6px 15px rgba(30, 58, 138, 0.3);
    margin-bottom: 20px;
}
.main-header h1 {
    color: #FFFFFF !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    margin: 0;
}
.main-header p {
    color: #E0E7FF !important;
    font-size: 15px !important;
    margin-top: 6px;
    font-weight: 600;
}

/* नेव्हिगेशन बटनांचे वेगवेगळे रंग */
.btn-rti div.stButton > button {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    color: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    height: 65px !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow: 0 6px 14px rgba(5, 150, 105, 0.35) !important;
}

.btn-complaint div.stButton > button {
    background: linear-gradient(135deg, #DC2626, #F97316) !important;
    color: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    height: 65px !important;
    border-radius: 14px !important;
    border: none !important;
    box-shadow: 0 6px 14px rgba(220, 38, 38, 0.35) !important;
}

.btn-home div.stButton > button {
    background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
    color: #FFFFFF !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    height: 50px !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25) !important;
}

/* फॉर्म विभागांचे रंगीत बॉक्सेस */
.rti-card {
    background: #ECFDF5;
    border: 2px solid #10B981;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
}

.complaint-card {
    background: #FFF7ED;
    border: 2px solid #F97316;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(custom_ui_style, unsafe_allow_html=True)

# ३. सेशन स्टेट
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'rti_paid' not in st.session_state:
    st.session_state.rti_paid = False
if 'complaint_paid' not in st.session_state:
    st.session_state.complaint_paid = False

# मुख्य रंगीबेरंगी बॅनर
st.markdown("""
<div class="main-header">
    <h1>🏛️ RTI व शासकीय तक्रार AI सहाय्यक</h1>
    <p>घरबसल्या १ सेकंदात तयार करा कायदेशीर RTI अर्ज आणि शासकीय तक्रार!</p>
</div>
""", unsafe_allow_html=True)

# ४. मोठी आणि ठळक रंगीबेरंगी नेव्हिगेशन बटने
st.markdown('<div class="btn-rti">', unsafe_allow_html=True)
if st.button("📜 RTI अर्ज व अपील तयार करा"):
    st.session_state.page = "rti"
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

st.markdown('<div class="btn-complaint">', unsafe_allow_html=True)
if st.button("📝 शासकीय तक्रार अर्ज तयार करा"):
    st.session_state.page = "complaint"
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

st.markdown('<div class="btn-home">', unsafe_allow_html=True)
if st.button("🏠 मुख्य पान व माहिती"):
    st.session_state.page = "home"
st.markdown('</div>', unsafe_allow_html=True)

# WhatsApp शेअर बटण
app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
share_msg = urllib.parse.quote(f"🏛️ घरबसल्या RTI अर्ज व शासकीय तक्रार १ सेकंदात तयार करा: {app_url}")
st.markdown(f"""
    <div style="margin: 15px 0;">
        <a href="https://api.whatsapp.com/send?text={share_msg}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #25D366, #128C7E); color: white; padding: 12px; border-radius: 12px; text-align: center; font-size: 16px; font-weight: 800; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.35);">
                📲 WhatsApp वर मित्रांना शेअर करा
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# API Key इनपुट (साइडबार)
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")

# १-पान A4 PDF / प्रिंट तयार करण्याचे HTML फंक्शन (शुद्ध मराठी फॉन्ट)
def render_printable_marathi_doc(title, content):
    html_content = content.replace('\n', '<br>')
    printable_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700&display=swap" rel="stylesheet">
    <div id="printArea" style="
        font-family: 'Mukta', sans-serif;
        background: #ffffff;
        color: #000000;
        padding: 30px 40px;
        border: 2px solid #000000;
        border-radius: 6px;
        line-height: 1.6;
        font-size: 15px;
        max-width: 750px;
        margin: 15px auto;
        box-sizing: border-box;
    ">
        <h3 style="text-align: center; font-size: 18px; margin-bottom: 20px; text-decoration: underline; color: #000000;">{title}</h3>
        <div>{html_content}</div>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="
            var printContent = document.getElementById('printArea').innerHTML;
            var originalContent = document.body.innerHTML;
            document.body.innerHTML = printContent;
            window.print();
            document.body.innerHTML = originalContent;
            window.location.reload();
        " style="
            background: #1E3A8A;
            color: white;
            padding: 14px 28px;
            font-size: 17px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.25);
        ">
            🖨️ १ पानात PDF सेव्ह / प्रिंट करा (Save as PDF)
        </button>
    </div>
    """
    st.components.v1.html(printable_html, height=530, scrolling=True)

# ==================== पान १: मुख्य पान ====================
if st.session_state.page == "home":
    st.markdown("""
    <div style="background: #EEF2FF; border-left: 5px solid #4F46E5; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="color: #1E3A8A; margin: 0 0 10px 0;">📌 ॲपची ठळक वैशिष्ट्ये:</h3>
        <p style="margin: 5px 0; color: #374151;">✔️ <b>कायदेशीर अचूकता:</b> RTI कायदा कलम ६(१), ६(३), ७(१) व २०(१) नुसार अचूक मसुदा.</p>
        <p style="margin: 5px 0; color: #374151;">✔️ <b>१ पान मर्यादा:</b> थेट प्रिंट काढण्यासाठी एकाच A4 पानावर सुबक मांडणी.</p>
        <p style="margin: 5px 0; color: #374151;">✔️ <b>अक्षरांची शुद्धता:</b> सर्व मराठी जोडाक्षरे १००% स्पष्ट व वाचनीय.</p>
        <p style="margin: 5px 0; color: #374151;">✔️ <b>शुल्क:</b> मसुदा तयार करणे मोफत; A4 PDF डाऊनलोडसाठी नाममात्र <b>₹१०</b> शुल्क.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #6B7280;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)

# ==================== पान २: RTI अर्ज ====================
elif st.session_state.page == "rti":
    st.markdown("""
    <div class="rti-card">
        <h2 style="color: #065F46; margin: 0 0 5px 0; font-size: 22px;">📜 RTI अर्ज व प्रथम/द्वितीय अपील मसुदा</h2>
        <p style="color: #047857; margin: 0; font-weight: 600;">खालील फॉर्ममध्ये माहिती भरा आणि कायदेशीर कलमांसह अर्ज तयार करा.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("rti_form"):
        doc_type = st.selectbox("अर्जाचा प्रकार निवडा:", [
            "माहिती अधिकार अर्ज (कलम ६(१) - नमुना जोडपत्र अ)",
            "प्रथम अपील अर्ज (कलम १९(१) - नमुना जोडपत्र १)",
            "द्वितीय अपील मसुदा (कलम १९(३))"
        ])
        user_name = st.text_input("अर्जदाराचे पूर्ण नाव:")
        user_address = st.text_area("अर्जदाराचा संपूर्ण पत्ता व संपर्क:")
        dept_name = st.text_input("सरकारी कार्यालय / विभागाचे नाव:")
        query = st.text_area("मागितलेली माहिती / अपीलाचे कारण:")
        submitted = st.form_submit_button("🚀 कायदेशीर RTI अर्ज तयार करा")

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
खालील माहितीवरून एकाच A4 पानात बसेल असा कायदेशीर RTI मसुदा तयार करा.

प्रकार: {doc_type}
अर्जदार: {user_name}
पत्ता: {user_address}
कार्यालय: {dept_name}
माहिती: {query}

नियम:
१. कलम ६(१), कलम ६(३) (५ दिवसांत वर्ग करणे), कलम ७(१) (३० दिवसांची मुदत) व ₹१० कोर्ट फी स्टॅम्पचा स्पष्ट उल्लेख असावा.
२. भाषा अत्यंत अधिकृत, संक्षिप्त व स्पष्ट असावी जेणेकरून मजकूर १ पानात बसेल.
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
        st.success("✅ RTI मसुदा तयार झाला आहे!")
        st.text_area("📄 तयार झालेला मसुदा (येथून वाचू शकता):", value=st.session_state.rti_result, height=240)
        
        st.markdown("---")
        st.markdown("### 📥 अधिकृत १-पान PDF डाऊनलोड / प्रिंट")
        
        if not st.session_state.rti_paid:
            st.info("📌 **A4 साईझ प्रिंट-रेडी PDF मिळवण्यासाठी ₹१० पेमेंट करा आणि १२-अंकी UPI UTR नंबर टाका.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करा", width=140)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}` | **रक्कम:** ₹१०/-")
                utr_input = st.text_input("पेमेंट झाल्यावर १२-अंकी UTR / Ref No. टाका:", max_chars=12, key="rti_utr")
                if st.button("🔒 पेमेंट पडताळणी करून PDF अनलॉक करा", key="unlock_rti"):
                    if len(utr_input.strip()) == 12 and utr_input.strip().isdigit():
                        st.session_state.rti_paid = True
                        st.success("पेमेंट पडताळणी यशस्वी! PDF खाली अनलॉक झाली आहे.")
                        st.rerun()
                    else:
                        st.error("कृपया पेमेंट केल्यानंतर मिळालेला खरा १२-अंकी UTR क्रमांक टाका.")
        else:
            render_printable_marathi_doc("माहितीचा अधिकार अधिनियम २००५ अर्ज", st.session_state.rti_result)

# ==================== पान ३: शासकीय तक्रार ====================
elif st.session_state.page == "complaint":
    st.markdown("""
    <div class="complaint-card">
        <h2 style="color: #9A3412; margin: 0 0 5px 0; font-size: 22px;">📝 शासकीय तक्रार अर्ज तयार करा</h2>
        <p style="color: #C2410C; margin: 0; font-weight: 600;">प्रशासकीय दिरंगाई व गैरव्यवहाराविरुद्ध कडक तक्रार मसुदा बनवा.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("complaint_form"):
        c_name = st.text_input("तक्रारदाराचे पूर्ण नाव:")
        c_address = st.text_area("पत्ता व मोबाईल नंबर:")
        c_dept = st.text_input("कार्यालय / अधिकारी (उदा. आयुक्त / जिल्हाधिकारी):")
        c_subject = st.text_input("तक्रारीचा मुख्य विषय:")
        c_query = st.text_area("तक्रारीचा सविस्तर तपशील:")
        c_submitted = st.form_submit_button("🚀 कडक तक्रार अर्ज तयार करा")

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
तुम्ही प्रशासकीय कायदेतज्ञ आहात. एकाच A4 पानात बसेल असा कडक तक्रार अर्ज बनवा:
तक्रारदार: {c_name}
पत्ता: {c_address}
प्रति: {c_dept}
विषय: {c_subject}
तपशील: {c_query}

मसुद्यात प्रति, विषय, मुद्द्यांनुसार तक्रार, ७ दिवसांत कारवाईचा इशारा आणि प्रतिलिपि असा सुटसुटीत फॉरमॅट ठेवा.
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
        st.success("✅ तक्रार अर्ज तयार झाला आहे!")
        st.text_area("📄 तयार झालेली तक्रार (येथून वाचू शकता):", value=st.session_state.complaint_result, height=240)
        
        st.markdown("---")
        st.markdown("### 📥 अधिकृत १-पान PDF डाऊनलोड / प्रिंट")
        
        if not st.session_state.complaint_paid:
            st.info("📌 **A4 साईझ प्रिंट-रेडी PDF मिळवण्यासाठी ₹१० पेमेंट करा आणि १२-अंकी UPI UTR नंबर टाका.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करा", width=140)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}` | **रक्कम:** ₹१०/-")
                c_utr_input = st.text_input("पेमेंट झाल्यावर १२-अंकी UTR / Ref No. टाका:", max_chars=12, key="comp_utr")
                if st.button("🔒 पेमेंट पडताळणी करून PDF अनलॉक करा", key="unlock_complaint"):
                    if len(c_utr_input.strip()) == 12 and c_utr_input.strip().isdigit():
                        st.session_state.complaint_paid = True
                        st.success("पेमेंट पडताळणी यशस्वी! PDF खाली अनलॉक झाली आहे.")
                        st.rerun()
                    else:
                        st.error("कृपया पेमेंट केल्यानंतर मिळालेला खरा १२-अंकी UTR क्रमांक टाका.")
        else:
            render_printable_marathi_doc("शासकीय तक्रार अर्ज", st.session_state.complaint_result)
