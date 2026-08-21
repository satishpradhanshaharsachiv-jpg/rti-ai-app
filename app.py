import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. प्रोफेशनल सॉफ्टवेअर आर्किटेक्चर आणि स्टाईलिंग (CSS Grid)
# ==============================================================================
st.set_page_config(page_title="RTI & Legal AI Master", layout="centered", page_icon="⚖️")

st.markdown("""
<style>
/* ॲपची मूळ रचना - हे '4-Column Grid' ला जबरदस्तीने लागू करेल */
.stApp { background-color: #F8FAFC; }
.main-title { color: #0F172A; font-weight: 800; text-align: center; font-size: 22px; margin-bottom: 5px; }

/* ॲप आयकॉन ग्रिड (4-Column) */
.grid-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    padding: 10px;
}

div[data-testid="stButton"] > button {
    height: 70px !important; width: 100% !important; border-radius: 16px !important;
    font-size: 9px !important; font-weight: 700 !important; color: white !important;
    border: none !important; box-shadow: 0 3px 6px rgba(0,0,0,0.1) !important;
    white-space: normal !important; line-height: 1.1 !important; margin: 0 !important;
}

/* बटन रंगांचे 'पॅलेट' */
.stButton:nth-of-type(1) > button { background: #10B981 !important; }
.stButton:nth-of-type(2) > button { background: #EC4899 !important; }
.stButton:nth-of-type(3) > button { background: #1E293B !important; }
.stButton:nth-of-type(4) > button { background: #3B82F6 !important; }
.stButton:nth-of-type(5) > button { background: #7C3AED !important; }
.stButton:nth-of-type(6) > button { background: #EF4444 !important; }
.stButton:nth-of-type(7) > button { background: #F59E0B !important; }
.stButton:nth-of-type(8) > button { background: #64748B !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. प्रगत AI बॅकएंड (Robust Error Handling)
# ==============================================================================
class LegalAIEngine:
    def __init__(self):
        self.api_key = st.secrets.get("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def get_response(self, prompt, img=None):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([prompt, img] if img else prompt)
            return response.text
        except Exception as e:
            return f"त्रुटी: {str(e)}"

# ॲप इंजिन इनिशियलायझेशन
ai_engine = LegalAIEngine()

# ==============================================================================
# ३. ॲप स्टेट मॅनेजमेंट
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "Home"
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""

# ==============================================================================
# ४. मुख्य इंटरफेस (4x2 ग्रिड - 8 बटणे)
# ==============================================================================
st.markdown("<h1 class='main-title'>RTI महा-सहाय्यक</h1>", unsafe_allow_html=True)

# बटणांची ओळ १ (४ बटणे)
c1, c2, c3, c4 = st.columns(4)
with c1: 
    if st.button("📄\nअर्ज"): st.session_state.active_tab = "जोडपत्र 'अ'"
with c2: 
    if st.button("⚖️\nप्रथम"): st.session_state.active_tab = "जोडपत्र 'ब'"
with c3: 
    if st.button("🏛️\nआयोग"): st.session_state.active_tab = "जोडपत्र 'क'"
with c4: 
    if st.button("✨\nAI"): st.session_state.active_tab = "AI सल्लागार"

# बटणांची ओळ २ (४ बटणे)
c5, c6, c7, c8 = st.columns(4)
with c5: 
    if st.button("📜\nकोर्ट"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with c6: 
    if st.button("📢\nतक्रार"): st.session_state.active_tab = "शासकीय तक्रार"
with c7: 
    if st.button("📝\nशपथ"): st.session_state.active_tab = "प्रतिज्ञापत्र"
with c8: 
    if st.button("🛒\nग्राहक"): st.session_state.active_tab = "ग्राहक मंच"

st.markdown("---")

# ==============================================================================
# ५. विभाग लॉजिक (Modular Sections)
# ==============================================================================
if st.session_state.active_tab == "AI सल्लागार":
    st.subheader("🤖 AI सल्लागार")
    img = st.file_uploader("फोटो:")
    msg = st.chat_input("प्रश्न विचारा...")
    if msg: st.write(ai_engine.get_response(msg, Image.open(img) if img else None))

elif st.session_state.active_tab != "Home":
    st.subheader(f"📝 {st.session_state.active_tab}")
    with st.form("main_form"):
        name = st.text_input("नाव:")
        addr = st.text_area("पत्ता:")
        dept = st.text_input("कार्यालय:")
        detail = st.text_area("तपशील:")
        if st.form_submit_button("मसुदा बनवा"):
            st.session_state.final_draft = f"प्रति, {dept}\n{name}, {addr}\nविषय: {detail}"
            st.success("मसुदा तयार!")

# ==============================================================================
# ६. भविष्यातील अपडेट्ससाठी राखीव जागा (येथे नवीन फंक्शन वाढवा)
# ==============================================================================
# ------------------------------------------------------------------------------
# [येथे तुमचा कोड वाढवा - यापुढे मी जागा सोडली आहे]
# ------------------------------------------------------------------------------
if st.session_state.final_draft:
    st.text_area("अंतिम मसुदा:", st.session_state.final_draft)
    st.download_button("📥 डाऊनलोड", st.session_state.final_draft, "Legal_Draft.txt")
