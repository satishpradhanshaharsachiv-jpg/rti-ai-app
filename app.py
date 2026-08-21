import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. आधुनिक मोबाईल स्क्रीन डिझाइन (CSS) - जागा कमी व कॉम्पॅक्ट 4x4 ग्रिड
# ==============================================================================
st.set_page_config(page_title="RTI व कायदेशीर AI महा-सहाय्यक", page_icon="⚖️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

/* वरील नको असलेली रिकामी जागा काढली */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

.main-title {
    color: #0F172A;
    font-weight: 800;
    text-align: center;
    font-size: 20px;
    margin-top: -10px;
    margin-bottom: 2px;
}
.sub-title {
    text-align: center;
    color: #475569;
    font-size: 12px;
    margin-bottom: 12px;
}

/* मोबाईल होम स्क्रीनवरील छोटे ॲप आयकॉन बटणे */
div[data-testid="stColumn"] .stButton > button {
    height: 68px !important;
    width: 100% !important;
    border-radius: 16px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 3px 6px rgba(0,0,0,0.15) !important;
    white-space: pre-wrap !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 2px auto !important;
    padding: 2px !important;
    line-height: 1.15 !important;
    transition: transform 0.2s !important;
}

div[data-testid="stColumn"] .stButton > button:hover {
    transform: scale(1.04) !important;
}

/* ओळ १ मधील ४ बटणांचे रंग */
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(1) .stButton > button {
    background: linear-gradient(135deg, #10B981, #059669) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(2) .stButton > button {
    background: linear-gradient(135deg, #EC4899, #F59E0B) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(3) .stButton > button {
    background: linear-gradient(135deg, #1E293B, #0F172A) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(4) .stButton > button {
    background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
}

/* ओळ २ मधील ४ बटणांचे रंग */
div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="stColumn"]:nth-of-type(1) .stButton > button {
    background: linear-gradient(135deg, #7C3AED, #4C1D95) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="stColumn"]:nth-of-type(2) .stButton > button {
    background: linear-gradient(135deg, #EF4444, #B91C1C) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="stColumn"]:nth-of-type(3) .stButton > button {
    background: linear-gradient(135deg, #F97316, #C2410C) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="stColumn"]:nth-of-type(4) .stButton > button {
    background: linear-gradient(135deg, #0284C7, #0369A1) !important;
}

/* चॅट बबल्स */
.chat-bubble-user {
    background: #2563EB; color: #FFFFFF; padding: 10px 14px; border-radius: 16px 16px 2px 16px;
    margin-bottom: 8px; max-width: 85%; margin-left: auto; font-size: 14px;
}
.chat-bubble-ai {
    background: #F8FAFC; color: #0F172A; padding: 12px 16px; border-radius: 16px 16px 16px 2px;
    margin-bottom: 10px; max-width: 90%; margin-right: auto; font-size: 14px; border-left: 4px solid #2563EB;
    border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;
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
    'chat_messages': [
        {"role": "assistant", "content": "✨ **नमस्कार!** मी तुमचा कायदेशीर व प्रशासकीय AI महा-सहाय्यक आहे.\n\nतुम्ही मला कोणताही कायदेशीर प्रश्न विचारू शकता किंवा **कागदपत्राचा फोटो** जोडून सविस्तर विश्लेषण करून घेऊ शकता.", "image": None}
    ]
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

APP_URL = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/?v=3"
date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. 404 त्रुटीमुक्त AI इंजिन (Auto-Detection & Fallback)
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def ask_ai(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Secrets मध्ये GEMINI_API_KEY तपासा."
    
    genai.configure(api_key=active_api_key)
    
    # चालू असलेल्या अधिकृत मॉडेल्सची यादी
    candidate_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    last_err = ""
    for m_name in candidate_models:
        try:
            model = genai.GenerativeModel(m_name)
            if image_obj:
                res = model.generate_content([prompt_text, image_obj])
            else:
                res = model.generate_content(prompt_text)
            
            if res and res.text:
                return res.text
        except Exception as e:
            last_err = str(e)
            continue
            
    return f"AI त्रुटी: {last_err}"

# ==============================================================================
# ४. मुख्य हेडर
# ==============================================================================
st.markdown("<h1 class='main-title'>⚖️ RTI व कायदेशीर AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>नागरिकांचे हक्क, कायदेशीर अर्ज व एका क्लिकवर अचूक मसुदा</div>", unsafe_allow_html=True)

# ==============================================================================
# ५. 4x4 ग्रिड - मोबाईल स्क्रीन बटणे (ओळ १: ४ बटणे | ओळ २: ४ बटणे)
# ==============================================================================
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1:
    if st.button("📄\nजोडपत्र 'अ'", key="tab1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with r1_c2:
    if st.button("⚖️\nप्रथम अपील", key="tab2"): st.session_state.active_tab = "जोडपत्र 'ब'"
with r1_c3:
    if st.button("🏛️\nमाहिती आयोग", key="tab3"): st.session_state.active_tab = "जोडपत्र 'क'"
with r1_c4:
    if st.button("✨\nAI चॅट", key="tab4"): st.session_state.active_tab = "AI चॅट"

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
with r2_c1:
    if st.button("📜\nकोर्ट याचिका", key="tab5"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with r2_c2:
    if st.button("📢\nशासकीय तक्रार", key="tab6"): st.session_state.active_tab = "शासकीय तक्रार"
with r2_c3:
    if st.button("📝\nप्रतिज्ञापत्र", key="tab7"): st.session_state.active_tab = "प्रतिज्ञापत्र"
with r2_c4:
    if st.button("🛒\nग्राहक तक्रार", key="tab8"): st.session_state.active_tab = "ग्राहक मंच"

st.markdown("---")

# ==============================================================================
# विभाग १: जोडपत्र 'अ'
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.subheader("📄 जोडपत्र 'अ' - माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्देसूद):", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 जोडपत्र 'अ' अर्ज तयार करा"):
            with st.spinner("कायदेशीर मसुदा तयार होत आहे..."):
                p = f"महाराष्ट्र RTI नियम २००५ कलम ६(१) जोडपत्र 'अ' अर्ज बनवा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}, दिनांक: {date_today}."
                res = ask_ai(p)
                st.session_state.final_draft = res if "AI त्रुटी" not in res else f"""जोडपत्र - 'अ'\n(नियम ३ पहा)\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अर्जदाराचे नाव: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. माहितीचा तपशील:\n{st.session_state.original_query}\n४. माहितीचा कालावधी: चालू वर्ष / संबंधित वर्ष\n५. अर्ज शुल्क: ₹१०/- चा कोर्ट फी स्टॅम्प जोडला आहे.\n\nदिनांक: {date_today}\nस्वाक्षरी: ({st.session_state.user_name})"""
            st.success("✅ जोडपत्र 'अ' तयार झाले!")

# ==============================================================================
# विभाग २: प्रथम अपील (जोडपत्र 'ब')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.subheader("⚖️ जोडपत्र 'ब' - प्रथम अपील (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("१. अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        reason = st.text_area("४. अपीलाचे कारण:", value="विहित ३० दिवसांत जन माहिती अधिकाऱ्याने कोणतीही माहिती उपलब्ध करून दिली नाही.")
        
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'ब'\n(नियम ५(१) पहा)\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अपीलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. जन माहिती अधिकारी: {st.session_state.dept_name}\n४. अपीलाचे कारण: {reason}\n५. मूळ माहितीचा विषय: {st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({st.session_state.user_name})"""
            st.success("✅ प्रथम अपील तयार झाले!")

# ==============================================================================
# विभाग ३: द्वितीय अपील (जोडपत्र 'क')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.subheader("🏛️ जोडपत्र 'क' - द्वितीय अपील (राज्य माहिती आयोग)")
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("१. अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        bench = st.text_input("४. माहिती आयोग खंडपीठ:", value="छत्रपती संभाजीनगर")
        
        if st.form_submit_button("🚀 द्वितीय अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'क'\n(नियम ६ पहा)\nराज्य माहिती आयोगाकडे करावयाचे द्वितीय अपील (कलम १९(३)).\n\nप्रति,\nमा. राज्य माहिती आयुक्त,\nराज्य माहिती आयोग खंडपीठ, {bench}\n\n१. अपीलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. प्रतिवादी: जन माहिती अधिकारी व प्रथम अपीलीय अधिकारी, {st.session_state.dept_name}\n४. मूळ माहितीचा विषय: {st.session_state.original_query}\n५. प्रार्थना: माहिती विनामूल्य मिळावी व कलम २० नुसार दोषी अधिकाऱ्यावर कारवाई व्हावी.\n\nदिनांक: {date_today}\nस्वाक्षरी: ({st.session_state.user_name})"""
            st.success("✅ द्वितीय अपील तयार झाले!")

# ==============================================================================
# विभाग ४: AI चॅटबॉट व फोटो विश्लेषण
# ==============================================================================
elif st.session_state.active_tab == "AI चॅट":
    st.subheader("✨ AI कायदेशीर सल्लागार व दस्तऐवज विश्लेषक")

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">👤 <b>तुम्ही:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"):
                st.image(msg["image"], width=220)
        else:
            st.markdown(f'<div class="chat-bubble-ai">✨ <b>AI सहाय्यक:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    uploaded_photo = st.file_uploader("➕ फोटो किंवा कागदपत्र जोडा (विश्लेषणासाठी):", type=["png", "jpg", "jpeg"])

    if user_prompt := st.chat_input("येथे प्रश्न विचारा (उदा. या कागदपत्रातील कायदेशीर त्रुटी काय आहेत?)..."):
        img_data = Image.open(uploaded_photo) if uploaded_photo else None
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt, "image": img_data})
        st.rerun()

    if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        last_user_msg = st.session_state.chat_messages[-1]
        with st.spinner("✨ कायदेशीर बाबी तपासत आहे..."):
            sys_instruct = "तुम्ही एक अनुभवी कायदेशीर AI सल्लागार आहात. सर्व उत्तरे स्पष्ट, अचूक आणि मराठीत द्या."
            full_query = f"{sys_instruct}\n\nप्रश्न: {last_user_msg['content']}"
            
            ai_reply = ask_ai(full_query, last_user_msg.get("image"))
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply, "image": None})
            st.rerun()

# ==============================================================================
# विभाग ५: न्यायालयीन मसुदा
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.subheader("📜 न्यायालयीन याचिका मसुदा")
    with st.form("form_court"):
        st.session_state.user_name = st.text_input("१. याचिकाकर्ता नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रतिवादी पक्षकार:", value=st.session_state.dept_name)
        court_subj = st.text_input("४. विषय:", value="प्रशासकीय दिरंगाई व नुकसानभरपाई बाबत")
        court_body = st.text_area("५. वस्तुस्थिती व नुकसान:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 न्यायालयीन मसुदा तयार करा"):
            st.session_state.final_draft = f"""मा. सक्षम न्यायालय / लवाद यांच्या न्यायालयात\n\n{st.session_state.user_name}\nरा. {st.session_state.user_address}\n... याचिकाकर्ता\nविरुद्ध\n{st.session_state.dept_name}\n... प्रतिवादी\n\nविषय: {court_subj}\n\n१. वस्तुस्थिती: {court_body}\n२. प्रार्थना: योग्य तो कायदेशीर दिलासा व नुकसानभरपाई मंजूर करण्यात यावी.\n\nदिनांक: {date_today}\nस्वाक्षरी: ({st.session_state.user_name})"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ==============================================================================
# विभाग ६: शासकीय तक्रार
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.subheader("📢 प्रशासकीय व शासकीय तक्रार अर्ज")
    with st.form("form_comp"):
        st.session_state.user_name = st.text_input("१. तक्रारदाराचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. प्रति / अधिकारी:", value=st.session_state.dept_name)
        c_sub = st.text_input("४. विषय:", value="शासकीय योजनेतील गैरप्रकार व तातडीने चौकशी करणेबाबत")
        c_body = st.text_area("५. तक्रारीचा सविस्तर तपशील:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"""प्रति,\nमा. {st.session_state.dept_name},\n\nविषय: {c_sub}\n\nतक्रारदार: {st.session_state.user_name}\nपत्ता: {st.session_state.user_address}\n\nमहोदय,\n{c_body}\n\nतरी वरील प्रकरणाची सखोल चौकशी करून दोषींवर तात्काळ कारवाई करावी ही विनंती.\n\nदिनांक: {date_today}\nआपला नम्र,\n({st.session_state.user_name})"""
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला!")

# ==============================================================================
# विभाग ७: प्रतिज्ञापत्र (Affidavit)
# ==============================================================================
elif st.session_state.active_tab == "प्रतिज्ञापत्र":
    st.subheader("📝 सर्वसाधारण प्रतिज्ञापत्र (Affidavit)")
    with st.form("form_affidavit"):
        st.session_state.user_name = st.text_input("१. प्रतिज्ञापत्र करणाऱ्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पूर्ण पत्ता व वय:", value=st.session_state.user_address)
        aff_purpose = st.text_input("३. प्रतिज्ञापत्राचा उद्देश / कारण:", value="शासकीय योजनेच्या लाभासाठी सत्यता प्रतिज्ञापत्र")
        aff_points = st.text_area("४. प्रतिज्ञापूर्वक कथन करावयाचे मुद्दे:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 प्रतिज्ञापत्र मसुदा तयार करा"):
            st.session_state.final_draft = f"""।। सत्यता प्रतिज्ञापत्र ।।\n\nमी, {st.session_state.user_name}, वय वर्षे: __, राहणार: {st.session_state.user_address} येथे प्रतिज्ञापूर्वक खालीलप्रमाणे लिहून देतो/देते की -\n\n१. हे की, {aff_purpose}.\n२. हे की, {aff_points}\n३. वरील सर्व माहिती माझ्या वैयक्तिक माहिती व समजुतीनुसार खरी व बरोबर आहे.\n\nदिनांक: {date_today}\nस्थळ: -\n\nप्रतिज्ञापत्र लिहून देणार:\n({st.session_state.user_name})"""
            st.success("✅ प्रतिज्ञापत्र मसुदा तयार झाला!")

# ==============================================================================
# विभाग ८: ग्राहक तक्रार (Consumer Forum)
# ==============================================================================
elif st.session_state.active_tab == "ग्राहक मंच":
    st.subheader("🛒 ग्राहक तक्रार निवारण अर्ज (Consumer Complaint)")
    with st.form("form_consumer"):
        st.session_state.user_name = st.text_input("१. ग्राहकाचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("२. पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("३. विक्रेता / कंपनीचे नाव:", value=st.session_state.dept_name)
        con_issue = st.text_area("४. फसवणूक / सदोष सेवेचा तपशील:", value=st.session_state.original_query)
        con_claim = st.text_input("५. मागितलेली नुकसानभरपाई रक्कम (₹):", value="५०,०००/-")
        
        if st.form_submit_button("🚀 ग्राहक तक्रार मसुदा तयार करा"):
            st.session_state.final_draft = f"""मा. जिल्हा ग्राहक तक्रार निवारण आयोग\n\nतक्रारदार: {st.session_state.user_name}\nपत्ता: {st.session_state.user_address}\n\nविरुद्ध\n\nप्रतिवादी (कंपनी/विक्रेता): {st.session_state.dept_name}\n\nविषय: ग्राहक संरक्षण कायदा २०१९ अंतर्गत सदोष सेवा व फसवणुकीबाबत तक्रार.\n\n१. वस्तुस्थिती: {con_issue}\n२. झालेले नुकसान व मागितलेली भरपाई: ₹{con_claim}\n३. प्रार्थना: सदर रक्कम सव्याज मिळवून देण्यात यावी व मानसिक त्रासापोटी नुकसानभरपाई द्यावी.\n\nदिनांक: {date_today}\nतक्रारदार: ({st.session_state.user_name})"""
            st.success("✅ ग्राहक तक्रार तयार झाली!")

# ==============================================================================
# ६. अंतिम मसुदा, डाऊनलोड व WhatsApp शेअरिंग
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI चॅट":
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अधिकृत मसुदा:")
    st.text_area("मसुदा तपासा किंवा एडिट करा:", value=st.session_state.final_draft, height=220)

    doc_share_msg = urllib.parse.quote(st.session_state.final_draft)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(
            label="📥 मसुदा डाऊनलोड (.txt)",
            data=st.session_state.final_draft,
            file_name=f"Legal_Draft_{datetime.now().strftime('%d%m%Y_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with d_col2:
        st.markdown(
            f'<a href="https://api.whatsapp.com/send?text={doc_share_msg}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:40px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">'
            f'📲 WhatsApp वर पाठवा</button></a>',
            unsafe_allow_html=True
        )
