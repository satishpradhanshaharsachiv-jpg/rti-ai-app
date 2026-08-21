import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
from PIL import Image
import os

# ==============================================================================
# १. पेज कॉन्फिगरेशन आणि डिझाइन
# ==============================================================================
st.set_page_config(page_title="RTI व कायदेशीर महा-सहाय्यक", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap');
* { font-family: 'Mukta', sans-serif !important; }

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

h1 { color: #1E3A8A; font-weight: 800; text-align: center; font-size: 20px; margin-bottom: 2px; }

/* शेअर मेनू स्टाईल */
.share-box {
    background: #F3F4F6;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 12px;
    text-align: center;
}
.share-btn {
    display: inline-block;
    padding: 6px 14px;
    margin: 4px;
    border-radius: 6px;
    color: white !important;
    text-decoration: none;
    font-size: 13px;
    font-weight: bold;
}
.btn-wa { background: #25D366; }
.btn-fb { background: #1877F2; }
.btn-tg { background: #0088CC; }
.btn-ms { background: #0084FF; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# २. सेशन्स मॅनेजमेंट
# ==============================================================================
if 'active_tab' not in st.session_state: st.session_state.active_tab = "जोडपत्र 'अ'"
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'original_query' not in st.session_state: st.session_state.original_query = ""
if 'final_draft' not in st.session_state: st.session_state.final_draft = ""
if 'show_share' not in st.session_state: st.session_state.show_share = False

# चॅट मेमरी
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "नमस्कार! मी तुमचा AI महा-सहाय्यक आहे. मला कायदा, शासकीय कामे किंवा जगातील कोणताही प्रश्न विचारा किंवा फोटो अपलोड करून माहिती मिळवा."}
    ]

APP_URL = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/?v=3"

# ==============================================================================
# ३. मल्टी-मॉडल AI कॉल (टेक्स्ट + फोटो + जागतिक ज्ञान)
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def get_ai_multimodal_response(prompt_text, image_data=None):
    if active_api_key:
        try:
            genai.configure(api_key=active_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            if image_data:
                res = model.generate_content([prompt_text, image_data])
            else:
                res = model.generate_content(prompt_text)
                
            if res and res.text:
                return res.text
        except Exception as e:
            return f"त्रुटी: {str(e)}"
    return "कृपया API Key तपासा."

# ==============================================================================
# ४. होम पेज हेडर, बॅनर व शेअर मेनू
# ==============================================================================
st.markdown("<h1>⚖️ RTI, तक्रार व कायदेशीर महा-सहाय्यक</h1>", unsafe_allow_html=True)

head_col1, head_col2 = st.columns([5, 1])
with head_col1:
    st.caption("नागरिकांसाठी सर्व कायदेशीर, प्रशासकीय व AI माहिती केंद्र")
with head_col2:
    if st.button("↗️ शेअर", key="main_share_btn", use_container_width=True):
        st.session_state.show_share = not st.session_state.show_share

if st.session_state.show_share:
    share_msg = urllib.parse.quote(f"⚖️ RTI, शासकीय तक्रार व ऑल-इन-वन AI सहाय्यक ॲप:\n{APP_URL}")
    st.markdown(f"""
    <div class="share-box">
        <p style="margin:0 0 6px 0; font-weight:bold; font-size:14px; color:#374151;">ॲप लिंक सोशल मीडियावर शेअर करा:</p>
        <a class="share-btn btn-wa" href="https://api.whatsapp.com/send?text={share_msg}" target="_blank">WhatsApp</a>
        <a class="share-btn btn-fb" href="https://www.facebook.com/sharer/sharer.php?u={APP_URL}" target="_blank">Facebook</a>
        <a class="share-btn btn-tg" href="https://t.me/share/url?url={APP_URL}&text={share_msg}" target="_blank">Telegram</a>
        <a class="share-btn btn-ms" href="fb-messenger://share/?link={APP_URL}" target="_blank">Messenger</a>
    </div>
    """, unsafe_allow_html=True)

if os.path.exists("banner.png"):
    st.image("banner.png", use_container_width=True)

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
    if st.button("🤖 AI चॅटबॉट", key="tab4", use_container_width=True): st.session_state.active_tab = "AI चॅटबॉट"
with b5:
    if st.button("🟣 कोर्ट याचिका", key="tab5", use_container_width=True): st.session_state.active_tab = "न्यायालयीन मसुदा"
with b6:
    if st.button("🔴 शासकीय तक्रार", key="tab6", use_container_width=True): st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# ६. विभाग (Forms & Full AI Chatbot)
# ==============================================================================
date_today = datetime.now().strftime("%d/%m/%Y")

# १. मूळ RTI
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.subheader("🟢 जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व मोबाईल क्र.:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मागितलेली माहिती:", value=st.session_state.original_query)
        if st.form_submit_button("🚀 अर्ज तयार करा"):
            prompt = f"महाराष्ट्र RTI कलम ६(१) जोडपत्र 'अ' अर्ज तयार करा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}."
            ai_out = get_ai_multimodal_response(prompt)
            st.session_state.final_draft = ai_out if "त्रुटी" not in ai_out else f"""जोडपत्र - 'अ'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अर्जदार: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. माहिती: {st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ अर्ज तयार झाला!")

# २. प्रथम अपील
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.subheader("🔵 जोडपत्र 'ब' - प्रथम अपील (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("अपिलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        reason = st.text_area("अपीलाचे कारण:", value="विहित ३० दिवसांत माहिती दिली नाही.")
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'ब'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अपिलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. कारण: {reason}\n४. मूळ माहिती: {st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ प्रथम अपील तयार झाले!")

# ३. द्वितीय अपील
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.subheader("🟠 जोडपत्र 'क' - द्वितीय अपील (राज्य माहिती आयोग)")
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / विभाग:", value=st.session_state.dept_name)
        if st.form_submit_button("🚀 द्वितीय अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'क'\nमाहिती अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपील.\n\nप्रति,\nमा. राज्य माहिती आयोग खंडपीठ,\n\n१. अपीलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. प्रतिवादी: जन माहिती अधिकारी, {st.session_state.dept_name}\n४. मूळ माहिती: {st.session_state.original_query}\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ द्वितीय अपील तयार झाले!")

# ४. 🤖 संपूर्ण AI चॅटबॉट (ChatGPT / Gemini सारखा + फोटो अपलोड)
elif st.session_state.active_tab == "AI चॅटबॉट":
    st.subheader("🤖 ऑल-इन-वन AI चॅटबॉट (वर्ल्ड नॉलेज + डॉक्युमेंट स्कॅनर)")
    st.caption("कायदेशीर सल्ला, सामान्य ज्ञान किंवा फोटो/कागदपत्र अपलोड करून प्रश्न विचारा:")

    # चॅट मेसेज डिस्प्ले
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # फोटो अपलोड पर्याय (+)
    uploaded_img = st.file_uploader("➕ फोटो / कागदपत्र जोडा (ऐच्छिक):", type=["png", "jpg", "jpeg"])
    
    # चॅट इनपुट बॉक्स
    if prompt := st.chat_input("येथे कोणताही प्रश्न विचारा (उदा. या कागदपत्रात काय लिहिले आहे? किंवा जगातील कोणताही प्रश्न)..."):
        # युझर मेसेज दाखवणे
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI कडून उत्तर मिळवणे
        with st.chat_message("assistant"):
            with st.spinner("AI विचार करत आहे..."):
                img = None
                if uploaded_img:
                    img = Image.open(uploaded_img)
                
                system_instruction = "तुम्ही एक शक्तिशाली आणि हुशार AI सहाय्यक आहात. युझरने विचारलेल्या कोणत्याही विषयावर (कायदा, विज्ञान, इतिहास, सामान्य ज्ञान किंवा कागदपत्र विश्लेषण) मराठीत सविस्तर, स्पष्ट आणि अचूक उत्तर द्या."
                full_prompt = f"{system_instruction}\n\nवापरकर्त्याचा प्रश्न: {prompt}"
                
                response_text = get_ai_multimodal_response(full_prompt, img)
                st.markdown(response_text)
                
                st.session_state.chat_messages.append({"role": "assistant", "content": response_text})

# ५. न्यायालयीन मसुदा
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.subheader("🟣 न्यायालयीन याचिका मसुदा")
    with st.form("form_court"):
        st.session_state.user_name = st.text_input("याचिकाकर्ता नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी नाव:", value=st.session_state.dept_name)
        court_subj = st.text_input("विषय:", value="प्रशासकीय दिरंगाई व नुकसानभरपाई बाबत")
        if st.form_submit_button("🚀 कोर्ट मसुदा तयार करा"):
            st.session_state.final_draft = f"""मा. सक्षम न्यायालय / लवाद\n\n{st.session_state.user_name}, रा. {st.session_state.user_address}\n... याचिकाकर्ता\nविरुद्ध\n{st.session_state.dept_name}\n... प्रतिवादी\n\nविषय: {court_subj}\n\n१. वस्तुस्थिती: {st.session_state.original_query}\n२. प्रार्थना: योग्य तो कायदेशीर न्याय मिळावा.\n\nदिनांक: {date_today}\nयाचिकाकर्ता: {st.session_state.user_name}"""
            st.success("✅ न्यायालयीन मसुदा तयार झाला!")

# ६. शासकीय तक्रार
elif st.session_state.active_tab == "शासकीय तक्रार":
    st.subheader("🔴 शासकीय तक्रार अर्ज")
    with st.form("form_comp"):
        st.session_state.user_name = st.text_input("तक्रारदाराचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व मोबाईल:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रति / अधिकारी:", value=st.session_state.dept_name)
        c_sub = st.text_input("विषय:", value="दिव्यांगांना जागा उपलब्ध करून देणे व कारवाई करणेबाबत")
        c_body = st.text_area("तक्रारीचा तपशील:", value=st.session_state.original_query)
        if st.form_submit_button("🚀 तक्रार अर्ज तयार करा"):
            st.session_state.final_draft = f"""प्रति,\nमा. {st.session_state.dept_name},\n\nविषय: {c_sub}\nतक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}\n\nमहोदय,\nमी खालीलप्रमाणे तक्रार नोंदवत आहे:\n{c_body}\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ तक्रार अर्ज तयार झाला!")

# ==============================================================================
# ७. निकाल व डाऊनलोड
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI चॅटबॉट":
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
