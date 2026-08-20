import io
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- पेज कॉन्फिगरेशन ---
st.set_page_config(page_title="RTI & तक्रार सहाय्यक", page_icon="🏛️", layout="centered")

# --- कस्टम CSS (आधुनिक लूकसाठी) ---
st.markdown("""
<style>
    .stApp {background-color: #f8f9fa;}
    h1 {color: #1a73e8; text-align: center; font-family: sans-serif;}
    .card {background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .stButton>button {width: 100%; border-radius: 20px; font-weight: bold;}
    .share-btn {background: linear-gradient(135deg, #25D366, #128C7E); color: white; padding: 15px; border: none; border-radius: 50px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- PDF फंक्शन ---
def generate_pdf(content_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=16)
    elements = [Paragraph(p.replace('\n', '<br/>'), normal_style) for p in content_text.split('\n\n')]
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- नेव्हिगेशन लॉजिक ---
if 'page' not in st.session_state: st.session_state.page = "home"

st.markdown("<h1>🏛️ RTI व तक्रार AI सहाय्यक</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
if col1.button("🏠 मुख्य पान"): st.session_state.page = "home"
if col2.button("📜 RTI अर्ज"): st.session_state.page = "rti"
if col3.button("📝 तक्रार"): st.session_state.page = "complaint"

st.markdown("<hr>", unsafe_allow_html=True)

# --- मुख्य पान ---
if st.session_state.page == "home":
    st.markdown("<div class='card'><h3>👋 नमस्कार!</h3><p>हे ॲप तुम्हाला कायदेशीर अर्ज तयार करण्यात मदत करते. हे पूर्णपणे विनामूल्य आहे.</p></div>", unsafe_allow_html=True)
    
    app_url = "https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/"
    
    st.markdown(f"""
        <div style="text-align: center;">
            <button onclick="
                if (navigator.share) {{ navigator.share({{title: 'RTI ॲप', text: 'सहज अर्ज बनवा:', url: '{app_url}'}}); }}
            " class="share-btn">📤 मित्रांना शेअर करा</button>
        </div>
    """, unsafe_allow_html=True)

# --- RTI पान ---
elif st.session_state.page == "rti":
    st.subheader("📜 RTI अर्ज मसुदा")
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    
    with st.form("rti_form"):
        user_name = st.text_input("तुमचे नाव:")
        dept = st.text_input("सरकारी विभाग:")
        query = st.text_area("माहितीचा तपशील:")
        submit = st.form_submit_button("🚀 अर्ज तयार करा")
        
        if submit:
            if api_key:
                genai.configure(api_key=api_key)
                res = genai.GenerativeModel("gemini-1.5-flash").generate_content(f"RTI अर्ज तयार करा: {user_name}, विभाग: {dept}, तपशील: {query}")
                final_text = res.text
            else:
                final_text = f"अर्जदार: {user_name}\nविभाग: {dept}\nतपशील: {query}"
            
            st.code(final_text, language='text')
            st.download_button("📥 PDF डाउनलोड", data=generate_pdf(final_text), file_name="RTI.pdf")

# --- तक्रार पान ---
elif st.session_state.page == "complaint":
    st.subheader("📝 शासकीय तक्रार अर्ज")
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    
    with st.form("comp_form"):
        name = st.text_input("तुमचे नाव:")
        dept = st.text_input("कार्यालय:")
        query = st.text_area("तक्रारीचे कारण:")
        submit = st.form_submit_button("🚀 तक्रार तयार करा")
        
        if submit:
            if api_key:
                genai.configure(api_key=api_key)
                prompt = f"कायदेशीर व प्रभावी तक्रार अर्ज बनवा (आक्रमक भाषेत पण शिस्तबद्ध): {name}, विभाग: {dept}, विषय: {query}"
                final_text = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text
            else:
                final_text = f"प्रति, {dept}\nअर्जदार: {name}\nतक्रार: {query}"
                
            st.code(final_text, language='text')
            st.download_button("📥 PDF डाउनलोड", data=generate_pdf(final_text), file_name="Complaint.pdf")

st.markdown("<hr><p style='text-align:center;'>विकासक: सतीश अशोक प्रधान | छत्रपती संभाजीनगर</p>", unsafe_allow_html=True)
