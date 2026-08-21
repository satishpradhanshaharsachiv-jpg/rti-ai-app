import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. आधुनिक Gemini / ChatGPT स्टाईल डिझाइन (UI & CSS)
# ==============================================================================
st.set_page_config(page_title="RTI व कायदेशीर AI महा-सहाय्यक", page_icon="✨", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

h1 { color: #1E3A8A; font-weight: 800; text-align: center; font-size: 22px; margin-bottom: 2px; }

/* शेअर मेनू */
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
.btn-ms { background: #0084FF; }

/* ChatGPT / Gemini स्टाईल चॅट कार्ड्स */
.chat-bubble-user {
    background: #E0E7FF; color: #1E1B4B; padding: 12px 16px; border-radius: 16px 16px 2px 16px;
    margin-bottom: 10px; max-width: 85%; margin-left: auto; font-size: 15px;
}
.chat-bubble-ai {
    background: #F1F5F9; color: #0F172A; padding: 14px 18px; border-radius: 16px 16px 16px 2px;
    margin-bottom: 15px; max-width: 90%; margin-right: auto; font-size: 15px; border-left: 4px solid #3B82F6;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट मॅनेजमेंट
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
        {"role": "assistant", "content": "✨ **नमस्कार!** मी तुमचा ऑल-इन-वन AI सहाय्यक आहे.\n\nतुम्ही मला **RTI, शासकीय नियम, न्यायालयीन कायदे, जगातील सामान्य ज्ञान** विचारू शकता किंवा **फोटो / कागदपत्र अपलोड करून** त्यावरील मजकुराचे विश्लेषण करून घेऊ शकता.", "image": None}
    ]

APP_URL = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/?v=3"

# ==============================================================================
# ३. डायनॅमिक AI इंजिन (४०४ त्रुटी कायमची दूर करणारे ऑटो-डिटेक्ट लॉजिक)
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def get_best_generative_model():
    if not active_api_key:
        return None
    genai.configure(api_key=active_api_key)
    try:
        # उपलब्ध मॉडेल्सची यादी तपासणे
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # प्राधान्यक्रम
        preferred = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro",
            "models/gemini-2.0-flash",
            "models/gemini-pro"
        ]
        for p in preferred:
            if p in models:
                return genai.GenerativeModel(p)
        if models:
            return genai.GenerativeModel(models[0])
    except Exception:
        pass
    return genai.GenerativeModel("gemini-1.5-flash")

def ask_ai(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया प्रथम Streamlit Secrets मध्ये 'GEMINI_API_KEY' प्रविष्ट करा."
    try:
        model = get_best_generative_model()
        if not model:
            return "AI मॉडेल लोड होऊ शकले नाही. कृपया API Key तपासा."
        
        if image_obj:
            response = model.generate_content([prompt_text, image_obj])
        else:
            response = model.generate_content(prompt_text)
            
        if response and response.text:
            return response.text
    except Exception as e:
        return f"AI त्रुटी: {str(e)}"
    return "माहिती तयार करण्यात अडचण आली, कृपया पुन्हा प्रयत्न करा."

# ==============================================================================
# ४. मुख्य हेडर व ↗️ शेअर बटण
# ==============================================================================
st.markdown("<h1>✨ RTI, तक्रार व कायदेशीर AI महा-सहाय्यक</h1>", unsafe_allow_html=True)

h_c1, h_c2 = st.columns([5, 1])
with h_c1:
    st.caption("नागरिकांसाठी सर्व कायदेशीर, प्रशासकीय व बहुउद्देशीय AI माहिती केंद्र")
with h_c2:
    if st.button("↗️ शेअर", key="main_share_btn", use_container_width=True):
        st.session_state.show_share = not st.session_state.show_share

if st.session_state.show_share:
    share_msg = urllib.parse.quote(f"⚖️ RTI, शासकीय तक्रार व ऑल-इन-वन AI सहाय्यक ॲप:\n{APP_URL}")
    st.markdown(f"""
    <div class="share-box">
        <p style="margin:0 0 6px 0; font-weight:bold; font-size:14px; color:#374151;">ॲप सोशल मीडियावर शेअर करा:</p>
        <a class="share-btn btn-wa" href="https://api.whatsapp.com/send?text={share_msg}" target="_blank">WhatsApp</a>
        <a class="share-btn btn-fb" href="https://www.facebook.com/sharer/sharer.php?u={APP_URL}" target="_blank">Facebook</a>
        <a class="share-btn btn-tg" href="https://t.me/share/url?url={APP_URL}&text={share_msg}" target="_blank">Telegram</a>
        <a class="share-btn btn-ms" href="fb-messenger://share/?link={APP_URL}" target="_blank">Messenger</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# ५. मुख्य ६ नॅव्हिगेशन बटने
# ==============================================================================
b1, b2, b3, b4, b5, b6 = st.columns(6)
with b1:
    if st.button("🟢 जोडपत्र 'अ'", key="tab1", use_container_width=True): st.session_state.active_tab = "जोडपत्र 'अ'"
with b2:
    if st.button("🔵 प्रथम अपील", key="tab2", use_container_width=True): st.session_state.active_tab = "जोडपत्र 'ब'"
with b3:
    if st.button("🟠 माहिती आयोग", key="tab3", use_container_width=True): st.session_state.active_tab = "जोडपत्र 'क'"
with b4:
    if st.button("✨ Gemini / AI चॅट", key="tab4", use_container_width=True): st.session_state.active_tab = "AI चॅट"
with b5:
    if st.button("🟣 कोर्ट याचिका", key="tab5", use_container_width=True): st.session_state.active_tab = "न्यायालयीन मसुदा"
with b6:
    if st.button("🔴 शासकीय तक्रार", key="tab6", use_container_width=True): st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# विभाग १: जोडपत्र 'अ' (RTI अर्ज)
# ==============================================================================
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.subheader("🟢 जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("सरकारी कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मागितलेल्या माहितीचा तपशील (मुद्दे):", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 अर्ज तयार करा"):
            p = f"महाराष्ट्र RTI कलम ६(१) जोडपत्र 'अ' अर्ज बनवा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}."
            res = ask_ai(p)
            st.session_state.final_draft = res if "त्रुटी" not in res else f"""जोडपत्र - 'अ'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अर्जदार: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. माहितीचा तपशील:\n{st.session_state.original_query}\n\nशुल्क: ₹१०/- कोर्ट फी जोडली आहे.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ जोडपत्र 'अ' तयार झाले!")

# ==============================================================================
# विभाग २: प्रथम अपील (जोडपत्र 'ब')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.subheader("🔵 जोडपत्र 'ब' - प्रथम अपील (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("अपिलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        reason = st.text_area("अपीलाचे कारण:", value="विहित ३० दिवसांत जन माहिती अधिकाऱ्याने कोणतीही माहिती उपलब्ध करून दिली नाही.")
        
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'ब'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अपिलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. कारण: {reason}\n४. मूळ माहिती: {st.session_state.original_query}\n\nमागणी: माहिती विनामूल्य उपलब्ध करून देण्याचे आदेश व्हावेत.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ प्रथम अपील तयार झाले!")

# ==============================================================================
# विभाग ३: द्वितीय अपील (जोडपत्र 'क')
# ==============================================================================
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.subheader("🟠 जोडपत्र 'क' - द्वितीय अपील (राज्य माहिती आयोग)")
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी कार्यालय / विभाग:", value=st.session_state.dept_name)
        
        if st.form_submit_button("🚀 द्वितीय अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'क'\nमाहिती अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपील.\n\nप्रति,\nमा. राज्य माहिती आयोग खंडपीठ,\n\n१. अपीलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. प्रतिवादी: जन माहिती अधिकारी, {st.session_state.dept_name}\n४. मूळ माहिती: {st.session_state.original_query}\n\nप्रार्थना: कलम २०(१) अन्वये दंड आकारून माहिती विनामूल्य देण्यात यावी.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ द्वितीय अपील तयार झाले!")

# ==============================================================================
# विभाग ४: ✨ अस्सल Gemini / ChatGPT स्टाईल AI चॅटबॉट (फोटो + सर्व प्रश्न)
# ==============================================================================
elif st.session_state.active_tab == "AI चॅट":
    st.markdown("### ✨ ऑल-इन-वन AI सहाय्यक (Gemini / ChatGPT Style)")
    st.caption("फोटो/कागदपत्र अपलोड करा किंवा जगातील कोणताही प्रश्न मराठीतून विचारा.")

    # चॅट इतिहास
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">👤 <b>तुम्ही:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"):
                st.image(msg["image"], width=240)
        else:
            st.markdown(f'<div class="chat-bubble-ai">✨ <b>AI सहाय्यक:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    # फोटो जोडणे (+)
    uploaded_photo = st.file_uploader("➕ फोटो किंवा कागदपत्र जोडा (फोटोवरील मजकूर वाचण्यासाठी किंवा विश्लेषणासाठी):", type=["png", "jpg", "jpeg"])

    # प्रश्न विचारणे
    if user_prompt := st.chat_input("येथे प्रश्न विचारा (उदा. या फोटोत काय लिहिले आहे? किंवा कोणताही सामान्य ज्ञानाचा प्रश्न)..."):
        img_data = Image.open(uploaded_photo) if uploaded_photo else None
        
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt, "image": img_data})
        st.rerun()

    # शेवटच्या युझर मेसेजवर प्रक्रिया
    if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        last_user_msg = st.session_state.chat_messages[-1]
        with st.spinner("✨ विचार करत आहे..."):
            sys_instruct = "तुम्ही एक हुशार, आधुनिक आणि सर्वसमावेशक AI आहात. वापरकर्त्याच्या प्रश्नाचे किंवा फोटोचे सविस्तर, मुद्देसूद आणि अचूक विश्लेषण मराठीत करा."
            full_query = f"{sys_instruct}\n\nप्रश्न: {last_user_msg['content']}"
            
            ai_reply = ask_ai(full_query, last_user_msg.get("image"))
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply, "image": None})
            st.rerun()

# ==============================================================================
# विभाग ५: न्यायालयीन मसुदा
# ==============================================================================
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.subheader("🟣 न्यायालयीन याचिका मसुदा")
    with st.form("form_court"):
        st.session_state.user_name = st.text_input("याचिकाकर्ता नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी नाव:", value=st.session_state.dept_name)
        court_subj = st.text_input("विषय:", value="प्रशासकीय दिरंगाई व नुकसानभरपाई बाबत")
        
        if st.form_submit_button("🚀 कोर्ट मसुदा तयार करा"):
            st.session_state.final_draft = f"""मा. सक्षम न्यायालय / लवाद\n\n{st.session_state.user_name}, रा. {st.session_state.user_address}\n... याचिकाकर्ता\nविरुद्ध\n{st.session_state.dept_name}\n... प्रतिवादी\n\nविषय: {court_subj}\n\n१. वस्तुस्थिती: {st.session_state.original_query}\n२. प्रार्थना: योग्य तो कायदेशीर दिलासा देण्यात यावा.\n\nदिनांक: {date_today}\nयाचिकाकर्ता: {st.session_state.user_name}"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ==============================================================================
# विभाग ६: शासकीय तक्रार अर्ज
# ==============================================================================
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.subheader("🔴 शासकीय तक्रार अर्ज")
    with st.form("form_comp"):
        st.session_state.user_name = st.text_input("तक्रारदाराचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व संपर्क:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रति / अधिकारी:", value=st.session_state.dept_name)
        c_sub = st.text_input("विषय:", value="दिव्यांगांना जागा उपलब्ध करून देणे व कारवाई करणेबाबत")
        c_body = st.text_area("तक्रारीचा तपशील:", value=st.session_state.original_query)
        
        if st.form_submit_button("🚀 तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"""प्रति,\nमा. {st.session_state.dept_name},\n\nविषय: {c_sub}\nतक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}\n\nमहोदय,\n{c_body}\n\nसदर प्रकरणी योग्य निर्णय घेऊन त्वरित न्याय देण्यात यावा.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ तक्रार अर्ज तयार झाला!")

# ==============================================================================
# ७. मसुदा निकाल, डाऊनलोड व WhatsApp शेअर
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI चॅट":
    st.markdown("---")
    st.markdown("### 📄 तयार झालेला अंतिम मसुदा:")
    st.text_area("मसुदा तपासा किंवा कॉपी करा:", value=st.session_state.final_draft, height=200)

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
            f'<button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:6px; cursor:pointer;">'
            f'📲 मसुदा WhatsApp वर पाठवा</button></a>',
            unsafe_allow_html=True
        )
