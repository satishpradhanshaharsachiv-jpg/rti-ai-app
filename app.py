import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि अखंड मोबाईल स्टाईलिंग
# ==============================================================================
st.set_page_config(page_title="RTI AI महा-सहाय्यक", page_icon="⚖️", layout="centered")

params = st.query_params
if "tab" in params:
    st.session_state.active_tab = params["tab"]
elif "active_tab" not in st.session_state:
    st.session_state.active_tab = "जोडपत्र 'अ'"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800;900&display=swap');
* { font-family: 'Mukta', sans-serif !important; box-sizing: border-box !important; }
html, body { overflow-x: hidden !important; max-width: 100vw !important; }

.block-container {
    padding-top: 0.5rem !important; padding-bottom: 3.5rem !important;
    padding-left: 0.5rem !important; padding-right: 0.5rem !important;
    max-width: 480px !important; margin: 0 auto !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

.glowing-title {
    font-size: 20px !important; font-weight: 900 !important; text-align: center;
    background: linear-gradient(90deg, #FF1361, #FFF800, #00E676, #00B0FF, #D500F9);
    background-size: 300% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite; margin-bottom: 2px;
}
@keyframes shine { to { background-position: 300% center; } }

.user-banner {
    text-align: center; font-size: 13px; font-weight: 800; color: #1E3A8A;
    background: #E0F2FE; border: 1px solid #38BDF8; padding: 4px 8px; border-radius: 8px; margin-bottom: 8px;
}

.sub-tagline { text-align: center; font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 10px; }

.app-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-bottom: 12px; width: 100%; }
.app-card {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 68px; border-radius: 12px; color: #FFFFFF !important; text-decoration: none !important;
    font-size: 10.5px; font-weight: 800; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}
.app-card:active { transform: scale(0.94); }
.app-icon { font-size: 18px; margin-bottom: 1px; }

.btn-1 { background: linear-gradient(135deg, #10B981, #059669); }
.btn-2 { background: linear-gradient(135deg, #EC4899, #F59E0B); }
.btn-3 { background: linear-gradient(135deg, #1E293B, #0F172A); }
.btn-4 { background: linear-gradient(135deg, #3B82F6, #6366F1); }
.btn-5 { background: linear-gradient(135deg, #7C3AED, #4C1D95); }
.btn-6 { background: linear-gradient(135deg, #EF4444, #B91C1C); }
.btn-7 { background: linear-gradient(135deg, #F97316, #C2410C); }
.btn-8 { background: linear-gradient(135deg, #0284C7, #0369A1); }

.chat-user { background: #2563EB; color: #FFFFFF; padding: 8px 12px; border-radius: 14px 14px 2px 14px; margin-bottom: 8px; font-size: 13.5px; max-width: 88%; margin-left: auto; }
.chat-ai { background: #F1F5F9; color: #0F172A; padding: 10px 12px; border-radius: 14px 14px 14px 2px; margin-bottom: 8px; font-size: 13.5px; border-left: 4px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट व्यवस्थापन
# ==============================================================================
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ नमस्कार! कायदेशीर सल्ला विचारा किंवा खाली फोटो जोडून माहिती घ्या.", "image": None}
    ]

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. API Key मॅनेजमेंट (Sidebar आणि Secrets दोन्ही)
# ==============================================================================
sidebar_api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")
active_api_key = sidebar_api_key if sidebar_api_key else st.secrets.get("GEMINI_API_KEY", "")

def ask_ai_dynamic(prompt_text, image_obj=None):
    if not active_api_key:
        return "❌ API Key सापडली नाही. डाव्या बाजूच्या मेनूमध्ये (Sidebar) तुमची Gemini API Key टाका किंवा Streamlit Secrets मध्ये सेट करा."
    
    try:
        genai.configure(api_key=active_api_key)
        # अपडेटेड मॉडेल
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        payload = [prompt_text, image_obj] if image_obj else prompt_text
        res = model.generate_content(payload)
        if res and res.text:
            return res.text
        return "AI कडून उत्तर मिळाले नाही."
    except Exception as e:
        return f"❌ AI त्रुटी: {str(e)}"

# ==============================================================================
# ४. मुख्य हेडर व तुमचे नाव (Personal Branding)
# ==============================================================================
st.markdown('<div class="glowing-title">⚖️ RTI AI महा-सहाय्यक</div>', unsafe_allow_html=True)
st.markdown('<div class="user-banner">👨‍💼 संकल्पना व निर्मिती: सतीश अशोक प्रधान</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-tagline">⚡ १ मिनिटात सर्व शासकीय व न्यायालयीन मसुदे तयार करा</div>', unsafe_allow_html=True)

# ==============================================================================
# ५. ४x२ ग्रिड (८ बटणे)
# ==============================================================================
st.markdown("""
<div class="app-grid">
    <a href="?tab=जोडपत्र 'अ'" target="_self" class="app-card btn-1"><span class="app-icon">📄</span><span>जोडपत्र 'अ'</span></a>
    <a href="?tab=जोडपत्र 'ब'" target="_self" class="app-card btn-2"><span class="app-icon">⚖️</span><span>प्रथम अपील</span></a>
    <a href="?tab=जोडपत्र 'क'" target="_self" class="app-card btn-3"><span class="app-icon">🏛️</span><span>माहिती आयोग</span></a>
    <a href="?tab=AI चॅट" target="_self" class="app-card btn-4"><span class="app-icon">✨</span><span>AI चॅट</span></a>
    <a href="?tab=न्यायालयीन मसुदा" target="_self" class="app-card btn-5"><span class="app-icon">📜</span><span>कोर्ट याचिका</span></a>
    <a href="?tab=शासकीय तक्रार" target="_self" class="app-card btn-6"><span class="app-icon">📢</span><span>शासकीय तक्रार</span></a>
    <a href="?tab=प्रतिज्ञापत्र" target="_self" class="app-card btn-7"><span class="app-icon">📝</span><span>प्रतिज्ञापत्र</span></a>
    <a href="?tab=ग्राहक मंच" target="_self" class="app-card btn-8"><span class="app-icon">🛒</span><span>ग्राहक मंच</span></a>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# ६. विभागांचे फॉर्म्स
# ==============================================================================
active = st.session_state.active_tab

if active == "AI चॅट":
    st.subheader("✨ AI कायदेशीर सल्लागार")
    
    # आधीचे चॅट दाखवा
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 <b>तुम्ही:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"): st.image(msg["image"], width=170)
        else:
            st.markdown(f'<div class="chat-ai">✨ <b>AI:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    # गॅलरी/कॅमेरा अपलोडर सुटसुटीत
    st.markdown("<b>📷 फोटो/नोटीस जोडा (गॅलरीमधून निवडा):</b>", unsafe_allow_html=True)
    up_img = st.file_uploader("गॅलरीतून फोटो निवडा:", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if q_prompt := st.chat_input("येथे कायदेशीर प्रश्न विचारा..."):
        img = Image.open(up_img) if up_img else None
        st.session_state.chat_messages.append({"role": "user", "content": q_prompt, "image": img})
        with st.spinner("AI मसुदा तपासत आहे..."):
            ans = ask_ai_dynamic(q_prompt, img)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans, "image": None})
        st.rerun()

elif active == "जोडपत्र 'अ'":
    st.subheader("📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))")
    with st.form("form_a"):
        u_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व फोन:")
        dept = st.text_input("३. सार्वजनिक प्राधिकरण / कार्यालयाचे नाव:")
        q_info = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्देसूद):")
        if st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा"):
            st.session_state.final_draft = f"जोडपत्र - 'अ'\n(नियम ३ पहा)\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {dept}\n\n१. अर्जदाराचे नाव: {u_name}\n२. पत्ता व मोबाइल: {u_addr}\n३. मागितलेल्या माहितीचा तपशील:\n{q_info}\n४. अर्ज फी: ₹१०/- चा कोर्ट फी स्टॅम्प जोडला आहे.\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ जोडपत्र 'अ' तयार झाला!")

elif active == "जोडपत्र 'ब'":
    st.subheader("⚖️ प्रथम अपील (कलम १९(१)) - जोडपत्र 'ब'")
    with st.form("form_b"):
        u_name = st.text_input("१. अपीलकर्त्याचे पूर्ण नाव:")
        u_addr = st.text_area("२. पत्ता व मोबाइल:")
        dept = st.text_input("३. प्रथम अपीलीय अधिकारी व कार्यालय:")
        appeal_reason = st.text_area("४. अपीलाचे कारण:", value="विहित ३० दिवसांत माहिती न मिळाल्यामुळे.")
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"जोडपत्र - 'ब'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {dept}\n\n१. अपीलकर्त्याचे नाव: {u_name}\n२. पत्ता: {u_addr}\n३. अपीलाचे कारण: {appeal_reason}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ प्रथम अपील तयार झाला!")

# (इतर फॉर्म्स देखील याच पद्धतीने चालतील)

# ==============================================================================
# ७. मसुदा निकाल, डाऊनलोड व WhatsApp शेअरिंग (१००% वर्किंग)
# ==============================================================================
if st.session_state.final_draft and active != "AI चॅट":
    st.markdown("---")
    st.text_area("तयार झालेला अधिकृत मसुदा:", value=st.session_state.final_draft, height=200)
    
    encoded_text = urllib.parse.quote(st.session_state.final_draft)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 टेक्स्ट फाईल डाऊनलोड", st.session_state.final_draft, "Legal_Draft.txt", use_container_width=True)
    with col2:
        st.markdown(f'''
            <a href="{whatsapp_url}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">
                    📲 WhatsApp वर पाठवा
                </button>
            </a>
        ''', unsafe_allow_html=True)
