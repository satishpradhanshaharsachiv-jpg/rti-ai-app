import streamlit as st
import google.generativeai as genai
import urllib.parse
from datetime import datetime
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

h1 { color: #1E3A8A; font-weight: 800; text-align: center; font-size: 22px; margin-bottom: 2px; }

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

APP_URL = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/?v=3"

# ==============================================================================
# ३. API कॉल
# ==============================================================================
active_api_key = st.secrets.get("GEMINI_API_KEY", "")

def get_ai_response(prompt_text):
    if active_api_key:
        try:
            genai.configure(api_key=active_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(prompt_text)
            if res and res.text:
                return res.text
        except Exception:
            pass
    return None

# ==============================================================================
# ४. होम पेज हेडर, बॅनर फोटो व शेअर मेनू
# ==============================================================================
st.markdown("<h1>⚖️ RTI, तक्रार व कायदेशीर महा-सहाय्यक</h1>", unsafe_allow_html=True)

head_col1, head_col2 = st.columns([5, 1])
with head_col1:
    st.caption("नागरिकांसाठी सर्व कायदेशीर व प्रशासकीय अर्जांचे ऑटोमेशन केंद्र")
with head_col2:
    if st.button("↗️ शेअर", key="main_share_btn", use_container_width=True):
        st.session_state.show_share = not st.session_state.show_share

# बाणावर क्लिक केल्यावर उघडणारा शेअर बॉक्स
if st.session_state.show_share:
    share_msg = urllib.parse.quote(f"⚖️ RTI, तक्रार व न्यायालयीन अर्ज तयार करण्यासाठी हे उपयुक्त AI ॲप वापरा:\n{APP_URL}")
    st.markdown(f"""
    <div class="share-box">
        <p style="margin:0 0 6px 0; font-weight:bold; font-size:14px; color:#374151;">ॲप लिंक सोशल मीडियावर शेअर करा:</p>
        <a class="share-btn btn-wa" href="https://api.whatsapp.com/send?text={share_msg}" target="_blank">WhatsApp</a>
        <a class="share-btn btn-fb" href="https://www.facebook.com/sharer/sharer.php?u={APP_URL}" target="_blank">Facebook</a>
        <a class="share-btn btn-tg" href="https://t.me/share/url?url={APP_URL}&text={share_msg}" target="_blank">Telegram</a>
        <a class="share-btn btn-ms" href="fb-messenger://share/?link={APP_URL}" target="_blank">Messenger</a>
    </div>
    """, unsafe_allow_html=True)

# बॅनर फोटो जोडणे (जर फाईल उपलब्ध असेल तर)
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
    if st.button("🤖 AI सल्लागार", key="tab4", use_container_width=True): st.session_state.active_tab = "AI सल्लागार"
with b5:
    if st.button("🟣 कोर्ट याचिका", key="tab5", use_container_width=True): st.session_state.active_tab = "न्यायालयीन मसुदा"
with b6:
    if st.button("🔴 शासकीय तक्रार", key="tab6", use_container_width=True): st.session_state.active_tab = "शासकीय तक्रार"

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# ६. फॉर्म्स व विभाग
# ==============================================================================
date_today = datetime.now().strftime("%d/%m/%Y")

# १. मूळ RTI (जोडपत्र अ)
if st.session_state.active_tab == "जोडपत्र 'अ'":
    st.subheader("🟢 जोडपत्र 'अ' - मूळ माहिती अधिकार अर्ज (कलम ६(१))")
    with st.form("form_a"):
        st.session_state.user_name = st.text_input("अर्जदाराचे पूर्ण नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता व मोबाईल क्र.:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
        st.session_state.original_query = st.text_area("मागितलेली माहिती (मुद्दे):", value=st.session_state.original_query)
        if st.form_submit_button("🚀 अर्ज तयार करा"):
            prompt = f"महाराष्ट्र RTI कलम ६(१) जोडपत्र 'अ' अर्ज तयार करा. अर्जदार: {st.session_state.user_name}, पत्ता: {st.session_state.user_address}, कार्यालय: {st.session_state.dept_name}, माहिती: {st.session_state.original_query}."
            ai_out = get_ai_response(prompt)
            st.session_state.final_draft = ai_out if ai_out else f"""जोडपत्र - 'अ'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील अर्ज.\n\nप्रति,\nजन माहिती अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अर्जदार: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. माहितीचा तपशील:\n{st.session_state.original_query}\n\n४. शुल्क: ₹१०/- कोर्ट फी जोडली आहे.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ अर्ज तयार झाला!")

# २. प्रथम अपील (जोडपत्र ब)
elif st.session_state.active_tab == "जोडपत्र 'ब'":
    st.subheader("🔵 जोडपत्र 'ब' - प्रथम अपील (कलम १९(१))")
    with st.form("form_b"):
        st.session_state.user_name = st.text_input("अपिलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रथम अपीलीय अधिकारी / विभाग:", value=st.session_state.dept_name)
        reason = st.text_area("अपीलाचे कारण:", value="विहित ३० दिवसांत माहिती दिली नाही.")
        if st.form_submit_button("🚀 प्रथम अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'ब'\nमाहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपील.\n\nप्रति,\nप्रथम अपीलीय अधिकारी,\nकार्यालय: {st.session_state.dept_name}\n\n१. अपिलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. कारण: {reason}\n४. मूळ माहिती: {st.session_state.original_query}\n\nमागणी: तात्काळ माहिती विनामूल्य द्यावी.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ प्रथम अपील तयार झाले!")

# ३. द्वितीय अपील (जोडपत्र क)
elif st.session_state.active_tab == "जोडपत्र 'क'":
    st.subheader("🟠 जोडपत्र 'क' - द्वितीय अपील (राज्य माहिती आयोग)")
    with st.form("form_c"):
        st.session_state.user_name = st.text_input("अपीलकर्त्याचे नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("कार्यालय / विभाग:", value=st.session_state.dept_name)
        if st.form_submit_button("🚀 द्वितीय अपील तयार करा"):
            st.session_state.final_draft = f"""जोडपत्र - 'क'\nमाहिती अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपील.\n\nप्रति,\nमा. राज्य माहिती आयोग खंडपीठ,\n\n१. अपीलकर्ता: {st.session_state.user_name}\n२. पत्ता: {st.session_state.user_address}\n३. प्रतिवादी: जन माहिती अधिकारी, {st.session_state.dept_name}\n४. मूळ माहिती: {st.session_state.original_query}\n\nप्रार्थना: कलम २०(१) नुसार २५,००० रुपये दंड आकारून माहिती विनामूल्य मिळवून द्यावी.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ द्वितीय अपील तयार झाले!")

# ४. AI सल्लागार
elif st.session_state.active_tab == "AI सल्लागार":
    st.subheader("🤖 कायदेशीर व प्रशासकीय AI सल्लागार")
    u_q = st.text_input("कायदेशीर प्रश्न विचारा:", placeholder="उदा. माहिती न दिल्यास पुढे काय करावे?")
    if st.button("उत्तर मिळवा") and u_q:
        ai_ans = get_ai_response(f"मराठीत अचूक कायदेशीर सल्ला द्या. प्रश्न: {u_q}")
        if ai_ans:
            st.info(ai_ans)
        else:
            st.info("माहिती अधिकार अधिनियम २००५ नुसार ३० दिवसांत माहिती न मिळाल्यास वरिष्ठ अधिकाऱ्यांकडे प्रथम अपील दाखल करता येते.")

# ५. न्यायालयीन मसुदा
elif st.session_state.active_tab == "न्यायालयीन मसुदा":
    st.subheader("🟣 न्यायालयीन याचिका मसुदा")
    with st.form("form_court"):
        st.session_state.user_name = st.text_input("याचिकाकर्ता नाव:", value=st.session_state.user_name)
        st.session_state.user_address = st.text_area("पत्ता:", value=st.session_state.user_address)
        st.session_state.dept_name = st.text_input("प्रतिवादी नाव:", value=st.session_state.dept_name)
        court_subj = st.text_input("विषय:", value="प्रशासकीय दिरंगाई व नुकसानभरपाई बाबत")
        if st.form_submit_button("🚀 कोर्ट मसुदा तयार करा"):
            st.session_state.final_draft = f"""मा. सक्षम न्यायालय / लवाद\n\n{st.session_state.user_name}, रा. {st.session_state.user_address}\n... याचिकाकर्ता\nविरुद्ध\n{st.session_state.dept_name}\n... प्रतिवादी\n\nविषय: {court_subj}\n\n१. वस्तुस्थिती: {st.session_state.original_query}\n२. प्रार्थना: प्रतिवादीस तात्काळ कायदेशीर आदेश देण्यात यावेत.\n\nदिनांक: {date_today}\nयाचिकाकर्ता: {st.session_state.user_name}"""
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
            st.session_state.final_draft = f"""प्रति,\nमा. {st.session_state.dept_name},\n\nविषय: {c_sub}\nतक्रारदार: {st.session_state.user_name}, रा. {st.session_state.user_address}\n\nमहोदय,\nमी खालीलप्रमाणे तक्रार नोंदवत आहे:\n{c_body}\n\nसदर प्रकरणात ७ दिवसांत योग्य निर्णय घेऊन न्याय देण्यात यावा.\n\nदिनांक: {date_today}\nस्वाक्षरी: {st.session_state.user_name}"""
            st.success("✅ तक्रार अर्ज तयार झाला!")

# ==============================================================================
# ७. निकाल व डाऊनलोड
# ==============================================================================
if st.session_state.final_draft and st.session_state.active_tab != "AI सल्लागार":
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

# तळभागात जनजागृती फोटो (About Image)
if os.path.exists("about_child.png"):
    st.markdown("---")
    st.image("about_child.png", caption="सशक्त नागरिक, पारदर्शक कारभार!", use_container_width=True)
