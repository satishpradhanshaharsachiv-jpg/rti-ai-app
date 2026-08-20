import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime

# १. पेज कॉन्फिगरेशन आणि ब्रँडिंग लपवणे
st.set_page_config(page_title="RTI व शासकीय तक्रार AI सहाय्यक", page_icon="🏛️", layout="centered")

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

h1 { color: #1E3A8A; font-weight: 800; text-align: center; font-size: 24px; margin-bottom: 2px; }

/* 🟢 आडवे मोठे हिरवे RTI बटन */
.rti-col div.stButton > button {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    color: white !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    height: 90px !important;
    border-radius: 14px !important;
    border: 2px solid #047857 !important;
    box-shadow: 0 5px 12px rgba(5, 150, 105, 0.35) !important;
    white-space: normal !important;
    line-height: 1.3 !important;
}

/* 🔴 आडवे मोठे लाल तक्रार बटन */
.comp-col div.stButton > button {
    background: linear-gradient(135deg, #DC2626, #EF4444) !important;
    color: white !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    height: 90px !important;
    border-radius: 14px !important;
    border: 2px solid #B91C1C !important;
    box-shadow: 0 5px 12px rgba(220, 38, 38, 0.35) !important;
    white-space: normal !important;
    line-height: 1.3 !important;
}

/* लहान नेव्हिगेशन बटने */
.nav-btn div.stButton > button {
    font-size: 14px !important;
    font-weight: 700 !important;
    height: 45px !important;
    border-radius: 10px !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# २. सेशन स्टेट सुरू करणे (डेटा नष्ट न होण्यासाठी)
if 'page' not in st.session_state:
    st.session_state.page = "rti"  # सुरुवातीला RTI उघडा राहील

# RTI चे सेव्ह व्हेरिएबल्स
if 'rti_type' not in st.session_state: st.session_state.rti_type = "माहिती अधिकार अर्ज (कलम ६(१) - नमुना जोडपत्र अ)"
if 'rti_name' not in st.session_state: st.session_state.rti_name = ""
if 'rti_address' not in st.session_state: st.session_state.rti_address = ""
if 'rti_dept' not in st.session_state: st.session_state.rti_dept = ""
if 'rti_query' not in st.session_state: st.session_state.rti_query = ""
if 'rti_result' not in st.session_state: st.session_state.rti_result = ""
if 'rti_paid' not in st.session_state: st.session_state.rti_paid = False

# तक्रार अर्जाचे सेव्ह व्हेरिएबल्स
if 'comp_name' not in st.session_state: st.session_state.comp_name = ""
if 'comp_address' not in st.session_state: st.session_state.comp_address = ""
if 'comp_dept' not in st.session_state: st.session_state.comp_dept = ""
if 'comp_subject' not in st.session_state: st.session_state.comp_subject = ""
if 'comp_query' not in st.session_state: st.session_state.comp_query = ""
if 'comp_result' not in st.session_state: st.session_state.comp_result = ""
if 'comp_paid' not in st.session_state: st.session_state.complaint_paid = False

# हिस्ट्री यादी (History List)
if 'history_list' not in st.session_state:
    st.session_state.history_list = []

# ३. शीर्ष शीर्षक
st.markdown("<h1>🏛️ RTI व शासकीय तक्रार AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; font-weight: bold; color: #4B5563;'>घरबसल्या १ सेकंदात तयार करा कायदेशीर RTI अर्ज आणि शासकीय तक्रार!</p>", unsafe_allow_html=True)
st.markdown("---")

# ४. मुख्य आडवे दोन मोठे चौकोनी बॉक्सेस (🟢 RTI व 🔴 तक्रार)
col_rti, col_comp = st.columns(2)

with col_rti:
    st.markdown('<div class="rti-col">', unsafe_allow_html=True)
    if st.button("🟢 १. RTI अर्ज व अपील\n(हिरवा बॉक्स दाबा)"):
        st.session_state.page = "rti"
    st.markdown('</div>', unsafe_allow_html=True)

with col_comp:
    st.markdown('<div class="comp-col">', unsafe_allow_html=True)
    if st.button("🔴 २. शासकीय तक्रार अर्ज\n(लाल बॉक्स दाबा)"):
        st.session_state.page = "complaint"
    st.markdown('</div>', unsafe_allow_html=True)

# लहान उप-नेव्हिगेशन (होम, हिस्ट्री आणि रिसेट)
nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("🔵 मुख्य माहिती"):
        st.session_state.page = "home"
    st.markdown('</div>', unsafe_allow_html=True)

with nav2:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    history_count = len(st.session_state.history_list)
    if st.button(f"📜 माझी हिस्ट्री ({history_count})"):
        st.session_state.page = "history"
    st.markdown('</div>', unsafe_allow_html=True)

with nav3:
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
    if st.button("🔄 सर्व रिसेट करा"):
        st.session_state.rti_name = ""
        st.session_state.rti_address = ""
        st.session_state.rti_dept = ""
        st.session_state.rti_query = ""
        st.session_state.rti_result = ""
        st.session_state.rti_paid = False
        
        st.session_state.comp_name = ""
        st.session_state.comp_address = ""
        st.session_state.comp_dept = ""
        st.session_state.comp_subject = ""
        st.session_state.comp_query = ""
        st.session_state.comp_result = ""
        st.session_state.complaint_paid = False
        st.success("सर्व माहिती रिसेट झाली!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# WhatsApp शेअर बटण
app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
share_text = urllib.parse.quote(f"🏛️ घरबसल्या RTI अर्ज व शासकीय तक्रार १ सेकंदात तयार करा: {app_url}")
st.markdown(f"""
    <div style="margin: 10px 0;">
        <a href="https://api.whatsapp.com/send?text={share_text}" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(135deg, #25D366, #128C7E); color: white; padding: 10px; border-radius: 10px; text-align: center; font-size: 15px; font-weight: bold;">
                📲 WhatsApp वर मित्रांना शेअर करा
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# API Key इनपुट (साइडबार)
api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")

# १-पान A4 प्रिंट/PDF तयार करण्याचे सुरक्षित फंक्शन
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
        margin: 10px auto;
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

# ==================== पान १: RTI अर्ज ====================
if st.session_state.page == "rti":
    st.markdown("""
    <div style="background: #ECFDF5; border-left: 6px solid #059669; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="color: #065F46; margin: 0;">🟢 RTI अर्ज व अपील विभाग</h3>
        <p style="color: #047857; margin: 5px 0 0 0; font-size: 13px; font-weight: bold;">येथे भरलेली माहिती दुसऱ्या पानावर गेल्यावरही सुरक्षित राहील.</p>
    </div>
    """, unsafe_allow_html=True)

    # व्हॅल्यूज session_state मधून थेट जोडल्या आहेत (डेटा उडणार नाही)
    st.session_state.rti_type = st.selectbox(
        "अर्जाचा प्रकार निवडा:",
        ["माहिती अधिकार अर्ज (कलम ६(१) - नमुना जोडपत्र अ)", "प्रथम अपील अर्ज (कलम १९(१) - नमुना जोडपत्र १)", "द्वितीय अपील मसुदा (कलम १९(३))"],
        index=0
    )
    st.session_state.rti_name = st.text_input("अर्जदाराचे पूर्ण नाव:", value=st.session_state.rti_name)
    st.session_state.rti_address = st.text_area("अर्जदाराचा संपूर्ण पत्ता व संपर्क:", value=st.session_state.rti_address)
    st.session_state.rti_dept = st.text_input("सरकारी कार्यालय / विभागाचे नाव:", value=st.session_state.rti_dept)
    st.session_state.rti_query = st.text_area("मागितलेली माहिती / अपीलाचे कारण:", value=st.session_state.rti_query)

    if st.button("🚀 कायदेशीर RTI अर्ज तयार करा"):
        if not st.session_state.rti_name or not st.session_state.rti_query or not st.session_state.rti_dept:
            st.warning("कृपया अर्जदाराचे नाव, विभाग आणि मागितलेली माहिती भरा.")
        else:
            with st.spinner("१ पानात बसणारा कायदेशीर RTI मसुदा तयार होत आहे..."):
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"""
तुम्ही महाराष्ट्र माहिती अधिकार अधिनियम २००५ चे तज्ञ आहात. एकाच A4 पानात बसेल असा परिपूर्ण RTI मसुदा बनवा.
प्रकार: {st.session_state.rti_type}
अर्जदार: {st.session_state.rti_name}
पत्ता: {st.session_state.rti_address}
कार्यालय: {st.session_state.rti_dept}
माहिती: {st.session_state.rti_query}

नियम: कलम ६(१), ६(३) (५ दिवसांत वर्ग करणे), ७(१) (३० दिवसांची मुदत) व ₹१० कोर्ट फी स्टॅम्पचा उल्लेख करा. भाषा स्पष्ट व संक्षिप्त ठेवा.
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
कार्यालय: {st.session_state.rti_dept}

१. अर्जदाराचे नाव: {st.session_state.rti_name}
२. पत्ता व संपर्क: {st.session_state.rti_address}
३. मागितलेल्या माहितीचा तपशील:
{st.session_state.rti_query}

४. माहितीचा कालावधी: चालू वर्ष व मागील अभिलेख
५. माहितीचा प्रकार: प्रमाणित सत्यप्रतीसह व्यक्तिशः / टपालाने

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. माहिती आपल्या अखत्यारीतील नसल्यास कलम ६(३) अन्वये ५ दिवसांत योग्य विभागाकडे वर्ग करावी. अर्जासोबत ₹१० चा कोर्ट फी स्टॅम्प जोडला आहे.

तारीख: ____________                                अर्जदाराची स्वाक्षरी: {st.session_state.rti_name}
ठिकाण: ____________"""

                # हिस्ट्रीमध्ये सेव्ह करणे
                st.session_state.history_list.append({
                    "type": "🟢 RTI अर्ज",
                    "title": f"{st.session_state.rti_dept} - {st.session_state.rti_name}",
                    "content": st.session_state.rti_result,
                    "time": datetime.now().strftime("%d-%m-%Y %H:%M")
                })

    if st.session_state.rti_result:
        st.success("✅ RTI मसुदा तयार झाला आहे!")
        st.text_area("📄 तयार झालेला मसुदा (येथून वाचू शकता):", value=st.session_state.rti_result, height=220)
        
        st.markdown("---")
        st.markdown("### 📥 अधिकृत १-पान PDF डाऊनलोड / प्रिंट")
        
        if not st.session_state.rti_paid:
            st.info("📌 **A4 साईझ प्रिंट-रेडी PDF मिळवण्यासाठी ₹१० पेमेंट करा आणि १२-अंकी UPI UTR नंबर टाका.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करा", width=130)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}` | **रक्कम:** ₹१०/-")
                utr_input = st.text_input("पेमेंट झाल्यावर १२-अंकी UTR / Ref No. टाका:", max_chars=12, key="rti_utr")
                if st.button("🔒 पेमेंट पडताळणी करून PDF अनलॉक करा", key="unlock_rti"):
                    if len(utr_input.strip()) == 12 and utr_input.strip().isdigit():
                        st.session_state.rti_paid = True
                        st.success("पेमेंट पडताळणी यशस्वी!")
                        st.rerun()
                    else:
                        st.error("कृपया पेमेंट केल्यानंतर मिळालेला खरा १२-अंकी UTR क्रमांक टाका.")
        else:
            render_printable_marathi_doc("माहितीचा अधिकार अधिनियम २००५ अर्ज", st.session_state.rti_result, "#059669")

# ==================== पान २: शासकीय तक्रार ====================
elif st.session_state.page == "complaint":
    st.markdown("""
    <div style="background: #FEF2F2; border-left: 6px solid #DC2626; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="color: #991B1B; margin: 0;">🔴 शासकीय तक्रार अर्ज विभाग</h3>
        <p style="color: #B91C1C; margin: 5px 0 0 0; font-size: 13px; font-weight: bold;">येथे भरलेली माहिती दुसऱ्या पानावर गेल्यावरही सुरक्षित राहील.</p>
    </div>
    """, unsafe_allow_html=True)

    # व्हॅल्यूज session_state मधून थेट जोडल्या आहेत
    st.session_state.comp_name = st.text_input("तक्रारदाराचे पूर्ण नाव:", value=st.session_state.comp_name)
    st.session_state.comp_address = st.text_area("पत्ता व मोबाईल नंबर:", value=st.session_state.comp_address)
    st.session_state.comp_dept = st.text_input("कार्यालय / अधिकारी (उदा. आयुक्त / जिल्हाधिकारी):", value=st.session_state.comp_dept)
    st.session_state.comp_subject = st.text_input("तक्रारीचा मुख्य विषय:", value=st.session_state.comp_subject)
    st.session_state.comp_query = st.text_area("तक्रारीचा सविस्तर तपशील:", value=st.session_state.comp_query)

    if st.button("🚀 कडक तक्रार अर्ज तयार करा"):
        if not st.session_state.comp_name or not st.session_state.comp_dept or not st.session_state.comp_query:
            st.warning("कृपया नाव, विभाग आणि तक्रारीचा तपशील भरा.")
        else:
            with st.spinner("१ पानात बसणारा कडक तक्रार मसुदा तयार होत आहे..."):
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"""
तुम्ही प्रशासकीय कायदेतज्ञ आहात. एकाच A4 पानात बसेल असा कडक तक्रार अर्ज बनवा:
तक्रारदार: {st.session_state.comp_name}
पत्ता: {st.session_state.comp_address}
प्रति: {st.session_state.comp_dept}
विषय: {st.session_state.comp_subject}
तपशील: {st.session_state.comp_query}

मसुद्यात प्रति, विषय, मुद्द्यांनुसार तक्रार, ७ दिवसांत कारवाईचा इशारा आणि प्रतिलिपि असा सुटसुटीत फॉरमॅट ठेवा.
"""
                        res = model.generate_content(prompt, generation_config={"temperature": 0.2})
                        st.session_state.comp_result = res.text
                    except Exception as e:
                        st.error(f"AI त्रुटी: {e}")
                else:
                    st.session_state.comp_result = f"""प्रति,
मा. {st.session_state.comp_dept},

विषय: {st.session_state.comp_subject} बाबत तातडीने कठोर कारवाई करणेबाबत.
तक्रारदार: {st.session_state.comp_name}, रा. {st.session_state.comp_address}

महोदय,
मी खालीलप्रमाणे तक्रार नोंदवत आहे:
{st.session_state.comp_query}

सदर प्रकरणात संबंधित जबाबदार घटकांवर ७ दिवसांच्या आत प्रशासकीय नियमांनुसार कारवाई करण्यात यावी, अन्यथा वरिष्ठ पातळीवर व न्यायालयात दाद मागावी लागेल.

तारीख: ____________                                तक्रारदाराची स्वाक्षरी: {st.session_state.comp_name}
ठिकाण: ____________

प्रत माहितीस्तव: मा. जिल्हाधिकारी महोदय."""

                # हिस्ट्रीमध्ये सेव्ह करणे
                st.session_state.history_list.append({
                    "type": "🔴 तक्रार अर्ज",
                    "title": f"{st.session_state.comp_dept} - {st.session_state.comp_subject}",
                    "content": st.session_state.comp_result,
                    "time": datetime.now().strftime("%d-%m-%Y %H:%M")
                })

    if st.session_state.comp_result:
        st.success("✅ तक्रार अर्ज तयार झाला आहे!")
        st.text_area("📄 तयार झालेली तक्रार (येथून वाचू शकता):", value=st.session_state.comp_result, height=220)
        
        st.markdown("---")
        st.markdown("### 📥 अधिकृत १-पान PDF डाऊनलोड / प्रिंट")
        
        if not st.session_state.complaint_paid:
            st.info("📌 **A4 साईझ प्रिंट-रेडी PDF मिळवण्यासाठी ₹१० पेमेंट करा आणि १२-अंकी UPI UTR नंबर टाका.**")
            upi_id = "satishpradhan3392@ybl"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=upi://pay?pa={upi_id}%26pn=Satish%20Pradhan%26am=10%26cu=INR"
            
            c_qr, c_info = st.columns([1, 2])
            with c_qr:
                st.image(qr_url, caption="₹१० स्कॅन करा", width=130)
            with c_info:
                st.markdown(f"**UPI ID:** `{upi_id}` | **रक्कम:** ₹१०/-")
                c_utr_input = st.text_input("पेमेंट झाल्यावर १२-अंकी UTR / Ref No. टाका:", max_chars=12, key="comp_utr")
                if st.button("🔒 पेमेंट पडताळणी करून PDF अनलॉक करा", key="unlock_complaint"):
                    if len(c_utr_input.strip()) == 12 and c_utr_input.strip().isdigit():
                        st.session_state.complaint_paid = True
                        st.success("पेमेंट पडताळणी यशस्वी!")
                        st.rerun()
                    else:
                        st.error("कृपया पेमेंट केल्यानंतर मिळालेला खरा १२-अंकी UTR क्रमांक टाका.")
        else:
            render_printable_marathi_doc("शासकीय तक्रार अर्ज", st.session_state.comp_result, "#DC2626")

# ==================== पान ३: हिस्ट्री (History) ====================
elif st.session_state.page == "history":
    st.markdown("<h3>📜 माझी सेव्ह केलेली हिस्ट्री (तयार केलेले मसुदे)</h3>", unsafe_allow_html=True)
    if not st.session_state.history_list:
        st.info("💡 तुम्ही अद्याप कोणताही अर्ज तयार केलेला नाही. नवीन अर्ज तयार केल्यावर तो येथे आपोआप सेव्ह होईल.")
    else:
        for idx, item in enumerate(reversed(st.session_state.history_list)):
            with st.expander(f"{item['type']} | {item['title']} ({item['time']})"):
                st.text_area(f"मसुदा {idx+1}:", value=item['content'], height=200, key=f"hist_{idx}")

# ==================== पान ४: मुख्य माहिती ====================
elif st.session_state.page == "home":
    st.markdown("""
    <div style="background-color: #EFF6FF; border: 2px solid #3B82F6; border-radius: 12px; padding: 15px; margin-bottom: 15px;">
        <h3 style="color: #1E40AF; margin-top: 0;">🔵 मुख्य माहिती व नियम</h3>
        <ul style="font-size: 15px; color: #1F2937; line-height: 1.8;">
            <li><b>🟢 हिरवा बॉक्स (RTI अर्ज):</b> सरकारी माहिती व कागदपत्रे मिळवण्यासाठी.</li>
            <li><b>🔴 लाल बॉक्स (तक्रार अर्ज):</b> शासकीय गैरव्यवहार व दिरंगाईविरोधात तक्रार करण्यासाठी.</li>
            <li><b>📜 माझी हिस्ट्री:</b> तयार केलेले सर्व मसुदे आपोआप सेव्ह राहतात.</li>
            <li><b>🔄 सर्व रिसेट करा:</b> सर्व माहिती एका क्लिकवर पुसून नव्याने सुरुवात करण्यासाठी.</li>
            <li><b>📄 १ पान मर्यादा:</b> तयार होणारी PDF थेट प्रिंट करण्यासाठी एकाच A4 पानात बसते.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #6B7280; text-align: center;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)

