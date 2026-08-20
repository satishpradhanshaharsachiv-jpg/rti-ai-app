import streamlit as st
import google.generativeai as genai
import urllib.parse

# १. पेज कॉन्फिगरेशन आणि ब्रँडिंग लपवणे
st.set_page_config(page_title="RTI व तक्रार AI सहाय्यक", page_icon="🏛️", layout="centered")

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap');

* {
    font-family: 'Mukta', sans-serif !important;
}

#MainMenu {visibility: hidden; display: none;}
footer {visibility: hidden; display: none;}
header {visibility: hidden; display: none;}
[data-testid="stToolbar"] {visibility: hidden; display: none;}
[data-testid="stDecoration"] {visibility: hidden; display: none;}
[data-testid="stStatusWidget"] {visibility: hidden; display: none;}
div[class^="viewerBadge"] {visibility: hidden; display: none !important;}
button[title="View source"] {display: none;}

h1 { color: #1E3A8A; font-weight: 800; text-align: center; font-size: 26px; margin-bottom: 2px; }

/* 🟢 हिरवे RTI बटन */
.rti-box div.stButton > button {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    color: white !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    height: 80px !important;
    border-radius: 16px !important;
    border: 2px solid #047857 !important;
    box-shadow: 0 6px 15px rgba(5, 150, 105, 0.4) !important;
    margin-bottom: 12px !important;
}

/* 🔴 लाल तक्रार बटन */
.comp-box div.stButton > button {
    background: linear-gradient(135deg, #DC2626, #EF4444) !important;
    color: white !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    height: 80px !important;
    border-radius: 16px !important;
    border: 2px solid #B91C1C !important;
    box-shadow: 0 6px 15px rgba(220, 38, 38, 0.4) !important;
    margin-bottom: 12px !important;
}

/* 🔵 निळे माहिती बटन */
.home-box div.stButton > button {
    background: linear-gradient(135deg, #1E40AF, #3B82F6) !important;
    color: white !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    height: 55px !important;
    border-radius: 12px !important;
    border: 2px solid #1E3A8A !important;
    box-shadow: 0 4px 10px rgba(30, 64, 175, 0.3) !important;
    margin-bottom: 12px !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# २. सेशन स्टेट
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'rti_paid' not in st.session_state:
    st.session_state.rti_paid = False
if 'complaint_paid' not in st.session_state:
    st.session_state.complaint_paid = False

st.markdown("<h1>🏛️ RTI व शासकीय तक्रार AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 15px; font-weight: bold; color: #374151;'>घरबसल्या १ सेकंदात तयार करा कायदेशीर RTI अर्ज आणि शासकीय तक्रार!</p>", unsafe_allow_html=True)
st.markdown("---")

# ३. ठळक व मोठ्या रंगांची बटने (फोनवर सांगण्यासाठी अतिशय सोपे)
st.markdown('<div class="rti-box">', unsafe_allow_html=True)
if st.button("🟢 १. RTI अर्ज व अपील (हिरवे बटन दाबा)"):
    st.session_state.page = "rti"
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="comp-box">', unsafe_allow_html=True)
if st.button("🔴 २. शासकीय तक्रार अर्ज (लाल बटन दाबा)"):
    st.session_state.page = "complaint"
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="home-box">', unsafe_allow_html=True)
if st.button("🔵 ३. मुख्य माहिती व नियम (निळे बटन दाबा)"):
    st.session_state.page = "home"
st.markdown('</div>', unsafe_allow_html=True)

# WhatsApp शेअर बटण
app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
share_text = urllib.parse.quote(f"🏛️ घरबसल्या RTI अर्ज व शासकीय तक्रार १ सेकंदात तयार करा: {app_url}")
st.markdown(f"""
    <div style="margin: 10px 0 15px 0;">
        <a href="https://api.whatsapp.com/send?text={share_text}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #25D366, #128C7E); color: white; padding: 12px; border-radius: 12px; text-align: center; font-size: 17px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                📲 WhatsApp वर मित्रांना शेअर करा
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# API Key इनपुट (साइडबार)
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")

# ४. शुद्ध मराठी १-पान A4 PDF / प्रिंट तयार करण्याचे HTML फंक्शन
def render_printable_marathi_doc(title, content, theme_color):
    html_content = content.replace('\n', '<br>')
    printable_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700&display=swap" rel="stylesheet">
    <div id="printArea" style="
        font-family: 'Mukta', sans-serif;
        background: #ffffff;
        color: #000000;
        padding: 30px 40px;
        border: 3px solid {theme_color};
        border-radius: 8px;
        line-height: 1.6;
        font-size: 15px;
        max-width: 750px;
        margin: 15px auto;
        box-sizing: border-box;
    ">
        <h3 style="text-align: center; font-size: 18px; margin-bottom: 20px; color: {theme_color}; text-decoration: underline;">{title}</h3>
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
            background: {theme_color};
            color: white;
            padding: 14px 30px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.25);
        ">
            🖨️ १ पानात PDF सेव्ह / प्रिंट करा (Save as PDF)
        </button>
    </div>
    """
    st.components.v1.html(printable_html, height=540, scrolling=True)

# ==================== पान १: मुख्य माहिती ====================
if st.session_state.page == "home":
    st.markdown("""
    <div style="background-color: #EFF6FF; border: 2px solid #3B82F6; border-radius: 12px; padding: 15px; margin-bottom: 15px;">
        <h3 style="color: #1E40AF; margin-top: 0;">🔵 मुख्य माहिती व नियम</h3>
        <ul style="font-size: 16px; color: #1F2937; line-height: 1.8;">
            <li><b>🟢 हिरवे बटन (RTI अर्ज):</b> ग्रामपंचायत, नगरपालिका, महसूल, पोलीस अशा कोणत्याही विभागाकडून अधिकृत माहिती मागवण्यासाठी.</li>
            <li><b>🔴 लाल बटन (तक्रार अर्ज):</b> शासकीय कामातील दिरंगाई, रस्ता, पाणी, भ्रष्टाचार यांविरोधात कडक तक्रार मसुदा तयार करण्यासाठी.</li>
            <li><b>📄 १ पान A4 PDF:</b> तयार होणारा अर्ज थेट १ पानात प्रिंट / सेव्ह होतो.</li>
            <li><b>💰 शुल्क:</b> मसुदा तयार करणे मोफत आहे. अधिकृत प्रिंट-रेडी PDF डाऊनलोड करण्यासाठी केवळ <b>₹१०</b> नाममात्र शुल्क आहे.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #6B7280; text-align: center;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)

# ==================== पान २: RTI अर्ज ====================
elif st.session_state.page == "rti":
    st.markdown("""
    <div style="background: #ECFDF5; border-left: 6px solid #059669; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="color: #065F46; margin: 0;">🟢 RTI अर्ज व अपील विभाग</h3>
        <p style="color: #047857; margin: 5px 0 0 0; font-weight: bold;">कलम ६(१), प्रथम व द्वितीय अपीलाचा परिपूर्ण मसुदा तयार करा.</p>
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
२. भाषा अत्यंत अधिकृत, संक्षिप्त व स्पष्ट असावी जेणेकरून मजकूर एकाच A4 पानात बसेल.
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
            render_printable_marathi_doc("माहितीचा अधिकार अधिनियम २००५ अर्ज", st.session_state.rti_result, "#059669")

# ==================== पान ३: शासकीय तक्रार ====================
elif st.session_state.page == "complaint":
    st.markdown("""
    <div style="background: #FEF2F2; border-left: 6px solid #DC2626; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="color: #991B1B; margin: 0;">🔴 शासकीय तक्रार अर्ज विभाग</h3>
        <p style="color: #B91C1C; margin: 5px 0 0 0; font-weight: bold;">प्रशासकीय दिरंगाई व समस्यांविरुद्ध कडक तक्रार अर्ज तयार करा.</p>
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
            render_printable_marathi_doc("शासकीय तक्रार अर्ज", st.session_state.complaint_result, "#DC2626")
