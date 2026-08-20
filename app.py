import io
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# १. पेज कॉन्फिगरेशन
st.set_page_config(page_title="RTI & तक्रार AI सहाय्यक", page_icon="🏛️", layout="centered")

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

# ३. स्टेट आणि सेशन मॅनेजमेंट
if 'rti_count' not in st.session_state:
    st.session_state.rti_count = 0
if 'complaint_count' not in st.session_state:
    st.session_state.complaint_count = 0
if 'is_upgraded' not in st.session_state:
    st.session_state.is_upgraded = False

query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"]

if 'page' not in st.session_state:
    st.session_state.page = "home"

st.markdown("<h1>🏛️ RTI व तक्रार AI सहाय्यक</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 15px; font-weight: bold; color: #4B5563;'>घरबसल्या सहज तयार करा कायदेशीर RTI अर्ज आणि शासकीय तक्रार अर्ज!</p>", unsafe_allow_html=True)
st.markdown("---")

# मोठी आणि रंगीत नेव्हिगेशन बटने
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
    st.markdown("### 📊 तुमच्या वापराची सद्यस्थिती:")
    st.markdown(f"""
    - **मोफत RTI अर्ज शिल्लक:** {max(0, 10 - st.session_state.rti_count)} / 10
    - **मोफत तक्रार अर्ज शिल्लक:** {max(0, 10 - st.session_state.complaint_count)} / 10
    """)
    
    if not st.session_state.is_upgraded:
        st.warning("⚠️ तुमच्या मोफत अर्जांची मर्यादा संपल्यानंतर ॲपच्या पुढील वापरासाठी शुल्क (Charges) लागू होईल.")
        if st.button("⭐ ॲप प्रो आवृत्तीमध्ये अपग्रेड करा (Upgrade)"):
            st.session_state.is_upgraded = True
            st.success("अभिनंदन! तुमचे ॲप यशस्वीरित्या 'प्रो' आवृत्तीत अपडेट झाले आहे.")
            st.rerun()
    else:
        st.success("✨ तुमचे ॲप प्रो (Pro) आवृत्तीवर सुरू आहे (अमर्याद सेवा चालू आहे).")

    st.markdown("---")
    st.markdown("<p style='font-size: 15px; font-weight: bold; color: #374151;'>🌐 हे ॲप मित्रांना व गरजू नागरिकांना शेअर करा:</p>", unsafe_allow_html=True)
    
    app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
    
    # कार्यक्षम शेअर बटण (शेवटी दिलेले)
    st.markdown(f"""
        <div style="text-align: center; margin: 25px 0;">
            <button onclick="
                if (navigator.share) {{
                    navigator.share({{
                        title: 'RTI व तक्रार अर्ज AI सहाय्यक',
                        text: 'घरबसल्या सहज आरटीआय आणि तक्रार अर्ज तयार करण्यासाठी हे ॲप वापरा:',
                        url: '{app_url}'
                    }});
                }} else {{
                    alert('तुमचा ब्राउझर शेअरिंगला सपोर्ट करत नाही. लिंक: {app_url}');
                }}
            " style="
                background: linear-gradient(135deg, #25D366, #128C7E); 
                color: white; 
                padding: 20px 40px; 
                border: none; 
                border-radius: 50px; 
                font-size: 20px; 
                font-weight: bold; 
                cursor: pointer; 
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 400px;
            ">
                📤 ॲप शेअर करा (WhatsApp इ.)
            </button>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='font-size: 12px; color: #4B5563;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)

# ५. RTI पान
elif page == "rti":
    st.markdown("<h2>📜 RTI अर्ज व अपील मसुदा तयार करा</h2>", unsafe_allow_html=True)
    
    # मर्यादा तपासणी
    if not st.session_state.is_upgraded and st.session_state.rti_count >= 10:
        st.error("❌ तुमची १० मोफत RTI अर्जांची मर्यादा संपली आहे. पुढे अर्ज करण्यासाठी मुख्य पानावरील 'अपग्रेड करा' या बटणावर क्लिक करा.")
    else:
        if not st.session_state.is_upgraded:
            st.markdown(f"<p style='color: #047857; font-weight: bold;'>शिल्लक मोफत RTI अर्ज: {10 - st.session_state.rti_count} / 10</p>", unsafe_allow_html=True)
            
        api_key = st.sidebar.text_input("Gemini API Key टाका:", type="password")

        with st.form("rti_form"):
            doc_type = st.selectbox("अर्ज निवडा:", ["जोडपत्र अ", "जोडपत्र ब", "AI द्वारे सविस्तर मसुदा"])
            user_name = st.text_input("तुमचे पूर्ण नाव :")
            user_address = st.text_area("तुमचा संपूर्ण पत्ता :")
            dept_name = st.text_input("सरकारी विभाग :")
            query = st.text_area("तपशील :")
            submitted = st.form_submit_button("🚀 तयार करा")

        if submitted:
            if not st.session_state.is_upgraded:
                st.session_state.rti_count += 1
                
            final_text = "अर्ज तयार होत आहे..."
            if "AI" in doc_type and api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"सविस्तर RTI अर्ज बनवा: {user_name}, {user_address}, {dept_name}, {query}"
                    res = model.generate_content(prompt)
                    final_text = res.text
                except Exception as e:
                    final_text = f"त्रुटी: {e}"
            else:
                final_text = f"अर्जदार: {user_name}\nपत्ता: {user_address}\nविषय: {dept_name}\nतपशील: {query}"
            
            st.session_state.rti_result = final_text

    if 'rti_result' in st.session_state and st.session_state.rti_result:
        st.text_area("मसुदा:", value=st.session_state.rti_result, height=300)
        pdf_data = generate_pdf(st.session_state.rti_result)
        st.download_button("📥 PDF डाउनलोड", data=pdf_data, file_name="RTI_Arj.pdf")

# ६. तक्रार पान
elif page == "complaint":
    st.markdown("<h2>📝 शासकीय तक्रार अर्ज</h2>", unsafe_allow_html=True)
    
    # मर्यादा तपासणी
    if not st.session_state.is_upgraded and st.session_state.complaint_count >= 10:
        st.error("❌ तुमची १० मोफत तक्रार अर्जांची मर्यादा संपली आहे. पुढे अर्ज करण्यासाठी मुख्य पानावरील 'अपग्रेड करा' या बटणावर क्लिक करा.")
    else:
        if not st.session_state.is_upgraded:
            st.markdown(f"<p style='color: #B91C1C; font-weight: bold;'>शिल्लक मोफत तक्रार अर्ज: {10 - st.session_state.complaint_count} / 10</p>", unsafe_allow_html=True)
            
        c_api_key = st.sidebar.text_input("Gemini API Key टाका:", type="password")
        
        with st.form("complaint_form"):
            c_name = st.text_input("तुमचे नाव :")
            c_address = st.text_area("पत्ता :")
            c_phone = st.text_input("मोबाईल :")
            c_dept = st.text_input("विभाग :")
            c_query = st.text_area("तक्रारीचा विषय :")
            c_submitted = st.form_submit_button("🚀 तक्रार अर्ज तयार करा")

        if c_submitted:
            if not st.session_state.is_upgraded:
                st.session_state.complaint_count += 1
                
            complaint_text = ""
            if c_api_key:
                try:
                    genai.configure(api_key=c_api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    c_prompt = f"""तक्रारकर्ता: {c_name}, विभाग: {c_dept}, विषय: {c_query}. 
                    अत्यंत प्रभावी आणि आक्रमक भाषेत तक्रार अर्ज बनवा."""
                    with st.spinner("AI तक्रार अर्ज तयार करत आहे..."):
                        res = model.generate_content(c_prompt)
                        complaint_text = res.text
                except Exception as e:
                    complaint_text = f"त्रुटी: {e}"
            
            if not complaint_text:
                complaint_text = f"प्रति, {c_dept}\nअर्जदार: {c_name}\nपत्ता: {c_address}\nविषय: {c_query}"

            st.session_state.complaint_result = complaint_text

    if 'complaint_result' in st.session_state and st.session_state.complaint_result:
        st.text_area("मसुदा:", value=st.session_state.complaint_result, height=300)
        c_pdf = generate_pdf(st.session_state.complaint_result)
        st.download_button("📥 PDF डाउनलोड", data=c_pdf, file_name="Complaint.pdf")
