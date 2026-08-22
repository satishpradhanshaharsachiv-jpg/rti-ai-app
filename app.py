import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि जेमिनी-स्टाईल UI
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

.chat-user { background: #2563EB; color: #FFFFFF; padding: 10px 14px; border-radius: 18px 18px 2px 18px; margin-bottom: 8px; font-size: 14px; max-width: 85%; margin-left: auto; }
.chat-ai { background: #F1F5F9; color: #0F172A; padding: 10px 14px; border-radius: 18px 18px 18px 2px; margin-bottom: 8px; font-size: 14px; border-left: 4px solid #3B82F6; }

/* Popover 'expand_more' एरर फिक्स आणि Gemini ➕ बटण */
div[data-testid="stPopover"] button {
    background-color: #E2E8F0 !important;
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    padding: 0px !important;
    border: none !important;
}
div[data-testid="stPopover"] button p {
    font-size: 22px !important;
    display: block !important;
    margin: 0 !important;
}
div[data-testid="stPopover"] button span:nth-child(2) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट व्यवस्थापन
# ==============================================================================
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ नमस्कार सतीश जी! कायदेशीर किंवा प्रशासकीय सल्ला विचारा.", "image": None}
    ]

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. मल्टी-मॉडेल (Multi-Model Multi-Try) AI इंजिन
# ==============================================================================
sidebar_api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")
active_api_key = sidebar_api_key if sidebar_api_key else st.secrets.get("GEMINI_API_KEY", "")

def generate_ai_response(prompt_text, image_obj=None):
    if not active_api_key:
        return "❌ API Key टाकलेली नाही. Sidebar मध्ये Gemini API Key भरा किंवा Secrets चेक करा."
    
    genai.configure(api_key=active_api_key)
    
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        'gemini-1.5-pro',
        'gemini-1.0-pro',
        'gemini-2.0-flash-exp',
        'gemini-2.0-flash'
    ]
    
    payload = [prompt_text, image_obj] if image_obj else prompt_text
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(payload)
            if response and response.text:
                return response.text
        except Exception:
            continue

    return "माफ करा, सर्व AI मॉडेल्स सध्या व्यस्त आहेत. कृपया थोड्या वेळाने प्रयत्न करा."

# ==============================================================================
# ४. मुख्य हेडर
# ==============================================================================
st.markdown('<div class="glowing-title">⚖️ RTI AI महा-सहाय्यक</div>', unsafe_allow_html=True)
st.markdown('<div class="user-banner">👨‍💼 संकल्पना व निर्मिती: सतीश अशोक प्रधान</div>', unsafe_allow_html=True)

# ==============================================================================
# ५. ८ बटणांची ग्रिड
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
# ६. मुख्य फॉर्म व AI चॅट विभाग
# ==============================================================================
active = st.session_state.active_tab

if active == "AI चॅट":
    st.subheader("✨ Gemini AI कायदेशीर सहाय्यक")
    
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"): st.image(msg["image"], width=180)
        else:
            st.markdown(f'<div class="chat-ai">✨ <b>Gemini:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    up_img = None
    col1, col2 = st.columns([1.5, 8])
    with col1:
        with st.popover("➕"):
            up_img = st.file_uploader("फोटो/नोटीस जोडा:", type=["png", "jpg", "jpeg"])
    with col2:
        st.caption("👈 फोटो जोडण्यासाठी **➕** वर क्लिक करा.")

    if q_prompt := st.chat_input("Gemini ला विचारण्यासाठी इथे लिहा..."):
        img = Image.open(up_img) if up_img else None
        st.session_state.chat_messages.append({"role": "user", "content": q_prompt, "image": img})
        with st.spinner("उत्तर शोधत आहे..."):
            ans = generate_ai_response(q_prompt, img)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans, "image": None})
        st.rerun()

elif active == "जोडपत्र 'अ'":
    st.subheader("📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))")
    with st.form("form_a"):
        u_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:")
        u_addr = st.text_area("२. अर्जदाराचा पूर्ण पत्ता व मोबाईल नंबर:")
        dept = st.text_input("३. जन माहिती अधिकारी / कार्यालयाचे नाव व पत्ता:")
        
        st.markdown("---")
        st.markdown("**४. हव्या असलेल्या माहितीचा तपशील:**")
        q_subject = st.text_input("(एक) माहितीचा विषय:")
        q_period = st.text_input("(दोन) ज्या कालावधीसंबंधात माहिती हवी असेल तो कालावधी:")
        q_desc = st.text_area("(तीन) हव्या असलेल्या माहितीचे वर्णन (मुद्देसूद):")
        
        q_delivery = st.radio("(चार) माहिती टपालाद्वारे हवी आहे की व्यक्तिशः हवी आहे?", 
                              ["व्यक्तिशः (Self)", "टपालाद्वारे (साधे टपाल / नोंदणीकृत / स्पीड पोस्ट)"])
        
        is_bpl = st.radio("५. अर्जदार दारिद्र्यरेषेखालील आहे किंवा कसे?", 
                          ["नाही", "होय (दारिद्र्यरेषेखालील पुराव्याची प्रत जोडली आहे)"])
        
        if st.form_submit_button("🚀 परिपूर्ण जोडपत्र 'अ' अर्ज तयार करा"):
            st.session_state.final_draft = f"""महाराष्ट्र शासन राजपत्र, असा., नोव्हेंबर १८, २००५
जोडपत्र अ
(नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ अन्वये माहिती मिळविण्यासाठीच्या अर्जाचा नमुना

प्रति,
राज्य जन माहिती अधिकारी,
{dept}

१. अर्जदाराचे संपूर्ण नाव : {u_name}

२. पत्ता : {u_addr}

३. हव्या असलेल्या माहितीचा तपशील :
   (एक) माहितीचा विषय : {q_subject}
   (दोन) ज्या कालावधी संबंधात माहिती हवी असेल तो कालावधी : {q_period}
   (तीन) हव्या असलेल्या माहितीचे वर्णन :
   {q_desc}
   (चार) माहिती टपालाद्वारे हवी आहे की व्यक्तिशः हवी आहे : {q_delivery}
        (टपालाद्वारे हवी असल्यास: नोंदणीकृत / शीघ्र पोस्ट)

४. अर्जदार दारिद्र्यरेषेखालील आहे किंवा कसे : {is_bpl}
   (असल्यास, त्याबाबतच्या पुराव्याची छायांकित प्रत जोडली आहे)

ठिकाण : 
दिनांक : {date_today}

                                                अर्जदाराची सही / अंगठा
                                                ({u_name})

----------------------------------------------------------------------
[टीप: अर्जदाराने येथे १० रुपयाचा न्यायालय फी मुद्रांक (Court Fee Stamp) चिकटवावा]"""
            st.success("✅ अधिकृत राजपत्राच्या नमुन्यानुसार जोडपत्र 'अ' तयार झाला आहे!")

# ==============================================================================
# ७. डाऊनलोड व शेअर
# ==============================================================================
if st.session_state.final_draft and active != "AI चॅट":
    st.markdown("---")
    st.text_area("तयार झालेला अधिकृत मसुदा:", value=st.session_state.final_draft, height=300)
    
    encoded_text = urllib.parse.quote(st.session_state.final_draft)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 टेक्स्ट डाऊनलोड", st.session_state.final_draft, "Draft.txt", use_container_width=True)
    with col2:
        st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">📲 WhatsApp शेअर</button></a>', unsafe_allow_html=True)
