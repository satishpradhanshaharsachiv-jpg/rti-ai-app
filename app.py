import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. सर्व्हर सेटिंग्ज आणि प्री-लोडिंग
# ==============================================================================
st.set_page_config(page_title="RTI महा-सहाय्यक", layout="centered")

st.markdown("""
<style>
/* 4x4 ग्रिड मोबाईलसाठी */
[data-testid="column"] { width: 25% !important; flex: 0 0 25% !important; padding: 2px !important; }
div[data-testid="stButton"] > button {
    height: 70px !important; width: 100% !important; border-radius: 15px !important;
    font-size: 10px !important; font-weight: 700 !important; color: white !important;
    border: none !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    white-space: normal !important; line-height: 1.1 !important; margin: 0 !important;
}
/* बटण कलर्स */
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
# २. AI इंजिन (बुलटप्रूफ)
# ==============================================================================
def ask_ai(prompt, img=None):
    key = st.secrets.get("GEMINI_API_KEY", "")
    if not key: return "API Key नाही."
    genai.configure(api_key=key)
    try:
        # डायनॅमिक मॉडेल सिलेक्शन (404 एरर टाळण्यासाठी)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = "gemini-1.5-flash" if "gemini-1.5-flash" in models else models[0]
        model = genai.GenerativeModel(target)
        return model.generate_content([prompt, img] if img else prompt).text
    except Exception as e: return f"त्रुटी: {str(e)}"

# ==============================================================================
# ३. सेशन्स स्टेट
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "AI चॅट"
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""

# ==============================================================================
# ४. मुख्य ॲप ग्रिड (4x4)
# ==============================================================================
st.markdown("<h3 style='text-align:center;'>RTI महा-सहाय्यक</h3>", unsafe_allow_html=True)

r1 = st.columns(4)
with r1[0]: 
    if st.button("📄\nअर्ज"): st.session_state.active_tab = "जोडपत्र 'अ'"
with r1[1]: 
    if st.button("⚖️\nप्रथम"): st.session_state.active_tab = "जोडपत्र 'ब'"
with r1[2]: 
    if st.button("🏛️\nआयोग"): st.session_state.active_tab = "जोडपत्र 'क'"
with r1[3]: 
    if st.button("✨\nAI"): st.session_state.active_tab = "AI चॅट"

r2 = st.columns(4)
with r2[0]: 
    if st.button("📜\nकोर्ट"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with r2[1]: 
    if st.button("📢\nतक्रार"): st.session_state.active_tab = "शासकीय तक्रार"
with r2[2]: 
    if st.button("📝\nशपथ"): st.session_state.active_tab = "प्रतिज्ञापत्र"
with r2[3]: 
    if st.button("🛒\nग्राहक"): st.session_state.active_tab = "ग्राहक मंच"

st.markdown("---")

# ==============================================================================
# ५. विभाग लॉजिक (सर्व फॉर्म्स)
# ==============================================================================
if st.session_state.active_tab == "AI चॅट":
    st.subheader("🤖 AI सल्लागार")
    img = st.file_uploader("फोटो/कागदपत्र:")
    q = st.chat_input("प्रश्न विचारा...")
    if q: st.write(ask_ai(q, Image.open(img) if img else None))

else:
    st.subheader(f"📝 {st.session_state.active_tab}")
    with st.form("form"):
        name = st.text_input("नाव:")
        addr = st.text_area("पत्ता:")
        dept = st.text_input("कार्यालय:")
        text = st.text_area("माहिती/तपशील:")
        if st.form_submit_button("मसुदा बनवा"):
            st.session_state.final_draft = f"प्रति, {dept}\n{name}, {addr}\n\nविषय: {text}"
            st.success("मसुदा तयार!")

# निकाल व डाऊनलोड
if st.session_state.final_draft:
    st.text_area("अंतिम मसुदा:", st.session_state.final_draft)
    st.download_button("📥 डाऊनलोड", st.session_state.final_draft, "Legal_Doc.txt")

# ==============================================================================
# ६. भविष्यातील अपडेट्ससाठी जागा (खाली कोड जोडा)
# ==============================================================================
# [START_FOR_FUTURE_UPDATES]
# ==============================================================================
