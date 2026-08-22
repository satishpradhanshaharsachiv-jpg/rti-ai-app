import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="आकांक्षा AI - सतीश अशोक प्रधान",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. SECRETS API KEY & MODEL SETUP (404 एरर जाणार)
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # नवीन आणि सुरक्षित मॉडेल नाव
    model = genai.GenerativeModel("gemini-3.6-flash")
except Exception as e:
    st.error("⚠️ कृपया Streamlit Secrets मध्ये 'GEMINI_API_KEY' अचूक सेट करा!")

# Session State Initialization
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "जोडपत्र 'अ'"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ==========================================
# 3. CUSTOM CSS - 4x2 MOBILE GRID & SHINY BUTTONS
# ==========================================
st.markdown("""
    <style>
    * { box-sizing: border-box !important; }
    html, body, [data-testid="stAppViewContainer"], .main, .stApp {
        background-color: #FFFFFF;
        color: #0F172A;
    }
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        max-width: 100% !important;
    }

    /* TOP SHINY BANNER */
    .brand-top-banner {
        text-align: center;
        background: linear-gradient(135deg, #0F172A, #1E1B4B, #312E81);
        padding: 10px 4px;
        border-radius: 12px;
        border: 2px solid #FFD700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        margin-bottom: 8px;
    }
    
    .free-dhamaka-tag {
        display: inline-block;
        background: linear-gradient(90deg, #FF0055, #FF5E00);
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 900;
        padding: 2px 12px;
        border-radius: 20px;
        margin-bottom: 4px;
        letter-spacing: 1px;
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.7);
    }

    .brand-title-1 {
        font-size: 18px;
        font-weight: 900;
        background: linear-gradient(90deg, #FFD700, #FFF5A5, #FFA500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 3px;
    }

    .brand-title-2 {
        font-size: 13px;
        font-weight: 800;
        background: linear-gradient(90deg, #00FFCC, #FFD700, #FF3366);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    .brand-title-3 {
        color: #FFD700;
        font-size: 12px;
        font-weight: 700;
        border-top: 1px dashed rgba(255, 215, 0, 0.6);
        padding-top: 4px;
        margin-top: 2px;
    }

    /* 4 BUTTONS PER ROW GRID (MOBILE OPTIMIZED) */
    .button-zone div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        justify-content: space-between !important;
        margin-bottom: 3px !important;
        width: 100% !important;
    }
    
    .button-zone div[data-testid="column"] {
        width: 24.5% !important;
        flex: 1 1 24.5% !important;
        min-width: 0px !important;
        padding: 0px !important;
    }

    .button-zone div.stButton > button {
        width: 100% !important;
        height: 62px !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        padding: 1px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.3) !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
    }

    /* VIBRANT COLORFUL GRADIENTS FOR 8 BUTTONS */
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(1) button { background: linear-gradient(135deg, #00C853, #00E676) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(2) button { background: linear-gradient(135deg, #FF6D00, #FF9100) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(3) button { background: linear-gradient(135deg, #1A237E, #3F51B5) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(4) button { background: linear-gradient(135deg, #6200EA, #7C4DFF) !important; }

    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(1) button { background: linear-gradient(135deg, #4A148C, #8E24AA) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(2) button { background: linear-gradient(135deg, #D50000, #FF1744) !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(3) button { background: linear-gradient(135deg, #FFAB00, #FFD600) !important; color: #000000 !important; }
    .button-zone div[data-testid="stHorizontalBlock"]:nth-of-type(2) > div:nth-child(4) button { background: linear-gradient(135deg, #00B8D4, #00E5FF) !important; color: #000000 !important; }

    /* FORM STACKED VERTICALLY */
    div[data-testid="stForm"] {
        border: 1px solid #CBD5E1;
        padding: 8px;
        border-radius: 10px;
        background-color: #F8FAFC;
    }
    
    .form-title-box {
        background: #0F172A;
        color: #FFD700;
        padding: 8px 10px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 800;
        border-left: 4px solid #FFD700;
        margin-top: 6px;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. TOP SHINY BRANDING BANNER
# ==========================================
st.markdown("""
    <div class='brand-top-banner'>
        <div><span class='free-dhamaka-tag'>🔥 फ्री धमाका 🔥</span></div>
        <div class='brand-title-1'>✨ आकांक्षा AI - RTI व कायदेशीर महा-सहाय्यक ✨</div>
        <div class='brand-title-2'>⚡ एका सेकंदात अर्ज A4 साईज मध्ये मिळवा ⚡</div>
        <div class='brand-title-3'>👤 सतीश अशोक प्रधान | 📱 मो. ८६६८२३५३९५</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. BUTTON ZONE (4 x 2 GRID - 8 BUTTONS)
# ==========================================
st.markdown("<div class='button-zone'>", unsafe_allow_html=True)

r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1:
    if st.button("📄\nजोडपत्र 'अ'", key="b1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with r1_c2:
    if st.button("⚖️\nप्रथम अपील", key="b2"): st.session_state.active_tab = "प्रथम अपील"
with r1_c3:
    if st.button("🏛️\nमाहिती आयोग", key="b3"): st.session_state.active_tab = "माहिती आयोग"
with r1_c4:
    if st.button("✨\nAI चॅट", key="b4"): st.session_state.active_tab = "AI चॅट"

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
with r2_c1:
    if st.button("📜\nकोर्ट याचिका", key="b5"): st.session_state.active_tab = "कोर्ट याचिका"
with r2_c2:
    if st.button("📢\nशासकीय तक्रार", key="b6"): st.session_state.active_tab = "शासकीय तक्रार"
with r2_c3:
    if st.button("✏️\nप्रतिज्ञापत्र", key="b7"): st.session_state.active_tab = "प्रतिज्ञापत्र"
with r2_c4:
    if st.button("🛒\nग्राहक मंच", key="b8"): st.session_state.active_tab = "ग्राहक मंच"

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 6. FORM & GENERATION ENGINE
# ==========================================
curr = st.session_state.active_tab

if curr == "AI चॅट":
    st.markdown("<div class='form-title-box'>✨ आकांक्षा AI कायदेशीर चॅट महा-सहाय्यक</div>", unsafe_allow_html=True)
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_query = st.chat_input("तुमचा प्रश्न येथे विचारा...")
    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("उत्तर तयार होत आहे..."):
                try:
                    response = model.generate_content(f"तुम्ही कायदेशीर सहाय्यक आहात. मराठीत उत्तर द्या: {user_query}")
                    response_text = response.text
                except Exception as e:
                    response_text = f"त्रुटी आली: {e}"
                
                st.write(response_text)
                st.session_state.chat_messages.append({"role": "assistant", "content": response_text})

else:
    titles = {
        "जोडपत्र 'अ'": "📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))",
        "प्रथम अपील": "⚖️ जोडपत्र 'ब' (प्रथम अपील अर्ज नियम ५(१))",
        "माहिती आयोग": "🏛️ जोडपत्र 'क' (द्वितीय अपील नियम ७(१))",
        "कोर्ट याचिका": "📜 न्यायालयीन मसुदा / याचिका अर्ज",
        "शासकीय तक्रार": "📢 प्रशासकीय व शासकीय तक्रार अर्ज",
        "प्रतिज्ञापत्र": "✏️ स्व-घोषणापत्र / प्रतिज्ञापत्र (Affidavit)",
        "ग्राहक मंच": "🛒 ग्राहक संरक्षण मंच तक्रार अर्ज"
    }
    
    st.markdown(f"<div class='form-title-box'>{titles.get(curr, curr)}</div>", unsafe_allow_html=True)

    with st.form(key="app_main_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            app_name = st.text_input("१. अर्जदाराचे नाव:", placeholder="अर्जदाराचे नाव प्रविष्ट करा...")
            app_address = st.text_area("२. पूर्ण पत्ता व मोबाईल नंबर:", placeholder="अर्जदाराचा पूर्ण पत्ता व मोबाईल नंबर...", height=90)
        
        with col2:
            auth_name = st.text_input("३. जन माहिती अधिकारी / विरोधी पक्ष / कार्यालय नाव:", placeholder="उदा. जन माहिती अधिकारी...")
            auth_address = st.text_area("४. कार्यालयाचा पूर्ण पत्ता:", placeholder="कार्यालयीन पत्ता प्रविष्ट करा...", height=90)

        subject = st.text_input("५. विषय / माहितीचा तपशील:", value="माहिती अधिकार अधिनियम २००५ अन्वये माहिती मिळणेबाबत.")
        info_details = st.text_area("६. मागितलेल्या माहितीचा सुटसुटीत तपशील (१, २, ३ मुद्दे लिहा):", height=110)

        submit = st.form_submit_button(label="🚀 परिपूर्ण मसुदा तयार करा (Generate Draft)")

    if submit:
        master_prompt = f"""
        तुम्ही वरिष्ठ वकील व शासकीय कायदेशीर मसुदा तज्ज्ञ आहात.
        खालील माहितीचा वापर करून महाराष्ट्र शासन नियमांनुसार सुटसुटीत आणि पूर्ण पानावर बसणारा कायदेशीर मराठी मसुदा तयार करा:

        सेवा: {curr}
        अर्जदार: {app_name}
        पत्ता: {app_address}
        कार्यालय/विरोधक: {auth_name}
        कार्यालय पत्ता: {auth_address}
        विषय: {subject}
        तपशील: {info_details}
        """
        
        with st.spinner("⚡ AI द्वारे परिपूर्ण मसुदा तयार होत आहे..."):
            try:
                response = model.generate_content(master_prompt)
                draft_text = response.text
                st.success("✅ मसुदा यशस्वीरीत्या तयार झाला आहे!")
                edited_draft = st.text_area("✏️ तयार झालेला मसुदा (संपादित करा):", value=draft_text, height=350)
            except Exception as e:
                st.error(f"त्रुटी आली: {e}")
