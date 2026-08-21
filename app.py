import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image
import time

# ==============================================================================
# १. प्रीमियम UI, CSS आणि ॲडव्हान्स्ड स्टाईलिंग
# ==============================================================================
st.set_page_config(page_title="RTI & Legal AI Master", layout="wide", page_icon="⚖️")

st.markdown("""
<style>
.stApp { background-color: #F8FAFC; }
.main-title { color: #0F172A; font-weight: 800; text-align: center; font-size: 28px; margin-bottom: 5px; }
.sub-title { text-align: center; color: #64748B; font-size: 16px; margin-bottom: 20px; }

/* प्रोफेशनल ग्रिड बटणे */
div[data-testid="stColumn"] .stButton > button {
    height: 100px !important; width: 100% !important; border-radius: 20px !important;
    font-size: 15px !important; font-weight: 700 !important; color: white !important;
    border: none !important; box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
    transition: all 0.3s ease !important;
}
/* बटण ग्रिड रंग */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(1) > button { background: linear-gradient(135deg, #059669, #10B981); }
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(1) > button { background: linear-gradient(135deg, #D946EF, #EC4899); }
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(2) > button { background: linear-gradient(135deg, #1E293B, #334155); }
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(2) > button { background: linear-gradient(135deg, #3B82F6, #2563EB); }
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #7C3AED, #6D28D9); }
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #EF4444, #B91C1C); }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. प्रगत AI लॉजिक आणि एरर हँडलिंग
# ==============================================================================
def get_ai_model():
    key = st.secrets.get("GEMINI_API_KEY", "")
    if not key: return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-1.5-flash")

def process_legal_request(prompt, img=None):
    model = get_ai_model()
    if not model: return "API Key आढळली नाही. कृपया सेटिंग तपासा."
    try:
        if img: return model.generate_content([prompt, img]).text
        return model.generate_content(prompt).text
    except Exception as e:
        return f"तांत्रिक त्रुटी (Error): {str(e)}. कृपया पुन्हा प्रयत्न करा."

# ==============================================================================
# ३. ॲप स्ट्रक्चर (Sidebar + Main)
# ==============================================================================
st.sidebar.title("🛠️ कंट्रोल पॅनल")
st.sidebar.markdown("---")
if st.sidebar.button("🏠 मुख्य पृष्ठ"): st.session_state.active_tab = "Home"

st.markdown("<h1 class='main-title'>⚖️ RTI व कायदेशीर AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>सुरक्षित, वेगवान आणि कायदेशीर मसुदा निर्माता</div>", unsafe_allow_html=True)

# ==============================================================================
# ४. होम स्क्रीन ग्रिड (तुमचे आवडते डिझाइन)
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "Home"

if st.session_state.active_tab == "Home":
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📄\nRTI जोडपत्र 'अ'"): st.session_state.active_tab = "RTI_A"
        if st.button("🏛️\nमाहिती आयोग अपील"): st.session_state.active_tab = "RTI_C"
        if st.button("📜\nन्यायालयीन याचिका"): st.session_state.active_tab = "Legal_Draft"
    with c2:
        if st.button("⚖️\nप्रथम अपील (ब)"): st.session_state.active_tab = "RTI_B"
        if st.button("✨\nAI कायदेशीर सल्ला"): st.session_state.active_tab = "AI_Chat"
        if st.button("📢\nशासकीय तक्रार"): st.session_state.active_tab = "Gov_Complaint"

# ==============================================================================
# ५. प्रत्येक विभागाचे सविस्तर लॉजिक (येथे ॲप वाढवले आहे)
# ==============================================================================
def render_form(title, prompt_prefix):
    st.subheader(title)
    with st.form("main_form"):
        name = st.text_input("पूर्ण नाव:")
        address = st.text_area("पत्ता:")
        dept = st.text_input("विभाग / अधिकारी:")
        subject = st.text_area("तपशील:")
        if st.form_submit_button("✅ मसुदा तयार करा"):
            if not name or not dept: st.error("कृपया नाव आणि विभाग भरा!")
            else:
                with st.spinner("AI मसुदा तयार करत आहे..."):
                    res = process_legal_request(f"{prompt_prefix} {name}, {address}, {dept}, {subject}")
                    st.session_state.final_draft = res
                    st.success("तयार झाले!")

if st.session_state.active_tab == "RTI_A": render_form("RTI अर्ज (जोडपत्र 'अ')", "महाराष्ट्र RTI नियम कलम ६(१) नुसार अर्ज लिहा:")
elif st.session_state.active_tab == "RTI_B": render_form("प्रथम अपील", "माहिती अधिकार कलम १९(१) नुसार प्रथम अपील करा:")
elif st.session_state.active_tab == "RTI_C": render_form("माहिती आयोग", "राज्य माहिती आयोगासाठी द्वितीय अपील तयार करा:")
elif st.session_state.active_tab == "Legal_Draft": render_form("न्यायालयीन याचिका", "सक्षम न्यायालयासाठी कायदेशीर याचिका मसुदा करा:")
elif st.session_state.active_tab == "Gov_Complaint": render_form("शासकीय तक्रार", "शासकीय अधिकाऱ्याविरुद्ध सविस्तर तक्रार अर्ज लिहा:")
elif st.session_state.active_tab == "AI_Chat":
    st.subheader("🤖 AI सल्लागार")
    msg = st.chat_input("प्रश्न विचारा...")
    if msg: st.write(process_legal_request(msg))

# ==============================================================================
# ६. शेवटचा निकाल आणि शेअरिंग
# ==============================================================================
if 'final_draft' in st.session_state and st.session_state.final_draft:
    st.markdown("---")
    st.subheader("📄 अंतिम मसुदा")
    st.text_area("येथून कॉपी करा:", st.session_state.final_draft, height=250)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button("📥 डाउनलोड", st.session_state.final_draft, "Draft.txt")
    with col_b:
        st.markdown(f"[📲 WhatsApp](https://wa.me/?text={urllib.parse.quote(st.session_state.final_draft)})")
