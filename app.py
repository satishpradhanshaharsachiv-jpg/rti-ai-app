import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. प्रोफेशनल आर्किटेक्चर - CSS स्टाईलिंग (पिल बार + परफेक्ट ग्रिड)
# ==============================================================================
st.set_page_config(page_title="RTI महा-सहाय्यक", page_icon="⚖️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800;900&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

.block-container { max-width: 500px !important; padding: 1rem 0.5rem !important; }
#MainMenu, footer { display: none !important; }

.glowing-title {
    font-size: 20px !important; font-weight: 900 !important; text-align: center;
    background: linear-gradient(90deg, #FF1361, #FFF800, #00E676);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.app-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 15px; }
.app-card {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 65px; border-radius: 12px; color: #FFFFFF !important; font-size: 10px; font-weight: 800;
    text-align: center; text-decoration: none !important; box-shadow: 0 3px 6px rgba(0,0,0,0.15);
}
.app-icon { font-size: 18px; margin-bottom: 2px; }

[data-testid="stChatInput"] { border-radius: 50px !important; border: 1px solid #E2E8F0 !important; }
[data-testid="stChatInput"] > div { border-radius: 50px !important; }

.btn-1 { background: #10B981; } .btn-2 { background: #EC4899; }
.btn-3 { background: #1E293B; } .btn-4 { background: #3B82F6; }
.btn-5 { background: #7C3AED; } .btn-6 { background: #EF4444; }
.btn-7 { background: #F97316; } .btn-8 { background: #0284C7; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. AI इंजिन (बुलटप्रूफ)
# ==============================================================================
def get_ai_response(prompt, img=None):
    key = st.secrets.get("GEMINI_API_KEY", "")
    genai.configure(api_key=key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content([prompt, img] if img else prompt)
        return res.text
    except Exception as e: return f"AI त्रुटी: {str(e)}"

# ==============================================================================
# ३. ॲप स्टेट
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""

# ==============================================================================
# ४. हेडर आणि ग्रिड
# ==============================================================================
st.markdown('<div class="glowing-title">⚖️ RTI AI महा-सहाय्यक</div>', unsafe_allow_html=True)
grid = """
<div class="app-grid">
    <a href="?tab=जोडपत्र 'अ'" class="app-card btn-1"><span>📄</span><span>अर्ज</span></a>
    <a href="?tab=जोडपत्र 'ब'" class="app-card btn-2"><span>⚖️</span><span>प्रथम</span></a>
    <a href="?tab=जोडपत्र 'क'" class="app-card btn-3"><span>🏛️</span><span>आयोग</span></a>
    <a href="?tab=AI चॅट" class="app-card btn-4"><span>✨</span><span>AI</span></a>
    <a href="?tab=कोर्ट याचिका" class="app-card btn-5"><span>📜</span><span>कोर्ट</span></a>
    <a href="?tab=शासकीय तक्रार" class="app-card btn-6"><span>📢</span><span>तक्रार</span></a>
    <a href="?tab=प्रतिज्ञापत्र" class="app-card btn-7"><span>📝</span><span>शपथ</span></a>
    <a href="?tab=ग्राहक मंच" class="app-card btn-8"><span>🛒</span><span>ग्राहक</span></a>
</div>
"""
st.markdown(grid, unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# ५. कायदेशीर फॉर्म्स (विस्तृत माहिती)
# ==============================================================================
active = st.session_state.active_tab

if active == "AI चॅट":
    st.subheader("🤖 AI सल्लागार")
    uploaded_file = st.file_uploader("➕ फोटो जोडा", type=["jpg", "png"])
    if prompt := st.chat_input("AI ला कायदेशीर प्रश्न विचारा..."):
        img = Image.open(uploaded_file) if uploaded_file else None
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"): st.write(get_ai_response(prompt, img))

else:
    st.subheader(f"📝 {active}")
    with st.form("main_form"):
        # सर्व फॉर्मसाठी एकत्रित प्रोफेशनल इनपुट फील्ड्स
        name = st.text_input("पूर्ण नाव:")
        addr = st.text_area("पूर्ण पत्ता:")
        dept = st.text_input("कार्यालय / प्रतिवादी विभाग:")
        details = st.text_area("तपशील / मुख्य मुद्दा:")
        
        if st.form_submit_button("🚀 मसुदा तयार करा"):
            st.session_state.final_draft = f"""
            प्रति, मा. {dept}
            अर्जदार: {name}
            पत्ता: {addr}
            विषय: {active}
            
            तपशील: {details}
            
            दिनांक: {datetime.now().strftime('%d/%m/%Y')}
            """
            st.success("मसुदा यशस्वीरित्या तयार झाला!")

# ==============================================================================
# ६. रिझल्ट्स
# ==============================================================================
if st.session_state.final_draft:
    st.text_area("अंतिम मसुदा:", st.session_state.final_draft, height=200)
    col1, col2 = st.columns(2)
    with col1: st.download_button("📥 डाऊनलोड", st.session_state.final_draft, "draft.txt")
    with col2: st.link_button("📲 WhatsApp", f"https://api.whatsapp.com/send?text={urllib.parse.quote(st.session_state.final_draft)}")
