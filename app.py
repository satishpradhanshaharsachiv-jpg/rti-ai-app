import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि जेमिनी-स्टाईल UI डिझाइन
# ==============================================================================
st.set_page_config(page_title="RTI AI महा-सहाय्यक", page_icon="⚖️", layout="centered")

# URL मधील टॅब पॅरामीटर तपासणे
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
    max-width: 500px !important; margin: 0 auto !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

.glowing-title {
    font-size: 22px !important; font-weight: 900 !important; text-align: center;
    background: linear-gradient(90deg, #FF1361, #FFF800, #00E676, #00B0FF, #D500F9);
    background-size: 300% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite; margin-bottom: 2px;
}
@keyframes shine { to { background-position: 300% center; } }

.sub-tagline {
    text-align: center; font-size: 13px; font-weight: 700; color: #D97706; margin-bottom: 6px;
}

.user-banner {
    text-align: center; font-size: 13px; font-weight: 800; color: #1E3A8A;
    background: #E0F2FE; border: 1px solid #38BDF8; padding: 5px 10px; border-radius: 8px; margin-bottom: 12px;
}

.app-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 12px; width: 100%; }
.app-card {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 72px; border-radius: 12px; color: #FFFFFF !important; text-decoration: none !important;
    font-size: 11px; font-weight: 800; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.18);
    transition: transform 0.2s;
}
.app-card:active { transform: scale(0.92); }
.app-icon { font-size: 20px; margin-bottom: 2px; }

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

/* Popover 'expand_more' एरर पूर्ण फिक्स आणि जेमिनी ➕ बटण */
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
# ४. मुख्य हेडर व ब्रँडिंग
# ==============================================================================
st.markdown('<div class="glowing-title">⚖️ RTI AI महा-सहाय्यक</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-tagline">⚡ एका सेकंदात कायदेशीर अर्ज तयार करा!</div>', unsafe_allow_html=True)
st.markdown('<div class="user-banner">👨‍💼 संकल्पना व निर्मिती: सतीश अशोक प्रधान</div>', unsafe_allow_html=True)

# ==============================================================================
# ५. ८ बटणांची ग्रिड (URL Query Params वर आधारित)
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
# ६. ८ही बटनांनुसार फॉर्म व कार्यप्रणाली
# ==============================================================================
active = st.session_state.active_tab

# ---------- १. जोडपत्र 'अ' (माहिती अधिकार मूळ अर्ज) ----------
if active == "जोडपत्र 'अ'":
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

# ---------- २. प्रथम अपील (जोडपत्र 'ब') ----------
elif active == "जोडपत्र 'ब'":
    st.subheader("⚖️ प्रथम अपील अर्ज (जोडपत्र 'ब' - नियम ५(१))")
    with st.form("form_b"):
        u_name = st.text_input("१. अपीलकाराचे पूर्ण नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व संपर्क क्रमांक:")
        prio_officer = st.text_input("३. प्रथम अपीलीय प्राधिकरणाचे पदनाम व पत्ता:")
        pio_officer = st.text_input("४. संबंधित जन माहिती अधिकाऱ्याचा तपशील:")
        orig_date = st.text_input("५. मूळ अर्ज (जोडपत्र अ) सादर केल्याची तारीख:")
        appeal_reason = st.text_area("६. प्रथम अपील करण्याचे कारण (उदा. माहिती न मिळणे / चुकीची माहिती देणे):")
        
        if st.form_submit_button("🚀 प्रथम अपील अर्ज तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र "ब"
(नियम ५(१) पहा)
प्रथम अपिलासाठी करावयाच्या अर्जाचा नमुना
माहितीचा अधिकार कायदा, २००५ - कलम १९(१) अन्वये अपील

प्रति,
मा. प्रथम अपीलीय अधिकारी,
{prio_officer}

(१) अपीलकाराचे पूर्ण नाव : {u_name}
(२) पूर्ण पत्ता : {u_addr}
(३) संबंधित जन माहिती अधिकाऱ्याचा तपशील : {pio_officer}
(४) ज्याविरुद्ध अपील करावयाचे आहे त्या मूळ अर्जाची तारीख : {orig_date}
(५) अपील करण्याचे प्रयोजन :
{appeal_reason}

(६) आवश्यक असलेल्या माहितीचा तपशील : सोबत मूळ जोडपत्र 'अ' अर्जाची प्रत जोडली आहे.

ठिकाण : 
दिनांक : {date_today}

                                                अपीलकाराची सही
                                                ({u_name})

फीविषयक: सोबत रुपये २०/- चा कोर्ट फी स्टॅम्प चिकटवला आहे."""
            st.success("✅ प्रथम अपील अर्ज तयार झाला आहे!")

# ---------- ३. द्वितीय अपील (जोडपत्र 'क') ----------
elif active == "जोडपत्र 'क'":
    st.subheader("🏛️ द्वितीय अपील अर्ज (जोडपत्र 'क' - कलम १९(३))")
    with st.form("form_c"):
        u_name = st.text_input("१. अपीलकाराचे पूर्ण नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व ईमेल/मोबाईल:")
        commissioner = st.text_input("३. मा. माहिती आयुक्त / माहिती आयोगाचा पत्ता:")
        pio_info = st.text_input("४. जन माहिती अधिकाऱ्याचा तपशील:")
        first_app_info = st.text_input("५. प्रथम अपीलीय अधिकाऱ्याचा तपशील:")
        first_app_date = st.text_input("६. प्रथम अपिलाच्या निर्णयाची तारीख (असला तर):")
        ground_reason = st.text_area("७. दुसरे अपील करण्याचे प्रयोजन व स्पष्ट कारणे:")
        
        if st.form_submit_button("🚀 द्वितीय अपील अर्ज तयार करा"):
            st.session_state.final_draft = f"""माहितीचा अधिकार कायदा, २००५ - कलम १९ (३) अन्वये द्वितीय अपील अर्ज
(जोडपत्र "क" नियम ५(२) नुसार)

प्रेषक :
{u_name}
{u_addr}

प्रति,
मा. माहिती आयुक्त,
राज्य माहिती आयोग कार्यालय,
{commissioner}

(१) अपीलकाराचे पूर्ण नाव : {u_name}
(२) पत्रव्यवहाराचा पत्ता : {u_addr}
(३) संबंधित जन माहिती अधिकाऱ्याचा तपशील : {pio_info}
(४) प्रथम अपीलीय प्राधिकरणाचा तपशील : {first_app_info}
(५) प्रथम अपिलाच्या निर्णयाची तारीख : {first_app_date}
(६) दुसरे अपील करण्याचे प्रयोजन :
{ground_reason}

(७) आवश्यक असलेल्या माहितीचा तपशील : मूळ अर्ज जोडपत्र 'अ' व प्रथम अपील जोडपत्र 'ब' ची प्रत सोबत जोडली आहे.

ठिकाण : 
दिनांक : {date_today}

                                                अपीलकाराची सही
                                                ({u_name})

फीविषयक: सोबत रुपये २०/- रोखीने / कोर्ट फी स्टॅम्पद्वारे जोडले आहेत."""
            st.success("✅ द्वितीय अपील अर्ज तयार झाला आहे!")

# ---------- ४. AI चॅट विभाग ----------
elif active == "AI चॅट":
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

# ---------- ५. न्यायालयीन मसुदा ----------
elif active == "न्यायालयीन मसुदा":
    st.subheader("📜 कोर्ट याचिका / न्यायालयीन मसुदा")
    with st.form("form_court"):
        court_name = st.text_input("१. न्यायालयाचे नाव (उदा. मा. जिल्हा व सत्र न्यायालय / उच्च न्यायालय):")
        petitioner = st.text_input("२. याचिकाकर्त्याचे नाव:")
        respondent = st.text_input("३. विरोधातील पक्षकार (Respondent / Opponent):")
        case_subject = st.text_input("४. याचिकेचा विषय:")
        case_facts = st.text_area("५. मुख्य मुद्दे व वस्तुस्थिती:")
        prayer = st.text_area("६. न्यायालयास विनंती / मागणी (Prayer):")
        
        if st.form_submit_button("🚀 न्यायालयीन मसुदा तयार करा"):
            st.session_state.final_draft = f"""माहिती व न्याय मिळण्यासाठी न्यायालयासमोर याचिका मसुदा

मा. {court_name} यांचे न्यायालयात

याचिका क्रमांक:       / २०२६

{petitioner}
... याचिकाकर्ता / अर्जदार

विरूद्ध

{respondent}
... विरुद्ध अर्जदार / प्रतिवादी

विषय : {case_subject} बाबत.

सदर याचिकेद्वारे नम्र अर्ज देतो की,
१. याचिकाकर्ता हा भारतीय नागरिक असून न्याय मागणीसाठी सादर अर्ज करत आहे.
२. प्रकरणाची मुख्य वस्तुस्थिती खालीलप्रमाणे :
{case_facts}

प्रार्थना / विनंती (PRAYER):
{prayer}

ठिकाण : 
दिनांक : {date_today}

                                                याचिकाकर्त्याची सही
                                                ({petitioner})"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला आहे!")

# ---------- ६. शासकीय तक्रार ----------
elif active == "शासकीय तक्रार":
    st.subheader("📢 शासकीय तक्रार अर्ज (प्रशासकीय गैरकारभाराविरुद्ध)")
    with st.form("form_gov"):
        u_name = st.text_input("१. तक्रारदाराचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व संपर्क:")
        officer_to = st.text_input("३. प्रति (ज्या अधिकाऱ्याकडे तक्रार करायची आहे - उदा. मा. जिल्हाधिकारी):")
        complaint_dept = st.text_input("४. ज्या विभागाविरुद्ध तक्रार आहे त्या विभागाचे नाव:")
        complaint_details = st.text_area("५. तक्रारीचा विस्तृत तपशील व गैरप्रकार:")
        action_demand = st.text_input("६. कायदेशीर/प्रशासकीय कारवाईची मागणी:")
        
        if st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"""तक्रार अर्ज

प्रति,
{officer_to}

तक्रारदार : {u_name}, पत्ता : {u_addr}
विभागाचे नाव : {complaint_dept}

विषय : {complaint_dept} मधील गैरप्रकार व अनियमिततेबाबत कायदेशीर तक्रार अर्ज.

महोदय,
मी खालील स्वाक्षरीदार आपणास विनंती करतो की,
{complaint_details}

मागणी :
{action_demand}

तसेच दोषींवर त्वरित चौकशी करून कठोर कारवाई करण्यात यावी.

ठिकाण :
दिनांक : {date_today}

                                                आपला नम्र,
                                                ({u_name})"""
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला आहे!")

# ---------- ७. प्रतिज्ञापत्र ----------
elif active == "प्रतिज्ञापत्र":
    st.subheader("📝 प्रतिज्ञापत्र (Affidavit Draft)")
    with st.form("form_affi"):
        u_name = st.text_input("१. प्रतिज्ञापत्र करणाऱ्याचे पूर्ण नाव:")
        u_age = st.text_input("२. वय:")
        u_addr = st.text_area("३. पूर्ण पत्ता:")
        reason_affi = st.text_input("४. प्रतिज्ञापत्राचे कारण (उदा. शासकीय कामासाठी / नावातील बदलासाठी):")
        statements = st.text_area("५. मी प्रतिज्ञापूर्वक लिहून देतो की (मुद्दे):")
        
        if st.form_submit_button("🚀 प्रतिज्ञापत्र मसुदा तयार करा"):
            st.session_state.final_draft = f"""प्रतिज्ञापत्र (AFFIDAVIT)

मी {u_name}, वय वर्षे: {u_age}, राहणार: {u_addr}, सत्यप्रतिज्ञापूर्वक लिहून देतो की,

१. मी वरील पत्यावरील मूळ रहिवासी आहे.
२. हे प्रतिज्ञापत्र मी {reason_affi} या कारणासाठी सादर करत आहे.
३. मी खालीलप्रमाणे सत्य विधान करत आहे:
{statements}

४. वरील दिलेली सर्व माहिती माझ्या ज्ञानानुसार आणि समजुतीनुसार सत्य व बरोबर आहे. त्यात कोणतीही बाब लपवलेली नाही.

ठिकाण :
दिनांक : {date_today}

                                                प्रतिज्ञापत्र देणाऱ्याची स्वाक्षरी
                                                ({u_name})"""
            st.success("✅ प्रतिज्ञापत्र तयार झाले आहे!")

# ---------- ८. ग्राहक मंच ----------
elif active == "ग्राहक मंच":
    st.subheader("🛒 ग्राहक मंच तक्रार अर्ज (Consumer Forum)")
    with st.form("form_consumer"):
        u_name = st.text_input("१. तक्रारदार ग्राहकाचे नाव:")
        u_addr = st.text_area("२. पूर्ण पत्ता व मोबाईल:")
        company_name = st.text_input("३. विरोधी कंपनी / विक्रेत्याचे नाव व पत्ता:")
        product_info = st.text_input("४. खरेदी केलेल्या वस्तू/सेवेचा तपशील व रक्कम:")
        defect_info = st.text_area("५. सेवेतील त्रुटी / फसवणुकीचा तपशील:")
        compensation = st.text_input("६. मागितलेली भरपाई रक्कम (रु.):")
        
        if st.form_submit_button("🚀 ग्राहक मंच अर्ज तयार करा"):
            st.session_state.final_draft = f"""मा. जिल्हा ग्राहक निवारण आयोग यांच्याकडे
ग्राहक तक्रार अर्ज

तक्रारदार ग्राहक :
{u_name}
{u_addr}

विरूद्ध

विरोधी पक्षकार (कंपनी/विक्रेता) :
{company_name}

तक्रारीचा विषय : {product_info} बाबत ग्राहकाची झालेली फसवणूक व सेवेतील त्रुटी.

१. तक्रारदाराने विरोधी पक्षकाराकडून वस्तू/सेवा खरेदी केली होती.
२. विरोधी पक्षकाराने खालीलप्रमाणे फसवणूक / त्रुटी केली आहे :
{defect_info}

प्रार्थना / मागण्या :
१. तक्रारदारास मूळ रक्कम परत करण्यात यावी.
२. मानसिक त्रासापोटी व भरपाई म्हणून रु. {compensation}/- देण्याचे आदेश व्हावेत.

ठिकाण :
दिनांक : {date_today}

                                                तक्रारदाराची सही
                                                ({u_name})"""
            st.success("✅ ग्राहक मंच तक्रार अर्ज तयार झाला आहे!")

# ==============================================================================
# ७. डाऊनलोड व व्हॉट्सॲप शेअर विभाग
# ==============================================================================
if st.session_state.final_draft and active != "AI चॅट":
    st.markdown("---")
    st.subheader("📋 तयार झालेला अधिकृत मसुदा:")
    st.text_area("", value=st.session_state.final_draft, height=300)
    
    encoded_text = urllib.parse.quote(st.session_state.final_draft)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 टेक्स्ट फाइल डाऊनलोड करा", st.session_state.final_draft, "Official_Draft.txt", use_container_width=True)
    with col2:
        st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; height:42px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer; font-size:15px;">📲 WhatsApp वर शेअर करा</button></a>', unsafe_allow_html=True)
