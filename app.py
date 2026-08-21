import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि ब्रँडिंग लपवणे
# ==============================================================================
st.set_page_config(page_title="RTI, तक्रार व न्यायालयीन AI महा-सहाय्यक", page_icon="⚖️", layout="wide")

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800;900&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    visibility: hidden; display: none !important;
}
div[class^="viewerBadge"] { visibility: hidden; display: none !important; }
button[title="View source"] { display: none; }

h1 { color: #1E3A8A; font-weight: 900; text-align: center; font-size: 24px; margin-bottom: 4px; }

/* मुख्य ४ रंगीत बटने */
div.st-key-btn_tab1 button {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    color: white !important; height: 60px !important; border-radius: 12px !important;
}
div.st-key-btn_tab2 button {
    background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
    color: white !important; height: 60px !important; border-radius: 12px !important;
}
div.st-key-btn_tab3 button {
    background: linear-gradient(135deg, #D97706, #F59E0B) !important;
    color: white !important; height: 60px !important; border-radius: 12px !important;
}
div.st-key-btn_tab4 button {
    background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important;
    color: white !important; height: 60px !important; border-radius: 12px !important;
}
div.st-key-btn_tab5 button {
    background: linear-gradient(135deg, #DC2626, #EF4444) !important;
    color: white !important; height: 60px !important; border-radius: 12px !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# २. सेशन स्टेट मॅनेजमेंट (डेटा कायम पुढे कॅरी-फॉरवर्ड करण्यासाठी)
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'appeal_reason' not in st.session_state: st.session_state.appeal_reason = "विहित ३० दिवसांची मुदत संपूनही जन माहिती अधिकाऱ्याने कोणतीही माहिती दिली नाही / दिलेली माहिती अपूर्ण व दिशाभूल करणारी आहे."
if 'court_type' not in st.session_state: st.session_state.court_type = "मा. उच्च न्यायालय (रिट याचिका - कलम २२६)"
if 'court_prayer' not in st.session_state: st.session_state.court_prayer = ""
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'history_list' not in st.session_state: st.session_state.history_list = []

# ==============================================================================
# ३. अधिकृत पत्ते व डेटाबेस (माहिती आयोग व न्यायालये)
# ==============================================================================
COMMISSION_ADDRESSES = {
    "छत्रपती संभाजीनगर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ छत्रपती संभाजीनगर, शासकीय सुभेदारी विश्रामगृह समोर, बाबा पेट्रोल पंपाजवळ, छत्रपती संभाजीनगर - ४३१००१ (फोन: ०२४०-२३५२५४४)",
    "मुंबई मुख्य खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य मुख्य माहिती आयुक्त, राज्य माहिती आयोग, १३ वा मजला, नवीन प्रशासकीय इमारत, मंत्रालयासमोर, मादाम कामा रोड, मुंबई - ४०००३२ (फोन: ०२२-२२८५६०७८)",
    "पुणे खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ पुणे, नवीन प्रशासकीय इमारत, कौन्सिल हॉल समोर, पुणे - ४११००१",
    "नागपूर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नागपूर, रवी भवन, नागपूर - ४४०००१",
    "नाशिक खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नाशिक, जिल्हाधिकारी कार्यालय आवार, नाशिक - ४२२००२",
    "अमरावती खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ अमरावती, प्रशासकीय इमारत, अमरावती - ४४४६०१",
    "कोकण खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ कोकण भवन, सी.बी.डी. बेलापूर, नवी मुंबई - ४००६१४",
    "केंद्रीय माहिती आयोग (CIC New Delhi)": "मा. मुख्य माहिती आयुक्त, केंद्रीय माहिती आयोग (CIC), बाबा गंगनाथ मार्ग, मुनिरका, नवी दिल्ली - ११००६७"
}

COURT_ADDRESSES = {
    "मा. उच्च न्यायालय (रिट याचिका - कलम २२६)": "मा. उच्च न्यायालय मुंबई, खंडपीठ छत्रपती संभाजीनगर / मुंबई / नागपूर",
    "जिल्हा ग्राहक तक्रार निवारण आयोग (ग्राहक संरक्षण कायदा २०१९)": "मा. अध्यक्ष / सदस्य, जिल्हा ग्राहक तक्रार निवारण आयोग",
    "जिल्हा व सत्र न्यायालय (दिवाणी / फौजदारी दावा)": "मा. प्रमुख जिल्हा व सत्र न्यायाधीश महोदय",
    "केंद्रीय प्रशासकीय न्यायाधिकरण (CAT) / MAT": "मा. महाराष्ट्र प्रशासकीय न्यायाधिकरण (MAT) / CAT खंडपीठ"
}

# ==============================================================================
# ४. API की आणि AI फंक्शन
# ==============================================================================
sidebar_api_key = st.sidebar.text_input("🔑 Gemini API Key (ऐच्छिक):", type="password")
active_api_key = sidebar_api_key if sidebar_api_key else st.secrets.get("GEMINI_API_KEY", "")

def generate_ai_draft(prompt_text):
    if active_api_key:
        try:
            genai.configure(api_key=active_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            res = model.generate_content(prompt_text, generation_config={"temperature": 0.2})
            return res.text
        except Exception as e:
            st.error(f"AI त्रुटी: {e}")
            return None
    return None

def render_printable_doc(title, content, theme_color="#059669"):
    html_content = content.replace('\n', '<br>')
    printable_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700&display=swap" rel="stylesheet">
    <div id="printArea" style="
        font-family: 'Mukta', sans-serif; background: #ffffff; color: #000000; padding: 30px 40px;
        border: 3px solid {theme_color}; border-radius: 8px; line-height: 1.6; font-size: 15px;
        max-width: 800px; margin: 10px auto; box-sizing: border-box;
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
            background: {theme_color}; color: white; padding: 12px 28px; font-size: 17px; font-weight: bold;
            border: none; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.25);
        ">
            🖨️ १ पानात PDF सेव्ह / प्रिंट करा (Save as PDF)
        </button>
    </div>
    """
    st.components.v1.html(printable_html, height=540, scrolling=True)

# ==============================================================================
# ५. मुख्य शीर्ष व नॅव्हिगेशन बटने
# ==============================================================================
st.markdown("<h1>⚖️ RTI, तक्रार व न्यायालयीन AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 13px; font-weight: bold; color: #4B5563;'>जोडपत्र अ ➔ जोडपत्र ब ➔ जोडपत्र क (माहिती आयोग) ➔ न्यायालयीन याचिका (ऑटो-डेटा ट्रान्सफर)</p>", unsafe_allow_html=True)
st.markdown("---")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("🟢 १. जोडपत्र 'अ'\n(मूळ RTI अर्ज)", key="btn_tab1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with c2:
    if st.button("🔵 २. जोडपत्र 'ब'\n(प्रथम अपील)", key="btn_tab2"): st.session_state.active_tab = "जोडपत्र 'ब'"
with c3:
    if st.button("🟠 ३. जोडपत्र 'क'\n(माहिती आयोग)", key="btn_tab3"): st.session_state.active_tab = "जोडपत्र 'क'"
with c4:
    if st.button("🟣 ४. न्यायालयीन मसुदा\n(Court / Petition)", key="btn_tab4"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with c5:
    if st.button("🔴 ५. शासकीय तक्रार\n(कडक तक्रार अर्ज)", key="btn_tab5"): st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# विभाग १: जोडपत्र 'अ' (मूळ RTI अर्ज - कलम ६(१))
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.markdown("### 🟢 नमुना जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        u_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        u_addr = st.text_area("२. अर्जदाराचा संपूर्ण पत्ता व मोबाईल क्र.:", value=st.session_state.user_address)
        u_dept = st.text_input("३. सरकारी कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        u_query = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्दे):", value=st.session_state.original_query)
        
        sub_a = st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा व पुढील अपीलासाठी डेटा सेव्ह करा")
        if sub_a:
            st.session_state.user_name = u_name
            st.session_state.user_address = u_addr
            st.session_state.dept_name = u_dept
            st.session_state.original_query = u_query
            date_str = datetime.now().strftime("%d/%m/%Y")
            
            ai_p = f"महाराष्ट्र RTI कायदा २००५ च्या कलम ६(१) नुसार जोडपत्र 'अ' तयार करा. अर्जदार: {u_name}, पत्ता: {u_addr}, कार्यालय: {u_dept}, माहिती: {u_query}. कलम ६(३), ७(१) व ₹१० कोर्ट फी चा उल्लेख करा."
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'अ' (नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील माहिती मिळवण्यासाठीचा अर्ज.

प्रति,
जन माहिती अधिकारी,
कार्यालय: {u_dept}

१. अर्जदाराचे पूर्ण नाव : {u_name}
२. अर्जदाराचा पत्ता व संपर्क : {u_addr}
३. मागितलेल्या माहितीचा तपशील :
{u_query}

४. माहितीचा कालावधी : चालू वर्ष व मागील उपलब्ध अभिलेख
५. माहितीचा प्रकार : प्रमाणित सत्यप्रतीसह व्यक्तिशः / टपालाने
६. अर्ज शुल्क : ₹१०/- (कोर्ट फी स्टॅम्प / चलनाद्वारे जोडले आहे).

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. माहिती आपल्या कार्यालयाशी संबंधित नसल्यास कलम ६(३) अन्वये ५ दिवसांत योग्य विभागाकडे वर्ग करावी. अर्जात काही गोपनीय भाग असल्यास कलम १० (विभक्तता तत्त्व) चा वापर करून उर्वरित माहिती विहित मुदतीत पुरवण्यात यावी.

दिनांक: {date_str}                                     अर्जदाराची स्वाक्षरी: {u_name}
ठिकाण: ________________"""

            st.success("✅ जोडपत्र 'अ' तयार झाले! हाच डेटा आता जोडपत्र 'ब' आणि 'क' मध्ये आपोआप जोडला गेला आहे.")

# ==============================================================================
# विभाग २: जोडपत्र 'ब' (प्रथम अपील - कलम १९(१))
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.markdown("### 🔵 नमुना जोडपत्र 'ब' - प्रथम अपील अर्ज (कलम १९(१))")
    st.info("💡 **जोडपत्र 'अ' मधील नाव, पत्ता, कार्यालय व मागितलेली माहिती येथे आपोआप भरली गेली आहे.**")
    
    with st.form("form_b"):
        u_name = st.text_input("१. अपिलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
        u_addr = st.text_area("२. अपिलकर्त्याचा संपूर्ण पत्ता:", value=st.session_state.user_address)
        u_dept = st.text_input("३. प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        u_query = st.text_area("४. मूळ अर्जात मागितलेली माहिती:", value=st.session_state.original_query)
        u_reason = st.text_area("५. प्रथम अपीलाचे कारण:", value=st.session_state.appeal_reason)
        
        sub_b = st.form_submit_button("🚀 जोडपत्र 'ब' तयार करा व माहिती आयोगासाठी डेटा ट्रान्सफर करा")
        if sub_b:
            st.session_state.user_name = u_name
            st.session_state.user_address = u_addr
            st.session_state.dept_name = u_dept
            st.session_state.original_query = u_query
            st.session_state.appeal_reason = u_reason
            date_str = datetime.now().strftime("%d/%m/%Y")
            
            ai_p = f"महाराष्ट्र RTI कायदा २००५ कलम १९(१) जोडपत्र 'ब' प्रथम अपील बनवा. अपिलकर्ता: {u_name}, पत्ता: {u_addr}, कार्यालय: {u_dept}, माहिती: {u_query}, कारण: {u_reason}. कलम १०, कलम २० दंडात्मक कारवाई व सेवापुस्तकात नोंद करण्याची मागणी जोडा."
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'ब' (नियम ५ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपिलाचा नमुना.

प्रति,
प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी,
कार्यालय: {u_dept}

१. अपिलकर्त्याचे पूर्ण नाव : {u_name}
२. अपिलकर्त्याचा पत्ता व संपर्क : {u_addr}
३. जन माहिती अधिकाऱ्याचा तपशील : जन माहिती अधिकारी, {u_dept}
४. मूळ अर्ज (जोडपत्र 'अ') सादर केल्याचा दिनांक : विहित मुदतीपूर्वी
५. प्रथम अपीलाचे कारण : {u_reason}
६. मागितलेली मूळ माहिती :
{u_query}

७. मागितलेली दाद (Relief Sought) :
   १) कलम १० चा वापर करून तात्काळ संपूर्ण व प्रमाणित माहिती विनामूल्य देण्याचे आदेश जन माहिती अधिकाऱ्यास द्यावेत.
   २) माहिती दडवून ठेवल्याबद्दल संबंधित अधिकाऱ्यावर कलम २० अन्वये दंडात्मक कारवाई प्रस्तावित करावी व सेवापुस्तकात नोंद व्हावी.

दिनांक: {date_str}                                     अपिलकर्त्याची स्वाक्षरी: {u_name}
ठिकाण: ________________"""

            st.success("✅ जोडपत्र 'ब' तयार झाले! सर्व डेटा आता जोडपत्र 'क' (माहिती आयोग) मध्ये ऑटो-लोड झाला आहे.")

# ==============================================================================
# विभाग ३: जोडपत्र 'क' (द्वितीय अपील - माहिती आयोग कलम १९(३))
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.markdown("### 🟠 नमुना जोडपत्र 'क' - द्वितीय अपील (राज्य / केंद्रीय माहिती आयोग - कलम १९(३))")
    
    selected_bench = st.selectbox("१. माहिती आयोग खंडपीठ निवडा (पत्ता आपोआप भरला जाईल):", list(COMMISSION_ADDRESSES.keys()))
    bench_addr = COMMISSION_ADDRESSES[selected_bench]
    st.success(f"📍 **निवडलेला आयोग:** {bench_addr}")

    uploaded_pdf = st.file_uploader("पूर्वीचा RTI अर्ज किंवा प्रथम अपील आदेश अपलोड करा (ऐच्छिक):", type=["pdf", "png", "jpg"])

    with st.form("form_c"):
        u_name = st.text_input("अपीलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
        u_addr = st.text_area("अपीलकर्त्याचा पत्ता व संपर्क:", value=st.session_state.user_address)
        u_dept = st.text_input("प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        u_query = st.text_area("मूळ मागितलेली माहिती:", value=st.session_state.original_query)
        u_reason = st.text_area("द्वितीय अपीलाचे कायदेशीर आधार / कारणे:", value=f"प्रथम अपीलीय अधिकाऱ्यांनी आदेश देऊनही माहिती दिली नाही / {st.session_state.appeal_reason}")

        sub_c = st.form_submit_button("⚖️ संपूर्ण द्वितीय अपील (जोडपत्र क) मसुदा जनरेट करा")
        if sub_c:
            date_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"महाराष्ट्र RTI कलम १९(३) जोडपत्र 'क' द्वितीय अपील मसुदा बनवा. आयोग: {bench_addr}, अपिलकर्ता: {u_name}, पत्ता: {u_addr}, कार्यालय: {u_dept}, माहिती: {u_query}, आधार: {u_reason}. कलम १०, कलम २०(१) ₹२५,००० दंड व कलम २०(२) शिस्तभंगाची मागणी जोडा."
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'क'
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपिलाचा अधिकृत नमुना.

प्रति,
{bench_addr}

१. अपिलकर्त्याचे पूर्ण नाव : {u_name}
२. अपिलकर्त्याचा पत्ता व संपर्क : {u_addr}
३. जन माहिती अधिकारी : जन माहिती अधिकारी, {u_dept}
४. प्रथम अपीलीय अधिकारी : प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी, {u_dept}
५. द्वितीय अपीलाचे कारण व मागितलेली माहिती :
{u_query}

६. कायदेशीर आधार : {u_reason}
७. मागितलेली दाद / प्रार्थना :
   १) कलम १० (विभक्तता तत्त्व) नुसार संपूर्ण अभिलेख विनामूल्य उपलब्ध करून देण्याचे आदेश व्हावेत.
   २) विहित मुदतीत माहिती न दिल्याबद्दल जन माहिती अधिकाऱ्यावर कलम २०(१) अन्वये २५,०००/- रुपये कमाल दंड आकारण्यात यावा व कलम २०(२) अन्वये शिस्तभंगाची कारवाई करून सेवापुस्तकात नोंद व्हावी.

दिनांक: {date_str}                                     अपिलकर्त्याची स्वाक्षरी: {u_name}
ठिकाण: ________________"""
            st.success("✅ जोडपत्र 'क' द्वितीय अपील मसुदा तयार झाला आहे!")

# ==============================================================================
# विभाग ४: न्यायालयीन मसुदा (Court Petition / Legal Draft)
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.markdown("### 🟣 न्यायालयीन याचिका व कायदेशीर ड्राफ्ट (Court Petition / Legal Notice)")
    st.info("💡 **माहिती आयोग, ग्राहक संरक्षण, किंवा प्रशासकीय दिरंगाईविरोधात थेट न्यायालयीन मसुदा ऑटो-जनरेट करा.**")

    court_choice = st.selectbox("१. न्यायालय / लवादाचे नाव निवडा:", list(COURT_ADDRESSES.keys()))
    court_full = COURT_ADDRESSES[court_choice]
    st.success(f"🏛️ **न्यायालय:** {court_full}")

    with st.form("form_court"):
        u_name = st.text_input("वादी / याचिकाकर्त्याचे नाव (Petitioner):", value=st.session_state.user_name)
        u_addr = st.text_area("पत्ता व संपर्क:", value=st.session_state.user_address)
        u_dept = st.text_input("प्रतिवादी कार्यालय / व्यक्ती (Respondent):", value=st.session_state.dept_name)
        case_subject = st.text_input("प्रकरणाचा संक्षिप्त विषय:", value="माहिती न देणे / प्रशासकीय दिरंगाई / सेवेतील त्रुटी व नुकसानभरपाई बाबत")
        case_facts = st.text_area("प्रकरणाची सविस्तर पार्श्वभूमी व हकीकत:", value=f"मूळ मागणी: {st.session_state.original_query}\nतक्रार/अपील कारण: {st.session_state.appeal_reason}")
        court_prayer_input = st.text_area("न्यायालयाकडून मागितलेली दाद (Prayer / Relief):", value="प्रतिवादीस तात्काळ आदेश देऊन न्याय मिळवून देण्यात यावा व झालेल्या मानसिक व आर्थिक त्रासापोटी योग्य नुकसानभरपाई मंजूर करण्यात यावी.")

        sub_court = st.form_submit_button("⚖️ संपूर्ण न्यायालयीन मसुदा (Legal Petition) जनरेट करा")
        if sub_court:
            date_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"""
तुम्ही उच्च न्यायालयीन कायदेतज्ञ आहात. खालील माहितीवरून परिपूर्ण मराठी न्यायालयीन मसुदा (Petition/Application) बनवा:
न्यायालय: {court_full}
याचिकाकर्ता (Petitioner): {u_name}, रा. {u_addr}
प्रतिवादी (Respondent): {u_dept}
विषय: {case_subject}
हकीकत व मुद्दे: {case_facts}
प्रार्थना (Prayer): {court_prayer_input}

मसुद्यात: १. न्यायालयाचे नाव, २. पक्षकारांची नावे, ३. प्रकरणाची वस्तुस्थिती, ४. कायदेशीर मुद्दे, ५. प्रार्थना (Prayer), ६. सत्यप्रतिज्ञा (Verification) असा योग्य कायदेशीर फॉरमॅट तयार करा.
"""
            ai_res = generate_ai_draft(ai_p)
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""मा. {court_full}
याचिका / अर्ज क्र. _________ / २०२६

{u_name}, वय: प्रौढ, रा. {u_addr}
... याचिकाकर्ता / वादी

विरुद्ध

{u_dept}
... प्रतिवादी

विषय: {case_subject}

याचिकाकर्त्याची सविनय विनंती खालीलप्रमाणे आहे:
१. वस्तुस्थिती (Brief Facts):
{case_facts}

२. कायदेशीर आधार: प्रतिवादीने नैसर्गिक न्यायतत्त्वांचे आणि वैधानिक कर्तव्याचे उल्लंघन केले आहे.

३. प्रार्थना (Prayer):
अ) {court_prayer_input}
ब) या अर्जाचा संपूर्ण खर्च प्रतिवादीकडून याचिकाकर्त्यास मिळवून देण्यात यावा.

सत्यप्रतिज्ञा (Verification):
मी, {u_name}, याद्वारे घोषित करतो की वरील परिच्छेदांमधील मजकूर माझ्या व्यक्तिगत माहितीनुसार सत्य व बिनचूक आहे.

दिनांक: {date_str}                                     याचिकाकर्त्याची स्वाक्षरी: {u_name}
ठिकाण: ________________"""
            st.success("✅ न्यायालयीन मसुदा यशस्वीरीत्या जनरेट झाला आहे!")

# ==============================================================================
# विभाग ५: शासकीय तक्रार अर्ज
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.markdown("### 🔴 शासकीय तक्रार अर्ज विभाग")
    with st.form("form_comp"):
        u_name = st.text_input("तक्रारदाराचे नाव:", value=st.session_state.user_name)
        u_addr = st.text_area("पत्ता व मोबाईल:", value=st.session_state.user_address)
        u_dept = st.text_input("कार्यालय / अधिकारी (उदा. जिल्हाधिकारी / आयुक्त):", value=st.session_state.dept_name)
        comp_sub = st.text_input("तक्रारीचा विषय:", value="प्रशासकीय दिरंगाई व कारवाई करणेबाबत")
        comp_body = st.text_area("तक्रारीचा तपशील:", value=st.session_state.appeal_reason)

        sub_comp = st.form_submit_button("🚀 कडक शासकीय तक्रार अर्ज तयार करा")
        if sub_comp:
            st.session_state.user_name = u_name
            st.session_state.user_address = u_addr
            st.session_state.dept_name = u_dept
            date_str = datetime.now().strftime("%d/%m/%Y")
            
            ai_p = f"प्रशासकीय तक्रार अर्ज बनवा. तक्रारदार: {u_name}, पत्ता: {u_addr}, प्रति: {u_dept}, विषय: {comp_sub}, तपशील: {comp_body}. ७ दिवसांत कारवाईचा इशारा द्या."
            ai_res = generate_ai_draft(ai_p)
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""प्रति,
मा. {u_dept},

विषय: {comp_sub} बाबत तातडीने कठोर कारवाई करणेबाबत.
तक्रारदार: {u_name}, रा. {u_addr}

महोदय,
मी खालीलप्रमाणे तक्रार नोंदवत आहे:
{comp_body}

सदर प्रकरणात जबाबदार घटकांवर ७ दिवसांच्या आत कायदेशीर व प्रशासकीय नियमांनुसार कारवाई करण्यात यावी, अन्यथा वरिष्ठ पातळीवर व न्यायालयात दाद मागावी लागेल.

दिनांक: {date_str}                                     तक्रारदाराची स्वाक्षरी: {u_name}
ठिकाण: ________________"""
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला आहे!")

# ==============================================================================
# निकाल, १-पान A4 PDF प्रिंट व कॉपी पर्याय
# ==============================================================================
if st.session_state.final_draft:
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अंतिम कायदेशीर मसुदा:")
    st.text_area("मसुदा वाचा किंवा कॉपी करा:", value=st.session_state.final_draft, height=260)
    
    st.markdown("### 📥 १-पानात PDF डाऊनलोड / प्रिंट")
    render_printable_doc(st.session_state.active_tab, st.session_state.final_draft, "#1E3A8A")

# ==============================================================================
# 🚀 भविष्यकालीन नवीन अपडेट्स व कोर्ट केसेससाठी राखीव जागा (CUSTOM EXTENSION AREA)
# ==============================================================================
# भविष्यात कोणतेही नवीन फीचर, नवीन कोर्ट ड्राफ्ट किंवा कोड जोडण्यासाठी खालील जागा राखीव आहे:
# ------------------------------------------------------------------------------

# (येथे खाली नवीन कोड पेस्ट करा...)
// draftGenerator.js - कोर ऑटोमेशन लॉजिक

const legalRules = {
  "ग्राहक_तक्रार": {
    court: "जिल्हा ग्राहक वाद निवारण आयोग",
    sections: "ग्राहक संरक्षण कायदा, २०१९ चे कलम ३५ अन्वये",
    prayer: "अनुचित व्यापारी प्रथा (Unfair Trade Practice) व सेवेतील त्रुटीबद्दल नुकसानभरपाई मिळणेबाबत."
  },
  "माहिती_अधिकार_प्रथम_अपिल": {
    court: "प्रथम अपिलीय अधिकारी कार्यालय",
    sections: "माहितीचा अधिकार अधिनियम, २००५ चे कलम १९(१) अन्वये",
    prayer: "मुदतीत व अचूक माहिती विनामूल्य मिळणेबाबत आदेश व्हावेत."
  },
  "फसवणूक_फौजदारी": {
    court: "प्रथम वर्ग न्यायदंडाधिकारी न्यायालय (JMFC)",
    sections: "भारतीय नागरिक सुरक्षा संहिता (BNSS) / IPC सुसंगत कलमे",
    prayer: "आरोपीविरुद्ध कायदेशीर चौकशी करून योग्य ती कारवाई करणेबाबत."
  }
};

function generateCourtDraft(data) {
  const { caseType, applicantName, applicantAddress, oppositePartyName, oppositePartyAddress, incidentDetails, claimAmount } = data;
  
  const rule = legalRules[caseType] || {
    court: data.customCourt || "मा. न्यायालय / सक्षम प्राधिकरण",
    sections: "सुसंगत कायदेशीर कलमांन्वये",
    prayer: "योग्य तो कायदेशीर न्याय मिळणेबाबत."
  };

  const draftText = `
न्यायालय: ${rule.court}
--------------------------------------------------------------------------------
अर्ज क्र. / तक्रार क्र.: ________ / २०२६

${applicantName}
रा. ${applicantAddress}
... अर्जदार / तक्रारदार

विरुद्ध

${oppositePartyName}
रा. ${oppositePartyAddress}
... गैरअर्जदार / प्रतिवादी

विषय: ${rule.sections} दाखल केलेला अर्ज/तक्रार.

महोदय,
अर्जदार खालीलप्रमाणे सविस्तर तक्रार/अर्ज सादर करतो:

१. अर्जदाराचा प्राथमिक तपशील:
   अर्जदार हा वरील पत्त्यावर राहत असून सुजाण नागरिक आहे.

२. प्रकरणाची पार्श्वभूमी व तथ्ये:
   ${incidentDetails}

३. कायदेशीर आधार व कलमे:
   सदर प्रकरणात गैरअर्जदाराने केलेल्या कृत्यामुळे ${rule.sections} चे उल्लंघन झाले असून अर्जदाराचे थेट आर्थिक/मानसिक नुकसान झाले आहे.

४. नुकसानीची मागणी / क्लेम:
   ${claimAmount ? `एकूण मागणी / भरपाई रक्कम: ₹ ${claimAmount}` : 'कायद्यानुसार योग्य ती नुकसानभरपाई व कारवाई.'}

५. प्रार्थना (Prayer):
   अ) गैरअर्जदारावर कायद्यानुसार कारवाई करून वरील विषयानुसार दाद मिळावी.
   ब) ${rule.prayer}
   क) इतर योग्य वाटणारा दिलासा अर्जदारास देण्यात यावा.

दिनांक: ${new Date().toLocaleDateString('mr-IN')}
ठिकाण: ____________                                        (स्वाक्षरी)
                                                   ${applicantName}
                                                   (अर्जदार/तक्रारदार)
--------------------------------------------------------------------------------
`;

  return {
    status: "success",
    draft: draftText.trim(),
    metadata: {
      generatedAt: new Date().toISOString(),
      court: rule.court,
      sections: rule.sections
    }
  };
}

module.exports = { generateCourtDraft };
// server.js
const express = require('express');
const { generateCourtDraft } = require('./draftGenerator');
const app = express();

app.use(express.json());

app.post('/api/generate-draft', (req, res) => {
  try {
    const draftResponse = generateCourtDraft(req.body);
    res.status(200).json(draftResponse);
  } catch (error) {
    res.status(500).json({ status: "error", message: error.message });
  }
});

app.listen(3000, () => {
  console.log("Legal Drafting Engine running on port 3000");
});

# ==============================================================================
# १. पेज सेटिंग्ज आणि डिझाइन
# ==============================================================================
st.set_page_config(page_title="RTI व न्यायालयीन AI महा-सहाय्यक", page_icon="⚖️", layout="wide")

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800;900&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    visibility: hidden; display: none !important;
}
div[class^="viewerBadge"] { visibility: hidden; display: none !important; }
button[title="View source"] { display: none; }

h1 { color: #1E3A8A; font-weight: 900; text-align: center; font-size: 24px; margin-bottom: 4px; }

/* मुख्य ५ रंगीत नेव्हिगेशन बटने */
div.st-key-btn_a button { background: linear-gradient(135deg, #059669, #10B981) !important; color: white !important; height: 55px !important; border-radius: 10px !important; }
div.st-key-btn_b button { background: linear-gradient(135deg, #2563EB, #3B82F6) !important; color: white !important; height: 55px !important; border-radius: 10px !important; }
div.st-key-btn_c button { background: linear-gradient(135deg, #D97706, #F59E0B) !important; color: white !important; height: 55px !important; border-radius: 10px !important; }
div.st-key-btn_court button { background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important; color: white !important; height: 55px !important; border-radius: 10px !important; }
div.st-key-btn_comp button { background: linear-gradient(135deg, #DC2626, #EF4444) !important; color: white !important; height: 55px !important; border-radius: 10px !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# २. ऑटोमॅटिक सेशन स्टेट (डेटा आपोआप पुढे नेण्यासाठी)
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'appeal_reason' not in st.session_state: st.session_state.appeal_reason = "विहित ३० दिवसांची मुदत संपूनही जन माहिती अधिकाऱ्याने कोणतीही माहिती उपलब्ध करून दिली नाही / माहिती अपूर्ण व दिशाभूल करणारी आहे."
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""

# ==============================================================================
# ३. पत्ते व अधिकृत संस्था डेटाबेस
# ==============================================================================
COMMISSION_DATA = {
    "छत्रपती संभाजीनगर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ छत्रपती संभाजीनगर, शासकीय सुभेदारी विश्रामगृह समोर, बाबा पेट्रोल पंपाजवळ, छत्रपती संभाजीनगर - ४३१००१ (फोन: ०२४०-२३५२५४४)",
    "मुंबई मुख्य खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य मुख्य माहिती आयुक्त, राज्य माहिती आयोग, १३ वा मजला, नवीन प्रशासकीय इमारत, मंत्रालयासमोर, मादाम कामा रोड, मुंबई - ४०००३२ (फोन: ०२२-२२८५६०७८)",
    "पुणे खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ पुणे, नवीन प्रशासकीय इमारत, कौन्सिल हॉल समोर, पुणे - ४११००१",
    "नागपूर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नागपूर, रवी भवन, नागपूर - ४४०००१",
    "नाशिक खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नाशिक, जिल्हाधिकारी कार्यालय आवार, नाशिक - ४२२००२",
    "केंद्रीय माहिती आयोग (CIC नवी दिल्ली)": "मा. मुख्य माहिती आयुक्त, केंद्रीय माहिती आयोग (CIC), बाबा गंगनाथ मार्ग, मुनिरका, नवी दिल्ली - ११००६७"
}

COURT_DATA = {
    "मा. उच्च न्यायालय (रिट याचिका - कलम २२६)": "मा. उच्च न्यायालय मुंबई, खंडपीठ छत्रपती संभाजीनगर / मुंबई / नागपूर",
    "जिल्हा ग्राहक तक्रार निवारण आयोग (ग्राहक संरक्षण कायदा २०१९)": "मा. अध्यक्ष / सदस्य, जिल्हा ग्राहक तक्रार निवारण आयोग",
    "जिल्हा व सत्र न्यायालय (दिवाणी / फौजदारी दावा)": "मा. प्रमुख जिल्हा व सत्र न्यायाधीश महोदय"
}

# ==============================================================================
# ४. AI फंक्शन व १-पान A4 PDF प्रिंट
# ==============================================================================
sidebar_key = st.sidebar.text_input("🔑 Gemini API Key (ऐच्छिक):", type="password")
active_key = sidebar_key if sidebar_key else st.secrets.get("GEMINI_API_KEY", "")

def generate_ai(prompt_text):
    if active_key:
        try:
            genai.configure(api_key=active_key)
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            return model.generate_content(prompt_text, generation_config={"temperature": 0.2}).text
        except Exception as e:
            st.error(f"AI त्रुटी: {e}")
    return None

def print_pdf_box(title, content, color):
    html_c = content.replace('\n', '<br>')
    p_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700&display=swap" rel="stylesheet">
    <div id="printArea" style="font-family:'Mukta',sans-serif; background:#fff; color:#000; padding:30px; border:2px solid {color}; border-radius:8px; line-height:1.6; font-size:14.5px; max-width:800px; margin:auto;">
        <h3 style="text-align:center; color:{color}; text-decoration:underline; margin-bottom:15px;">{title}</h3>
        <div>{html_c}</div>
    </div>
    <div style="text-align:center; margin-top:15px;">
        <button onclick="var p=document.getElementById('printArea').innerHTML; var o=document.body.innerHTML; document.body.innerHTML=p; window.print(); document.body.innerHTML=o; window.location.reload();" style="background:{color}; color:white; padding:12px 28px; font-size:16px; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">
            🖨️ १ पानात PDF सेव्ह / प्रिंट करा (Save as PDF)
        </button>
    </div>
    """
    st.components.v1.html(p_html, height=520, scrolling=True)

# ==============================================================================
# ५. मुख्य शीर्ष व नेव्हिगेशन
# ==============================================================================
st.markdown("<h1>⚖️ RTI, तक्रार व न्यायालयीन AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 13px; font-weight: bold; color: #4B5563;'>एकदा डेटा भरा ➔ जोडपत्र अ ➔ ब ➔ क ➔ कोर्ट ड्राफ्ट आपोआप तयार करा!</p>", unsafe_allow_html=True)
st.markdown("---")

b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    if st.button("🟢 १. जोडपत्र 'अ'\n(मूळ RTI)", key="btn_a"): st.session_state.active_tab = "जोडपत्र 'अ'"
with b2:
    if st.button("🔵 २. जोडपत्र 'ब'\n(प्रथम अपील)", key="btn_b"): st.session_state.active_tab = "जोडपत्र 'ब'"
with b3:
    if st.button("🟠 ३. जोडपत्र 'क'\n(माहिती आयोग)", key="btn_c"): st.session_state.active_tab = "जोडपत्र 'क'"
with b4:
    if st.button("🟣 ४. न्यायालयीन याचिका\n(Court Draft)", key="btn_court"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with b5:
    if st.button("🔴 ५. शासकीय तक्रार\n(तक्रार अर्ज)", key="btn_comp"): st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# विभाग १: जोडपत्र 'अ' (मूळ RTI)
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.markdown("### 🟢 जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अर्जदाराचा संपूर्ण पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. सरकारी कार्यालय / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्दे):", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा (डेटा आपोआप सर्व फॉर्म्समध्ये सेव्ह होईल)"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai(f"महाराष्ट्र RTI २००५ कलम ६(१) जोडपत्र 'अ' बनवा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}. कलम ६(३), ७(१) व ₹१० कोर्ट फी चा उल्लेख करा.")
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'अ' (नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील माहिती मिळवण्यासाठीचा अर्ज.

प्रति,
जन माहिती अधिकारी,
कार्यालय: {st.session_state.dept_name}

१. अर्जदाराचे पूर्ण नाव : {st.session_state.user_name}
२. अर्जदाराचा पत्ता व संपर्क : {st.session_state.user_address}
३. मागितलेल्या माहितीचा तपशील :
{st.session_state.original_query}

४. माहितीचा कालावधी : चालू वर्ष व मागील उपलब्ध अभिलेख
५. माहितीचा प्रकार : प्रमाणित सत्यप्रतीसह व्यक्तिशः / टपालाने
६. अर्ज शुल्क : ₹१०/- (कोर्ट फी स्टॅम्प / चलनाद्वारे जोडले आहे).

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. माहिती आपल्या कार्यालयाशी संबंधित नसल्यास कलम ६(३) अन्वये ५ दिवसांत योग्य विभागाकडे वर्ग करावी. अर्जात काही गोपनीय भाग असल्यास कलम १० (विभक्तता तत्त्व) चा वापर करून उर्वरित माहिती विहित मुदतीत पुरवण्यात यावी.

दिनांक: {d_str}                                     अर्जदाराची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ जोडपत्र 'अ' तयार झाले! हा डेटा जोडपत्र 'ब' आणि 'क' मध्ये ऑटो-लोड झाला आहे.")

# ==============================================================================
# विभाग २: जोडपत्र 'ब' (प्रथम अपील)
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.markdown("### 🔵 जोडपत्र 'ब' - प्रथम अपील अर्ज (कलम १९(१))")
    st.info("💡 **जोडपत्र 'अ' मधील नाव, पत्ता व माहिती येथे आपोआप भरली आहे.**")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("१. अपिलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अपिलकर्त्याचा पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मूळ मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.appeal_reason = st.text_area("५. अपीलाचे कारण:", value=st.session_state.appeal_reason)
        
        if st.form_submit_button("🚀 जोडपत्र 'ब' तयार करा व माहिती आयोगासाठी ट्रान्सफर करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai(f"महाराष्ट्र RTI २००५ कलम १९(१) जोडपत्र 'ब' बनवा. अपिलकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, कारण: {st.session_state.appeal_reason}. कलम १०, कलम २० दंडात्मक कारवाई व सेवापुस्तकात नोंद करण्याची मागणी जोडा.")
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'ब' (नियम ५ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपिलाचा नमुना.

प्रति,
प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी,
कार्यालय: {st.session_state.dept_name}

१. अपिलकर्त्याचे पूर्ण नाव : {st.session_state.user_name}
२. अपिलकर्त्याचा पत्ता व संपर्क : {st.session_state.user_address}
३. जन माहिती अधिकारी : जन माहिती अधिकारी, {st.session_state.dept_name}
४. प्रथम अपीलाचे कारण : {st.session_state.appeal_reason}
५. मूळ माहिती :
{st.session_state.original_query}

६. मागितलेली दाद : तात्काळ कलम १० नुसार माहिती विनामूल्य द्यावी व दोषी अधिकाऱ्यावर कलम २० अन्वये कारवाई व्हावी.

दिनांक: {d_str}                                     अपिलकर्त्याची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ जोडपत्र 'ब' तयार झाले! डेटा जोडपत्र 'क' (माहिती आयोग) साठी तयार आहे.")

# ==============================================================================
# विभाग ३: जोडपत्र 'क' (द्वितीय अपील - माहिती आयोग)
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.markdown("### 🟠 जोडपत्र 'क' - द्वितीय अपील (राज्य / केंद्रीय माहिती आयोग कलम १९(३))")
    sel_bench = st.selectbox("१. माहिती आयोग खंडपीठ निवडा (पत्ता आपोआप भरला जाईल):", list(COMMISSION_DATA.keys()))
    bench_address = COMMISSION_DATA[sel_bench]
    st.success(f"📍 **आयोगाचा पत्ता:** {bench_address}")

    up_file = st.file_uploader("पूर्वीचा RTI अर्ज किंवा प्रथम अपील आदेश अपलोड करा (ऐच्छिक - PDF/Img):", type=["pdf", "png", "jpg"])

    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("अपीलकर्त्याचा पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मूळ मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.appeal_reason = st.text_area("द्वितीय अपीलाचे कायदेशीर आधार:", value=st.session_state.appeal_reason)

        if st.form_submit_button("⚖️ संपूर्ण द्वितीय अपील (जोडपत्र क) जनरेट करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai(f"महाराष्ट्र RTI कलम १९(३) जोडपत्र 'क' द्वितीय अपील मसुदा बनवा. आयोग: {bench_address}, अपिलकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, आधार: {st.session_state.appeal_reason}. कलम १०, कलम २०(१) ₹२५,००० दंड व कलम २०(२) सेवापुस्तकात नोंद करण्याची मागणी समाविष्ट करा.")
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'क'
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपिलाचा अधिकृत नमुना.

प्रति,
{bench_address}

१. अपिलकर्त्याचे पूर्ण नाव : {st.session_state.user_name}
२. अपिलकर्त्याचा पत्ता : {st.session_state.user_address}
३. प्रतिवादी जन माहिती अधिकारी : {st.session_state.dept_name}
४. द्वितीय अपीलाचा विषय व मागितलेली माहिती :
{st.session_state.original_query}

५. कायदेशीर आधार : {st.session_state.appeal_reason}
६. मागितलेली दाद (Prayer) :
   १) कलम १० नुसार संपूर्ण व प्रमाणित अभिलेख विनामूल्य उपलब्ध करून देण्याचे आदेश व्हावेत.
   २) विहित मुदतीत माहिती न दिल्याबद्दल जन माहिती अधिकाऱ्यावर कलम २०(१) अन्वये २५,०००/- रुपये कमाल दंड आकारण्यात यावा व कलम २०(२) अन्वये शिस्तभंगाची कारवाई करून सेवापुस्तकात नोंद व्हावी.

दिनांक: {d_str}                                     अपिलकर्त्याची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ जोडपत्र 'क' द्वितीय अपील मसुदा तयार झाला!")

# ==============================================================================
# विभाग ४: न्यायालयीन मसुदा (Court Petition / Legal Notice)
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.markdown("### 🟣 न्यायालयीन याचिका व कायदेशीर ड्राफ्ट (Court Petition / Legal Notice)")
    sel_court = st.selectbox("१. न्यायालय / लवाद निवडा (पत्ता ऑटो-मॅप होईल):", list(COURT_DATA.keys()))
    court_address = COURT_DATA[sel_court]
    st.success(f"🏛️ **न्यायालय:** {court_address}")

    with st.form("form_court"):
        st.session_state.user_name = st.text_input("याचिकाकर्ता / वादीचे नाव (Petitioner):", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी कार्यालय / व्यक्ती (Respondent):", value=st.session_state.dept_name)
        case_subject = st.text_input("प्रकरणाचा संक्षिप्त विषय:", value="माहिती न देणे / प्रशासकीय गैरव्यवहार व नुकसानभरपाई बाबत")
        case_facts = st.text_area("प्रकरणाची पार्श्वभूमी व हकीकत:", value=f"मूळ मागणी: {st.session_state.original_query}\nतक्रार/अपील पार्श्वभूमी: {st.session_state.appeal_reason}")
        court_prayer = st.text_area("न्यायालयाकडून मागितलेली दाद (Prayer):", value="प्रतिवादीस तात्काळ आदेश देऊन न्याय मिळवून देण्यात यावा व झालेल्या मानसिक-आर्थिक नुकसानीची भरपाई मंजूर करावी.")

        if st.form_submit_button("⚖️ संपूर्ण न्यायालयीन मसुदा (Court Petition) ऑटो-जनरेट करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai(f"उच्च न्यायालय / ग्राहक मंच याचिका मसुदा बनवा. न्यायालय: {court_address}, याचिकाकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, प्रतिवादी: {st.session_state.dept_name}, विषय: {case_subject}, हकीकत: {case_facts}, प्रार्थना: {court_prayer}. पक्षकारांची नावे, प्रकरणाची वस्तुस्थिती, कायदेशीर मुद्दे, प्रार्थना व सत्यप्रतिज्ञा (Verification) फॉरमॅट तयार करा.")
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""मा. {court_address}
याचिका / अर्ज क्र. _________ / २०२६

{st.session_state.user_name}, वय: प्रौढ, रा. {st.session_state.user_address}
... याचिकाकर्ता / वादी

विरुद्ध

{st.session_state.dept_name}
... प्रतिवादी

विषय: {case_subject}

याचिकाकर्त्याची सविनय विनंती खालीलप्रमाणे आहे:
१. वस्तुस्थिती (Brief Facts):
{case_facts}

२. कायदेशीर आधार: प्रतिवादीने वैधानिक कर्तव्याचे व नैसर्गिक न्यायतत्त्वांचे उल्लंघन केले आहे.

३. प्रार्थना (Prayer):
अ) {court_prayer}
ब) या अर्जाचा संपूर्ण खर्च प्रतिवादीकडून याचिकाकर्त्यास मिळवून देण्यात यावा.

सत्यप्रतिज्ञा (Verification):
मी, {st.session_state.user_name}, याद्वारे घोषित करतो की वरील सर्व मजकूर माझ्या माहितीनुसार सत्य व बिनचूक आहे.

दिनांक: {d_str}                                     याचिकाकर्त्याची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ==============================================================================
# विभाग ५: शासकीय तक्रार
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.markdown("### 🔴 शासकीय तक्रार अर्ज विभाग")
    with st.form("form_comp"):
        st.session_state.user_name = st.text_input("तक्रारदाराचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व मोबाईल:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / अधिकारी (उदा. जिल्हाधिकारी / आयुक्त):", value=st.session_state.dept_name)
        comp_subject = st.text_input("तक्रारीचा विषय:", value="प्रशासकीय दिरंगाई व गैरव्यवहारावर कारवाई करणेबाबत")
        comp_body = st.text_area("तक्रारीचा तपशील:", value=st.session_state.appeal_reason)

        if st.form_submit_button("🚀 कडक शासकीय तक्रार अर्ज तयार करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai(f"प्रशासकीय तक्रार अर्ज बनवा. तक्रारदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, प्रति: {st.session_state.dept_name}, विषय: {comp_subject}, तपशील: {comp_body}. ७ दिवसांत कारवाईचा इशारा द्या.")
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""प्रति,
मा. {st.session_state.dept_name},

विषय: {comp_subject} बाबत तातडीने कठोर कारवाई करणेबाबत.
तक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}

महोदय,
मी खालीलप्रमाणे तक्रार नोंदवत आहे:
{comp_body}

सदर प्रकरणात जबाबदार घटकांवर ७ दिवसांच्या आत कायदेशीर व प्रशासकीय नियमांनुसार कारवाई करण्यात यावी, अन्यथा वरिष्ठ पातळीवर व न्यायालयात दाद मागावी लागेल.

दिनांक: {d_str}                                     तक्रारदाराची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला!")

# ==============================================================================
# निकाल व १-पान A4 PDF प्रिंट
# ==============================================================================
if st.session_state.final_draft:
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अंतिम कायदेशीर मसुदा:")
    st.text_area("मसुदा वाचा किंवा कॉपी करा:", value=st.session_state.final_draft, height=260)
    
    st.markdown("### 📥 १-पानात PDF डाऊनलोड / प्रिंट")
    print_pdf_box(st.session_state.active_tab, st.session_state.final_draft, "#1E3A8A")

# ==============================================================================
# 🚀 भविष्यकालीन नवीन अपडेट्स व कोर्ट केसेससाठी राखीव जागा (CUSTOM EXTENSION AREA)
# ==============================================================================
# भविष्यात कोणतेही नवीन फीचर, नवीन कोर्ट ड्राफ्ट किंवा कोड जोडण्यासाठी खालील जागा राखीव आहे:
# ------------------------------------------------------------------------------

# (येथे खाली नवीन कोड पेस्ट करा...)





