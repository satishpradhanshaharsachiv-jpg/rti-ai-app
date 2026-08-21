import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. प्रीमियम UI, फॉन्ट आणि 'ॲप आयकॉन' स्टाईलिंग (CSS)
# ==============================================================================
st.set_page_config(page_title="RTI & Legal AI Master", layout="wide", page_icon="⚖️")

st.markdown("""
<style>
.stApp { background-color: #F8FAFC; }
.main-title { color: #0F172A; font-weight: 800; text-align: center; font-size: 24px; margin-bottom: 20px; }

/* ॲप आयकॉन स्टाईल (छोटे, गोल कोपरे) */
div[data-testid="stColumn"] .stButton > button {
    height: 75px !important; width: 75px !important; border-radius: 18px !important;
    font-size: 11px !important; font-weight: 700 !important; color: white !important;
    border: none !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    margin: 5px auto !important; padding: 5px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stColumn"] .stButton > button:hover { transform: scale(1.05); }

/* प्रत्येक बटणाचा खास रंग */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(1) > button { background: #25D366; } /* हिरवा */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(1) > button { background: #E1306C; } /* गुलाबी */
div[data-testid="stColumn"]:nth-of-type(3) div.stButton:nth-of-type(1) > button { background: #1E3A8A; } /* नेव्ही */
div[data-testid="stColumn"]:nth-of-type(4) div.stButton:nth-of-type(1) > button { background: #3B82F6; } /* निळा */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(2) > button { background: #7C3AED; } /* जांभळा */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(2) > button { background: #DC2626; } /* लाल */
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. प्रगत AI लॉजिक
# ==============================================================================
def process_legal_request(prompt, img=None):
    key = st.secrets.get("GEMINI_API_KEY", "")
    if not key: return "API Key नाही."
    genai.configure(api_key=key)
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content([prompt, img] if img else prompt)
        return res.text
    except Exception as e: return f"त्रुटी: {str(e)}"

# ==============================================================================
# ३. ॲप स्ट्रक्चर (Grid Menu)
# ==============================================================================
st.markdown("<h1 class='main-title'>RTI महा-सहाय्यक</h1>", unsafe_allow_html=True)

# ४ कॉलममध्ये बटणे (मोबाईलवर छोटे दिसतील)
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📄\nअ"): st.session_state.active_tab = "जोडपत्र 'अ'"
with c2:
    if st.button("⚖️\nब"): st.session_state.active_tab = "जोडपत्र 'ब'"
with c3:
    if st.button("🏛️\nक"): st.session_state.active_tab = "जोडपत्र 'क'"
with c4:
    if st.button("✨\nAI"): st.session_state.active_tab = "AI चॅट"

st.markdown("---")

# ==============================================================================
# ४. संपूर्ण कार्यक्षमता (All Forms)
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "AI चॅट"

if st.session_state.active_tab == "AI चॅट":
    st.subheader("🤖 AI सल्लागार")
    img = st.file_uploader("फोटो:")
    msg = st.chat_input("प्रश्न विचारा...")
    if msg: st.write(process_legal_request(msg, Image.open(img) if img else None))

else:
    # सर्व फॉर्म्ससाठी एकच शक्तिशाली लॉजिक
    st.subheader(f"📝 {st.session_state.active_tab} मसुदा")
    with st.form("form"):
        name = st.text_input("नाव:")
        addr = st.text_area("पत्ता:")
        dept = st.text_input("विभाग:")
        info = st.text_area("तपशील:")
        if st.form_submit_button("मसुदा बनवा"):
            st.session_state.final_draft = f"प्रति, {dept}\n\nविषय: {info}\nअर्जदार: {name}\n{addr}"
            st.success("तयार झाले!")

if 'final_draft' in st.session_state and st.session_state.final_draft:
    st.text_area("अंतिम मसुदा:", st.session_state.final_draft)
    st.download_button("डाउनलोड करा", st.session_state.final_draft, "Draft.txt")
