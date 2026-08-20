import io
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# १. पेज कॉन्फिगरेशन आणि आकर्षक रंगीत स्टाईल
st.set_page_config(page_title="RTI & Complaint AI Assistant", page_icon="📜", layout="centered")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; display: none;}
h1 { color: #1E3A8A; font-weight: bold; }
h2 { color: #047857; font-weight: bold; }
.stButton>button {
    font-size: 18px !important;
    font-weight: bold !important;
    padding: 10px 24px !important;
    border-radius: 10px !important;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# २. PDF तयार करण्याचे फंक्शन
def generate_pdf(content_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'NormalMarathi', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14
    )
    elements = []
    paragraphs = content_text.split('\n')
    for p in paragraphs:
        if p.strip():
            elements.append(Paragraph(p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), normal_style))
            elements.append(Spacer(1, 4))
        else:
            elements.append(Spacer(1, 6))
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ३. मुख्य पानावर मोठे पर्याय (Radio Buttons with Custom Style)
st.markdown("<h1 style='text-align: center; color: #B91C1C;'>🏛️ RTI व तक्रार अर्ज AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; font-weight: bold;'>घरबसल्या सहज तयार करा कायदेशीर RTI अर्ज, अपील आणि शासकीय तक्रार अर्ज!</p>", unsafe_allow_html=True)

page = st.radio(
    "👉 खालीलपैकी हवा असलेला पर्याय निवडा:", 
    ["🏠 मुख्य पान व माहिती", "📜 RTI अर्ज व अपील तयार करा", "📝 तक्रार अर्ज तयार करा"], 
    horizontal=True
)

st.markdown("---")

# ४. मुख्य पान (Home Page)
if page == "🏠 मुख्य पान व माहिती":
    st.markdown("## 🌟 ॲपची प्रमुख वैशिष्ट्ये:")
    st.markdown("### 📋 **१. आरटीआय (RTI) अर्ज व अपील**")
    st.write("माहिती अधिकार कायदा २००५ अंतर्गत मूळ अर्ज, प्रथम अपील आणि द्वितीय अपील झटपट तयार करा.")
    
    data_text = "🏛️ RTI व तक्रार अर्ज AI सहाय्यक - आता घरबसल्या मोबाईलवरून आरटीआय आणि तक्रार अर्ज तयार करा! लिंक उघडा:"
    app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
    
    st.markdown("### 📝 **२. शासकीय तक्रार अर्ज**")
    st.write("शासकीय कार्यालयातील दिरंगाई, समस्या किंवा तक्रारीसाठी थेट कायदेशीर अर्ज तयार करा.")
    
    st.markdown("---")
    st.markdown("## 🌐 हे ॲप आपल्या मित्रांना आणि सोशल मीडियावर शेअर करा:")
    
    # सोशल मीडिया शेअरिंग बटन्स (WhatsApp, Facebook, Telegram)
    whatsapp_url = f"https://api.whatsapp.com/send?text={data_text} {app_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={app_url}"
    telegram_url = f"https://t.me/share/url?url={app_url}&text={data_text}"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 15px; border-radius:8px; font-weight:bold; width:100%;">💬 WhatsApp</button></a>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<a href="{facebook_url}" target="_blank"><button style="background-color:#1877F2; color:white; border:none; padding:10px 15px; border-radius:8px; font-weight:bold; width:100%;">📘 Facebook</button></a>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<a href="{telegram_url}" target="_blank"><button style="background-color:#0088cc; color:white; border:none; padding:10px 15px; border-radius:8px; font-weight:bold; width:100%;">✈️ Telegram</button></a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 👤 विकासक व संपर्क माहिती:")
    st.markdown("**विकासक / संचालक:** सतीश अशोक प्रधान")
    st.markdown("**पत्ता:** छत्रपती संभाजीनगर, महाराष्ट्र")
    st.markdown("**मोबाईल नंबर:** ८६६८२३५३९५")
    st.markdown("**ईमेल:** Satishpradhan.shaharsachiv@gmail.com")

# ५. RTI अर्ज व अपील तयार करण्याचे पान
elif page == "📜 RTI अर्ज व अपील तयार करा":
    st.markdown("<h2>📜 RTI अर्ज व अपील मसुदा तयार करा</h2>", unsafe_allow_html=True)
    
    # Gemini API Key स्पष्टपणे दिसण्यासाठी
    st.sidebar.markdown("### 🔑 AI सेटिंग्ज")
    api_key = st.sidebar.text_input("Gemini API Key टाका (AI मसुद्यासाठी):", type="password")

    JODPATRA_A = """जोडपत्र - 'अ' (नियम ३ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम ६(१) खालील माहिती मिळवण्यासाठीचा अर्ज.

प्रति,
जन माहिती अधिकारी,
कार्यालयाचे नाव : {dept_name}
पत्ता : .......................................................................................

१. अर्जदाराचे पूर्ण नाव : {user_name}
२. अर्जदाराचा पत्ता : {user_address}
३. मागितलेली माहिती :
{query}

४. माहितीचा कालावधी : ...........................................................
५. माहिती टपालाने हवी की प्रत्यक्ष : ...........................................
६. अर्ज शुल्क : १० रुपये (कोर्ट फी स्टॅम्प / चलनाद्वारे जोडले आहे).

ठिकाण : .............................
दिनांक : .............................
(अर्जदाराची स्वाक्षरी / अंगठा)"""

    JODPATRA_B = """जोडपत्र - 'ब' (नियम ५ पहा)
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) खालील प्रथम अपिलाचा नमुना.

प्रति,
प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी,
कार्यालयाचे नाव : {dept_name}
पत्ता : .......................................................................................

१. अपिलकर्त्याचे नाव : {user_name}
२. अपिलकर्त्याचा पत्ता : {user_address}
३. जन माहिती अधिकाऱ्याचा तपशील : {dept_name}
४. मूळ अर्ज (जोडपत्र 'अ') सादर केल्याचा दिनांक : .............................
५. प्रथम अपील करण्याचे कारण :
{query}

६. मागितलेले सहाय्य : जन माहिती अधिकाऱ्यास विहित मुदतीत संपूर्ण माहिती विनामूल्य देण्याचे आदेश व्हावेत.

ठिकाण : .............................
दिनांक : .............................
(अपिलकर्त्याची स्वाक्षरी / अंगठा)"""

    JODPATRA_C = """जोडपत्र - 'क'
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(३) खालील द्वितीय अपिलाचा नमुना.

प्रति,
मा. राज्य माहिती आयुक्त,
राज्य माहिती आयोग, महाराष्ट्र राज्य.

१. अपिलकर्त्याचे नाव : {user_name}
२. अपिलकर्त्याचा पत्ता : {user_address}
३. संबंधित जन माहिती अधिकारी : {dept_name}
४. द्वितीय अपिलाचे कारण व मागितलेली दाद :
{query}

सत्यप्रतीज्ञा : वरील सर्व माहिती माझ्या समजुतीनुसार खरी व अचूक आहे.

ठिकाण : .............................
दिनांक : .............................
(अपिलकर्त्याची स्वाक्षरी / अंगठा)"""

    with st.form("rti_form"):
        doc_type = st.selectbox("अर्ज किंवा अपील निवडा:",
                                ["जोडपत्र अ (मूळ RTI अर्ज - कलम ६(१))", 
                                 "जोडपत्र ब (प्रथम अपील - कलम १९(१))", 
                                 "जोडपत्र क (द्वितीय अपील - कलम १९(३))", 
                                 "AI द्वारे नवीन मसुदा तयार करा"])
        user_name = st.text_input("तुमचे पूर्ण नाव :")
        user_address = st.text_area("तुमचा संपूर्ण पत्ता :")
        dept_name = st.text_input("सरकारी विभागाचे / कार्यालयाचे नाव :")
        query = st.text_area("मागितलेली माहिती / अपिलाचे कारण / प्रश्न :")
        submitted = st.form_submit_button("🚀 RTI अर्ज / ड्राफ्ट तयार करा")

    if submitted:
        if not user_name:
            st.warning("कृपया तुमचे नाव प्रविष्ट करा.")
        else:
            final_text = ""
            filename_prefix = "RTI"

            if "जोडपत्र अ" in doc_type:
                final_text = JODPATRA_A.format(user_name=user_name, user_address=user_address, dept_name=dept_name, query=query)
                filename_prefix = "Jodpatra_A_Original_RTI"
            elif "जोडपत्र ब" in doc_type:
                final_text = JODPATRA_B.format(user_name=user_name, user_address=user_address, dept_name=dept_name, query=query)
                filename_prefix = "Jodpatra_B_First_Appeal"
            elif "जोडपत्र क" in doc_type:
                final_text = JODPATRA_C.format(user_name=user_name, user_address=user_address, dept_name=dept_name, query=query)
                filename_prefix = "Jodpatra_C_Second_Appeal"
            else:
                if not api_key:
                    st.error("AI मसुद्यासाठी कृपया डावीकडील मेनूमध्ये/साईटबारमध्ये Gemini API Key प्रविष्ट करा.")
                else:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"तुम्ही RTI कायदा २००५ चे तज्ज्ञ आहात. खालील माहितीनुसार कायदेशीर मराठी अर्ज तयार करा:\nअर्जदार: {user_name}\nपत्ता: {user_address}\nविभाग: {dept_name}\nमाहिती: {query}"
                        with st.spinner("AI अर्ज तयार करत आहे..."):
                            res = model.generate_content(prompt)
                            final_text = res.text
                            filename_prefix = "Custom_RTI"
                    except Exception as e:
                        st.error(f"त्रुटी आली: {e}")

            if final_text:
                st.success("दस्तऐवज यशस्वीरीत्या तयार झाला आहे!")
                st.text_area("तयार झालेला मसुदा:", value=final_text, height=300)
                pdf_data = generate_pdf(final_text)
                st.download_button("📥 PDF फाईल डाउनलोड करा", data=pdf_data, file_name=f"{filename_prefix}_{user_name}.pdf", mime="application/pdf")
                st.download_button("📄 Text (.txt) फाईल डाउनलोड करा", data=final_text, file_name=f"{filename_prefix}_{user_name}.txt", mime="text/plain")

# ६. तक्रार अर्ज तयार करण्याचे नवीन पान (Complaint Form)
elif page == "📝 तक्रार अर्ज तयार करा":
    st.markdown("<h2>📝 शासकीय तक्रार अर्ज तयार करा</h2>", style="color: #B91C1C;")
    
    COMPLAINT_TEMPLATE = """शासकीय तक्रार अर्ज

प्रति,
मा. अधिकारी / विभाग प्रमुख,
कार्यालयाचे नाव : {dept_name}
पत्ता : .......................................................................................

विषय : शासकीय कामातील दिरंगाई / समस्येबाबत तक्रार अर्ज.

महोदय / महोदया,

१. तक्रारकर्त्याचे पूर्ण नाव : {user_name}
२. तक्रारकर्त्याचा पत्ता : {user_address}
३. तक्रारीचा सविस्तर विषय व तपशील :
{query}

तरी वरील विषयाबाबत योग्य ती चौकशी करून तातडीने कारवाई करण्यात यावी, ही विनंती.

ठिकाण : .............................
दिनांक : .............................

(तक्रारकर्त्याची स्वाक्षरी / अंगठा)
नांव: {user_name}
मोबाईल: {user_phone}"""

    with st.form("complaint_form"):
        c_name = st.text_input("तुमचे पूर्ण नाव :")
        c_address = st.text_area("तुमचा संपूर्ण पत्ता :")
        c_phone = st.text_input("मोबाईल नंबर :")
        c_dept = st.text_input("संबंधित सरकारी कार्यालय / विभागाचे नाव :")
        c_query = st.text_area("तक्रारीचा सविस्तर विषय / समस्या :")
        c_submitted = st.form_submit_button("🚀 तक्रार अर्ज तयार करा")

    if c_submitted:
        if not c_name or not c_query:
            st.warning("कृपया तुमचे नाव आणि तक्रारीचा तपशील प्रविष्ट करा.")
        else:
            complaint_text = COMPLAINT_TEMPLATE.format(
                user_name=c_name, 
                user_address=c_address, 
                user_phone=c_phone, 
                dept_name=c_dept, 
                query=c_query
            )
            st.success("तक्रार अर्ज यशस्वीरीत्या तयार झाला आहे!")
            st.text_area("तयार झालेला तक्रार अर्ज मसुदा:", value=complaint_text, height=300)
            
            c_pdf = generate_pdf(complaint_text)
            st.download_button("📥 तक्रार अर्ज PDF डाउनलोड करा", data=c_pdf, file_name=f"Complaint_Application_{c_name}.pdf", mime="application/pdf")
            st.download_button("📄 Text (.txt) फाईल डाउनलोड करा", data=complaint_text, file_name=f"Complaint_Application_{c_name}.txt", mime="text/plain")

