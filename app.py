import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. आधुनिक पोस्टर व मोबाइल डिझाइन (CSS)
# ==============================================================================
st.set_page_config(page_title="RTI व कायदेशीर AI महा-सहाय्यक", page_icon="⚖️", layout="wide")

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
    font-size: 24px;
    margin-top: -20px;
    margin-bottom: 2px;
}
.sub-title {
    text-align: center;
    color: #475569;
    font-size: 14px;
    margin-bottom: 15px;
}

/* ==========================================================================
   पोस्टर स्टाईल ६ रंगीत कार्ड्स बटणे (२ कॉलम्स ग्रिड)
   ========================================================================== */
div[data-testid="stColumn"] .stButton > button {
    height: 95px !important;
    width: 100% !important;
    border-radius: 16px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.18) !important;
    white-space: pre-wrap !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    margin-bottom: 8px !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}

div[data-testid="stColumn"] .stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 16px rgba(0,0,0,0.25) !important;
}

/* १. जोडपत्र 'अ' (व्हॉट्सॲप / हिरवा रंग) */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(1) > button {
    background: linear-gradient(135deg, #25D366, #128C7E) !important;
}

/* २. प्रथम अपील (इन्स्टाग्राम ग्रेडियंट / गुलाबी-केशरी) */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(1) > button {
    background: linear-gradient(135deg, #E1306C, #F77737) !important;
}

/* ३. माहिती आयोग (पोलीस / नेव्ही ब्लू रंग) */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(2) > button {
    background: linear-gradient(135deg, #0F172A, #1E3A8A) !important;
}

/* ४. AI चॅट (मॉडर्न गूगल / व्हायलेट निळा रंग) */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(2) > button {
    background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
}

/* ५. कोर्ट याचिका (फोनपे जांभळा रंग) */
div[data-testid="stColumn"]:nth-of-type(1) div.stButton:nth-of-type(3) > button {
    background: linear-gradient(135deg, #5F259F, #3F1070) !important;
}

/* ६. शासकीय तक्रार (डार्क रेड / शासकीय तक्रार रंग) */
div[data-testid="stColumn"]:nth-of-type(2) div.stButton:nth-of-type(3) > button {
    background: linear-gradient(135deg, #DC2626, #991B1B) !important;
}

/* चॅट बबल्स */
.chat-bubble-user {
    background: #2563EB; color: #FFFFFF; padding: 12px 16px; border-radius: 16px 16px 2px 16px;
    margin-bottom: 10px; max-width: 85%; margin-left: auto; font-size: 15px;
}
.chat-bubble-ai {
    background: #F8FAFC; color: #0F172A; padding: 14px 18px; border-radius: 16px 16px 16px 2px;
    margin-bottom: 15px; max-width: 90%; margin-right: auto; font-size: 15px; border-left: 4px solid #2563EB;
    border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;
}

.share-box {
    background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px;
    padding: 10px; margin-bottom: 12px; text-align: center;
}
.share-btn {
    display: inline-block; padding: 6px 14px; margin: 4px; border-radius: 6px;
    color: white !important; text-decoration: none; font-size: 13px; font-weight: bold;
}
.btn-wa { background: #25D366; }
.btn-fb { background: #1877F2; }
.btn-tg { background: #0088CC; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'show_share' not in st.session_state: st.session_state.show_share = False

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ **नमस्कार!** मी तुमचा कायदेशीर व प्रशासकीय AI सहाय्यक आहे.\n\nतुम्ही मला **RTI, शासकीय तक्रारी, कायदे** विचारू शकता किंवा **फोटो / कागदपत्र अपलोड करून** विश्लेषण करून घेऊ शकता.", "image": None}
    ]

APP_URL = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/?v=3"

# ==============================================================================
# ३. AI इंजिन (त्रुटीमुक्त चालू मॉडेल लिस्ट)
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def ask_ai(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Streamlit Secrets मध्ये तुमची API Key प्रविष्ट करा."
    
    genai.configure(api_key=active_api_key)
    
    model_list = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    last_err = ""
    for m in model_list:
        try:
            model = genai.GenerativeModel(m)
            if image_obj:
                res = model.generate_content([prompt_text, image_obj])
            else:
                res = model.generate_content(prompt_text)
            
            if res and res.text:
                return res.text
        except Exception as e:
            last_err = str(e)
            continue
            
    return f"AI त्रुटी: {last_err}"

# ==============================================================================
# ४. मुख्य शीर्षक व शेअर
# ==============================================================================
st.markdown("<h1 class='main-title'>⚖️ RTI व कायदेशीर AI महा-सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>तुमचा अधिकार, तुमच्या हातात – सर्व सेवा एकाच ठिकाणी</div>", unsafe_allow_html=True)

h_c1, h_c2 = st.columns([5, 1])
with h_c2:
    if st.button("↗️ शेअर", key="main_share_btn", use_container_width=True):
        st.session_state.show_share = not st.session_state.show_share

if st.session_state.show_share:
    share_msg = urllib.parse.quote(f"⚖️ RTI, शासकीय तक्रार व ऑल-इन-वन AI सहाय्यक:\n{APP_URL}")
    st.markdown(f"""
    <div class="share-box">
        <a class="share-btn btn-wa" href="https://api.whatsapp.com/send?text={share_msg}" target="_blank">WhatsApp</a>
        <a class="share-btn btn-fb" href="https://www.facebook.com/sharer/sharer.php?u={APP_URL}" target="_blank">Facebook</a>
        <a class="share-btn btn-tg" href="https://t.me/share/url?url={APP_URL}&text={share_msg}" target="_blank">Telegram</a>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ५. पोस्टरनुसार ६ मुख्य ॲप बटणे (२ बाय ३ ग्रिड)
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("📄\nजोडपत्र 'अ'\n(कलम ६(१))", key="tab1"):
        st.session_state.active_tab = "जोडपत्र 'अ'"
    if st.button("🏛️\nमाहिती आयोग\n(द्वितीय अपील)", key="tab3"):
        st.session_state.active_tab = "जोडपत्र 'क'"
    if st.button("📜\nकोर्ट याचिका\n(Petition)", key="tab5"):
        st.session_state.active_tab = "न्यायालयीन मसुदा"

with col2:
    if st.button("⚖️\nप्रथम अपील\n(कलम १९(१))", key="tab2"):
        st.session_state.active_tab = "जोडपत्र 'ब'"
    if st.button("✨\nAI महा-सहाय्यक\n(चॅट व फोटो)", key="tab4"):
        st.session_state.active_tab = "AI चॅट"
    if st.button("📢\nशासकीय तक्रार\n(प्रशासकीय अर्ज)", key="tab6"):
        st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("---")
date_today = datetime.now().strftime("%d/%m/%Y")

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
        
        if st.form_submit_button("🚀 AI द्वारे अर्ज तयार करा"):
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
                st.image(msg["image"], width=240)
        else:
            st.markdown(f'<div class="chat-bubble-ai">✨ <b>AI सहाय्यक:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    uploaded_photo = st.file_uploader("➕ फोटो किंवा कागदपत्र जोडा (विश्लेषणासाठी):", type=["png", "jpg", "jpeg"])

    if user_prompt := st.chat_input("येथे प्रश्न विचारा (उदा. या कागदपत्रातील सारांश काय आहे?)..."):
        img_data = Image.open(uploaded_photo) if uploaded_photo else None
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt, "image": img_data})
        st.rerun()

    if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        last_user_msg = st.session_state.chat_messages[-1]
        with st.spinner("✨ माहिती तपासत आहे..."):
            sys_instruct = "तुम्ही एक तज्ज्ञ भारतीय कायदेशीर आणि प्रशासकीय AI आहात. वापरकर्त्याच्या प्रश्नाचे किंवा कागदपत्राचे अचूक व स्पष्ट मार्गदर्शन मराठीत करा."
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
            label="📥 मसुदा डाऊनलोड करा (.txt)",
            data=st.session_state.final_draft,
            file_name=f"Legal_Draft_{date_today}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with d_col2:
        st.markdown(
            f'<a href="https://api.whatsapp.com/send?text={doc_share_msg}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:42px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">'
            f'📲 मसुदा WhatsApp वर पाठवा</button></a>',
            unsafe_allow_html=True
        )
