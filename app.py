import io
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# १. पेज कॉन्फिगरेशन
st.set_page_config(page_title="RTI & Complaint AI Assistant", page_icon="📜", layout="centered")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; display: none;}
h1 { color: #1E3A8A; font-weight: bold; text-align: center; }
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

# ३. URL क्वेरी पॅरामीटर्सद्वारे पानांचे व्यवस्थापन
query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"]

if 'page' not in st.session_state:
    st.session_state.page = "home"

st.markdown("<h1>🏛️ RTI व तक्रार अर्ज AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 15px; font-weight: bold; color: #4B5563;'>घरबसल्या सहज तयार करा कायदेशीर RTI अर्ज, अपील आणि शासकीय तक्रार अर्ज!</p>", unsafe_allow_html=True)
st.markdown("---")

# अत्यंत मोठे, लांब आणि आकर्षक रंगीत बटन्स
st.markdown("""
<div style="display: flex; flex-direction: column; gap: 14px; margin: 15px 0;">
    <a href="?page=home" target="_self" style="text-decoration: none;">
        <div style="background: linear-gradient(135deg, #1E3A8A, #3B82F6); color: white; padding: 22px; border-radius: 16px; text-align: center; font-size: 22px; font-weight: bold; box-shadow: 0 6px 15px rgba(0,0,0,0.3);">
            🏠 मुख्य पान व माहिती
        </div>
    </a>
    <a href="?page=rti" target="_self" style="text-decoration: none;">
        <div style="background: linear-gradient(135deg, #047857, #10B981); color: white; padding: 22px; border-radius: 16px; text-align: center; font-size: 22px; font-weight: bold; box-shadow: 0 6px 15px rgba(0,0,0,0.3);">
            📜 RTI अर्ज व अपील तयार करा
        </div>
    </a>
    <a href="?page=complaint" target="_self" style="text-decoration: none;">
        <div style="background: linear-gradient(135deg, #B91C1C, #F59E0B); color: white; padding: 22px; border-radius: 16px; text-align: center; font-size: 22px; font-weight: bold; box-shadow: 0 6px 15px rgba(0,0,0,0.3);">
            📝 शासकीय तक्रार अर्ज तयार करा
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
page = st.session_state.get("page", "home")

# ४. मुख्य पान (Home Page)
if page == "home":
    st.markdown("<p style='font-size: 13px; font-weight: bold; color: #374151; margin-bottom: 2px;'>✨ ॲपची प्रमुख वैशिष्ट्ये:</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 11px; color: #4B5563; margin: 0;'>• आरटीआय मूळ अर्ज, प्रथम व द्वितीय अपील.<br>• शासकीय कार्यालये व अधिकाऱ्यांविरुद्ध प्रभावी तक्रार अर्ज.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 12px; font-weight: bold; color: #374151; margin-top: 12px; margin-bottom: 4px;'>🌐 मित्रांना शेअर करा:</p>", unsafe_allow_html=True)
    
    app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
    
    # सर्व चॅट ॲप्सवर (WhatsApp, Instagram, FB, Messenger) जाण्यासाठी युनिव्हर्सल शेअर बटण
    st.markdown(f"""
        <div style="margin-top: 4px;">
            <button onclick="
                if (navigator.share) {{
                    navigator.share({{
                        title: 'RTI व तक्रार अर्ज AI सहाय्यक',
                        text: 'घरबसल्या मोबाईलवरून आरटीआय आणि शासकीय तक्रार अर्ज तयार करा!',
                        url: '{app_url}'
                    }}).catch(console.error);
                }} else {{
                    alert('लिंक कॉपी करा: {app_url}');
                }}
            " style="background: #25D366; color: white; padding: 7px 14px; border: none; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer;">
                📤 सर्व ॲप्सवर शेअर करा (WhatsApp, Insta, FB इ.)
            </button>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='font-size: 12px; color: #4B5563;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर | ८६६८२३५३९५</p>", unsafe_allow_html=True)

# ५. RTI अर्ज व अपील तयार करण्याचे पान
elif page == "rti":
    st.markdown("<h2>📜 RTI अर्ज व अपील मसुदा तयार करा</h2>", unsafe_allow_html=True)
    
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
३. मागितलेली सविस्तर माहिती :
{query}

४. माहितीचा कालावधी : ...........................................................
५. माहिती टपालाने हवी की प्रत्यक्ष : ...........................................
६. अर्ज शुल्क : १० रुपये (कोर्ट फी स्टॅम्प / चलनाद्वारे जोडले आहे).

ठिकाण : .............................
दिनांक : .............................
(अर्जदाराची स्वाक्षरी / अंगठा)"""

    JODPATRA_B = """जोडपत्र - 'ब' (नियम ५ पहा) - प्रथम अपील
माहितीचा अधिकार अधिनियम, २००५ च्या कलम १९(१) व कलम १० अन्वये प्रथम अपिलाचा नमुना.

प्रति,
प्रथम अपीलीय अधिकारी तथा वरिष्ठ अधिकारी,
कार्यालयाचे नाव : {dept_name}
पत्ता : .......................................................................................

विषय : जन माहिती अधिकाऱ्याने माहिती देण्यास टाळाटाळ केल्याबाबत प्रथम अपील व कलम १० (विभाजनशीलता) नुसार माहिती देण्याबाबत.

महोदय,
१. अपिलकर्त्याचे नाव : {user_name}
२. अपिलकर्त्याचा पत्ता : {user_address}
३. संबंधित जन माहिती अधिकारी : {dept_name}
४. मूळ अर्ज सादर केल्याचा दिनांक : .............................
५. अपिलाचे सविस्तर कारण व जन माहिती अधिकाऱ्याची कसूर:
{query}

कायदेशीर मुद्दा: माहिती अधिकार अधिनियम २००५ च्या **कलम १० (Section 10 - Severability / विभाजनशीलता)** नुसार जी माहिती अपवादात्मक कलमात येते ती वगळून उर्वरित सर्व जनहितार्थ व कायदेशीर माहिती तात्काळ विनामूल्य उपलब्ध करून देण्यात यावी.

तरी वरील मुद्यांचा विचार करून मला विहित मुदतीत संपूर्ण माहिती मिळवून देण्यात यावी.

ठिकाण : .............................
दिनांक : .............................
(अपिलकर्त्याची स्वाक्षरी / अंगठा)"""

    with st.form("rti_form"):
        doc_type = st.selectbox("अर्ज किंवा अपील निवडा:",
                                ["जोडपत्र अ (मूळ RTI अर्ज - कलम ६(१))", 
                                 "जोडपत्र ब (प्रथम अपील - कलम १९(१) व कलम १० सह)", 
                                 "AI द्वारे अत्यंत सविस्तर व प्रभावी मसुदा तयार करा"])
        user_name = st.text_input("तुमचे पूर्ण नाव :")
        user_address = st.text_area("तुमचा संपूर्ण पत्ता :")
        dept_name = st.text_input("सरकारी विभागाचे / कार्यालयाचे नाव :")
        query = st.text_area("मागितलेली माहिती / अपिलाचा तपशील :")
        submitted = st.form_submit_button("🚀 RTI अर्ज / अपील तयार करा")

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
                filename_prefix = "Jodpatra_B_First_Appeal_Section10"
            else:
                if not api_key:
                    st.error("AI सविस्तर मसुद्यासाठी कृपया साईडबारमध्ये Gemini API Key प्रविष्ट करा.")
                else:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        prompt = f"""तुम्ही कायदेशीर तज्ज्ञ आहात. खालील माहितीनुसार अत्यंत सविस्तर, प्रभावी आणि कायदेशीर मराठी RTI अर्ज किंवा अपील तयार करा (३०० ते १००० शब्दांपर्यंत सविस्तर, जशी युजरची भावना आहे):
अर्जदार: {user_name}
पत्ता: {user_address}
विभाग/कार्यालय: {dept_name}
तपशील/समस्या: {query}

मार्गदर्शक तत्त्वे:
- युजरच्या भावना आणि उद्देश पूर्णपणे समजून घेऊन अत्यंत मजबूत कायदेशीर भाषा वापरून अर्ज तयार करा.
- अपिलामध्ये **कलम १० (Section 10 - Severability / विभाजनशीलता)** चा आवर्जून वापर करा."""
                        with st.spinner("AI सविस्तर कायदेशीर मसुदा तयार करत आहे..."):
                            res = model.generate_content(prompt)
                            final_text = res.text
                            filename_prefix = "AI_Deep_RTI"
                    except Exception as e:
                        st.error(f"त्रुटी आली: {e}")

            if final_text:
                st.success("दस्तऐवज यशस्वीरीत्या तयार झाला आहे!")
                st.text_area("तयार झालेला सविस्तर मसुदा:", value=final_text, height=350)
                pdf_data = generate_pdf(final_text)
                st.download_button("📥 PDF फाईल डाउनलोड करा", data=pdf_data, file_name=f"{filename_prefix}_{user_name}.pdf", mime="application/pdf")
                st.download_button("📄 Text (.txt) फाईल डाउनलोड करा", data=final_text, file_name=f"{filename_prefix}_{user_name}.txt", mime="text/plain")

# ६. तक्रार अर्ज तयार करण्याचे पान (सर्वसामान्य नागरिकांसाठी व कार्यकर्त्यांसाठी लवचिक)
elif page == "complaint":
    st.markdown("<h2>📝 शासकीय तक्रार अर्ज तयार करा</h2>", unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🔑 AI तक्रार सेटिंग्ज")
    c_api_key = st.sidebar.text_input("Gemini API Key टाका (सविस्तर तक्रारीसाठी):", type="password")

    with st.form("complaint_form"):
        c_name = st.text_input("तुमचे पूर्ण नाव :")
        c_address = st.text_area("तुमचा संपूर्ण पत्ता :")
        c_phone = st.text_input("मोबाईल नंबर :")
        c_dept = st.text_input("संबंधित सरकारी कार्यालय / विभागाचे नाव (उदा. महानगरपालिका, तहसीलदार, पोलीस स्टेशन इ.) :")
        c_query = st.text_area("तक्रारीचा सविस्तर विषय व तपशील (तुमच्या शब्दात लिहा - उदा. अधिकाऱ्याचे निलंबन करणे, रस्ते काम, शाळेतील समस्या इ.):")
        c_submitted = st.form_submit_button("🚀 सविस्तर तक्रार अर्ज तयार करा")

    if c_submitted:
        if not c_name or not c_query:
            st.warning("कृपया तुमचे नाव आणि तक्रारीचा तपशील प्रविष्ट करा.")
        else:
            complaint_text = ""
            if c_api_key:
                try:
                    genai.configure(api_key=c_api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    c_prompt = f"""तुम्ही शासकीय कायदेशीर सल्लागार आहात. सर्वसामान्य नागरिक किंवा सामाजिक/राजकीय कार्यकर्त्याच्या भावना समजून घेऊन एक अत्यंत सविस्तर, प्रभावी आणि दणकेबाज मराठी तक्रार अर्ज तयार करा (३०० ते १००० शब्दांपर्यंत सविस्तर):
तक्रारकर्ता: {c_name}
पत्ता: {c_address}
मोबाईल: {c_phone}
कार्यालय/विभाग: {c_dept}
तक्रारीचा विषय व तपशील: {c_query}

महत्त्वाच्या सूचना:
- अर्जात कोणत्याही प्रकारच्या विनाकारण कोर्टकचेऱ्या किंवा उपोषणाच्या धमक्या देऊ नका, तर विनम्र परंतु अत्यंत खणखणीत आणि आक्रमक प्रशासकीय भाषेत (उदा. तात्काळ चौकशी, अधिकाऱ्यावर कारवाई किंवा निलंबन, काम पूर्ण करणे इ.) अर्ज बनवा.
- युजरचा हेतू आणि भावना शब्दात परिपूर्ण व स्पष्टपणे दिसावी."""
                        with st.spinner("AI सविस्तर तक्रार अर्ज तयार करत आहे..."):
                            res = model.generate_content(c_prompt)
                            complaint_text = res.text
                except Exception as e:
                    st.error(f"AI त्रुटी: {e}")
            
            # जर API Key नसेल तर उत्तम डिफॉल्ट टेम्पलेट
            if not complaint_text:
                complaint_text = f"""शासकीय तक्रार अर्ज व निवेदन

प्रति,
मा. अधिकारी / विभाग प्रमुख,
कार्यालयाचे नाव : {c_dept}
पत्ता : संबंधित कार्यालय.

विषय : अत्यंत महत्त्वाच्या समस्येबाबत व तात्काळ कारवाई करण्याबाबत तक्रार अर्ज.

महोदय / महोदया,

१. तक्रारकर्त्याचे पूर्ण नाव : {c_name}
२. तक्रारकर्त्याचा पत्ता : {c_address}
३. मोबाईल नंबर : {c_phone}
४. तक्रारीचा सविस्तर विषय व तपशील :
{c_query}

महोदय, वरील विषयानुसार आमच्या भागात निर्माण झालेल्या समस्येमुळे नागरिकांचे हाल होत आहेत. प्रशासनाच्या दुर्लक्षामुळे जनमानसात असंतोष पसरला आहे. वारंवार पाठपुरावा करूनही कारवाई होत नसल्यामुळे हा कायदेशीर तक्रार अर्ज सादर करावा लागत आहे.

तरी वरील विषयाबाबत तातडीने योग्य ती पाहणी करून तात्काळ कारवाई किंवा योग्य तो निर्णय घेण्यात यावा, ही विनंती. अन्यथा नियमांनुसार पुढील लोकतांत्रिक व कायदेशीर पाठपुरावा करण्यात येईल याची नोंद घ्यावी.

ठिकाण : छत्रपती संभाजीनगर
दिनांक : आजचा दिनांक

(तक्रारकर्त्याची स्वाक्षरी / अंगठा)
नांव: {c_name}
मोबाईल: {c_phone}"""

            st.success("तक्रार अर्ज यशस्वीरीत्या तयार झाला आहे!")
            st.text_area("तयार झालेला सविस्तर तक्रार अर्ज मसुदा:", value=complaint_text, height=350)
            
            c_pdf = generate_pdf(complaint_text)
            st.download_button("📥 तक्रार अर्ज PDF डाउनलोड करा", data=c_pdf, file_name=f"Complaint_{c_name}.pdf", mime="application/pdf")
            st.download_button("📄 Text (.txt) फाईल डाउनलोड करा", data=complaint_text, file_name=f"Complaint_{c_name}.txt", mime="text/plain")
