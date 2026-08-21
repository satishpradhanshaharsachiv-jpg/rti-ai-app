import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि डिझाइन
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

h1 { color: #1E3A8A; font-weight: 900; text-align: center; font-size: 22px; margin-bottom: 4px; }

/* मुख्य ६ रंगीत बटने */
div.st-key-btn_tab1 button { background: linear-gradient(135deg, #059669, #10B981) !important; color: white !important; height: 50px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab2 button { background: linear-gradient(135deg, #2563EB, #3B82F6) !important; color: white !important; height: 50px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab3 button { background: linear-gradient(135deg, #D97706, #F59E0B) !important; color: white !important; height: 50px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab4 button { background: linear-gradient(135deg, #0D9488, #14B8A6) !important; color: white !important; height: 50px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab5 button { background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important; color: white !important; height: 50px !important; border-radius: 8px !important; font-weight: bold; }
div.st-key-btn_tab6 button { background: linear-gradient(135deg, #DC2626, #EF4444) !important; color: white !important; height: 50px !important; border-radius: 8px !important; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# २. ऑटोमॅटिक सेशन स्टेट
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'complaint_reason' not in st.session_state: st.session_state.complaint_reason = ""
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_messages' not in st.session_state: 
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "नमस्कार! मी तुमचा कायदेशीर व प्रशासकीय AI सहाय्यक आहे. RTI, न्यायालयीन कायदे किंवा तक्रार अर्जाबाबत कोणताही प्रश्न विचारा."}
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
# ४. अचूक AI फंक्शन व १-पानात PDF प्रिंटर (Isolation Mode)
# ==============================================================================
sidebar_api_key = st.sidebar.text_input("🔑 Gemini API Key (ऐच्छिक):", type="password")
active_api_key = sidebar_api_key if sidebar_api_key else st.secrets.get("GEMINI_API_KEY", "")

def generate_ai_draft(prompt_text):
    if active_api_key:
        models_to_try = ["gemini-1.5-flash", "gemini-pro", "models/gemini-1.5-flash"]
        for m_name in models_to_try:
            try:
                genai.configure(api_key=active_api_key)
                model = genai.GenerativeModel(m_name)
                res = model.generate_content(prompt_text, generation_config={"temperature": 0.2})
                return res.text
            except Exception:
                continue
    return None

def render_printable_doc(title, content, theme_color="#1E3A8A"):
    formatted_content = content.replace('\n', '<br>')
    printable_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Mukta', sans-serif; margin: 0; padding: 10px; background: transparent; }}
            #doc-container {{
                background: #ffffff; color: #000000; padding: 25px 30px;
                border: 2px solid {theme_color}; border-radius: 6px;
                line-height: 1.6; font-size: 15px; max-width: 750px; margin: 0 auto;
                box-sizing: border-box;
            }}
            .print-btn {{
                display: block; width: 280px; margin: 15px auto; padding: 10px 15px;
                background: {theme_color}; color: #ffffff; font-weight: bold; font-size: 16px;
                border: none; border-radius: 6px; cursor: pointer; text-align: center;
                box-shadow: 0 3px 6px rgba(0,0,0,0.2);
            }}
            .print-btn:hover {{ opacity: 0.9; }}
        </style>
    </head>
    <body>
        <div id="doc-container">
            <h3 style="text-align: center; margin-top: 0; margin-bottom: 15px; text-decoration: underline; color: {theme_color};">{title}</h3>
            <div>{formatted_content}</div>
        </div>
        <button class="print-btn" onclick="printCleanDoc()">🖨️ फक्त अर्ज PDF सेव्ह करा</button>

        <script>
        function printCleanDoc() {{
            var content = document.getElementById('doc-container').innerHTML;
            var win = window.open('', '', 'height=800,width=800');
            win.document.write('<html><head><title>{title}</title>');
            win.document.write('<link href="https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700&display=swap" rel="stylesheet">');
            win.document.write('<style>body{{font-family:"Mukta",sans-serif;padding:30px;font-size:14.5px;line-height:1.6;color:#000;}} h3{{text-align:center;text-decoration:underline;margin-bottom:20px;}} @page{{size:A4;margin:15mm;}}</style>');
            win.document.write('</head><body>');
            win.document.write(content);
            win.document.write('</body></html>');
            win.document.close();
            win.focus();
            setTimeout(function(){{ win.print(); win.close(); }}, 350);
        }}
        </script>
    </body>
    </html>
    """
    st.components.v1.html(printable_html, height=520, scrolling=True)

# ==============================================================================
# ५. मुख्य नेव्हिगेशन बटने
# ==============================================================================
st.markdown("<h1>⚖️ RTI, तक्रार व कायदेशीर महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:13px;font-weight:bold;color:#4B5563;'>जोडपत्र अ ➔ ब ➔ क ➔ AI सल्लागार ➔ कोर्ट याचिका ➔ शासकीय तक्रार</p>", unsafe_allow_html=True)
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

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# विभाग १: जोडपत्र 'अ'
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.markdown("### 🟢 नमुना जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अर्जदाराचा संपूर्ण पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. सरकारी कार्यालय / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्दे):", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"महाराष्ट्र RTI कायदा २००५ कलम ६(१) जोडपत्र 'अ' अर्ज बनवा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}. कलम ६(३), कलम ७(१), कलम १० चा उल्लेख असावा."
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""जोडपत्र - 'अ' (नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील माहिती मिळवण्यासाठीचा अर्ज.

प्रति,
जन माहिती अधिकारी,
कार्यालय: {st.session_state.dept_name}

१. अर्जदाराचे नाव : {st.session_state.user_name}
२. अर्जदाराचा पत्ता व संपर्क : {st.session_state.user_address}
३. मागितलेल्या माहितीचा तपशील :
{st.session_state.original_query}

४. माहितीचा कालावधी : उपलब्ध संपूर्ण अभिलेख
५. माहितीचा प्रकार : प्रमाणित सत्यप्रतीसह व्यक्तिशः / टपालाने
६. अर्ज शुल्क : ₹१०/- (कोर्ट फी स्टॅम्प जोडला आहे).

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. अर्जात काही गोपनीय भाग असल्यास कलम १० चा वापर करून उर्वरित माहिती विहित मुदतीत पुरवण्यात यावी.

दिनांक: {d_str}                                     स्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ जोडपत्र 'अ' तयार झाले!")

# ==============================================================================
# विभाग २: जोडपत्र 'ब'
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.markdown("### 🔵 नमुना जोडपत्र 'ब' - प्रथम अपील (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("१. अपिलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. अपिलकर्त्याचा पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मूळ अर्जात मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.complaint_reason = st.text_area("५. अपीलाचे कारण:", value="विहित ३० दिवसांची मुदत संपूनही जन माहिती अधिकाऱ्याने माहिती दिली नाही.")
        
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

६. मागितलेली दाद : माहिती विनामूल्य उपलब्ध करून देण्याचे आदेश व्हावेत व कलम २० अन्वये कारवाई व्हावी.

दिनांक: {d_str}                                     स्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ जोडपत्र 'ब' तयार झाले!")

# ==============================================================================
# विभाग ३: जोडपत्र 'क'
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.markdown("### 🟠 नमुना जोडपत्र 'क' - द्वितीय अपील (कलम १९(३))")
    selected_bench = st.selectbox("माहिती आयोग खंडपीठ निवडा:", list(COMMISSION_ADDRESSES.keys()))
    bench_addr = COMMISSION_ADDRESSES[selected_bench]
    
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("अपीलकर्त्याचा पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मूळ मागितलेली माहिती:", value=st.session_state.original_query)
        st.session_state.complaint_reason = st.text_area("कायदेशीर कारणे / आधार:", value="प्रथम अपीलीय अधिकाऱ्यांनी आदेश देऊनही जन माहिती अधिकाऱ्याने माहिती पुरवली नाही.")

        if st.form_submit_button("⚖️ जोडपत्र 'क' जनरेट करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"महाराष्ट्र RTI कलम १९(३) जोडपत्र 'क' बनवा. आयोग: {bench_addr}, अपिलकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, कारण: {st.session_state.complaint_reason}. कलम २०(१) व २०(२) दंड व कारवाईची मागणी जोडा."
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
३. प्रतिवादी जन माहिती अधिकारी : {st.session_state.dept_name}
४. मूळ मागितलेली माहिती :
{st.session_state.original_query}

५. अपीलाची कारणे : {st.session_state.complaint_reason}
६. प्रार्थना : कलम २०(१) नुसार २५,००० रुपये दंड आणि कलम २०(२) नुसार शिस्तभंगाची कारवाई करून माहिती विनामूल्य उपलब्ध करून द्यावी.

दिनांक: {d_str}                                     स्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ जोडपत्र 'क' तयार झाले!")

# ==============================================================================
# विभाग ४: कायदेशीर AI सहाय्यक
# ==============================================================================
elif st.session_state.active_tab == "AI सल्लागार":
    st.markdown("### 🤖 कायदेशीर व प्रशासकीय AI सल्लागार")
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("तुमचा प्रश्न येथे विचारा..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            bot_reply = generate_ai_draft(f"तुम्ही एक कायदेतज्ञ आहात. मराठीत अचूक कायदेशीर सल्ला द्या. प्रश्न: {user_prompt}")
            if not bot_reply:
                bot_reply = "माफ करा, उत्तर तयार करण्यात अडचण येत आहे. कृपया तुमची API Key तपासा."
            st.markdown(bot_reply)
            st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})

# ==============================================================================
# विभाग ५: न्यायालयीन मसुदा (व्यवस्थित मांडणी)
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.markdown("### 🟣 न्यायालयीन याचिका व कायदेशीर मसुदा")
    court_choice = st.selectbox("न्यायालय निवडा:", list(COURT_ADDRESSES.keys()))
    court_full = COURT_ADDRESSES[court_choice]

    with st.form("form_court"):
        st.session_state.user_name = st.text_input("१. याचिकाकर्ता / वादीचे नाव (Petitioner):", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रतिवादी कार्यालय / व्यक्ती (Respondent):", value=st.session_state.dept_name)
        court_subj = st.text_input("४. याचिकेचा संक्षिप्त विषय:", value="प्रशासकीय दिरंगाई व कायदेशीर हक्काचे उल्लंघन बाबत")
        court_facts = st.text_area("५. प्रकरणाची वस्तुस्थिती / हकीकत:", value=st.session_state.original_query)
        court_prayer = st.text_area("६. न्यायालयाकडून मागितलेली दाद (Prayer):", value="प्रतिवादीस तात्काळ आदेश देऊन कायदेशीर कारवाई करण्यात यावी व योग्य दिलासा मिळावा.")

        if st.form_submit_button("⚖️ न्यायालयीन मसुदा जनरेट करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"""तुम्ही कायदेतज्ञ आहात. खालील तपशिलावरून अधिकृत मराठी न्यायालयीन मसुदा बनवा:
न्यायालय: {court_full}
याचिकाकर्ता: {st.session_state.user_name}, रा. {st.session_state.user_address}
प्रतिवादी: {st.session_state.dept_name}
विषय: {court_subj}
वस्तुस्थिती: {court_facts}
प्रार्थना: {court_prayer}"""
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

१. प्रकरणाची वस्तुस्थिती (Facts of the Case):
{court_facts}

२. कायदेशीर आधार:
प्रतिवादीने वैधानिक कर्तव्य पार पाडण्यात कसूर केली असून नैसर्गिक न्यायतत्त्वांचे उल्लंघन केले आहे.

३. प्रार्थना (Prayer):
अ) {court_prayer}
ब) या प्रकरणाचा सर्व खर्च प्रतिवादीकडून भरून देण्यात यावा.

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
        st.session_state.dept_name = st.text_input("३. प्रति / सक्षम प्राधिकारी (उदा. जिल्हाधिकारी / महापालिका आयुक्त):", value=st.session_state.dept_name)
        comp_sub = st.text_input("४. तक्रारीचा विषय:", value="दिव्यांगांना जागा उपलब्ध करून देण्याबाबत व प्रशासकीय दिरंगाईवर कारवाईबाबत")
        comp_facts = st.text_area("५. तक्रारीची पार्श्वभूमी व वस्तुस्थिती:", value=st.session_state.original_query)
        comp_demand = st.text_area("६. केलेली मुख्य मागणी / कारवाईचा इशारा:", value="सदर प्रकरणी ७ दिवसांत योग्य निर्णय घेऊन जागा उपलब्ध करून द्यावी, अन्यथा वरिष्ठ स्तरावर व न्यायालयात दाद मागण्यात येईल.")

        if st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा"):
            d_str = datetime.now().strftime("%d/%m/%Y")
            ai_p = f"""खालील माहितीवरून कडक व नियमानुसार शासकीय तक्रार अर्ज मराठीत तयार करा:
प्रति: मा. {st.session_state.dept_name}
तक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}
विषय: {comp_sub}
तपशील: {comp_facts}
मागणी: {comp_demand}"""
            ai_res = generate_ai_draft(ai_p)
            
            if ai_res:
                st.session_state.final_draft = ai_res
            else:
                st.session_state.final_draft = f"""प्रति,
मा. {st.session_state.dept_name},

विषय: {comp_sub}
संदर्भ: अर्जदार {st.session_state.user_name} यांचा अधिकृत तक्रार अर्ज.

महोदय,

मी खालीलप्रमाणे वस्तुस्थिती आपल्या निदर्शनास आणून देत आहे:

१. प्रकरणाची पार्श्वभूमी व तपशील:
{comp_facts}

२. अर्जदाराची मुख्य मागणी:
{comp_demand}

सदर प्रकरणात तातडीने चौकशी करून न्याय मिळवून देण्यात यावा, ही नम्र विनंती.

दिनांक: {d_str}
ठिकाण: ________________

                                                   तक्रारदाराची स्वाक्षरी
                                                   ({st.session_state.user_name})
                                                   मो. {st.session_state.user_address}"""
            st.success("✅ शासकीय तक्रार अर्ज व्यवस्थित तयार झाला!")

# ==============================================================================
# अंतिम निकाल व प्रिंट पर्याय
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI सल्लागार":
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अंतिम कायदेशीर मसुदा:")
    st.text_area("मसुदा तपासा किंवा कॉपी करा:", value=st.session_state.final_draft, height=240)
    
    st.markdown("### 📥 १-पानात PDF डाऊनलोड / प्रिंट")
    render_printable_doc(st.session_state.active_tab, st.session_state.final_draft, "#1E3A8A")
