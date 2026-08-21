import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. मोबाईल ॲप आयकॉन ग्रिड स्टाईलिंग (CSS)
# ==============================================================================
st.set_page_config(page_title="RTI व कायदेशीर AI महा-सहाय्यक", page_icon="⚖️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

.main-title {
    color: #0F172A;
    font-weight: 800;
    text-align: center;
    font-size: 22px;
    margin-top: -10px;
    margin-bottom: 2px;
}
.sub-title {
    text-align: center;
    color: #475569;
    font-size: 13px;
    margin-bottom: 15px;
}

/* मोबाईल स्क्रीनवरील ॲप आयकॉन बटणे */
div[data-testid="stColumn"] .stButton > button {
    height: 72px !important;
    width: 72px !important;
    border-radius: 18px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.18) !important;
    white-space: pre-wrap !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 4px auto !important;
    padding: 2px !important;
    transition: transform 0.2s !important;
}

div[data-testid="stColumn"] .stButton > button:hover {
    transform: scale(1.05) !important;
}

/* ओळ १ मधील ४ बटणांचे रंग */
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(1) .stButton > button {
    background: linear-gradient(135deg, #10B981, #059669) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(2) .stButton > button {
    background: linear-gradient(135deg, #EC4899, #F59E0B) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(3) .stButton > button {
    background: linear-gradient(135deg, #1E293B, #0F172A) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="stColumn"]:nth-of-type(4) .stButton > button {
    background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
}

/* ओळ २ मधील २ बटणांचे रंग */
div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="stColumn"]:nth-of-type(1) .stButton > button {
    background: linear-gradient(135deg, #7C3AED, #4C1D95) !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="stColumn"]:nth-of-type(2) .stButton > button {
    background: linear-gradient(135deg, #EF4444, #B91C1C) !important;
}

.chat-bubble-user {
    background: #2563EB; color: #FFFFFF; padding: 10px 14px; border-radius: 16px 16px 2px 16px;
    margin-bottom: 10px; max-width: 85%; margin-left: auto; font-size: 14px;
}
.chat-bubble-ai {
    background: #F8FAFC; color: #0F172A; padding: 12px 16px; border-radius: 16px 16px 16px 2px;
    margin-bottom: 12px; max-width: 90%; margin-right: auto; font-size: 14px; border-left: 4px solid #2563EB;
    border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;
}
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

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ **नमस्कार!** मी तुमचा कायदेशीर व प्रशासकीय AI सहाय्यक आहे.\n\nतुम्ही मला कायदेशीर प्रश्न विचारू शकता किंवा कागदपत्र तपासून घेऊ शकता.", "image": None}
    ]

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. 404 त्रुटीमुक्त AI इंजिन (Auto-Detection)
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def ask_ai(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Secrets मध्ये GEMINI_API_KEY प्रविष्ट करा."
    
    try:
        genai.configure(api_key=active_api_key)
        
        # सपोर्टेड मॉडेल्स शोधणे
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        target_model = None
        for pref in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
            if pref in available_models:
                target_model = pref
                break
        
        if not target_model and available_models:
            target_model = available_models[0]
            
        if not target_model:
            target_model = "gemini-1.5-flash"
            
        model = genai.GenerativeModel(target_model)
        if image_obj:
            res = model.generate_content([prompt_text, image_obj])
        else:
            res = model.generate_content(prompt_text)
            
        if res and res.text:
            return res.text
        return "AI कडून उत्तर मिळू शकले नाही."
    except Exception as e:
        return f"AI त्रुटी: {str(e)}"

# ==============================================================================
# ४. मुख्य हेडर
# ==============================================================================
st.markdown("<h1 class='main-title'>⚖️ RTI व कायदेशीर AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>तुमचा अधिकार, तुमच्या हातात – सर्व सेवा एकाच ठिकाणी</div>", unsafe_allow_html=True)

# ==============================================================================
# ५. मोबाईल ॲप स्क्रीन रचना (ओळ १: ४ बटणे | ओळ २: २ बटणे)
# ==============================================================================
row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
with row1_col1:
    if st.button("📄\nजोडपत्र 'अ'", key="tab1"): st.session_state.active_tab = "जोडपत्र 'अ'"
with row1_col2:
    if st.button("⚖️\nप्रथम अपील", key="tab2"): st.session_state.active_tab = "जोडपत्र 'ब'"
with row1_col3:
    if st.button("🏛️\nमाहिती आयोग", key="tab3"): st.session_state.active_tab = "जोडपत्र 'क'"
with row1_col4:
    if st.button("✨\nAI चॅट", key="tab4"): st.session_state.active_tab = "AI चॅट"

row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
with row2_col1:
    if st.button("📜\nकोर्ट याचिका", key="tab5"): st.session_state.active_tab = "न्यायालयीन मसुदा"
with row2_col2:
    if st.button("📢\nशासकीय तक्रार", key="tab6"): st.session_state.active_tab = "शासकीय तक्रार"
with row2_col3:
    st.write("")
with row2_col4:
    st.write("")

st.markdown("---")

# ==============================================================================
# विभाग १: जोडपत्र 'अ'
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.subheader("📄 जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("सरकारी कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मागितलेल्या माहितीचा तपशील (मुद्दे):", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 अर्ज तयार करा"):
            with st.spinner("अर्ज तयार होत आहे..."):
                p = f"महाराष्ट्र RTI कलम ६(१) जोडपत्र 'अ' अर्ज विहित नमुन्यात बनवा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}."
                res = ask_ai(p)
                st.session_state.final_draft = res if "AI त्रुटी" not in res else f"जोडपत्र - 'अ'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अर्जदार: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. माहितीचा तपशील:\n{st.session_state.original_query}\n\nशुल्क: ₹१०/- कोर्ट फी जोडली आहे.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"
            st.success("✅ जोडपत्र 'अ' तयार झाले!")

# ==============================================================================
# विभाग २: प्रथम अपील (जोडपत्र 'ब')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.subheader("⚖️ जोडपत्र 'ब' - प्रथम अपील (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("अपिलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        reason = st.text_area("अपीलाचे कारण:", value="विहित ३० दिवसांत जन माहिती अधिकाऱ्याने कोणतीही माहिती उपलब्ध करून दिली नाही.")
        
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"जोडपत्र - 'ब'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अपिलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. कारण: {reason}\n४. मूळ माहितीचा विषय: {st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"
            st.success("✅ प्रथम अपील तयार झाले!")

# ==============================================================================
# विभाग ३: द्वितीय अपील (जोडपत्र 'क')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.subheader("🏛️ जोडपत्र 'क' - द्वितीय अपील (राज्य माहिती आयोग)")
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        
        if st.form_submit_button("🚀 द्वितीय अपील तयार करा"):
            st.session_state.final_draft = f"जोडपत्र - 'क'\nमाहिती अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपील.\n\nप्रति,\nमा. राज्य माहिती आयोग खंडपीठ,\n\n१. अपीलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. प्रतिवादी: जन माहिती अधिकारी, {st.session_state.dept_name}\n४. मूळ माहितीचा विषय: {st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"
            st.success("✅ द्वितीय अपील तयार झाले!")

# ==============================================================================
# विभाग ४: AI चॅटबॉट व फोटो विश्लेषण
# ==============================================================================
elif st.session_state.active_tab == "AI चॅट":
    st.subheader("✨ AI कायदेशीर सल्लागार व दस्तऐवज विश्लेषक")

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">👤 <b>तुम्ही:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"):
                st.image(msg["image"], width=220)
        else:
            st.markdown(f'<div class="chat-bubble-ai">✨ <b>AI सहाय्यक:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    uploaded_photo = st.file_uploader("➕ फोटो किंवा कागदपत्र जोडा (विश्लेषणासाठी):", type=["png", "jpg", "jpeg"])

    if user_prompt := st.chat_input("येथे प्रश्न विचारा..."):
        img_data = Image.open(uploaded_photo) if uploaded_photo else None
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt, "image": img_data})
        st.rerun()

    if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        last_user_msg = st.session_state.chat_messages[-1]
        with st.spinner("✨ माहिती तपासत आहे..."):
            sys_instruct = "तुम्ही एक तज्ज्ञ कायदेशीर AI आहात. वापरकर्त्याच्या प्रश्नाचे किंवा कागदपत्राचे अचूक व स्पष्ट उत्तर मराठीत द्या."
            full_query = f"{sys_instruct}\n\nप्रश्न: {last_user_msg['content']}"
            
            ai_reply = ask_ai(full_query, last_user_msg.get("image"))
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply, "image": None})
            st.rerun()

# ==============================================================================
# विभाग ५: न्यायालयीन मसुदा
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.subheader("📜 न्यायालयीन याचिका मसुदा")
    with st.form("form_court"):
        st.session_state.user_name = st.text_input("याचिकाकर्ता नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी नाव:", value=st.session_state.dept_name)
        court_subj = st.text_input("विषय:", value="प्रशासकीय दिरंगाई व नुकसानभरपाई बाबत")
        
        if st.form_submit_button("🚀 कोर्ट मसुदा तयार करा"):
            st.session_state.final_draft = f"मा. सक्षम न्यायालय / लवाद\n\n{st.session_state.user_name}, रा. {st.session_state.user_address}\n... याचिकाकर्ता\nविरुद्ध\n{st.session_state.dept_name}\n... प्रतिवादी\n\nविषय: {court_subj}\n\n१. वस्तुस्थिती: {st.session_state.original_query}\n२. प्रार्थना: योग्य तो कायदेशीर दिलासा देण्यात यावा.\n\nदिनांक: {date_today}\nयाचिकाकर्ता: {st.session_state.user_name}"
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ==============================================================================
# विभाग ६: शासकीय तक्रार
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.subheader("📢 शासकीय तक्रार अर्ज")
    with st.form("form_comp"):
        st.session_state.user_name = st.text_input("तक्रारदाराचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रति / अधिकारी:", value=st.session_state.dept_name)
        c_sub = st.text_input("विषय:", value="शासकीय योजनेतील दिरंगाई व गैरव्यवहाराबाबत तक्रार")
        c_body = st.text_area("तक्रारीचा तपशील:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"प्रति,\nमा. {st.session_state.dept_name},\n\nविषय: {c_sub}\nतक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}\n\nमहोदय,\n{c_body}\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"
            st.success("✅ तक्रार अर्ज तयार झाला!")

# ==============================================================================
# ७. मसुदा निकाल व डाऊनलोड
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI चॅट":
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अंतिम मसुदा:")
    st.text_area("मसुदा तपासा किंवा कॉपी करा:", value=st.session_state.final_draft, height=220)

    doc_share_msg = urllib.parse.quote(st.session_state.final_draft)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(
            label="📥 मसुदा डाऊनलोड (.txt)",
            data=st.session_state.final_draft,
            file_name=f"Legal_Draft_{date_today}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with d_col2:
        st.markdown(
            f'<a href="https://api.whatsapp.com/send?text={doc_share_msg}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:40px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">'
            f'📲 WhatsApp वर पाठवा</button></a>',
            unsafe_allow_html=True
        )
