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

# बटन्स
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
                📤 सर्व ॲप्सवर शेअर करा
            </button>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='font-size: 12px; color: #4B5563;'><b>विकासक:</b> सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)

# ५. RTI पान
elif page == "rti":
    st.markdown("<h2>📜 RTI अर्ज व अपील मसुदा तयार करा</h2>", unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🔑 AI सेटिंग्ज")
    api_key = st.sidebar.text_input("Gemini API Key टाका:", type="password")

    with st.form("rti_form"):
        doc_type = st.selectbox("अर्ज निवडा:", ["जोडपत्र अ", "जोडपत्र ब", "AI द्वारे सविस्तर मसुदा"])
        user_name = st.text_input("तुमचे पूर्ण नाव :")
        user_address = st.text_area("तुमचा संपूर्ण पत्ता :")
        dept_name = st.text_input("सरकारी विभाग :")
        query = st.text_area("तपशील :")
        submitted = st.form_submit_button("🚀 तयार करा")

    if submitted:
        final_text = "अर्ज तयार होत आहे..."
        if "AI" in doc_type and api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"सविस्तर RTI अर्ज बनवा: {user_name}, {user_address}, {dept_name}, {query}"
            res = model.generate_content(prompt)
            final_text = res.text
        else:
            final_text = f"अर्जदार: {user_name}\nविषय: {dept_name}\nतपशील: {query}"
        
        st.text_area("मसुदा:", value=final_text, height=300)
        pdf_data = generate_pdf(final_text)
        st.download_button("📥 PDF डाउनलोड", data=pdf_data, file_name="RTI_Arj.pdf")

# ६. तक्रार पान
elif page == "complaint":
    st.markdown("<h2>📝 शासकीय तक्रार अर्ज</h2>", unsafe_allow_html=True)
    
    c_api_key = st.sidebar.text_input("Gemini API Key टाका:", type="password")
    
    with st.form("complaint_form"):
        c_name = st.text_input("तुमचे नाव :")
        c_address = st.text_area("पत्ता :")
        c_phone = st.text_input("मोबाईल :")
        c_dept = st.text_input("विभाग :")
        c_query = st.text_area("तक्रारीचा विषय :")
        c_submitted = st.form_submit_button("🚀 तक्रार अर्ज तयार करा")

    if c_submitted:
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
                st.error(f"त्रुटी: {e}")
        
        if not complaint_text:
            complaint_text = f"प्रति, {c_dept}\nअर्जदार: {c_name}\nविषय: {c_query}"

        st.text_area("मसुदा:", value=complaint_text, height=300)
        c_pdf = generate_pdf(complaint_text)
        st.download_button("📥 PDF डाउनलोड", data=c_pdf, file_name="Complaint.pdf")
