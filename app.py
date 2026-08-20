import io
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# १. वेबसाइट लेआउट आणि शीर्षक
st.set_page_config(page_title="RTI AI Assistant", page_icon="📜", layout="centered")
st.title("📜 AI RTI अर्ज व अपील सहाय्यक")
st.write("तुमची माहिती भरा किंवा 'जोडपत्र अ/ब/क' निवडून थेट अधिकृत PDF डाउनलोड करा.")

# २. साइडबार - API Key
api_key = st.sidebar.text_input("Gemini API Key टाका:", type="password")

# ३. PDF तयार करण्याचे फंक्शन
def generate_rti_pdf(content_text, title="RTI Document"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'NormalMarathi',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14
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

# ४. मूळ जोडपत्रांचे अधिकृत फॉरमॅट्स
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
   [ ] विहित मुदतीत (३० दिवसांत) कोणतीही माहिती मिळाली नाही.
   [ ] माहिती देण्यास नकार दिला.
   [ ] दिलेली माहिती अपूर्ण / चुकीची आहे.
६. मागितलेली माहिती व अपिलाचा गोषवारा :
{query}

७. मागितलेले सहाय्य : जन माहिती अधिकाऱ्यास विहित मुदतीत संपूर्ण माहिती विनामूल्य देण्याचे आदेश व्हावेत.

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
४. प्रथम अपीलीय अधिकाऱ्याचा तपशील : .....................................................
५. मूळ अर्ज दिनांक : ..................... | प्रथम अपील दिनांक : .....................
६. द्वितीय अपिलाचे कारण व मागितलेली दाद :
{query}

सत्यप्रतीज्ञा : वरील सर्व माहिती माझ्या समजुतीनुसार खरी व अचूक आहे.

ठिकाण : .............................
दिनांक : .............................
(अपिलकर्त्याची स्वाक्षरी / अंगठा)"""

# ५. इनपुट फॉर्म
with st.form("rti_form"):
    doc_type = st.selectbox(
        "कोणता दस्तऐवज हवा आहे निवडा:",
        ["जोडपत्र अ (मूळ RTI अर्ज - कलम ६(१))", 
         "जोडपत्र ब (प्रथम अपील - कलम १९(१))", 
         "जोडपत्र क (द्वितीय अपील - कलम १९(३))", 
         "AI द्वारे नवीन मजकूर तयार करा"]
    )
    user_name = st.text_input("तुमचे पूर्ण नाव :")
    user_address = st.text_area("तुमचा संपूर्ण पत्ता :")
    dept_name = st.text_input("सरकारी विभागाचे / कार्यालयाचे नाव :")
    query = st.text_area("मागितलेली माहिती / अपिलाचे कारण / प्रश्न :")
    submitted = st.form_submit_button("अर्ज / ड्राफ्ट तयार करा")

# ६. प्रक्रिया व डाऊनलोड
if submitted:
    if not user_name:
        st.warning("कृपया तुमचे नाव प्रविष्ट करा.")
    else:
        final_text = ""
        filename_prefix = "RTI"

        # युजरच्या निवडीनुसार जोडपत्र ओळखणे
        if "जोडपत्र अ" in doc_type or "मूळ" in query.lower():
            final_text = JODPATRA_A.format(user_name=user_name, user_address=user_address, dept_name=dept_name, query=query)
            filename_prefix = "Jodpatra_A_Original_RTI"
        elif "जोडपत्र ब" in doc_type or "प्रथम अपील" in query.lower() or "appeal" in query.lower():
            final_text = JODPATRA_B.format(user_name=user_name, user_address=user_address, dept_name=dept_name, query=query)
            filename_prefix = "Jodpatra_B_First_Appeal"
        elif "जोडपत्र क" in doc_type or "द्वितीय" in query.lower() or "second appeal" in query.lower():
            final_text = JODPATRA_C.format(user_name=user_name, user_address=user_address, dept_name=dept_name, query=query)
            filename_prefix = "Jodpatra_C_Second_Appeal"
        else:
            # AI द्वारे कस्टम मसुदा तयार करणे
            if not api_key:
                st.error("AI मसुद्यासाठी कृपया साइडबारमध्ये Gemini API Key प्रविष्ट करा.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"""
                    तुम्ही RTI कायदा २००५ चे तज्ज्ञ आहात. खालील माहितीनुसार कायदेशीर मराठी अर्ज तयार करा:
                    अर्जदार: {user_name}
                    पत्ता: {user_address}
                    विभाग: {dept_name}
                    माहिती: {query}
                    """
                    with st.spinner("AI अर्ज तयार करत आहे..."):
                        res = model.generate_content(prompt)
                        final_text = res.text
                        filename_prefix = "Custom_RTI"
                except Exception as e:
                    st.error(f"त्रुटी आली: {e}")

        if final_text:
            st.success("दस्तऐवज यशस्वीरीत्या तयार झाला आहे!")
            st.text_area("तयार झालेला मसुदा:", value=final_text, height=300)
            
            # PDF फाईल डाऊनलोड बटण
            pdf_data = generate_rti_pdf(final_text, title=filename_prefix)
            st.download_button(
                label="📥 PDF फाईल डाउनलोड करा",
                data=pdf_data,
                file_name=f"{filename_prefix}_{user_name}.pdf",
                mime="application/pdf"
            )
            
            # टेक्स्ट फाईल डाऊनलोड बटण
            st.download_button(
                label="📄 Text (.txt) फाईल डाउनलोड करा",
                data=final_text,
                file_name=f"{filename_prefix}_{user_name}.txt",
                mime="text/plain"
            )
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
