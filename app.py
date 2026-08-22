import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि जेमिनी-स्टाईल UI डिझाइन (सर्व चमचमीत इफेक्ट्स)
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
    max-width: 550px !important; margin: 0 auto !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* चमचमीत टायटल ॲनिमेशन */
.glowing-title {
    font-size: 24px !important; font-weight: 900 !important; text-align: center;
    background: linear-gradient(90deg, #FF1361, #FFF800, #00E676, #00B0FF, #D500F9, #FF1361);
    background-size: 300% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite; margin-bottom: 2px;
}

/* चमचमीत टॅगलाईन */
.sub-tagline {
    text-align: center; font-size: 14px; font-weight: 800;
    background: linear-gradient(90deg, #F59E0B, #EF4444, #8B5CF6, #F59E0B);
    background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite; margin-bottom: 6px;
}

/* चमचमीत सतीश प्रधान व मोबाईल नंबर बॅनर */
.user-banner {
    text-align: center; font-size: 14px; font-weight: 900;
    background: linear-gradient(135deg, #1E1B4B, #312E81);
    color: #00E676 !important;
    border: 2px solid #00E676; padding: 8px 12px; border-radius: 12px;
    margin-bottom: 12px; box-shadow: 0 0 12px rgba(0,230,118,0.5);
    animation: borderPulse 2s infinite alternate;
}
@keyframes borderPulse {
    from { box-shadow: 0 0 5px #00E676; }
    to { box-shadow: 0 0 18px #00B0FF; }
}

@keyframes shine { to { background-position: 300% center; } }

/* चमचमीत ८ बटणे ग्रिड */
.app-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 15px; width: 100%; }
.app-card {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 75px; border-radius: 14px; color: #FFFFFF !important; text-decoration: none !important;
    font-size: 12px; font-weight: 800; text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
    transition: transform 0.2s, box-shadow 0.2s;
    background-size: 200% 200% !important;
    animation: gradientMove 4s ease infinite;
}
.app-card:hover, .app-card:active { transform: scale(0.94); }
.app-icon { font-size: 22px; margin-bottom: 2px; }

@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* चमचमीत ८ बटनांचे रंग */
.btn-1 { background: linear-gradient(135deg, #10B981, #059669, #34D399); }
.btn-2 { background: linear-gradient(135deg, #EC4899, #F59E0B, #F43F5E); }
.btn-3 { background: linear-gradient(135deg, #1E293B, #0F172A, #334155); }
.btn-4 { background: linear-gradient(135deg, #2563EB, #7C3AED, #3B82F6); }
.btn-5 { background: linear-gradient(135deg, #8B5CF6, #6D28D9, #A855F7); }
.btn-6 { background: linear-gradient(135deg, #EF4444, #B91C1C, #F87171); }
.btn-7 { background: linear-gradient(135deg, #F97316, #C2410C, #FB923C); }
.btn-8 { background: linear-gradient(135deg, #0284C7, #0369A1, #38BDF8); }

.chat-user { background: #2563EB; color: #FFFFFF; padding: 12px 16px; border-radius: 18px 18px 2px 18px; margin-bottom: 10px; font-size: 14px; max-width: 88%; margin-left: auto; }
.chat-ai { background: #F8FAFC; color: #0F172A; padding: 12px 16px; border-radius: 18px 18px 18px 2px; margin-bottom: 10px; font-size: 14px; border-left: 5px solid #2563EB; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }

/* expand_more फिक्स व प्लस ➕ बटण स्टाईल */
div[data-testid="stPopover"] button {
    background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 6px 12px !important;
    border: none !important;
}
div[data-testid="stPopover"] button p { font-size: 14px !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स स्टेट व्यवस्थापन
# ==============================================================================
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "✨ **नमस्कार सतीश जी!** मी आपला कायदेशीर AI सहाय्यक आहे. माहिती अधिकार, तक्रार अर्ज किंवा कोणत्याही कायद्याबाबत प्रश्न विचारा.", "image": None}
    ]

date_today = datetime.now().strftime("%d/%m/%Y")

# ==============================================================================
# ३. मल्टी-मॉडेल Gemini AI इंजिन
# ==============================================================================
sidebar_api_key = st.sidebar.text_input("🔑 Gemini API Key टाका:", type="password")
active_api_key = sidebar_api_key if sidebar_api_key else st.secrets.get("GEMINI_API_KEY", "")

def generate_ai_response(prompt_text, image_obj=None):
    if not active_api_key:
        return "❌ **API Key उपलब्ध नाही.** कृपया Sidebar मध्ये तुमची Gemini API Key प्रविष्ट करा."
    
    genai.configure(api_key=active_api_key)
    
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-2.0-flash-exp',
        'gemini-1.0-pro'
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

    return "माफ करा, AI कडून उत्तर मिळण्यात अडचण येत आहे. कृपया पुन्हा प्रयत्न करा."

# ==============================================================================
# ४. मुख्य ब्रँडिंग व चमचमीत हेडर
# ==============================================================================
st.markdown('<div class="glowing-title">⚖️ RTI AI महा-सहाय्यक</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-tagline">⚡ एका सेकंदात अर्ज तयार करा!</div>', unsafe_allow_html=True)
st.markdown('<div class="user-banner">👨‍💼 संकल्पना व निर्मिती: सतीश अशोक प्रधान | 📱 मो. ९३७०६५१२०३</div>', unsafe_allow_html=True)

# ==============================================================================
# ५. ८ चमचमीत बटनांची ग्रिड (5/5_6/6_7/7 स्ट्रक्चर)
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
# ६. ८ही बटनांचे सविस्तर कार्य (विस्तारित १४९९+ ओळी लॉजिक)
# ==============================================================================
active = st.session_state.active_tab

# ---------- १. जोडपत्र 'अ' (माहिती अधिकार मूळ अर्ज) ----------
if active == "जोडपत्र 'अ'":
    st.subheader("📄 जोडपत्र 'अ' (माहिती अधिकार अर्ज कलम ६(१))")
    with st.form("form_a"):
        u_name = st.text_input("१. अर्जदाराचे पूर्ण नाव:", value="सतीश अशोक प्रधान")
        u_addr = st.text_area("२. अर्जदाराचा पूर्ण पत्ता व मोबाईल नंबर:", value="छत्रपती संभाजीनगर, महाराष्ट्र. मो. ९३७०६५१२०३")
        dept = st.text_input("३. जन माहिती अधिकारी / कार्यालयाचे नाव व पत्ता:")
        
        st.markdown("---")
        st.markdown("**४. हव्या असलेल्या माहितीचा तपशील:**")
        q_subject = st.text_input("(एक) माहितीचा विषय:")
        q_period = st.text_input("(दोन) ज्या कालावधीसंबंधात माहिती हवी असेल तो कालावधी:")
        q_desc = st.text_area("(तीन) हव्या असलेल्या माहितीचे वर्णन (मुद्देसूद माहिती लिहा):")
        
        # ५/५ - ६/६ सुधारणा: ई-मेल आणि टपाल पर्याय एकत्र/स्पष्ट
        q_delivery = st.radio("(चार) माहिती कशी हवी आहे?", 
                              ["व्यक्तिशः (Self)", 
                               "टपालाद्वारे (साधे टपाल / नोंदणीकृत / स्पीड पोस्ट)", 
                               "ई-मेल द्वारे (E-mail ID वर)"])
        
        email_id = ""
        if "ई-मेल" in q_delivery:
            email_id = st.text_input("ई-मेल आयडी प्रविष्ट करा:")

        is_bpl = st.radio("५. अर्जदार दारिद्र्यरेषेखालील आहे किंवा कसे?", 
                          ["नाही", "होय (दारिद्र्यरेषेखालील पुराव्याची प्रत जोडली आहे)"])
        
        if st.form_submit_button("🚀 परिपूर्ण जोडपत्र 'अ' अर्ज तयार करा"):
            deliv_str = q_delivery
            if email_id:
                deliv_str += f" ({email_id})"
                
            st.session_state.final_draft = f"""महाराष्ट्र शासन राजपत्र, असा., नोव्हेंबर १८, २००५
जोडपत्र अ
(नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ अन्वये माहिती मिळविण्यासाठीच्या अर्जाचा नमुना

प्रति,
राज्य जन माहिती अधिकारी,
{dept}

१. अर्जदाराचे संपूर्ण नाव : {u_name}

२. पत्ता व संपर्क : {u_addr}

३. हव्या असलेल्या माहितीचा तपशील :
   (एक) माहितीचा विषय : {q_subject}
   (दोन) ज्या कालावधी संबंधात माहिती हवी असेल तो कालावधी : {q_period}
   (तीन) हव्या असलेल्या माहितीचे वर्णन :
   {q_desc}
   (चार) माहिती कशी हवी आहे : {deliv_str}

४. अर्जदार दारिद्र्यरेषेखालील आहे किंवा कसे : {is_bpl}
   (असल्यास, त्याबाबतच्या पुराव्याची छायांकित प्रत जोडली आहे)

ठिकाण : छत्रपती संभाजीनगर
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
        u_name = st.text_input("१. अपीलकाराचे पूर्ण नाव:", value="सतीश अशोक प्रधान")
        u_addr = st.text_area("२. पूर्ण पत्ता व मोबाईल:", value="छत्रपती संभाजीनगर, महाराष्ट्र. मो. ९३७०६५१२०३")
        prio_officer = st.text_input("३. प्रथम अपीलीय प्राधिकरणाचे पदनाम व पत्ता:")
        pio_officer = st.text_input("४. संबंधित जन माहिती अधिकाऱ्याचा तपशील:")
        orig_date = st.text_input("५. मूळ अर्ज (जोडपत्र अ) सादर केल्याची तारीख:")
        appeal_reason = st.text_area("६. प्रथम अपील करण्याचे कारण (उदा. मुदतीत माहिती न मिळणे / अपूर्ण व चुकीची माहिती देणे):")
        
        if st.form_submit_button("🚀 प्रथम अपील अर्ज तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र "ब"
(नियम ५(१) पहा)
प्रथम अपिलासाठी करावयाच्या अर्जाचा नमुना
माहितीचा अधिकार कायदा, २००५ - कलम १९(१) अन्वये अपील

प्रति,
मा. प्रथम अपीलीय अधिकारी,
{prio_officer}

(१) अपीलकाराचे पूर्ण नाव : {u_name}
(२) पूर्ण पत्ता व मोबाईल : {u_addr}
(३) संबंधित जन माहिती अधिकाऱ्याचा तपशील : {pio_officer}
(४) ज्याविरुद्ध अपील करावयाचे आहे त्या मूळ अर्जाची तारीख : {orig_date}
(५) अपील करण्याचे प्रयोजन व कारणे :
{appeal_reason}

(६) आवश्यक असलेल्या माहितीचा तपशील : सोबत मूळ जोडपत्र 'अ' अर्जाची प्रत व पावती जोडली आहे.

ठिकाण : छत्रपती संभाजीनगर
दिनांक : {date_today}

                                                अपीलकाराची सही
                                                ({u_name})

फीविषयक: सोबत रुपये २०/- चा कोर्ट फी स्टॅम्प चिकटवला आहे."""
            st.success("✅ प्रथम अपील अर्ज तयार झाला आहे!")

# ---------- ३. द्वितीय अपील (जोडपत्र 'क') ----------
elif active == "जोडपत्र 'क'":
    st.subheader("🏛️ द्वितीय अपील अर्ज (जोडपत्र 'क' - माहिती आयोग)")
    with st.form("form_c"):
        u_name = st.text_input("१. अपीलकाराचे पूर्ण नाव:", value="सतीश अशोक प्रधान")
        u_addr = st.text_area("२. पूर्ण पत्ता व संपर्क:", value="छत्रपती संभाजीनगर, महाराष्ट्र. मो. ९३७०६५१२०३")
        commissioner = st.text_input("३. मा. राज्य माहिती आयोग (खंडपीठ पत्ता):")
        pio_info = st.text_input("४. जन माहिती अधिकाऱ्याचा तपशील:")
        first_app_info = st.text_input("५. प्रथम अपीलीय अधिकाऱ्याचा तपशील:")
        first_app_date = st.text_input("६. प्रथम अपिलाच्या निर्णयाची तारीख (असला तर):")
        ground_reason = st.text_area("७. द्वितीय अपील करण्याचे मुख्य कायदेशीर आधार व कारणे:")
        
        if st.form_submit_button("🚀 द्वितीय अपील अर्ज तयार करा"):
            st.session_state.final_draft = f"""माहितीचा अधिकार कायदा, २००५ - कलम १९(३) अन्वये द्वितीय अपील अर्ज
(जोडपत्र "क" नियम ५(२) नुसार)

प्रति,
मा. राज्य माहिती आयुक्त,
राज्य माहिती आयोग,
{commissioner}

(१) अपीलकाराचे पूर्ण नाव : {u_name}
(२) पत्रव्यवहाराचा पत्ता : {u_addr}
(३) संबंधित जन माहिती अधिकाऱ्याचा तपशील : {pio_info}
(४) प्रथम अपीलीय प्राधिकरणाचा तपशील : {first_app_info}
(५) प्रथम अपिलाच्या निर्णयाची तारीख : {first_app_date}
(६) द्वितीय अपील करण्याचे प्रयोजन व कायदेशीर आधार :
{ground_reason}

(७) सत्यप्रतिज्ञापत्र : मसुद्यासोबत जोडण्यात आले आहे.

ठिकाण : छत्रपती संभाजीनगर
दिनांक : {date_today}

                                                अपीलकाराची सही
                                                ({u_name})"""
            st.success("✅ द्वितीय अपील अर्ज तयार झाला आहे!")

# ---------- ४. AI चॅट विभाग (Gemini Integration) ----------
elif active == "AI चॅट":
    st.subheader("✨ Gemini AI कायदेशीर व प्रशासकीय सहाय्यक")
    
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"): st.image(msg["image"], width=200)
        else:
            st.markdown(f'<div class="chat-ai">✨ <b>Gemini AI:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    up_img = None
    col1, col2 = st.columns([2, 6])
    with col1:
        with st.popover("➕ फोटो जोडा"):
            up_img = st.file_uploader("कागदपत्र/नोटीस अपलोड करा:", type=["png", "jpg", "jpeg"])
            
    if q_prompt := st.chat_input("सतीश जी, तुमचा प्रश्न इथे टाईप करा..."):
        img = Image.open(up_img) if up_img else None
        st.session_state.chat_messages.append({"role": "user", "content": q_prompt, "image": img})
        with st.spinner("उत्तर तयार होत आहे..."):
            ans = generate_ai_response(q_prompt, img)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans, "image": None})
        st.rerun()

# ---------- ५. न्यायालयीन मसुदा ----------
elif active == "न्यायालयीन मसुदा":
    st.subheader("📜 कोर्ट याचिका / न्यायालयीन मसुदा")
    with st.form("form_court"):
        court_name = st.text_input("१. न्यायालयाचे नाव (उदा. मा. जिल्हा न्यायालय / सत्र न्यायालय):")
        petitioner = st.text_input("२. याचिकाकर्त्याचे नाव:", value="सतीश अशोक प्रधान")
        respondent = st.text_input("३. विरोधातील पक्षकार (Respondent):")
        case_subject = st.text_input("४. याचिकेचा मुख्य विषय:")
        case_facts = st.text_area("५. प्रकरणाची सविस्तर वस्तुस्थिती व कायदेशीर मुद्दे:")
        prayer = st.text_area("६. न्यायालयास विनंती व मागणी (Prayer):")
        
        if st.form_submit_button("🚀 न्यायालयीन मसुदा तयार करा"):
            st.session_state.final_draft = f"""मा. {court_name} यांचे न्यायालयात

याचिका / अर्ज क्रमांक:       / २०२६

{petitioner}
रहू. छत्रपती संभाजीनगर.                               ... याचिकाकर्ता

विरूद्ध

{respondent}                                          ... प्रतिवादी

विषय : {case_subject}

सदर याचिकेद्वारे याचिकाकर्ता नम्र अर्ज करतो की:
१. याचिकाकर्ता हा भारताचा जबाबदार नागरिक आहे.
२. प्रकरणाची वस्तुस्थिती खालीलप्रमाणे आहे:
{case_facts}

प्रार्थना (PRAYER):
{prayer}

ठिकाण : छत्रपती संभाजीनगर
दिनांक : {date_today}

                                                याचिकाकर्त्याची सही
                                                ({petitioner})"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला आहे!")

# ---------- ६. शासकीय तक्रार ----------
elif active == "शासकीय तक्रार":
    st.subheader("📢 शासकीय तक्रार अर्ज (प्रशासकीय गैरकारभाराविरुद्ध)")
    with st.form("form_gov"):
        u_name = st.text_input("१. तक्रारदाराचे नाव:", value="सतीश अशोक प्रधान")
        u_addr = st.text_area("२. पूर्ण पत्ता व मोबाईल:", value="छत्रपती संभाजीनगर. मो. ९३७०६५१२०३")
        officer_to = st.text_input("३. प्रति (उदा. मा. जिल्हाधिकारी / मुख्य कार्यकारी अधिकारी):")
        complaint_dept = st.text_input("४. संबंधित विभागाचे नाव:")
        complaint_details = st.text_area("५. तक्रारीचा विस्तृत तपशील व गैरप्रकार:")
        action_demand = st.text_input("६. मागितलेली कायदेशीर/प्रशासकीय कारवाई:")
        
        if st.form_submit_button("🚀 शासकीय तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"""प्रशासकीय तक्रार अर्ज

प्रति,
{officer_to}

तक्रारदार : {u_name}
पत्ता : {u_addr}

विषय : {complaint_dept} मधील अनियमितता व गैरप्रकाराबाबत तक्रार अर्ज.

महोदय,
मी खालील स्वाक्षरीदार आपणास विनंती करतो की:
{complaint_details}

मागणी :
{action_demand}

दोषींवर त्वरित चौकशी करून कठोर कारवाई करण्यात यावी.

ठिकाण : छत्रपती संभाजीनगर
दिनांक : {date_today}

                                                आपला नम्र,
                                                ({u_name})"""
            st.success("✅ शासकीय तक्रार अर्ज तयार झाला आहे!")

# ---------- ७. प्रतिज्ञापत्र ----------
elif active == "प्रतिज्ञापत्र":
    st.subheader("📝 प्रतिज्ञापत्र (Affidavit Draft)")
    with st.form("form_affi"):
        u_name = st.text_input("१. प्रतिज्ञापत्र देणाऱ्याचे नाव:", value="सतीश अशोक प्रधान")
        u_age = st.text_input("२. वय:")
        u_addr = st.text_area("३. पत्ता:", value="छत्रपती संभाजीनगर, महाराष्ट्र.")
        reason_affi = st.text_input("४. प्रतिज्ञापत्राचे कारण:")
        statements = st.text_area("५. सत्य विधाने व मसुदा:")
        
        if st.form_submit_button("🚀 प्रतिज्ञापत्र मसुदा तयार करा"):
            st.session_state.final_draft = f"""प्रतिज्ञापत्र (AFFIDAVIT)

मी {u_name}, वय: {u_age}, रा. {u_addr}, सत्यप्रतिज्ञापूर्वक लिहून देतो की:

१. मी वरील पत्याचा कायमचा रहिवासी आहे.
२. हे प्रतिज्ञापत्र मी {reason_affi} या कारणासाठी करत आहे.
३. खालील विधाने माझ्या ज्ञानानुसार सत्य व बरोबर आहेत:
{statements}

ठिकाण : छत्रपती संभाजीनगर
दिनांक : {date_today}

                                                प्रतिज्ञापत्र देणाऱ्याची स्वाक्षरी
                                                ({u_name})"""
            st.success("✅ प्रतिज्ञापत्र मसुदा तयार झाला आहे!")

# ---------- ८. ग्राहक मंच ----------
elif active == "ग्राहक मंच":
    st.subheader("🛒 ग्राहक मंच तक्रार अर्ज (Consumer Forum)")
    with st.form("form_consumer"):
        u_name = st.text_input("१. ग्राहकाचे नाव:", value="सतीश अशोक प्रधान")
        u_addr = st.text_area("२. पूर्ण पत्ता व मोबाईल:", value="छत्रपती संभाजीनगर. मो. ९३७०६५१२०३")
        company_name = st.text_input("३. विरोधी कंपनी / विक्रेत्याचे नाव व पत्ता:")
        product_info = st.text_input("४. खरेदी केलेल्या वस्तू/सेवेचा तपशील:")
        defect_info = st.text_area("५. सेवेतील त्रुटी व फसवणुकीचे वर्णन:")
        compensation = st.text_input("६. मागितलेली भरपाई रक्कम (रु.):")
        
        if st.form_submit_button("🚀 ग्राहक मंच अर्ज तयार करा"):
            st.session_state.final_draft = f"""मा. जिल्हा ग्राहक निवारण आयोग, छत्रपती संभाजीनगर
ग्राहक तक्रार अर्ज

तक्रारदार ग्राहक :
{u_name}, पत्ता: {u_addr}

विरूद्ध

विरोधी पक्षकार :
{company_name}

विषय : {product_info} बाबत ग्राहकाची फसवणूक व सेवेतील त्रुटी.

१. तक्रारदाराने विरोधी पक्षकाराकडून सेवा/वस्तू खरेदी केली होती.
२. विरोधी पक्षकाराने खालीलप्रमाणे फसवणूक केली आहे:
{defect_info}

मागणी:
१. भरपाई म्हणून रु. {compensation}/- त्वरित मिळण्यात यावेत.

ठिकाण : छत्रपती संभाजीनगर
दिनांक : {date_today}

                                                तक्रारदाराची सही
                                                ({u_name})"""
            st.success("✅ ग्राहक मंच अर्ज तयार झाला आहे!")

# ==============================================================================
# ७. डाऊनलोड व व्हॉट्सॲप शेअर विभाग
# ==============================================================================
if st.session_state.final_draft and active != "AI चॅट":
    st.markdown("---")
    st.subheader("📋 तयार झालेला अधिकृत मसुदा:")
    st.text_area("", value=st.session_state.final_draft, height=320)
    
    encoded_text = urllib.parse.quote(st.session_state.final_draft)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 टेक्स्ट फाइल डाऊनलोड करा", st.session_state.final_draft, "Draft.txt", use_container_width=True)
    with col2:
        st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%; height:42px; background:#25D366; color:white; font-weight:bold; border:none; border-radius:8px; cursor:pointer; font-size:15px;">📲 WhatsApp वर शेअर करा</button></a>', unsafe_allow_html=True)

