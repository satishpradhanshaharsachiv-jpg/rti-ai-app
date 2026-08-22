import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि कायमस्वरूपी सेव्ह केलेली परिपूर्ण ग्रिड डिझाइन (CSS)
# ==============================================================================
st.set_page_config(page_title="RTI महा-सहाय्यक", page_icon="⚖️", layout="centered")

params = st.query_params
if "tab" in params:
    st.session_state.active_tab = params["tab"]
elif "active_tab" not in st.session_state:
    st.session_state.active_tab = "जोडपत्र 'अ'"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800;900&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

.block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 0.8rem !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
    max-width: 500px !important;
    margin: 0 auto !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* चमकदार मल्टिकलर एका ओळीतील शीर्षक */
.glowing-title {
    font-size: 19px !important;
    font-weight: 900 !important;
    text-align: center;
    white-space: nowrap !important;
    background: linear-gradient(90deg, #FF1361, #FFF800, #00E676, #00B0FF, #D500F9);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite;
    margin-bottom: 2px;
}

@keyframes shine {
    to { background-position: 300% center; }
}

.sub-tagline {
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    color: #475569;
    margin-bottom: 12px;
}
.sub-tagline span {
    background: #FEF3C7;
    color: #D97706;
    padding: 2px 8px;
    border-radius: 20px;
    border: 1px dashed #F59E0B;
}

/* कायमस्वरूपी सेव्ह केलेली ४x२ ग्रिड रचना */
.app-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    margin-bottom: 12px;
    width: 100%;
}

.app-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 70px;
    border-radius: 14px;
    color: #FFFFFF !important;
    text-decoration: none !important;
    font-size: 11px;
    font-weight: 800;
    text-align: center;
    box-shadow: 0 3px 6px rgba(0,0,0,0.18);
    transition: transform 0.15s ease-in-out;
}

.app-card:active { transform: scale(0.92); }
.app-icon { font-size: 20px; margin-bottom: 1px; }

/* ८ बटणांचे चमकदार रंग */
.btn-1 { background: linear-gradient(135deg, #10B981, #059669); }
.btn-2 { background: linear-gradient(135deg, #EC4899, #F59E0B); }
.btn-3 { background: linear-gradient(135deg, #1E293B, #0F172A); }
.btn-4 { background: linear-gradient(135deg, #3B82F6, #6366F1); }
.btn-5 { background: linear-gradient(135deg, #7C3AED, #4C1D95); }
.btn-6 { background: linear-gradient(135deg, #EF4444, #B91C1C); }
.btn-7 { background: linear-gradient(135deg, #F97316, #C2410C); }
.btn-8 { background: linear-gradient(135deg, #0284C7, #0369A1); }

/* चॅट UI सुधारणा */
.chat-user {
    background: #2563EB; color: #FFFFFF; padding: 8px 12px; border-radius: 14px 14px 2px 14px;
    margin-bottom: 8px; font-size: 14px; max-width: 85%; margin-left: auto;
}
.chat-ai {
    background: #F1F5F9; color: #0F172A; padding: 10px 14px; border-radius: 14px 14px 14px 2px;
    margin-bottom: 8px; font-size: 14px; border-left: 4px solid #3B82F6;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट व्यवस्थापन
# ==============================================================================
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ नमस्कार! कायदेशीर सल्ला विचारा किंवा ➕ बटणाने फोटो जोडा.", "image": None}
    ]

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. हाय-स्पीड १-सेकंद AI इंजिन
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def ask_ai_fast(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Settings मध्ये Secrets -> GEMINI_API_KEY ऍड करा."
    try:
        genai.configure(api_key=active_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        content_payload = [prompt_text, image_obj] if image_obj else prompt_text
        res = model.generate_content(content_payload)
        return res.text if res and res.text else "उत्तर तयार होऊ शकले नाही."
    except Exception as e:
        # बॅकअप फॉलबॅक
        try:
            model_fallback = genai.GenerativeModel("gemini-pro")
            res_fb = model_fallback.generate_content(prompt_text)
            return res_fb.text
        except Exception:
            return f"त्रुटी आली: {str(e)}"

# ==============================================================================
# ४. मुख्य हेडर
# ==============================================================================
st.markdown("""
<div class="glowing-title">⚖️ RTI AI महा-सहाय्यक</div>
<div class="sub-tagline"><span>⚡ घरबसल्या एका मिनिटात अर्ज तयार करा</span></div>
""", unsafe_allow_html=True)

# ==============================================================================
# ५. कायमस्वरूपी सेव्ह केलेली ४x२ ग्रिड (८ ॲप आयकॉन्स)
# ==============================================================================
grid_html = """
<div class="app-grid">
    <a href="?tab=जोडपत्र 'अ'" target="_self" class="app-card btn-1">
        <span class="app-icon">📄</span><span>जोडपत्र 'अ'</span>
    </a>
    <a href="?tab=जोडपत्र 'ब'" target="_self" class="app-card btn-2">
        <span class="app-icon">⚖️</span><span>प्रथम अपील</span>
    </a>
    <a href="?tab=जोडपत्र 'क'" target="_self" class="app-card btn-3">
        <span class="app-icon">🏛️</span><span>माहिती आयोग</span>
    </a>
    <a href="?tab=AI चॅट" target="_self" class="app-card btn-4">
        <span class="app-icon">✨</span><span>AI चॅट</span>
    </a>
    <a href="?tab=न्यायालयीन मसुदा" target="_self" class="app-card btn-5">
        <span class="app-icon">📜</span><span>कोर्ट याचिका</span>
    </a>
    <a href="?tab=शासकीय तक्रार" target="_self" class="app-card btn-6">
        <span class="app-icon">📢</span><span>शासकीय तक्रार</span>
    </a>
    <a href="?tab=प्रतिज्ञापत्र" target="_self" class="app-card btn-7">
        <span class="app-icon">📝</span><span>प्रतिज्ञापत्र</span>
    </a>
    <a href="?tab=ग्राहक मंच" target="_self" class="app-card btn-8">
        <span class="app-icon">🛒</span><span>ग्राहक मंच</span>
    </a>
</div>
"""
st.markdown(grid_html, unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# ६. विभागानुसार फॉर्म्स आणि सुपर-फास्ट AI चॅट
# ==============================================================================
active = st.session_state.active_tab

if active == "AI चॅट":
    st.subheader("✨ AI कायदेशीर सल्लागार")
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 <b>तुम्ही:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"): st.image(msg["image"], width=180)
        else:
            st.markdown(f'<div class="chat-ai">✨ <b>AI:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    with st.expander("➕ फोटो / नोटीस जोडा", expanded=False):
        uploaded_doc = st.file_uploader("फाइल निवडा:", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if query := st.chat_input("प्रश्न विचारा..."):
        img = Image.open(uploaded_doc) if uploaded_doc else None
        st.session_state.chat_messages.append({"role": "user", "content": query, "image": img})
        
        with st.spinner("AI विचार करत आहे..."):
            ans = ask_ai_fast(query, img)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans, "image": None})
        st.rerun()

else:
    st.subheader(f"📝 {active}")
    with st.form("main_form"):
        st.session_state.user_name = st.text_input("नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / विभाग / प्रतिवादी:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("तपशील / मागितलेली माहिती:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 मसुदा तयार करा"):
            with st.spinner("१ सेकंदात मसुदा तयार होत आहे..."):
                prompt = f"{active} तयार करा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, तपशील: {st.session_state.original_query}, दिनांक: {date_today}."
                res = ask_ai_fast(prompt)
                st.session_state.final_draft = res if "त्रुटी" not in res else f"प्रति,\nमा. {st.session_state.dept_name}\n\nविषय: {active}\n\nअर्जदार: {st.session_state.user_name}\nपत्ता: {st.session_state.user_address}\n\nतपशील:\n{st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({st.session_state.user_name})"
                st.success("✅ मसुदा तयार झाला!")

# निकाल व WhatsApp शेअरिंग
if st.session_state.final_draft and active != "AI चॅट":
    st.markdown("---")
    st.text_area("तयार झालेला मसुदा:", value=st.session_state.final_draft, height=180)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 डाऊनलोड (.txt)", st.session_state.final_draft, "Draft.txt", use_container_width=True)
    with c2:
        msg_enc = urllib.parse.quote(st.session_state.final_draft)
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={msg_enc}" target="_blank"><button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)
