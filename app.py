import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि कायमस्वरूपी सेव्ह ग्रिड डिझाइन (CSS)
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

/* चॅट UI */
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
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ नमस्कार! कायदेशीर सल्ला विचारा किंवा ➕ बटणाने फोटो जोडा.", "image": None}
    ]

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. 404 त्रुटीमुक्त ऑटो-डिटेक्ट AI इंजिन
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def ask_ai_dynamic(prompt_text, image_obj=None):
    if not active_api_key:
        return "कृपया Streamlit Settings -> Secrets मध्ये GEMINI_API_KEY तपासा."
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
# ६. प्रत्येक कायदेशीर विभागासाठी स्वतंत्र आणि अचूक फॉर्म्स
# ==============================================================================
active = st.session_state.active_tab

# --- विभाग १: जोडपत्र 'अ' ---
if active == "जोडपत्र 'अ'":
    st.subheader("📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))")
    with st.form("form_a"):
        u_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व फोन:")
        dept = st.text_input("३. सार्वजनिक प्राधिकरण / कार्यालयाचे नाव:")
        q_info = st.text_area("४. मागितलेल्या माहितीचा तपशील (मुद्देसूद):")
        q_period = st.text_input("५. माहितीचा संबंधित कालावधी (उदा. २०२३ ते २०२६):", value="चालू वर्ष")
        
        if st.form_submit_button("🚀 जोडपत्र 'अ' तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'अ'
(नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.

प्रति,
जन माहिती अधिकारी,
कार्यालय: {dept}

१. अर्जदाराचे नाव: {u_name}
२. पत्ता व मोबाइल: {u_addr}
३. मागितलेल्या माहितीचा तपशील:
{q_info}
४. माहितीचा कालावधी: {q_period}
५. माहितीचा प्रकार: प्रमाणित सत्यप्रती टपालाने मिळाव्यात.
६. अर्ज फी: ₹१०/- चा कोर्ट फी स्टॅम्प चिकटवला आहे.

दिनांक: {date_today}
स्थळ: -

अर्जदाराची स्वाक्षरी:
({u_name})"""
            st.success("✅ जोडपत्र 'अ' मसुदा तयार झाला!")

# --- विभाग २: प्रथम अपील (जोडपत्र 'ब') ---
elif active == "जोडपत्र 'ब'":
    st.subheader("⚖️ प्रथम अपील (कलम १९(१)) - जोडपत्र 'ब'")
    with st.form("form_b"):
        u_name = st.text_input("१. अपीलकर्त्याचे पूर्ण नाव:")
        u_addr = st.text_area("२. पत्ता व मोबाइल:")
        dept = st.text_input("३. प्रथम अपीलीय अधिकारी व कार्यालय:")
        pio_details = st.text_input("४. संबंधित जन माहिती अधिकाऱ्याचा तपशील:")
        appeal_reason = st.text_area("५. अपीलाचे कारण (माहिती न मिळणे / चुकीची माहिती):", value="विहित ३० दिवसांत माहिती न मिळाल्यामुळे.")
        
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'ब'
(नियम ५(१) पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.

प्रति,
प्रथम अपीलीय अधिकारी,
कार्यालय: {dept}

१. अपीलकर्त्याचे नाव: {u_name}
२. पत्ता: {u_addr}
३. संबंधित जन माहिती अधिकारी: {pio_details}
४. अपीलाचे कारण:
{appeal_reason}
५. प्रार्थना: जन माहिती अधिकाऱ्यास विनामूल्य व तात्काळ माहिती देण्याचे आदेश व्हावेत.

दिनांक: {date_today}
अपीलकर्त्याची स्वाक्षरी: ({u_name})"""
            st.success("✅ प्रथम अपील मसुदा तयार झाला!")

# --- विभाग ३: माहिती आयोग (जोडपत्र 'क') ---
elif active == "जोडपत्र 'क'":
    st.subheader("🏛️ राज्य माहिती आयोग - द्वितीय अपील (कलम १९(३))")
    with st.form("form_c"):
        u_name = st.text_input("१. अपीलकर्त्याचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता:")
        bench = st.text_input("३. माहिती आयोग खंडपीठ (उदा. छत्रपती संभाजीनगर):", value="छत्रपती संभाजीनगर")
        resp_dept = st.text_input("४. प्रतिवादी विभाग / कार्यालय:")
        facts = st.text_area("५. वस्तुस्थिती व अपीलाचा आधार:")
        
        if st.form_submit_button("🚀 द्वितीय अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'क'
(नियम ६ पहा)
राज्य माहिती आयोगाकडे करावयाचे द्वितीय अपील (कलम १९(३)).

प्रति,
मा. राज्य माहिती आयुक्त,
राज्य माहिती आयोग खंडपीठ, {bench}

१. अपीलकर्ता: {u_name}
२. पत्ता: {u_addr}
३. प्रतिवादी: जन माहिती अधिकारी व प्रथम अपीलीय अधिकारी, {resp_dept}
४. वस्तुस्थिती:
{facts}
५. प्रार्थना: 
अ) माहिती विनामूल्य मिळवून देण्यात यावी.
ब) कलम २० नुसार कसूरदार अधिकाऱ्यावर दंडात्मक कारवाई व्हावी.

दिनांक: {date_today}
स्वाक्षरी: ({u_name})"""
            st.success("✅ द्वितीय अपील मसुदा तयार झाला!")

# --- विभाग ४: AI चॅट व फोटो सल्ला ---
elif active == "AI चॅट":
    st.subheader("✨ AI कायदेशीर सल्लागार")
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 <b>तुम्ही:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"): st.image(msg["image"], width=180)
        else:
            st.markdown(f'<div class="chat-ai">✨ <b>AI:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    up_img = st.file_uploader("➕ फोटो / नोटीस जोडा (पर्यायी):", type=["png", "jpg", "jpeg"])
    
    if q := st.chat_input("येथे प्रश्न विचारा..."):
        img = Image.open(up_img) if up_img else None
        st.session_state.chat_messages.append({"role": "user", "content": q, "image": img})
        with st.spinner("AI विचार करत आहे..."):
            ans = ask_ai_dynamic(q, img)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans, "image": None})
        st.rerun()

# --- विभाग ५: न्यायालयीन याचिका ---
elif active == "न्यायालयीन मसुदा":
    st.subheader("📜 न्यायालयीन याचिका / दाद मसुदा")
    with st.form("form_court"):
        u_name = st.text_input("१. याचिकाकर्ता / वादी नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता:")
        opp_name = st.text_input("३. विरोधी पक्षकार / प्रतिवादी:")
        court_name = st.text_input("४. सक्षम न्यायालय / लवाद:", value="मा. दिवाणी / उच्च न्यायालय")
        case_cause = st.text_area("५. वादाचे कायदेशीर कारण व नुकसान:")
        court_prayer = st.text_area("६. मागितलेला न्याय / अंतरिम दिलासा:")
        
        if st.form_submit_button("🚀 कोर्ट याचिका मसुदा तयार करा"):
            st.session_state.final_draft = f"""{court_name} येथे

याचिका क्रमांक: ______ / {datetime.now().year}

{u_name}
रा. {u_addr}
... याचिकाकर्ता / वादी

विरुद्ध

{opp_name}
... प्रतिवादी

विषय: कायदेशीर दाद व नुकसानभरपाई मिळणेबाबत.

१. वस्तुस्थिती व वादाचे कारण:
{case_cause}

२. प्रार्थना:
{court_prayer}

दिनांक: {date_today}
याचिकाकर्ता स्वाक्षरी: ({u_name})"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# --- विभाग ६: शासकीय तक्रार ---
elif active == "शासकीय तक्रार":
    st.subheader("📢 शासकीय व प्रशासकीय तक्रार अर्ज")
    with st.form("form_gov"):
        u_name = st.text_input("१. तक्रारदाराचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व संपर्क:")
        gov_off = st.text_input("३. तक्रार कोणाकडे करायची आहे (अधिकारी / कार्यालय):")
        comp_sub = st.text_input("४. तक्रारीचा विषय:")
        comp_facts = st.text_area("५. गैरप्रकार / तक्रारीचा सविस्तर तपशील:")
        
        if st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"""प्रति,
मा. {gov_off},

विषय: {comp_sub}

तक्रारदार: {u_name}
पत्ता: {u_addr}

महोदय,
मी खालीलप्रमाणे तक्रार नोंदवत आहे:
{comp_facts}

तरी वरील प्रकरणाची सखोल व निष्पक्ष चौकशी करून संबंधित दोषींवर त्वरित प्रशासकीय कारवाई करण्यात यावी ही नम्र विनंती.

दिनांक: {date_today}
आपला नम्र,
स्वाक्षरी: ({u_name})"""
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला!")

# --- विभाग ७: प्रतिज्ञापत्र ---
elif active == "प्रतिज्ञापत्र":
    st.subheader("📝 सत्यता प्रतिज्ञापत्र (Affidavit)")
    with st.form("form_aff"):
        u_name = st.text_input("१. प्रतिज्ञापत्र लिहून देणाऱ्याचे नाव:")
        u_age = st.text_input("२. वय व व्यवसाय:")
        u_addr = st.text_area("३. राहण्याचा पूर्ण पत्ता:")
        aff_reason = st.text_input("४. प्रतिज्ञापत्राचा उद्देश (उदा. शिधापत्रिका, वारस नोंद, योजना):")
        aff_statements = st.text_area("५. प्रतिज्ञापूर्वक कथन करावयाचे मुद्दे:")
        
        if st.form_submit_button("🚀 प्रतिज्ञापत्र मसुदा तयार करा"):
            st.session_state.final_draft = f"""।। सत्यता प्रतिज्ञापत्र ।।

मी, {u_name}, वय: {u_age}, राहणार: {u_addr} येथे प्रतिज्ञापूर्वक लिहून देतो/देते की -

१. हे की, सदर प्रतिज्ञापत्र मी {aff_reason} कामी सादर करत आहे.
२. हे की, खालील बाबी सत्य आहेत:
{aff_statements}
३. वरील सर्व माहिती माझ्या समजुतीनुसार खरी व बिनचूक असून यात काहीही खोटे आढळल्यास मी कायद्यानुसार शिक्षेस पात्र राहीन.

दिनांक: {date_today}
स्थळ: -

प्रतिज्ञापत्र लिहून देणार:
स्वाक्षरी: ({u_name})"""
            st.success("✅ प्रतिज्ञापत्र मसुदा तयार झाला!")

# --- विभाग ८: ग्राहक मंच ---
elif active == "ग्राहक मंच":
    st.subheader("🛒 ग्राहक तक्रार निवारण अर्ज (Consumer Forum)")
    with st.form("form_cons"):
        u_name = st.text_input("१. तक्रारदार ग्राहकाचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व मोबाइल:")
        seller_name = st.text_input("३. विक्रेता / कंपनी / सर्व्हिस प्रोव्हाइडरचे नाव:")
        prod_details = st.text_input("४. खरेदी केलेल्या वस्तू/सेवेचा तपशील (बिल नंबरसह):")
        issue_body = st.text_area("५. फसवणूक / सदोष सेवेचा तपशील:")
        comp_amt = st.text_input("६. मागितलेली नुकसानभरपाई रक्कम (₹):", value="५०,०००/-")
        
        if st.form_submit_button("🚀 ग्राहक तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"""मा. जिल्हा ग्राहक तक्रार निवारण आयोग

तक्रारदार: {u_name}
पत्ता: {u_addr}

विरुद्ध

प्रतिवादी: {seller_name}

विषय: ग्राहक संरक्षण कायद्यांतर्गत सदोष सेवा व फसवणुकीबाबत तक्रार.

१. वस्तू/सेवेचा तपशील: {prod_details}
२. तक्रारीचे कारण:
{issue_body}
३. प्रार्थना: सदरील रक्कम सव्याज परत मिळावी व मानसिक त्रासापोटी नुकसानभरपाई म्हणून ₹{comp_amt} मंजूर व्हावे.

दिनांक: {date_today}
तक्रारदाराची स्वाक्षरी: ({u_name})"""
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
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={msg_enc}" target="_blank"><button style="width:100%; height:38px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">📲 WhatsApp वर पाठवा</button></a>', unsafe_allow_html=True)
