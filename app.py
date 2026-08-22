import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि जेमिनी-स्टाईल पिल इनपुट बार CSS
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
    padding-bottom: 5rem !important;
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

/* चॅट UI */
.chat-user {
    background: #2563EB; color: #FFFFFF; padding: 8px 14px; border-radius: 16px 16px 2px 16px;
    margin-bottom: 8px; font-size: 14px; max-width: 85%; margin-left: auto;
}
.chat-ai {
    background: #F1F5F9; color: #0F172A; padding: 10px 14px; border-radius: 16px 16px 16px 2px;
    margin-bottom: 8px; font-size: 14px; border-left: 4px solid #3B82F6;
}

/* ========================================================================== */
/* Gemini सारखा पिल-शेप्ड (गोल) इनपुट बार डिझाइन */
/* ========================================================================== */
.gemini-pill-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 35px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    padding: 4px 8px;
    margin-top: 15px;
}

/* इनपुट बारमधील बटणे */
div[data-testid="column"] button[kind="secondary"] {
    background: #F1F5F9 !important;
    color: #475569 !important;
    border-radius: 50% !important;
    height: 42px !important;
    width: 42px !important;
    min-width: 42px !important;
    border: none !important;
    font-size: 18px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
    margin: 0 auto !important;
}

/* उजवीकडील निळे गोल ॲक्शन बटन (Mic/Audio Wave) */
div[data-testid="column"] button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
    color: #FFFFFF !important;
    border-radius: 50% !important;
    height: 42px !important;
    width: 42px !important;
    min-width: 42px !important;
    border: none !important;
    font-size: 16px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.35) !important;
    margin: 0 auto !important;
}

/* मध्यभागातील टेक्स्ट इनपुट */
.gemini-pill-container input {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    font-size: 14px !important;
    padding-left: 5px !important;
    color: #1E293B !important;
}
.gemini-pill-container input:focus {
    outline: none !important;
    border: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट व्यवस्थापन
# ==============================================================================
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'show_file_uploader' not in st.session_state: st.session_state.show_file_uploader = False
if 'uploaded_image' not in st.session_state: st.session_state.uploaded_image = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ नमस्कार! कायदेशीर सल्ला विचारा किंवा ➕ चिन्हाने फोटो/कागदपत्र जोडा.", "image": None}
    ]

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. हाय-स्पीड AI इंजिन
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def ask_ai_dynamic(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Settings -> Secrets मध्ये GEMINI_API_KEY तपासा."
    try:
        genai.configure(api_key=active_api_key)
        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        target = "models/gemini-1.5-flash"
        if target not in valid_models:
            if "models/gemini-pro" in valid_models: target = "models/gemini-pro"
            elif valid_models: target = valid_models[0]
            else: target = "gemini-pro"
            
        model = genai.GenerativeModel(target)
        payload = [prompt_text, image_obj] if image_obj else prompt_text
        res = model.generate_content(payload)
        return res.text if res and res.text else "उत्तर तयार होऊ शकले नाही."
    except Exception as e:
        return f"AI त्रुटी: {str(e)}"

# ==============================================================================
# ४. मुख्य हेडर
# ==============================================================================
st.markdown("""
<div class="glowing-title">⚖️ RTI AI महा-सहाय्यक</div>
<div class="sub-tagline"><span>⚡ घरबसल्या एका मिनिटात अर्ज तयार करा</span></div>
""", unsafe_allow_html=True)

# ==============================================================================
# ५. कायमस्वरूपी सेव्ह केलेली ४x२ ग्रिड
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
# ६. विभागानुसार फॉर्म्स आणि पिल-शेप्ड AI चॅट
# ==============================================================================
active = st.session_state.active_tab

if active == "AI चॅट":
    st.subheader("✨ AI कायदेशीर सल्लागार")
    
    # आधीचे मेसेज दाखवणे
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 <b>तुम्ही:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"): st.image(msg["image"], width=180)
        else:
            st.markdown(f'<div class="chat-ai">✨ <b>AI:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    # ➕ दाबली असल्यास फाइल पिकर दाखवणे
    if st.session_state.show_file_uploader:
        uploaded_file = st.file_uploader("कागदपत्र / नोटीस फोटो निवडा:", type=["png", "jpg", "jpeg"], key="doc_uploader")
        if uploaded_file:
            st.session_state.uploaded_image = Image.open(uploaded_file)
            st.success("✅ फोटो जोडला गेला आहे!")

    # ==========================================================================
    # जेमिनी पिल इनपुट बार (+ | टेक्स्ट बॉक्स | 🎙️)
    # ==========================================================================
    st.markdown('<div class="gemini-pill-container">', unsafe_allow_html=True)
    c_plus, c_input, c_action = st.columns([1.2, 7.6, 1.2])
    
    with c_plus:
        if st.button("➕", key="btn_plus_toggle", help="फोटो किंवा डॉक्युमेंट जोडा"):
            st.session_state.show_file_uploader = not st.session_state.show_file_uploader
            st.rerun()

    with c_input:
        user_query = st.text_input("input_box", placeholder="AI ला विचारा...", label_visibility="collapsed", key="gemini_text_input")

    with c_action:
        submit_btn = st.button("🎙️", key="btn_mic_send", type="primary", help="पाठवा / व्हॉइस")

    st.markdown('</div>', unsafe_allow_html=True)

    # प्रश्न पाठवल्यावर उत्तर जनरेट करणे
    if submit_btn and user_query:
        img_to_send = st.session_state.uploaded_image
        st.session_state.chat_messages.append({"role": "user", "content": user_query, "image": img_to_send})
        
        with st.spinner("AI विचार करत आहे..."):
            ans = ask_ai_dynamic(user_query, img_to_send)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans, "image": None})
        
        # रिसेट
        st.session_state.uploaded_image = None
        st.session_state.show_file_uploader = False
        st.rerun()

# --- इतर सर्व ७ कायदेशीर फॉर्म्स ---
elif active == "जोडपत्र 'अ'":
    st.subheader("📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))")
    with st.form("form_a"):
        u_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व फोन:")
        dept = st.text_input("३. सार्वजनिक प्राधिकरण / कार्यालयाचे नाव:")
        q_info = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्देसूद):")
        q_period = st.text_input("५. माहितीचा संबंधित कालावधी:", value="चालू वर्ष")
        if st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा"):
            st.session_state.final_draft = f"जोडपत्र - 'अ'\n(नियम ३ पहा)\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {dept}\n\n१. अर्जदाराचे नाव: {u_name}\n२. पत्ता व मोबाइल: {u_addr}\n३. मागितलेल्या माहितीचा तपशील:\n{q_info}\n४. कालावधी: {q_period}\n५. अर्ज फी: ₹१०/- चा कोर्ट फी स्टॅम्प जोडला आहे.\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ जोडपत्र 'अ' मसुदा तयार झाला!")

elif active == "जोडपत्र 'ब'":
    st.subheader("⚖️ प्रथम अपील (कलम १९(१)) - जोडपत्र 'ब'")
    with st.form("form_b"):
        u_name = st.text_input("१. अपीलकर्त्याचे पूर्ण नाव:")
        u_addr = st.text_area("२. पत्ता व मोबाइल:")
        dept = st.text_input("३. प्रथम अपीलीय अधिकारी व कार्यालय:")
        pio_details = st.text_input("४. संबंधित जन माहिती अधिकाऱ्याचा तपशील:")
        appeal_reason = st.text_area("५. अपीलाचे कारण:", value="विहित ३० दिवसांत माहिती न मिळाल्यामुळे.")
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"जोडपत्र - 'ब'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {dept}\n\n१. अपीलकर्त्याचे नाव: {u_name}\n२. पत्ता: {u_addr}\n३. जन माहिती अधिकारी: {pio_details}\n४. अपीलाचे कारण: {appeal_reason}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ प्रथम अपील मसुदा तयार झाला!")

elif active == "जोडपत्र 'क'":
    st.subheader("🏛️ राज्य माहिती आयोग - द्वितीय अपील (कलम १९(३))")
    with st.form("form_c"):
        u_name = st.text_input("१. अपीलकर्त्याचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता:")
        bench = st.text_input("३. माहिती आयोग खंडपीठ:", value="छत्रपती संभाजीनगर")
        resp_dept = st.text_input("४. प्रतिवादी विभाग / कार्यालय:")
        facts = st.text_area("५. वस्तुस्थिती व अपीलाचा आधार:")
        if st.form_submit_button("🚀 द्वितीय अपील तयार करा"):
            st.session_state.final_draft = f"जोडपत्र - 'क'\nराज्य माहिती आयोगाकडे करावयाचे द्वितीय अपील (कलम १९(३)).\n\nप्रति,\nमा. राज्य माहिती आयुक्त,\nखंडपीठ: {bench}\n\n१. अपीलकर्ता: {u_name}\n२. पत्ता: {u_addr}\n३. प्रतिवादी: {resp_dept}\n४. वस्तुस्थिती: {facts}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ द्वितीय अपील मसुदा तयार झाला!")

elif active == "न्यायालयीन मसुदा":
    st.subheader("📜 न्यायालयीन याचिका / दाद मसुदा")
    with st.form("form_court"):
        u_name = st.text_input("१. याचिकाकर्ता नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता:")
        opp_name = st.text_input("३. विरोधी पक्षकार / प्रतिवादी:")
        court_name = st.text_input("४. सक्षम न्यायालय / लवाद:", value="मा. दिवाणी / उच्च न्यायालय")
        case_cause = st.text_area("५. वादाचे कायदेशीर कारण व नुकसान:")
        court_prayer = st.text_area("६. मागितलेला न्याय / दिलासा:")
        if st.form_submit_button("🚀 कोर्ट याचिका मसुदा तयार करा"):
            st.session_state.final_draft = f"{court_name} येथे\n\nयाचिका क्रमांक: ______ / {datetime.now().year}\n\n{u_name}\nरा. {u_addr}\n... याचिकाकर्ता\nविरुद्ध\n{opp_name}\n... प्रतिवादी\n\n१. वस्तुस्थिती: {case_cause}\n२. प्रार्थना: {court_prayer}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

elif active == "शासकीय तक्रार":
    st.subheader("📢 शासकीय व प्रशासकीय तक्रार अर्ज")
    with st.form("form_gov"):
        u_name = st.text_input("१. तक्रारदाराचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व संपर्क:")
        gov_off = st.text_input("३. तक्रार कोणाकडे करायची आहे (अधिकारी / कार्यालय):")
        comp_sub = st.text_input("४. तक्रारीचा विषय:")
        comp_facts = st.text_area("५. गैरप्रकार / तक्रारीचा सविस्तर तपशील:")
        if st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"प्रति,\nमा. {gov_off},\n\nविषय: {comp_sub}\n\nतक्रारदार: {u_name}\nपत्ता: {u_addr}\n\nमहोदय,\n{comp_facts}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला!")

elif active == "प्रतिज्ञापत्र":
    st.subheader("📝 सत्यता प्रतिज्ञापत्र (Affidavit)")
    with st.form("form_aff"):
        u_name = st.text_input("१. प्रतिज्ञापत्र लिहून देणाऱ्याचे नाव:")
        u_age = st.text_input("२. वय व व्यवसाय:")
        u_addr = st.text_area("३. राहण्याचा पूर्ण पत्ता:")
        aff_reason = st.text_input("४. प्रतिज्ञापत्राचा उद्देश:")
        aff_statements = st.text_area("५. प्रतिज्ञापूर्वक कथन करावयाचे मुद्दे:")
        if st.form_submit_button("🚀 प्रतिज्ञापत्र मसुदा तयार करा"):
            st.session_state.final_draft = f"।। सत्यता प्रतिज्ञापत्र ।।\n\nमी, {u_name}, वय: {u_age}, रा. {u_addr} येथे प्रतिज्ञापूर्वक लिहून देतो/देते की -\n\n१. उद्देश: {aff_reason}\n२. वस्तुस्थिती:\n{aff_statements}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ प्रतिज्ञापत्र मसुदा तयार झाला!")

elif active == "ग्राहक मंच":
    st.subheader("🛒 ग्राहक तक्रार निवारण अर्ज (Consumer Forum)")
    with st.form("form_cons"):
        u_name = st.text_input("१. तक्रारदार ग्राहकाचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व मोबाइल:")
        seller_name = st.text_input("३. विक्रेता / कंपनीचे नाव:")
        prod_details = st.text_input("४. खरेदी केलेल्या वस्तू/सेवेचा तपशील:")
        issue_body = st.text_area("५. फसवणूक / सदोष सेवेचा तपशील:")
        comp_amt = st.text_input("६. मागितलेली नुकसानभरपाई रक्कम (₹):", value="५०,०००/-")
        if st.form_submit_button("🚀 ग्राहक तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"मा. जिल्हा ग्राहक तक्रार निवारण आयोग\n\nतक्रारदार: {u_name}\nपत्ता: {u_addr}\n\nविरुद्ध\n\nप्रतिवादी: {seller_name}\n\n१. खरेदी तपशील: {prod_details}\n२. तक्रार कारण: {issue_body}\n३. मागितलेली भरपाई: ₹{comp_amt}\n\nदिनांक: {date_today}\nस्वाक्षरी: ({u_name})"
            st.success("✅ ग्राहक तक्रार अर्ज तयार झाला!")

# ==============================================================================
# ७. मसुदा निकाल, डाऊनलोड व WhatsApp शेअरिंग
# ==============================================================================
if st.session_state.final_draft and active != "AI चॅट":
    st.markdown("---")
    st.text_area("तयार झालेला अधिकृत मसुदा:", value=st.session_state.final_draft, height=200)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 डाऊनलोड (.txt)", st.session_state.final_draft, "Legal_Draft.txt", use_container_width=True)
    with c2:
        msg_enc = urllib.parse.quote(st.session_state.final_draft)
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={msg_enc}" target="_blank"><button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px;">📲 WhatsApp वर पाठवा</button></a>', unsafe_allow_html=True)
