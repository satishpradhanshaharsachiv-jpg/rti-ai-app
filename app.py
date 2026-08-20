import io
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="RTI & तक्रार AI सहाय्यक", page_icon="🏛️", layout="centered")

# CSS: Manage App बटण लपवण्याचा प्रयत्न (हे पूर्णपणे जाणार नाही पण कमी गडद दिसेल)
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# PDF फंक्शन
def generate_pdf(content_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('NormalMarathi', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
    elements = [Paragraph(p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), normal_style) for p in content_text.split('\n')]
    doc.build(elements)
    buffer.seek(0)
    return buffer

# स्टेट मॅनेजमेंट
if 'final_text' not in st.session_state: st.session_state.final_text = ""
if 'paid' not in st.session_state: st.session_state.paid = False

st.markdown("<h1>🏛️ RTI व तक्रार AI सहाय्यक</h1>", unsafe_allow_html=True)

# बटन्स
col1, col2, col3 = st.columns(3)
if col1.button("🏠 मुख्य पान"): st.rerun()
if col2.button("📜 RTI अर्ज"): st.session_state.page = "rti"
if col3.button("📝 तक्रार"): st.session_state.page = "complaint"

# शेअर बटण (आता अधिक चांगल्या प्रकारे काम करेल)
st.markdown(f"""
    <button onclick="
        if (navigator.share) {{ navigator.share({{title: 'RTI ॲप', text: 'हे ॲप वापरा:', url: 'https://rti-ai-app-eydmnrwsmhvwhmryv7nn4v.streamlit.app/'}}); }}
        else {{ alert('लिंक कॉपी करा आणि शेअर करा'); }}
    " style="width:100%; padding:15px; background-color:#25D366; color:white; border:none; border-radius:10px; font-weight:bold;">
        📤 हे ॲप शेअर करा
    </button>
""", unsafe_allow_html=True)

st.markdown("---")

# पान निवड
page = st.session_state.get("page", "home")

# लॉजिक
if page == "rti":
    st.subheader("📜 RTI अर्ज तयार करा")
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    with st.form("rti_form"):
        doc_type = st.selectbox("अर्ज:", ["जोडपत्र अ (₹5)", "जोडपत्र ब (₹10)", "प्रथम अपील (₹10)"])
        name = st.text_input("नाव:")
        dept = st.text_input("विभाग:")
        query = st.text_area("तपशील:")
        submit = st.form_submit_button("🚀 अर्ज तयार करा")
        if submit:
            st.session_state.paid = False
            if api_key:
                genai.configure(api_key=api_key)
                st.session_state.final_text = genai.GenerativeModel("gemini-1.5-flash").generate_content(f"RTI: {name}, {dept}, {query}").text
            else:
                st.session_state.final_text = f"अर्ज: {doc_type}\nअर्जदार: {name}\nविभाग: {dept}\nतपशील: {query}"

elif page == "complaint":
    st.subheader("📝 तक्रार अर्ज तयार करा")
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")
    with st.form("comp_form"):
        name = st.text_input("नाव:")
        dept = st.text_input("कार्यालय:")
        query = st.text_area("तक्रार:")
        submit = st.form_submit_button("🚀 तक्रार तयार करा")
        if submit:
            st.session_state.paid = False
            if api_key:
                genai.configure(api_key=api_key)
                st.session_state.final_text = genai.GenerativeModel("gemini-1.5-flash").generate_content(f"तक्रार: {name}, {dept}, {query}").text
            else:
                st.session_state.final_text = f"प्रति, {dept}\nअर्जदार: {name}\nतक्रार: {query}"

# पीडीएफ पेमेंट आणि डाउनलोड भाग
if st.session_state.final_text:
    st.text_area("तुमचा मसुदा (मोफत):", value=st.session_state.final_text, height=200)
    
    st.markdown("---")
    st.markdown(f"### 💳 पीडीएफ डाउनलोड करण्यासाठी पेमेंट करा")
    st.info("यूपीआय आयडी: **satishpradhan3392@ybl**")
    
    if st.button("✅ मी ₹10 पेमेंट केले आहे"):
        st.session_state.paid = True
    
    if st.session_state.paid:
        st.download_button("📥 आता PDF डाउनलोड करा", data=generate_pdf(st.session_state.final_text), file_name="अर्ज.pdf")
    else:
        st.warning("पेमेंट केल्यावर 'मी पेमेंट केले आहे' या बटणावर क्लिक करा, मगच डाउनलोड बटण येईल.")

st.markdown("<p style='text-align:center;'>विकासक: सतीश अशोक प्रधान</p>", unsafe_allow_html=True)
