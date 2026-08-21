import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि मोबाइल-फ्रेंडली डिझाइन
# ==============================================================================
st.set_page_config(page_title="RTI व कायदेशीर महा-सहाय्यक", page_icon="⚖️", layout="wide")

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800;900&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    visibility: hidden; display: none !important;
}

h1 { color: #1E3A8A; font-weight: 900; text-align: center; font-size: 20px; margin-bottom: 2px; }

/* ६ मुख्य रंगीत बटने */
div.st-key-btn_tab1 button { background: linear-gradient(135deg, #059669, #10B981) !important; color: white !important; height: 48px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab2 button { background: linear-gradient(135deg, #2563EB, #3B82F6) !important; color: white !important; height: 48px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab3 button { background: linear-gradient(135deg, #D97706, #F59E0B) !important; color: white !important; height: 48px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab4 button { background: linear-gradient(135deg, #0D9488, #14B8A6) !important; color: white !important; height: 48px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab5 button { background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important; color: white !important; height: 48px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab6 button { background: linear-gradient(135deg, #DC2626, #EF4444) !important; color: white !important; height: 48px !important; border-radius: 8px !important; font-weight: bold; }

/* चॅट कंटेनर स्क्रोलिंग */
.chat-scroll-area {
    max-height: 320px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    background: #F9FAFB;
    margin-bottom: 10px;
}
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
if 'complaint_reason' not in st.session_state: st.session_state.complaint_reason = ""
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_history' not in st.session_state: 
    st.session_state.chat_history = [
        {"role": "assistant", "content": "नमस्कार! मी तुमचा AI सहाय्यक आहे. माहिती अधिकार (RTI) किंवा तक्रार अर्जाबाबत कोणताही प्रश्न विचारा."}
    ]

# ==============================================================================
# ३. अधिकृत पत्ते डेटाबेस
# ==============================================================================
COMMISSION_ADDRESSES = {
    "छत्रपती संभाजीनगर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ छत्रपती संभाजीनगर, शासकीय सुभेदारी विश्रामगृह समोर, बाबा पेट्रोल पंपाजवळ, छत्रपती संभाजीनगर - ४३१००१",
    "मुंबई मुख्य खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य मुख्य माहिती आयुक्त, राज्य माहिती आयोग, १३ वा मजला, नवीन प्रशासकीय इमारत, मंत्रालयासमोर, मुंबई - ४०००३२",
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
# ४. AI फंक्शन व मसुदा नियंत्रक
# ==============================================================================
sidebar_api_key = st.sidebar.text_input("🔑 Gemini API Key (ऐच्छिक):", type="password")
active_api_key = sidebar_api_key if sidebar_api_key else st.secrets.get("GEMINI_API_KEY", "")

def generate_ai_draft(prompt_text):
    if active_api_key:
        models = ["gemini-1.5-flash", "gemini-pro", "models/gemini-1.5-flash"]
        for m in models:
            try:
                genai.configure(api_key=active_api_key)
                model = genai.GenerativeModel(m)
                res = model.generate_content(prompt_text, generation_config={"temperature": 0.2})
                if res and res.text:
                    return res.text
            except Exception:
                continue
    return None

def render_document_actions(doc_title, doc_text):
    encoded_text = urllib.parse.quote(f"*{doc_title}*\n\n{doc_text}")
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            label="📥 मसुदा फाईल डाऊनलोड करा (.txt)",
            data=doc_text,
            file_name=f"{doc_title}_{datetime.now().strftime('%d%m%Y')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_b:
        st.markdown(
            f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:6px; cursor:pointer;">'
            f'📲 WhatsApp वर पाठवा / शेअर करा</button></a>', 
            unsafe_allow_html=True
        )

# ==============================================================================
# ५. मुख्य नेव्हिगेशन बटने
# ==============================================================================
st.markdown("<h1>⚖️ RTI, तक्रार व कायदेशीर महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:12px;font-weight:bold;color:#4B5563;'>जोडपत्र अ ➔ ब ➔ क ➔ AI सल्लागार ➔ कोर्ट याचिका ➔ शासकीय तक्रार</p>", unsafe_allow_html=True)
st.markdown("---")

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    if st.button("🟢 जोडपत्र 'अ'\n(मूळ RTI)", key="btn_tab1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with c2:
    if st.button("🔵 जोडपत्र 'ब'\n(प्रथम अपील)", key="btn_tab2"): st.session_state.active_tab = "जोडपत्र 'ब'"
with c3:
    if st.button("🟠 जोडपत्र 'क'\n(माहिती आयोग)", key="btn_tab3"): st.session_state.active_tab = "जोडपत्र 'क'"
with c4:
    if st.button("🤖 AI सल्लागार\n(कायदेशीर बॉट)", key="btn_tab4"): st.session_state.active_tab = "AI सल्लागार"
with c5:
    if st.button("🟣 कोर्ट याचिका\n(Petition)", key="btn_tab5"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with c6:
    if st.button("🔴 शासकीय तक्रार\n(कडक तक्रार)", key="btn_tab6"): st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# विभाग १: जोडपत्र 'अ' (RTI अर्ज)
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.markdown("### 🟢 जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अर्जदाराचा संपूर्ण पत्ता व मोबाइल क्र.:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. सरकारी कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्दे):", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"महाराष्ट्र RTI कायदा २००५ कलम ६(१) जोडपत्र 'अ' अर्ज तयार करा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}. कलम ६(३), कलम ७(१), कलम १० व ₹१० कोर्ट फी चा उल्लेख असावा."
            ai_res = generate_ai_draft(ai_p)
            
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

४. माहितीचा कालावधी : उपलब्ध संपूर्ण अभिलेख
५. माहितीचा प्रकार : प्रमाणित सत्यप्रतीसह व्यक्तिशः / टपालाने
६. अर्ज शुल्क : ₹१०/- (कोर्ट फी स्टॅम्प जोडला आहे).

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. अर्जात काही गोपनीय भाग असल्यास कलम १० (विभक्तता तत्त्व) चा वापर करून उर्वरित माहिती विहित मुदतीत पुरवण्यात यावी.

दिनांक: {d_str}                                     स्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ जोडपत्र 'अ' तयार झाले!")

# ==============================================================================
# विभाग २: जोडपत्र 'ब' (प्रथम अपील)
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.markdown("### 🔵 जोडपत्र 'ब' - प्रथम अपील अर्ज (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("१. अपिलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अपिलकर्त्याचा पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मूळ अर्जात मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.complaint_reason = st.text_area("५. प्रथम अपीलाचे कारण:", value="विहित ३० दिवसांची मुदत संपूनही जन माहिती अधिकाऱ्याने कोणतीही माहिती उपलब्ध करून दिली नाही.")
        
        if st.form_submit_button("🚀 जोडपत्र 'ब' तयार करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"महाराष्ट्र RTI कलम १९(१) जोडपत्र 'ब' बनवा. अपिलकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, कारण: {st.session_state.complaint_reason}."
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'ब' (नियम ५ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपिलाचा नमुना.

प्रति,
प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी,
कार्यालय: {st.session_state.dept_name}

१. अपिलकर्त्याचे नाव : {st.session_state.user_name}
२. अपिलकर्त्याचा पत्ता : {st.session_state.user_address}
३. जन माहिती अधिकारी : जन माहिती अधिकारी, {st.session_state.dept_name}
४. प्रथम अपीलाचे कारण : {st.session_state.complaint_reason}
५. मूळ माहितीचा तपशील :
{st.session_state.original_query}

६. मागितलेली दाद : कलम १० नुसार तात्काळ माहिती विनामूल्य द्यावी व दोषी अधिकाऱ्यावर कलम २० अन्वये कारवाई व्हावी.

दिनांक: {d_str}                                     स्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ जोडपत्र 'ब' तयार झाले!")

# ==============================================================================
# विभाग ३: जोडपत्र 'क' (द्वितीय अपील - माहिती आयोग)
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.markdown("### 🟠 जोडपत्र 'क' - द्वितीय अपील (कलम १९(३))")
    selected_bench = st.selectbox("१. माहिती आयोग खंडपीठ निवडा:", list(COMMISSION_ADDRESSES.keys()))
    bench_addr = COMMISSION_ADDRESSES[selected_bench]
    
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("अपीलकर्त्याचा पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मूळ मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.complaint_reason = st.text_area("द्वितीय अपीलाचे कायदेशीर आधार:", value="प्रथम अपीलीय अधिकाऱ्यांनी आदेश देऊनही जन माहिती अधिकाऱ्याने माहिती पुरवली नाही.")

        if st.form_submit_button("⚖️ जोडपत्र 'क' जनरेट करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"महाराष्ट्र RTI कलम १९(३) जोडपत्र 'क' बनवा. आयोग: {bench_addr}, अपिलकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, कारण: {st.session_state.complaint_reason}. कलम २०(१) व २०(२) दंड व कारवाई जोडा."
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'क'
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपिलाचा नमुना.

प्रति,
{bench_addr}

१. अपीलकर्त्याचे नाव : {st.session_state.user_name}
२. अपीलकर्त्याचा पत्ता : {st.session_state.user_address}
३. प्रतिवादी अधिकारी : जन माहिती अधिकारी, {st.session_state.dept_name}
४. मूळ मागितलेली माहिती :
{st.session_state.original_query}

५. अपीलाची कारणे : {st.session_state.complaint_reason}
६. प्रार्थना : कलम २०(१) नुसार २५,००० रुपये दंड आणि कलम २०(२) नुसार शिस्तभंगाची कारवाई करून माहिती विनामूल्य उपलब्ध करून द्यावी.

दिनांक: {d_str}                                     स्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ जोडपत्र 'क' तयार झाले!")

# ==============================================================================
# विभाग ४: कॉम्पॅक्ट AI कायदेशीर सल्लागार (Compact Chatbot)
# ==============================================================================
elif st.session_state.active_tab == "AI सल्लागार":
    st.markdown("### 🤖 कायदेशीर व प्रशासकीय AI सल्लागार")
    st.caption("कायदेशीर सल्ला किंवा नियमांबाबत प्रश्न विचारा:")

    # मर्यादित उंचीचा स्क्रोल चॅट कंटेनर
    st.markdown('<div class="chat-scroll-area">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**👤 तुम्ही:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI सहाय्यक:** {msg['content']}")
        st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("येथे प्रश्न लिहा:", placeholder="उदा. जन माहिती अधिकाऱ्याने मुदतीत माहिती दिली नाही तर काय करावे?")
        send_btn = st.form_submit_button("🚀 प्रश्न विचारा")

        if send_btn and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            ai_reply = generate_ai_draft(f"तुम्ही एक अनुभवी कायदेतज्ञ आहात. मराठीत अचूक कायदेशीर सल्ला द्या. प्रश्न: {user_input}")
            if not ai_reply:
                ai_reply = "माहिती अधिकार २००५ नुसार विहित ३० दिवसांत माहिती न मिळाल्यास कलम १९(१) अन्वये प्रथम अपीलीय अधिकाऱ्यांकडे प्रथम अपील दाखल करावे लागते."
            
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

# ==============================================================================
# विभाग ५: न्यायालयीन मसुदा (Court Draft)
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.markdown("### 🟣 न्यायालयीन याचिका व कायदेशीर मसुदा")
    court_choice = st.selectbox("न्यायालय निवडा:", list(COURT_ADDRESSES.keys()))
    court_full = COURT_ADDRESSES[court_choice]

    with st.form("form_court"):
        st.session_state.user_name = st.text_input("१. याचिकाकर्ता / वादी (Petitioner):", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रतिवादी (Respondent):", value=st.session_state.dept_name)
        court_subj = st.text_input("४. याचिकेचा विषय:", value="प्रशासकीय दिरंगाई व कायदेशीर हक्काचे उल्लंघन बाबत")
        court_facts = st.text_area("५. वस्तुस्थिती / हकीकत:", value=st.session_state.original_query)
        court_prayer = st.text_area("६. मागितलेली दाद (Prayer):", value="प्रतिवादीस तात्काळ आदेश देऊन कायदेशीर कारवाई करण्यात यावी.")

        if st.form_submit_button("⚖️ न्यायालयीन मसुदा तयार करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"न्यायालयीन मसुदा बनवा. न्यायालय: {court_full}, याचिकाकर्ता: {st.session_state.user_name}, प्रतिवादी: {st.session_state.dept_name}, विषय: {court_subj}, तथ्ये: {court_facts}, प्रार्थना: {court_prayer}"
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""मा. {court_full}
याचिका / अर्ज क्र. _________ / २०२६

{st.session_state.user_name}
रा. {st.session_state.user_address}
... याचिकाकर्ता / वादी

विरुद्ध

{st.session_state.dept_name}
... प्रतिवादी

विषय: {court_subj}

याचिकाकर्त्याची सविनय विनंती खालीलप्रमाणे आहे:

१. वस्तुस्थिती (Brief Facts):
{court_facts}

२. कायदेशीर आधार: प्रतिवादीने वैधानिक कर्तव्याचे उल्लंघन केले आहे.

३. प्रार्थना (Prayer):
अ) {court_prayer}
ब) अर्जाचा संपूर्ण खर्च प्रतिवादीकडून याचिकाकर्त्यास देण्यात यावा.

सत्यप्रतिज्ञा (Verification):
मी, {st.session_state.user_name}, याद्वारे जाहीर करतो की वरील सर्व मजकूर माझ्या माहितीनुसार सत्य व बिनचूक आहे.

दिनांक: {d_str}                                     याचिकाकर्ता: {st.session_state.user_name}"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ==============================================================================
# विभाग ६: शासकीय तक्रार अर्ज (सरळ व अचूक मांडणी)
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.markdown("### 🔴 शासकीय तक्रार अर्ज विभाग")
    with st.form("form_comp"):
        st.session_state.user_name = st.text_input("१. तक्रारदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. तक्रारदाराचा पत्ता व मोबाईल क्र.:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रति / सक्षम अधिकारी (उदा. जिल्हाधिकारी / महापालिका आयुक्त):", value=st.session_state.dept_name)
        comp_sub = st.text_input("४. तक्रारीचा विषय:", value="दिव्यांगांना जागा उपलब्ध करून देण्याबाबत व कारवाईबाबत")
        comp_facts = st.text_area("५. तक्रारीची पार्श्वभूमी व तपशील:", value=st.session_state.original_query)
        comp_demand = st.text_area("६. मुख्य मागणी / कारवाईचा इशारा:", value="सदर प्रकरणी ७ दिवसांत योग्य निर्णय घेऊन जागा उपलब्ध करून द्यावी, अन्यथा वरिष्ठ स्तरावर व न्यायालयात दाद मागण्यात येईल.")

        if st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"शासकीय तक्रार अर्ज मराठीत बनवा. प्रति: मा. {st.session_state.dept_name}, तक्रारदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, विषय: {comp_sub}, तपशील: {comp_facts}, मागणी: {comp_demand}."
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""प्रति,
मा. {st.session_state.dept_name},

विषय: {comp_sub}
तक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}

महोदय,

मी खालीलप्रमाणे वस्तुस्थिती आपल्या निदर्शनास आणून देत आहे:

१. प्रकरणाचा तपशील व पार्श्वभूमी:
{comp_facts}

२. तक्रारदाराची मुख्य मागणी:
{comp_demand}

सदर प्रकरणात तातडीने चौकशी करून न्याय मिळवून देण्यात यावा, ही नम्र विनंती.

दिनांक: {d_str}
ठिकाण: ________________

                                                   तक्रारदाराची स्वाक्षरी
                                                   ({st.session_state.user_name})
                                                   मो. {st.session_state.user_address}"""
            st.success("✅ शासकीय तक्रार अर्ज व्यवस्थित तयार झाला!")

# ==============================================================================
# अंतिम निकाल, डाऊनलोड व शेअर पर्याय
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI सल्लागार":
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अंतिम कायदेशीर मसुदा:")
    st.text_area("मसुदा तपासा किंवा कॉपी करा:", value=st.session_state.final_draft, height=220)
    
    render_document_actions(st.session_state.active_tab, st.session_state.final_draft)
