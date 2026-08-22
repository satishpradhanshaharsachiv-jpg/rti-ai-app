import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. मोबाईल स्क्रीनवर ४-४ बटणे आडवी (Lock) ठेवण्यासाठी CSS
# ==============================================================================
st.set_page_config(page_title="RTI महा-सहाय्यक", layout="centered")

st.markdown("""
<style>
/* मोबाईलवर ४ बटणे एका ओळीत आडवीच राहतील */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: space-between !important;
    gap: 4px !important;
}

div[data-testid="column"] {
    flex: 1 1 0px !important;
    width: 24% !important;
    min-width: 0px !important;
    padding: 0px !important;
}

div[data-testid="stButton"] > button {
    height: 65px !important; 
    width: 100% !important;
    border-radius: 12px !important;
    font-size: 10px !important; 
    font-weight: 700 !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
    padding: 2px !important;
    white-space: pre-wrap !important;
    line-height: 1.15 !important;
}

/* ओळ १ मधील ४ बटणांचे स्वतंत्र रंग */
[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(1) button { background: linear-gradient(135deg, #10B981, #059669) !important; }
[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(2) button { background: linear-gradient(135deg, #EC4899, #F59E0B) !important; }
[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(3) button { background: linear-gradient(135deg, #1E293B, #0F172A) !important; }
[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(4) button { background: linear-gradient(135deg, #3B82F6, #6366F1) !important; }

/* ओळ २ मधील ४ बटणांचे स्वतंत्र रंग */
[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(1) button { background: linear-gradient(135deg, #7C3AED, #4C1D95) !important; }
[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(2) button { background: linear-gradient(135deg, #EF4444, #B91C1C) !important; }
[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(3) button { background: linear-gradient(135deg, #F97316, #C2410C) !important; }
[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(4) button { background: linear-gradient(135deg, #0284C7, #0369A1) !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट व्यवस्थापन
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. सुरक्षित AI इंजिन
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def ask_ai(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Secrets मध्ये GEMINI_API_KEY तपासा."
    genai.configure(api_key=active_api_key)
    for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content([prompt_text, image_obj] if image_obj else prompt_text)
            if res and res.text:
                return res.text
        except Exception:
            continue
    return "AI कडून उत्तर मिळू शकले नाही."

# ==============================================================================
# ४. मुख्य हेडर
# ==============================================================================
st.markdown("<h3 style='text-align:center; margin-top:-15px;'>⚖️ RTI महा-सहाय्यक</h3>", unsafe_allow_html=True)

# ==============================================================================
# ५. मोबाईल ॲप ग्रिड (ओळ १: ४ बटणे | ओळ २: ४ बटणे)
# ==============================================================================
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1:
    if st.button("📄\nअर्ज", key="b1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with r1_c2:
    if st.button("⚖️\nप्रथम", key="b2"): st.session_state.active_tab = "जोडपत्र 'ब'"
with r1_c3:
    if st.button("🏛️\nआयोग", key="b3"): st.session_state.active_tab = "जोडपत्र 'क'"
with r1_c4:
    if st.button("✨\nAI", key="b4"): st.session_state.active_tab = "AI चॅट"

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
with r2_c1:
    if st.button("📜\nकोर्ट", key="b5"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with r2_c2:
    if st.button("📢\nतक्रार", key="b6"): st.session_state.active_tab = "शासकीय तक्रार"
with r2_c3:
    if st.button("📝\nशपथ", key="b7"): st.session_state.active_tab = "प्रतिज्ञापत्र"
with r2_c4:
    if st.button("🛒\nग्राहक", key="b8"): st.session_state.active_tab = "ग्राहक मंच"

st.markdown("---")

# ==============================================================================
# ६. विभागानुसार फॉर्म्स व AI चॅट
# ==============================================================================
if st.session_state.active_tab == "AI चॅट":
    st.subheader("✨ AI कायदेशीर सल्लागार")
    uploaded_photo = st.file_uploader("कागदपत्र / नोटीस फोटो जोडा:", type=["png", "jpg", "jpeg"])
    user_prompt = st.chat_input("प्रश्न येथे विचारा...")
    if user_prompt:
        img_data = Image.open(uploaded_photo) if uploaded_photo else None
        with st.spinner("माहिती तपासत आहे..."):
            ans = ask_ai(user_prompt, img_data)
            st.write(ans)

else:
    st.subheader(f"📝 {st.session_state.active_tab}")
    with st.form("dynamic_form"):
        st.session_state.user_name = st.text_input("नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / विभाग:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("तपशील / मागितलेली माहिती:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 मसुदा तयार करा"):
            st.session_state.final_draft = f"प्रति,\nमा. {st.session_state.dept_name}\n\nविषय: {st.session_state.active_tab}\n\nअर्जदार: {st.session_state.user_name}\nपत्ता: {st.session_state.user_address}\n\nतपशील:\n{st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({st.session_state.user_name})"
            st.success("✅ मसुदा तयार झाला!")

# ==============================================================================
# ७. डाऊनलोड व WhatsApp शेअरिंग
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI चॅट":
    st.markdown("---")
    st.text_area("तयार झालेला मसुदा:", value=st.session_state.final_draft, height=180)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button("📥 डाऊनलोड (.txt)", st.session_state.final_draft, "Draft.txt", use_container_width=True)
    with col_d2:
        msg_enc = urllib.parse.quote(st.session_state.final_draft)
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={msg_enc}" target="_blank"><button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px;">📲 WhatsApp</button></a>', unsafe_allow_html=True)
