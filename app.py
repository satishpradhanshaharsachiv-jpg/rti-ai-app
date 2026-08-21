import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि डिझाइन
# ==============================================================================
st.set_page_config(page_title="RTI व AI महा-सहाय्यक", page_icon="⚖️", layout="wide")

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
div.st-key-btn_tab1 button { background: linear-gradient(135deg, #059669, #10B981) !important; color: white !important; height: 55px !important; border-radius: 10px !important; font-weight: bold; }
div.st-key-btn_tab2 button { background: linear-gradient(135deg, #2563EB, #3B82F6) !important; color: white !important; height: 55px !important; border-radius: 10px !important; font-weight: bold; }
div.st-key-btn_tab3 button { background: linear-gradient(135deg, #D97706, #F59E0B) !important; color: white !important; height: 55px !important; border-radius: 10px !important; font-weight: bold; }
div.st-key-btn_tab4 button { background: linear-gradient(135deg, #10A37F, #0D8C6D) !important; color: white !important; height: 55px !important; border-radius: 10px !important; font-weight: bold; box-shadow: 0 0 10px rgba(16,163,127,0.4); }
div.st-key-btn_tab5 button { background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important; color: white !important; height: 55px !important; border-radius: 10px !important; font-weight: bold; }
div.st-key-btn_tab6 button { background: linear-gradient(135deg, #DC2626, #EF4444) !important; color: white !important; height: 55px !important; border-radius: 10px !important; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# २. ऑटोमॅटिक सेशन स्टेट मॅनेजमेंट
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'appeal_reason' not in st.session_state: st.session_state.appeal_reason = "विहित ३० दिवसांची मुदत संपूनही जन माहिती अधिकाऱ्याने कोणतीही माहिती उपलब्ध करून दिली नाही / माहिती अपूर्ण व दिशाभूल करणारी आहे."
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_messages' not in st.session_state: 
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "नमस्कार! मी तुमचा AI कायदेशीर सहाय्यक आहे. RTI, न्यायालयीन कायदे किंवा तक्रार अर्जाबाबत कोणताही प्रश्न विचारा."}
    ]

# ==============================================================================
# ३. पत्ते व अधिकृत संस्था डेटाबेस
# ==============================================================================
COMMISSION_ADDRESSES = {
    "छत्रपती संभाजीनगर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ छत्रपती संभाजीनगर, शासकीय सुभेदारी विश्रामगृह समोर, बाबा पेट्रोल पंपाजवळ, छत्रपती संभाजीनगर - ४३१००१ (फोन: ०२४०-२३५२५४४)",
    "मुंबई मुख्य खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य मुख्य माहिती आयुक्त, राज्य माहिती आयोग, १३ वा मजला, नवीन प्रशासकीय इमारत, मंत्रालयासमोर, मादाम कामा रोड, मुंबई - ४०००३२ (फोन: ०२२-२२८५६०७८)",
    "पुणे खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ पुणे, नवीन प्रशासकीय इमारत, कौन्सिल हॉल समोर, पुणे - ४११००१",
    "नागपूर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नागपूर, रवी भवन, नागपूर - ४४०००१",
    "नाशिक खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नाशिक, जिल्हाधिकारी कार्यालय आवार, नाशिक - ४२२००२",
    "केंद्रीय माहिती आयोग (CIC New Delhi)": "मा. मुख्य माहिती आयुक्त, केंद्रीय माहिती आयोग (CIC), बाबा गंगनाथ मार्ग, मुनिरका, नवी दिल्ली - ११००६७"
}

COURT_ADDRESSES = {
    "मा. उच्च न्यायालय (रिट याचिका - कलम २२६)": "मा. उच्च न्यायालय मुंबई, खंडपीठ छत्रपती संभाजीनगर / मुंबई / नागपूर",
    "जिल्हा ग्राहक तक्रार निवारण आयोग (ग्राहक संरक्षण कायदा २०१९)": "मा. अध्यक्ष / सदस्य, जिल्हा ग्राहक तक्रार निवारण आयोग",
    "जिल्हा व सत्र न्यायालय (दिवाणी / फौजदारी दावा)": "मा. प्रमुख जिल्हा व सत्र न्यायाधीश महोदय"
}

# ==============================================================================
# ४. AI फंक्शन व १-पान A4 PDF प्रिंट
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
# ५. मुख्य शीर्ष व नेव्हिगेशन बटने
# ==============================================================================
st.markdown("<h1>⚖️ RTI, तक्रार व न्यायालयीन AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 13px; font-weight: bold; color: #4B5563;'>जोडपत्र अ ➔ ब ➔ क ➔ ChatGPT AI सहाय्यक ➔ कोर्ट ड्राफ्ट ➔ तक्रार अर्ज</p>", unsafe_allow_html=True)
st.markdown("---")

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    if st.button("🟢 १. जोडपत्र 'अ'\n(मूळ RTI)", key="btn_tab1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with c2:
    if st.button("🔵 २. जोडपत्र 'ब'\n(प्रथम अपील)", key="btn_tab2"): st.session_state.active_tab = "जोडपत्र 'ब'"
with c3:
    if st.button("🟠 ३. जोडपत्र 'क'\n(माहिती आयोग)", key="btn_tab3"): st.session_state.active_tab = "जोडपत्र 'क'"
with c4:
    if st.button("🤖 ४. ChatGPT AI\n(कायदेशीर बॉट)", key="btn_tab4"): st.session_state.active_tab = "ChatGPT AI"
with c5:
    if st.button("🟣 ५. कोर्ट याचिका\n(Petition)", key="btn_tab5"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with c6:
    if st.button("🔴 ६. शासकीय तक्रार\n(कडक तक्रार)", key="btn_tab6"): st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# विभाग १: जोडपत्र 'अ'
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.markdown("### 🟢 नमुना जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अर्जदाराचा संपूर्ण पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. सरकारी कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मागितलेल्या माहितीचा तपशील:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा व डेटा सेव्ह करा"):
            date_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai_draft(f"महाराष्ट्र RTI कायदा २००५ कलम ६(१) जोडपत्र 'अ' तयार करा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}. कलम ६(३), ७(१), १० व ₹१० कोर्ट फी चा उल्लेख करा.")
            
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

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. माहिती आपल्या कार्यालयाशी संबंधित नसल्यास कलम ६(३) अन्वये ५ दिवसांत योग्य विभागाकडे वर्ग करावी. अर्जात काही गोपनीय भाग असल्यास कलम १० चा वापर करून उर्वरित माहिती विहित मुदतीत पुरवण्यात यावी.

दिनांक: {date_str}                                     अर्जदाराची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ जोडपत्र 'अ' तयार झाले!")

# ==============================================================================
# विभाग २: जोडपत्र 'ब'
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.markdown("### 🔵 नमुना जोडपत्र 'ब' - प्रथम अपील अर्ज (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("१. अपिलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अपिलकर्त्याचा संपूर्ण पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मूळ अर्जात मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.appeal_reason = st.text_area("५. प्रथम अपीलाचे कारण:", value=st.session_state.appeal_reason)
        
        if st.form_submit_button("🚀 जोडपत्र 'ब' तयार करा"):
            date_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai_draft(f"महाराष्ट्र RTI कायदा २००५ कलम १९(१) जोडपत्र 'ब' बनवा. अपिलकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, कारण: {st.session_state.appeal_reason}. कलम १० व कलम २० ची मागणी जोडा.")
            
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
३. जन माहिती अधिकाऱ्याचा तपशील : जन माहिती अधिकारी, {st.session_state.dept_name}
४. प्रथम अपीलाचे कारण : {st.session_state.appeal_reason}
५. मागितलेली मूळ माहिती :
{st.session_state.original_query}

६. मागितलेली दाद : कलम १० नुसार तात्काळ माहिती विनामूल्य द्यावी व दोषी अधिकाऱ्यावर कलम २० अन्वये कारवाई करावी.

दिनांक: {date_str}                                     अपिलकर्त्याची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ जोडपत्र 'ब' तयार झाले!")

# ==============================================================================
# विभाग ३: जोडपत्र 'क'
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.markdown("### 🟠 नमुना जोडपत्र 'क' - द्वितीय अपील (कलम १९(३))")
    selected_bench = st.selectbox("१. माहिती आयोग खंडपीठ निवडा:", list(COMMISSION_ADDRESSES.keys()))
    bench_addr = COMMISSION_ADDRESSES[selected_bench]
    
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("अपीलकर्त्याचा पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मूळ मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.appeal_reason = st.text_area("द्वितीय अपीलाचे कायदेशीर आधार:", value=st.session_state.appeal_reason)

        if st.form_submit_button("⚖️ जोडपत्र 'क' मसुदा जनरेट करा"):
            date_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai_draft(f"महाराष्ट्र RTI कलम १९(३) जोडपत्र 'क' बनवा. आयोग: {bench_addr}, अपिलकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, आधार: {st.session_state.appeal_reason}. कलम २०(१) व २०(२) समाविष्ट करा.")
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'क'
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपिलाचा अधिकृत नमुना.

प्रति,
{bench_addr}

१. अपिलकर्त्याचे नाव : {st.session_state.user_name}
२. अपिलकर्त्याचा पत्ता : {st.session_state.user_address}
३. प्रतिवादी अधिकारी : जन माहिती अधिकारी, {st.session_state.dept_name}
४. माहितीचा तपशील : {st.session_state.original_query}
५. कायदेशीर आधार : {st.session_state.appeal_reason}

६. प्रार्थना:
   १) कलम १० नुसार संपूर्ण अभिलेख विनामूल्य उपलब्ध करून देण्याचे आदेश व्हावेत.
   २) कलम २०(१) अन्वये २५,०००/- रुपये कमाल दंड व कलम २०(२) नुसार शिस्तभंगाची कारवाई व्हावी.

दिनांक: {date_str}                                     अपिलकर्त्याची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""
            st.success("✅ जोडपत्र 'क' तयार झाले!")

# ==============================================================================
# विभाग ४: ChatGPT सारखा AI चॅटबॉट (चौथे बटन)
# ==============================================================================
elif st.session_state.active_tab == "ChatGPT AI":
    st.markdown("### 🤖 ChatGPT कायदेशीर व प्रशासकीय AI सहाय्यक")
    st.caption("कायदेशीर सल्ला, अर्जांचे मुद्दे, शासकीय नियम किंवा कोणत्याही प्रश्नाचे उत्तर येथे थेट विचारा.")

    # मागील संभाषण दर्शवणे
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # युझर इनपुट
    if user_prompt := st.chat_input("तुमचा प्रश्न येथे विचारा (उदा. माहिती न दिल्यास पुढे काय करावे?)..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # AI द्वारे उत्तर निर्मिती
        system_instruction = "तुम्ही एक तज्ज्ञ भारतीय कायदेतज्ञ व प्रशासकीय सल्लागार आहात. युझरला मराठीतून स्पष्ट, मुद्देसूद आणि कायदेशीर कलमांसह अचूक मार्गदर्शन करा."
        full_query = f"{system_instruction}\n\nवापरकर्त्याचा प्रश्न: {user_prompt}"
        
        with st.chat_message("assistant"):
            bot_reply = generate_ai_draft(full_query)
            if not bot_reply:
                bot_reply = "माफ करा, सध्या उत्तर तयार करण्यात अडचण येत आहे. कृपया API Key तपासा किंवा काही वेळाने प्रयत्न करा."
            st.markdown(bot_reply)
            st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})

# ==============================================================================
# विभाग ५: न्यायालयीन मसुदा
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.markdown("### 🟣 न्यायालयीन याचिका व कायदेशीर ड्राफ्ट")
    court_choice = st.selectbox("न्यायालय निवडा:", list(COURT_ADDRESSES.keys()))
    court_full = COURT_ADDRESSES[court_choice]

    with st.form("form_court"):
        st.session_state.user_name = st.text_input("याचिकाकर्ता (Petitioner):", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी (Respondent):", value=st.session_state.dept_name)
        case_subject = st.text_input("विषय:", value="माहिती न देणे / प्रशासकीय दिरंगाई बाबत")
        case_facts = st.text_area("हकीकत:", value=f"मूळ मागणी: {st.session_state.original_query}\nपार्श्वभूमी: {st.session_state.appeal_reason}")
        court_prayer = st.text_area("प्रार्थना (Prayer):", value="प्रतिवादीस तात्काळ आदेश देऊन न्याय मिळवून देण्यात यावा.")

        if st.form_submit_button("⚖️ न्यायालयीन मसुदा जनरेट करा"):
            date_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai_draft(f"न्यायालयीन मसुदा बनवा. न्यायालय: {court_full}, याचिकाकर्ता: {st.session_state.user_name}, प्रतिवादी: {st.session_state.dept_name}, विषय: {case_subject}, तथ्ये: {case_facts}, प्रार्थना: {court_prayer}")
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""मा. {court_full}
याचिका / अर्ज क्र. _________ / २०२६

{st.session_state.user_name}, रा. {st.session_state.user_address} ... याचिकाकर्ता
विरुद्ध
{st.session_state.dept_name} ... प्रतिवादी

विषय: {case_subject}
१. वस्तुस्थिती: {case_facts}
२. प्रार्थना: {court_prayer}

दिनांक: {date_str}                                     याचिकाकर्ता: {st.session_state.user_name}"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ==============================================================================
# विभाग ६: शासकीय तक्रार
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.markdown("### 🔴 शासकीय तक्रार अर्ज विभाग")
    with st.form("form_comp"):
        st.session_state.user_name = st.text_input("तक्रारदाराचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व मोबाईल:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / अधिकारी:", value=st.session_state.dept_name)
        comp_sub = st.text_input("विषय:", value="प्रशासकीय दिरंगाई व कारवाई करणेबाबत")
        comp_body = st.text_area("तपशील:", value=st.session_state.appeal_reason)

        if st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा"):
            date_str = datetime.now().strftime("%d/%m/%Y")
            ai_res = generate_ai_draft(f"प्रशासकीय तक्रार अर्ज बनवा. तक्रारदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, प्रति: {st.session_state.dept_name}, विषय: {comp_sub}, तपशील: {comp_body}")
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""प्रति,
मा. {st.session_state.dept_name},
विषय: {comp_sub}
तक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}

महोदय,
{comp_body}

दिनांक: {date_str}                                     स्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला!")

# ==============================================================================
# अंतिम निकाल व प्रिंट पर्याय (फक्त डॉक्युमेंट टॅब्ससाठी)
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "ChatGPT AI":
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अंतिम कायदेशीर मसुदा:")
    st.text_area("मसुदा वाचा किंवा कॉपी करा:", value=st.session_state.final_draft, height=260)
    
    st.markdown("### 📥 १-पानात PDF डाऊनलोड / प्रिंट")
    render_printable_doc(st.session_state.active_tab, st.session_state.final_draft, "#1E3A8A")
