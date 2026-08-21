import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. प्रीमियम UI, फॉन्ट आणि आधुनिक डिझाइन (CSS)
# ==============================================================================
st.set_page_config(
    page_title="RTI व कायदेशीर AI महा-सहाय्यक (Ultra-Pro)",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

/* मुख्य हेडर */
.header-container {
    text-align: center;
    padding: 10px 0 15px 0;
    border-bottom: 2px solid #E2E8F0;
    margin-bottom: 20px;
}
.main-title {
    color: #0F172A;
    font-weight: 800;
    font-size: 26px;
    margin: 0;
}
.sub-title {
    color: #475569;
    font-size: 15px;
    font-weight: 600;
    margin-top: 4px;
}

/* ६ पोस्टर स्टाईल आकर्षक ग्रिड बटणे */
div[data-testid="stColumn"] .stButton > button {
    height: 90px !important;
    width: 100% !important;
    border-radius: 16px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
    white-space: pre-wrap !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    margin-bottom: 12px !important;
    transition: all 0.25s ease-in-out !important;
}

div[data-testid="stColumn"] .stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.22) !important;
}

/* १. जोडपत्र 'अ' (व्हॉट्सॲप ग्रीन) */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(1) > button {
    background: linear-gradient(135deg, #10B981, #059669) !important;
}
/* २. प्रथम अपील (इन्स्टाग्राम ग्रेडियंट) */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(1) > button {
    background: linear-gradient(135deg, #EC4899, #F59E0B) !important;
}
/* ३. माहिती आयोग (नेव्ही पोलीस ब्लू) */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(2) > button {
    background: linear-gradient(135deg, #1E293B, #0F172A) !important;
}
/* ४. AI महा-सहाय्यक (मॉडर्न व्हायलेट-ब्लू) */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(2) > button {
    background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
}
/* ५. कोर्ट याचिका (फोनपे रॉयल पर्पल) */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(3) > button {
    background: linear-gradient(135deg, #7C3AED, #4C1D95) !important;
}
/* ६. शासकीय तक्रार (डार्क क्रिमसन रेड) */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(3) > button {
    background: linear-gradient(135deg, #EF4444, #B91C1C) !important;
}

/* चॅट बबल्स */
.chat-bubble-user {
    background: #2563EB; color: #FFFFFF; padding: 12px 18px; border-radius: 18px 18px 2px 18px;
    margin-bottom: 12px; max-width: 85%; margin-left: auto; font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.08);
}
.chat-bubble-ai {
    background: #F8FAFC; color: #0F172A; padding: 14px 20px; border-radius: 18px 18px 18px 2px;
    margin-bottom: 15px; max-width: 90%; margin-right: auto; font-size: 15px; border-left: 5px solid #2563EB;
    border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.share-card {
    background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 12px;
    padding: 12px; margin-bottom: 15px; text-align: center;
}
.share-pill {
    display: inline-block; padding: 8px 16px; margin: 4px; border-radius: 8px;
    color: white !important; text-decoration: none; font-size: 14px; font-weight: bold;
}
.pill-wa { background: #25D366; }
.pill-fb { background: #1877F2; }
.pill-tg { background: #0088CC; }

.status-badge {
    display: inline-block; padding: 4px 10px; border-radius: 6px;
    background: #EEF2FF; color: #4338CA; font-weight: 700; font-size: 13px; margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट व्यवस्थापन
# ==============================================================================
defaults = {
    'active_tab': "जोडपत्र 'अ'",
    'user_name': "",
    'user_address': "",
    'dept_name': "",
    'original_query': "",
    'final_draft': "",
    'show_share': False,
    'chat_messages': [
        {"role": "assistant", "content": "✨ **नमस्कार!** मी तुमचा कायदेशीर व प्रशासकीय AI महा-सहाय्यक आहे.\n\nतुम्ही मला **RTI कलम, कायदे, शासकीय नियम** विचारू शकता किंवा **कागदपत्राचा फोटो** जोडून सविस्तर विश्लेषण करून घेऊ शकता.", "image": None}
    ]
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

APP_URL = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/?v=3"
date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. फॉलबॅक सुरक्षित AI इंजिन
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def generate_ai_response(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Streamlit Secrets मध्ये तुमची GEMINI_API_KEY तपासा."
    
    genai.configure(api_key=active_api_key)
    
    supported_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    last_exception = ""
    for model_name in supported_models:
        try:
            model = genai.GenerativeModel(model_name)
            if image_obj:
                res = model.generate_content([prompt_text, image_obj])
            else:
                res = model.generate_content(prompt_text)
            
            if res and res.text:
                return res.text
        except Exception as e:
            last_exception = str(e)
            continue
            
    return f"AI सेवा तात्पुरती अनुपलब्ध आहे: {last_exception}"

# ==============================================================================
# ४. मुख्य हेडर व शेअरिंग
# ==============================================================================
st.markdown("""
<div class="header-container">
    <div class="main-title">⚖️ RTI व कायदेशीर AI महा-सहाय्यक</div>
    <div class="sub-title">नागरिकांचे हक्क, कायदेशीर अर्ज व एका क्लिकवर अचूक मसुदा</div>
</div>
""", unsafe_allow_html=True)

h_col1, h_col2 = st.columns([5, 1])
with h_col2:
    if st.button("↗️ शेअर करा", key="main_share_toggle", use_container_width=True):
        st.session_state.show_share = not st.session_state.show_share

if st.session_state.show_share:
    share_text = urllib.parse.quote(f"⚖️ RTI, शासकीय तक्रार व कायदेशीर AI महा-सहाय्यक ॲप वापरा:\n{APP_URL}")
    st.markdown(f"""
    <div class="share-card">
        <a class="share-pill pill-wa" href="https://api.whatsapp.com/send?text={share_text}" target="_blank">WhatsApp</a>
        <a class="share-pill pill-fb" href="https://www.facebook.com/sharer/sharer.php?u={APP_URL}" target="_blank">Facebook</a>
        <a class="share-pill pill-tg" href="https://t.me/share/url?url={APP_URL}&text={share_text}" target="_blank">Telegram</a>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ५. मुख्य ६ ॲप ग्रिड बटणे
# ==============================================================================
col_left, col_right = st.columns(2)

with col_left:
    if st.button("📄\nजोडपत्र 'अ'\n(RTI अर्ज ६(१))", key="tab1"):
        st.session_state.active_tab = "जोडपत्र 'अ'"
    if st.button("🏛️\nमाहिती आयोग\n(द्वितीय अपील १९(३))", key="tab3"):
        st.session_state.active_tab = "जोडपत्र 'क'"
    if st.button("📜\nकोर्ट याचिका\n(कायदेशीर मसुदा)", key="tab5"):
        st.session_state.active_tab = "न्यायालयीन मसुदा"

with col_right:
    if st.button("⚖️\nप्रथम अपील\n(जोडपत्र 'ब' १९(१))", key="tab2"):
        st.session_state.active_tab = "जोडपत्र 'ब'"
    if st.button("✨\nAI महा-सहाय्यक\n(चॅट व फोटो सल्ला)", key="tab4"):
        st.session_state.active_tab = "AI चॅट"
    if st.button("📢\nशासकीय तक्रार\n(प्रशासकीय अर्ज)", key="tab6"):
        st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("---")

# ==============================================================================
# विभाग १: जोडपत्र 'अ'
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.markdown("<div class='status-badge'>🟢 मूळ माहिती अधिकार अर्ज (कलम ६(१))</div>", unsafe_allow_html=True)
    with st.form("form_a_full"):
        st.session_state.user_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता व संपर्क क्रमांक:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. सार्वजनिक प्राधिकरण / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्देसूद लिहा):", value=st.session_state.original_query)
        
        submitted = st.form_submit_button("🚀 परिपूर्ण RTI अर्ज तयार करा")
        if submitted:
            with st.spinner("कायदेशीर नियमांनुसार परिपूर्ण मसुदा तयार होत आहे..."):
                prompt = f"""
                महाराष्ट्र माहितीचा अधिकार नियम २००५ अंतर्गत जोडपत्र 'अ' (कलम ६(१)) चा अधिकृत अर्ज तयार करा.
                अर्जदार: {st.session_state.user_name}
                पत्ता: {st.session_state.user_address}
                कार्यालय: {st.session_state.dept_name}
                मागितलेली माहिती: {st.session_state.original_query}
                दिनांक: {date_today}
                नियम, कोर्ट फी स्टॅम्प ₹१० चा उल्लेख आणि स्वाक्षरीसाठी जागा जोडून अचूक मराठीत मसुदा द्या.
                """
                ai_res = generate_ai_response(prompt)
                st.session_state.final_draft = ai_res if "AI सेवा तात्पुरती अनुपलब्ध" not in ai_res else f"""जोडपत्र - 'अ'\n(नियम ३ पहा)\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अर्जदाराचे नाव: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. मागितलेल्या माहितीचा तपशील:\n{st.session_state.original_query}\n४. कालावधी: चालू वर्ष / संबंधित कालावधी.\n५. माहिती टपालाने / व्यक्तिशः हवी आहे.\n६. अर्ज शुल्क: ₹१०/- चा कोर्ट फी स्टॅम्प जोडला आहे.\n\nदिनांक: {date_today}\nस्थळ: -\n\nअर्जदाराची स्वाक्षरी:\n({st.session_state.user_name})"""
                st.success("✅ जोडपत्र 'अ' मसुदा यशस्वीरीत्या तयार झाला!")

# ==============================================================================
# विभाग २: प्रथम अपील (जोडपत्र 'ब')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.markdown("<div class='status-badge'>🔵 प्रथम अपील अर्ज (कलम १९(१))</div>", unsafe_allow_html=True)
    with st.form("form_b_full"):
        st.session_state.user_name = st.text_input("१. अपीलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रथम अपीलीय अधिकारी व कार्यालयाचे नाव:", value=st.session_state.dept_name)
        appeal_reason = st.text_area("४. प्रथम अपीलाचे कारण:", value="जन माहिती अधिकाऱ्याने विहित ३० दिवसांत माहिती दिली नाही / दिशाभूल करणारी माहिती दिली.")
        
        submitted = st.form_submit_button("🚀 प्रथम अपील मसुदा तयार करा")
        if submitted:
            with st.spinner("प्रथम अपील तयार होत आहे..."):
                prompt = f"""
                महाराष्ट्र माहिती अधिकार नियम २००५ मधील जोडपत्र 'ब' नुसार कलम १९(१) खालील प्रथम अपील मसुदा तयार करा.
                अपीलकर्ता: {st.session_state.user_name}
                पत्ता: {st.session_state.user_address}
                कार्यालय: {st.session_state.dept_name}
                कारण: {appeal_reason}
                मूळ माहितीचा विषय: {st.session_state.original_query}
                दिनांक: {date_today}
                """
                ai_res = generate_ai_response(prompt)
                st.session_state.final_draft = ai_res if "AI सेवा तात्पुरती अनुपलब्ध" not in ai_res else f"""जोडपत्र - 'ब'\n(नियम ५(१) पहा)\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अपीलकर्त्याचे नाव: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. जन माहिती अधिकाऱ्याचा तपशील: जन माहिती अधिकारी, {st.session_state.dept_name}\n४. अपीलाचे कारण:\n{appeal_reason}\n५. मागितलेली मूळ माहिती:\n{st.session_state.original_query}\n६. प्रार्थना: जन माहिती अधिकाऱ्यास विनामूल्य व त्वरित माहिती देण्याचे आदेश व्हावेत.\n\nदिनांक: {date_today}\nस्वाक्षरी: ({st.session_state.user_name})"""
                st.success("✅ प्रथम अपील मसुदा तयार झाला!")

# ==============================================================================
# विभाग ३: द्वितीय अपील (जोडपत्र 'क')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.markdown("<div class='status-badge'>🟠 राज्य माहिती आयोग - द्वितीय अपील (कलम १९(३))</div>", unsafe_allow_html=True)
    with st.form("form_c_full"):
        st.session_state.user_name = st.text_input("१. अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रतिवादी कार्यालय:", value=st.session_state.dept_name)
        bench_city = st.text_input("४. संबंधित माहिती आयोग खंडपीठ (उदा. छत्रपती संभाजीनगर, मुंबई, पुणे):", value="छत्रपती संभाजीनगर")
        
        submitted = st.form_submit_button("🚀 द्वितीय अपील (जोडपत्र 'क') तयार करा")
        if submitted:
            with st.spinner("माहिती आयोगासाठी मसुदा तयार होत आहे..."):
                prompt = f"""
                महाराष्ट्र माहिती अधिकार नियम २००५ अंतर्गत जोडपत्र 'क' (कलम १९(३)) द्वितीय अपील तयार करा.
                खंडपीठ: {bench_city}
                अपीलकर्ता: {st.session_state.user_name}
                पत्ता: {st.session_state.user_address}
                प्रतिवादी विभाग: {st.session_state.dept_name}
                तपशील: {st.session_state.original_query}
                कलम २० नुसार दंडात्मक कारवाईची मागणी आणि दिनांक {date_today} चा उल्लेख करा.
                """
                ai_res = generate_ai_response(prompt)
                st.session_state.final_draft = ai_res if "AI सेवा तात्पुरती अनुपलब्ध" not in ai_res else f"""जोडपत्र - 'क'\n(नियम ६ पहा)\nराज्य माहिती आयोगाकडे करावयाचे द्वितीय अपील (कलम १९(३)).\n\nप्रति,\nमा. राज्य माहिती आयुक्त,\nराज्य माहिती आयोग खंडपीठ, {bench_city}\n\n१. अपीलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. प्रतिवादी: जन माहिती अधिकारी व प्रथम अपीलीय अधिकारी, {st.session_state.dept_name}\n४. वस्तुस्थिती व मूळ माहितीचा विषय: {st.session_state.original_query}\n५. प्रार्थना:\nअ) माहिती विनामूल्य मिळवून देण्यात यावी.\nब) कलम २०(१) व २०(२) नुसार कसूरदार अधिकाऱ्यावर दंडात्मक व शिस्तभंगाची कारवाई व्हावी.\n\nदिनांक: {date_today}\nअपीलकर्ता स्वाक्षरी: ({st.session_state.user_name})"""
                st.success("✅ द्वितीय अपील तयार झाले!")

# ==============================================================================
# विभाग ४: AI महा-सहाय्यक (चॅट व फोटो)
# ==============================================================================
elif st.session_state.active_tab == "AI चॅट":
    st.markdown("<div class='status-badge'>✨ 24/7 कायदेशीर व प्रशासकीय AI सल्लागार</div>", unsafe_allow_html=True)
    st.caption("कोणताही शासकीय प्रश्न विचारा किंवा कागदपत्र/नोटीसचा फोटो जोडून कायदेशीर सल्ला मिळवा.")

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">👤 <b>तुम्ही:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"):
                st.image(msg["image"], width=220)
        else:
            st.markdown(f'<div class="chat-bubble-ai">✨ <b>AI सल्लागार:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    uploaded_doc = st.file_uploader("➕ कागदपत्र किंवा फोटो जोडा (तपासणीसाठी):", type=["png", "jpg", "jpeg"])

    if user_prompt := st.chat_input("येथे प्रश्न विचारा (उदा. या नोटिसीला उत्तर कसे द्यावे?)..."):
        img_obj = Image.open(uploaded_doc) if uploaded_doc else None
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt, "image": img_obj})
        st.rerun()

    if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        last_msg = st.session_state.chat_messages[-1]
        with st.spinner("✨ कायदेशीर बाबी तपासत आहे..."):
            system_instruction = "तुम्ही एक तज्ज्ञ भारतीय कायदेशीर, प्रशासकीय व RTI सल्लागार AI आहात. सर्व उत्तरे स्पष्ट, मुद्देसूद आणि मराठीत द्या."
            full_prompt = f"{system_instruction}\n\nप्रश्न: {last_msg['content']}"
            
            ai_reply = generate_ai_response(full_prompt, last_msg.get("image"))
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply, "image": None})
            st.rerun()

# ==============================================================================
# विभाग ५: न्यायालयीन मसुदा
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.markdown("<div class='status-badge'>🟣 न्यायालयीन व ग्राहक तक्रार याचिका मसुदा</div>", unsafe_allow_html=True)
    with st.form("form_court_full"):
        st.session_state.user_name = st.text_input("१. याचिकाकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. विरोधी पक्षकार / प्रतिवादी:", value=st.session_state.dept_name)
        court_subject = st.text_input("४. याचिकेचा विषय:", value="प्रशासकीय निष्काळजीपणा व भरपाई मिळणेबाबत")
        court_facts = st.text_area("५. प्रकरणाची खरी वस्तुस्थिती व झालेले नुकसान:", value=st.session_state.original_query)
        
        submitted = st.form_submit_button("🚀 कायदेशीर याचिका तयार करा")
        if submitted:
            with st.spinner("न्यायालयीन मसुदा तयार होत आहे..."):
                prompt = f"""
                भारतीय कायदेशीर प्रक्रियेनुसार खालील बाबींवर सक्षम न्यायालय/लवादासाठी याचिका मसुदा तयार करा:
                याचिकाकर्ता: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}
                प्रतिवादी: {st.session_state.dept_name}
                विषय: {court_subject}
                वस्तुस्थिती: {court_facts}
                प्रार्थना व अंतरिम दिलासा मराठीत योग्य कलमांसह मांडा.
                """
                ai_res = generate_ai_response(prompt)
                st.session_state.final_draft = ai_res if "AI सेवा तात्पुरती अनुपलब्ध" not in ai_res else f"""मा. सक्षम न्यायालय / लवाद यांच्या न्यायालयात\n\nयाचिका क्रमांक: ______ / {datetime.now().year}\n\n{st.session_state.user_name}\nरा. {st.session_state.user_address}\n... याचिकाकर्ता\n\nविरुद्ध\n\n{st.session_state.dept_name}\n... प्रतिवादी\n\nविषय: {court_subject}\n\n१. वस्तुस्थिती:\n{court_facts}\n\n२. कायदेशीर आधार: नैसर्गिक न्याय तत्त्व व संबंधित कायद्यांचे उल्लंघन झाले आहे.\n\n३. प्रार्थना:\nअ) प्रतिवादीवर योग्य ती कायदेशीर कारवाई करण्यात यावी.\nब) झालेल्या आर्थिक व मानसिक त्रासापोटी योग्य भरपाई मंजूर व्हावी.\n\nदिनांक: {date_today}\nयाचिकाकर्ता स्वाक्षरी: ({st.session_state.user_name})"""
                st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ==============================================================================
# विभाग ६: शासकीय तक्रार
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.markdown("<div class='status-badge'>🔴 प्रशासकीय व शासकीय तक्रार अर्ज</div>", unsafe_allow_html=True)
    with st.form("form_comp_full"):
        st.session_state.user_name = st.text_input("१. तक्रारदाराचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पत्ता व मोबाइल नंबर:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. तक्रार कोणाकडे करायची आहे (अधिकारी / कार्यालय):", value=st.session_state.dept_name)
        complaint_sub = st.text_input("४. तक्रारीचा विषय:", value="शासकीय योजनेतील गैरप्रकार व तातडीने कारवाई करणेबाबत")
        complaint_body = st.text_area("५. तक्रारीचा सविस्तर तपशील:", value=st.session_state.original_query)
        
        submitted = st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा")
        if submitted:
            with st.spinner("तक्रार अर्ज तयार होत आहे..."):
                prompt = f"""
                शासकीय नियमांनुसार परिपूर्ण आणि कडक प्रशासकीय तक्रार अर्ज तयार करा.
                तक्रारदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}
                प्रति: {st.session_state.dept_name}
                विषय: {complaint_sub}
                तक्रारीचा तपशील: {complaint_body}
                ७ दिवसांत चौकशी व कारवाईची मागणी जोडून शासकीय भाषेत मसुदा द्या.
                """
                ai_res = generate_ai_response(prompt)
                st.session_state.final_draft = ai_res if "AI सेवा तात्पुरती अनुपलब्ध" not in ai_res else f"""प्रति,\nमा. {st.session_state.dept_name},\n\nविषय: {complaint_sub}\n\nतक्रारदार: {st.session_state.user_name}\nपत्ता: {st.session_state.user_address}\n\nमहोदय,\n\nमी खालीलप्रमाणे तक्रार नोंदवत आहे:\n{complaint_body}\n\nतरी वरील बाबींची निष्पक्ष चौकशी करून संबंधित दोषींवर त्वरित प्रशासकीय कारवाई करण्यात यावी ही नम्र विनंती.\n\nदिनांक: {date_today}\nस्थळ: -\n\nआपला नम्र,\nस्वाक्षरी: ({st.session_state.user_name})"""
                st.success("✅ शासकीय तक्रार अर्ज तयार झाला!")

# ==============================================================================
# ७. निकाल, डाउनलोड व एक-क्लिक WhatsApp शेअरिंग
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI चॅट":
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अधिकृत मसुदा:")
    st.text_area("मसुदा तपासा किंवा एडिट करा:", value=st.session_state.final_draft, height=260)

    encoded_draft = urllib.parse.quote(st.session_state.final_draft)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(
            label="📥 मसुदा डाउनलोड करा (.txt)",
            data=st.session_state.final_draft,
            file_name=f"Legal_Document_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with d_col2:
        st.markdown(
            f'<a href="https://api.whatsapp.com/send?text={encoded_draft}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:45px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:10px; cursor:pointer; font-size:15px;">'
            f'📲 थेट WhatsApp वर पाठवा</button></a>',
            unsafe_allow_html=True
        )
