import io
import urllib.parse
from datetime import datetime
import streamlit as st
import google.generativeai as genai

# १. पेज कॉन्फिगरेशन
st.set_page_config(page_title="RTI व शासकीय तक्रार AI सहाय्यक", page_icon="🏛️", layout="centered")

# २. सेशन स्टेट मॅनेजमेंट (डेटा कायम टिकवून ठेवण्यासाठी)
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_address' not in st.session_state: st.session_state.user_address = ""
if 'dept_name' not in st.session_state: st.session_state.dept_name = ""
if 'query' not in st.session_state: st.session_state.query = ""
if 'selected_bench' not in st.session_state: st.session_state.selected_bench = "छत्रपती संभाजीनगर खंडपीठ (राज्य माहिती आयोग)"
if 'rti_type' not in st.session_state: st.session_state.rti_type = "माहिती अधिकार अर्ज (कलम ६(१) - नमुना जोडपत्र 'अ')"
if 'result_text' not in st.session_state: st.session_state.result_text = ""
if 'history_list' not in st.session_state: st.session_state.history_list = []

# ३. माहिती आयोगांची अधिकृत पत्ते यादी (State & Central Commissions)
COMMISSION_ADDRESSES = {
    "छत्रपती संभाजीनगर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ छत्रपती संभाजीनगर, शासकीय सुभेदारी विश्रामगृह समोर, बाबा पेट्रोल पंपाजवळ, छत्रपती संभाजीनगर - ४३१००१ (फोन: ०२४०-२३५२५४४)",
    "मुंबई मुख्य खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य मुख्य माहिती आयुक्त, राज्य माहिती आयोग, १३ वा मजला, नवीन प्रशासकीय इमारत, मंत्रालयासमोर, मादाम कामा रोड, मुंबई - ४०००३२ (फोन: ०२२-२२८५६०७८)",
    "पुणे खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ पुणे, नवीन प्रशासकीय इमारत, कौन्सिल हॉल समोर, पुणे - ४११००१ (फोन: ०२०-२६०५०५८०)",
    "नागपूर खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नागपूर, रवी भवन, नागपूर - ४४०००१ (फोन: ०७१२-२५६५१९२)",
    "नाशिक खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ नाशिक, जिल्हाधिकारी कार्यालय आवार, नाशिक - ४२२००२ (फोन: ०२५३-२२३२७६४)",
    "अमरावती खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ अमरावती, प्रशासकीय इमारत, अमरावती - ४४४६०१ (फोन: ०७२१-२६७३२३८)",
    "कोकण खंडपीठ (राज्य माहिती आयोग)": "मा. राज्य माहिती आयुक्त, राज्य माहिती आयोग खंडपीठ कोकण भवन, सी.बी.डी. बेलापूर, नवी मुंबई - ४००६१४ (फोन: ०२२-२७५७९४६३)",
    "केंद्रीय माहिती आयोग (CIC New Delhi - केंद्रीय विभाग)": "मा. मुख्य माहिती आयुक्त, केंद्रीय माहिती आयोग (CIC), बाबा गंगनाथ मार्ग, मुनिरका, नवी दिल्ली - ११००६७ (फोन: ०११-२६१८३९९६)"
}

# ४. प्रिंट व १-पान PDF फंक्शन
def render_printable_doc(title, content, theme_color="#059669"):
    html_content = content.replace('\n', '<br>')
    printable_html = f"""
    <div id="printArea" style="
        font-family: 'Mukta', sans-serif;
        background: #ffffff;
        color: #000000;
        padding: 25px 30px;
        border: 2px solid {theme_color};
        border-radius: 8px;
        line-height: 1.5;
        font-size: 13.5px;
        max-width: 750px;
        margin: 10px auto;
        box-sizing: border-box;
    ">
        <h3 style="text-align: center; font-size: 16px; margin-bottom: 12px; color: {theme_color}; text-decoration: underline;">{title}</h3>
        <div>{html_content}</div>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="
            var printContent = document.getElementById('printArea').innerHTML;
            var originalContent = document.body.innerHTML;
            document.body.innerHTML = printContent;
            window.print();
            document.body.innerHTML = originalContent;
            window.location.reload();
        " style="
            background: {theme_color};
            color: white;
            padding: 12px 25px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        ">
            🖨️ १ पानात PDF सेव्ह / प्रिंट करा (Save as PDF)
        </button>
    </div>
    """
    st.components.v1.html(printable_html, height=540, scrolling=True)

# ५. शीर्षक
st.markdown("<h1>🏛️ RTI व शासकीय अपील AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold; color: #4B5563;'>जोडपत्र अ, ब (प्रथम अपील) आणि क (माहिती आयोग) कडक कायदेशीर मसुदा</p>", unsafe_allow_html=True)

# रिसेट बटण
if st.button("🔄 सर्व माहिती रिसेट करा"):
    st.session_state.user_name = ""
    st.session_state.user_address = ""
    st.session_state.dept_name = ""
    st.session_state.query = ""
    st.session_state.result_text = ""
    st.success("सर्व माहिती रिसेट झाली!")
    st.rerun()

st.markdown("---")

# ६. मुख्य फॉर्म
st.session_state.rti_type = st.selectbox(
    "📌 अर्जाचा प्रकार निवडा (माहिती आपोआप पुढे कॅरी होईल):",
    [
        "माहिती अधिकार अर्ज (कलम ६(१) - नमुना जोडपत्र 'अ')",
        "प्रथम अपील अर्ज (कलम १९(१) - नमुना जोडपत्र 'ब')",
        "द्वितीय अपील अर्ज (कलम १९(३) - नमुना जोडपत्र 'क' / माहिती आयोग)"
    ],
    index=0
)

# जोडपत्र 'क' निवडल्यावर माहिती आयोगाचा पत्ता आपोआप निवडणे
if "जोडपत्र 'क'" in st.session_state.rti_type:
    st.info("🏛️ **द्वितीय अपीलासाठी माहिती आयोगाचे खंडपीठ निवडा (पत्ता आपोआप भरला जाईल):**")
    st.session_state.selected_bench = st.selectbox(
        "माहिती आयोग खंडपीठ निवडा:",
        list(COMMISSION_ADDRESSES.keys())
    )
    commission_full_address = COMMISSION_ADDRESSES[st.session_state.selected_bench]
    st.success(f"📍 **निवडलेला आयोग:** {commission_full_address}")

# इनपुट फील्ड्स (माहिती आपोआप कायम राहते)
st.session_state.user_name = st.text_input("अर्जदार / अपिलकर्त्याचे पूर्ण नाव:", value=st.session_state.user_name)
st.session_state.user_address = st.text_area("संपूर्ण पत्ता व संपर्क क्रमांक:", value=st.session_state.user_address)
st.session_state.dept_name = st.text_input("संबंधित मूळ सरकारी कार्यालय / विभागाचे नाव:", value=st.session_state.dept_name)
st.session_state.query = st.text_area("मागितलेली माहिती / अपीलाचे कारण / मुद्दे:", value=st.session_state.query)

# ७. मसुदा तयार करणे
if st.button("🚀 अधिकृत कायदेशीर मसुदा तयार करा"):
    if not st.session_state.user_name or not st.session_state.dept_name or not st.session_state.query:
        st.warning("कृपया तुमचे नाव, विभाग आणि मागितलेली माहिती/कारण भरा.")
    else:
        date_str = datetime.now().strftime("%d/%m/%Y")
        
        # १. जोडपत्र 'अ' (मूळ अर्ज)
        if "जोडपत्र 'अ'" in st.session_state.rti_type:
            st.session_state.result_text = f"""जोडपत्र - 'अ' (नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील माहिती मिळवण्यासाठीचा अर्ज.

प्रति,
जन माहिती अधिकारी,
कार्यालय: {st.session_state.dept_name}

१. अर्जदाराचे पूर्ण नाव : {st.session_state.user_name}
२. अर्जदाराचा पत्ता : {st.session_state.user_address}
३. मागितलेल्या माहितीचा तपशील :
{st.session_state.query}

४. माहितीचा कालावधी : चालू वर्ष व मागील अभिलेख
५. माहितीचा प्रकार : प्रमाणित सत्यप्रतीसह व्यक्तिशः / टपालाने
६. अर्ज शुल्क : ₹१०/- (कोर्ट फी स्टॅम्प / चलनाद्वारे जोडले आहे).

सदर माहिती ३० दिवसांत न मिळाल्यास कलम १९(१) अन्वये प्रथम अपील करण्यात येईल. माहिती आपल्या कार्यालयाशी संबंधित नसल्यास कलम ६(३) अन्वये ५ दिवसांत योग्य विभागाकडे वर्ग करावी. अर्जात काही गोपनीय भाग असल्यास कलम १० चा वापर करून उर्वरित सर्व माहिती विहित मुदतीत पुरवण्यात यावी.

दिनांक: {date_str}                                     अर्जदाराची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""

        # २. जोडपत्र 'ब' (प्रथम अपील)
        elif "जोडपत्र 'ब'" in st.session_state.rti_type:
            st.session_state.result_text = f"""जोडपत्र - 'ब' (नियम ५ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपिलाचा नमुना.

प्रति,
प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी,
कार्यालय: {st.session_state.dept_name}

१. अपिलकर्त्याचे पूर्ण नाव : {st.session_state.user_name}
२. अपिलकर्त्याचा पत्ता : {st.session_state.user_address}
३. जन माहिती अधिकाऱ्याचा तपशील : जन माहिती अधिकारी, {st.session_state.dept_name}
४. मूळ अर्ज (जोडपत्र 'अ') सादर केल्याचा दिनांक : विहित मुदतीपूर्वी
५. प्रथम अपीलाचे कारण :
   - जन माहिती अधिकाऱ्याने ३० दिवसांत माहिती दिली नाही / दिलेली माहिती अपूर्ण, अस्पष्ट व दिशाभूल करणारी आहे.
६. मागितलेली माहिती व अपीलाचा गोषवारा :
{st.session_state.query}

७. मागितलेले सहाय्य / दाद (Relief Sought) :
   १) माहिती अधिकार अधिनियम, २००५ च्या कलम १० (विभक्तता तत्त्व) चा वापर करून तात्काळ संपूर्ण व प्रमाणित माहिती विनामूल्य पुरवण्याचे आदेश जन माहिती अधिकाऱ्यास देण्यात यावेत.
   २) माहिती दडवून ठेवल्याबद्दल व कायद्याचे उल्लंघन केल्याबद्दल संबंधित दोषी अधिकाऱ्यावर कलम २० अन्वये दंडात्मक कारवाई प्रस्तावित करावी.
   ३) कर्तव्यात कसूर केल्याबद्दल दोषी अधिकाऱ्याविरुद्ध शिस्तभंगाच्या कारवाईची शिफारस करण्यात येऊन त्याची नोंद त्यांच्या सेवापुस्तकात (Service Book) करण्याचे आदेश व्हावेत.

सत्यप्रतीज्ञा : वरील सर्व तपशील माझ्या व्यक्तिगत माहिती व समजुतीनुसार खरा व अचूक आहे.

दिनांक: {date_str}                                     अपिलकर्त्याची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""

        # ३. जोडपत्र 'क' (द्वितीय अपील - माहिती आयोग)
        elif "जोडपत्र 'क'" in st.session_state.rti_type:
            comm_address = COMMISSION_ADDRESSES[st.session_state.selected_bench]
            st.session_state.result_text = f"""जोडपत्र - 'क'
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपिलाचा अधिकृत नमुना.

प्रति,
{comm_address}

१. अपिलकर्त्याचे पूर्ण नाव : {st.session_state.user_name}
२. अपिलकर्त्याचा पत्ता व संपर्क : {st.session_state.user_address}
३. जन माहिती अधिकाऱ्याचा तपशील : जन माहिती अधिकारी, {st.session_state.dept_name}
४. प्रथम अपीलीय अधिकाऱ्याचा तपशील : प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी, {st.session_state.dept_name}
५. मूळ अर्ज (जोडपत्र 'अ') व प्रथम अपील (जोडपत्र 'ब') करूनही विहित मुदतीत समाधानकारक माहिती मिळाली नाही.
६. द्वितीय अपीलाचा संक्षिप्त विषय व मागितलेली माहिती :
{st.session_state.query}

७. मागितलेली दाद / प्रार्थना :
   १) माहिती अधिकार अधिनियम, २००५ च्या कलम १० (Severability Clause) चा वापर करून संपूर्ण व प्रमाणित अभिलेख विनामूल्य उपलब्ध करून देण्याचे आदेश व्हावेत.
   २) विहित मुदतीत माहिती न दिल्याबद्दल व जाणूनबुजून टाळाटाळ केल्याबद्दल जन माहिती अधिकाऱ्यावर कलम २०(१) अन्वये २५,०००/- रुपये कमाल दंडात्मक कारवाई करण्यात यावी.
   ३) कलम २०(२) अन्वये दोषी अधिकाऱ्याविरुद्ध शिस्तभंगाच्या कारवाईची शिफारस करून सदर कारवाईची नोंद त्यांच्या सेवापुस्तकात (Service Book) घेण्याचे आदेश सक्षम प्राधिकरणास देण्यात यावेत.

सत्यप्रतीज्ञा : मी याद्वारे घोषित करतो/करते की, वरील सर्व तपशील माझ्या समजुतीनुसार आणि माहितीनुसार पूर्णतः सत्य व अचूक आहे.

दिनांक: {date_str}                                     अपिलकर्त्याची स्वाक्षरी: {st.session_state.user_name}
ठिकाण: ________________"""

        st.session_state.history_list.append({
            "type": st.session_state.rti_type,
            "title": f"{st.session_state.dept_name} - {st.session_state.user_name}",
            "content": st.session_state.result_text,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M")
        })

# ८. मसुदा दाखवणे व PDF डाऊनलोड / प्रिंट
if st.session_state.result_text:
    st.success("✅ कडक कायदेशीर मसुदा यशस्वीरीत्या तयार झाला आहे!")
    st.text_area("📄 तयार झालेला मसुदा (वाचण्यासाठी किंवा कॉपी करण्यासाठी):", value=st.session_state.result_text, height=260)
    
    st.markdown("---")
    st.markdown("### 📥 अधिकृत १-पान PDF डाऊनलोड / प्रिंट")
    
    # थेट १ पानात प्रिंट/PDF
    render_printable_doc(st.session_state.rti_type, st.session_state.result_text, "#059669")
