import streamlit as st
import google.generativeai as genai

# वेबसाईटचे नाव आणि लेआउट
st.set_page_config(page_title="RTI AI Assistant", page_icon="📜")

st.title("📜 AI RTI अर्ज सहाय्यक")
st.write("तुमची अडचण मराठीत टाका आणि १ सेकंदात अधिकृत RTI अर्ज तयार करा.")

# API Key इनपुट (साइडबारमध्ये)
api_key = st.sidebar.text_input("Gemini API Key टाका:", type="password")

# फॉर्म (युझरकडून माहिती घेण्यासाठी)
with st.form("rti_form"):
    user_name = st.text_input("तुमचे पूर्ण नाव:")
    user_address = st.text_area("तुमचा संपूर्ण पत्ता:")
    dept_name = st.text_input("सरकारी विभागाचे नाव (उदा. ग्रामपंचायत, नगरपरिषद, महसूल विभाग):")
    query = st.text_area("तुम्हाला नक्की काय माहिती/कागदपत्रे हवी आहेत? (साध्या मराठीत लिहा):")
    
    submitted = st.form_submit_button("RTI अर्ज तयार करा")

# अर्ज तयार करण्याची प्रक्रिया
if submitted:
    if not api_key:
        st.error("कृपया आधी Gemini API Key प्रविष्ट करा.")
    elif not user_name or not query:
        st.warning("कृपया तुमचे नाव आणि हवी असलेली माहिती भरा.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = f"""
            तुम्ही भारतीय माहिती अधिकार कायदा (RTI Act 2005) तज्ज्ञ आहात.
            खालील माहितीचा वापर करून जन माहिती अधिकाऱ्यासाठी एक कायदेशीर, अचूक आणि अधिकृत मराठी RTI अर्ज तयार करा.

            अर्जदाराचे नाव: {user_name}
            अर्जदाराचा पत्ता: {user_address}
            संबंधित कार्यालय/विभाग: {dept_name}
            मागितलेली माहिती: {query}

            अर्जाचा फॉरमॅट असा असावा:
            १. वर 'माहितीचा अधिकार अधिनियम २००५ च्या कलम ६(१) अन्वये अर्ज' असा विषय लिहा.
            २. प्रति, जन माहिती अधिकारी, {dept_name} यांना संबोधित करा.
            ३. मागितलेली माहिती मुद्देसूद (Point-by-Point) आणि स्पष्ट भाषेत मागा.
            ४. अर्जात कलम ६(३) (अर्ज योग्य विभागात वर्ग करणे) आणि कलम ७(१) (३० दिवसांत माहिती देणे) चा उल्लेख करा.
            ५. शेवटी १० रुपयांच्या कोर्ट फी स्टॅम्पचा उल्लेख, अर्जदाराचे नाव आणि सहीची जागा ठेवा.
            """

            with st.spinner("AI तुमचा कायदेशीर RTI अर्ज तयार करत आहे..."):
                response = model.generate_content(prompt)
                
                st.success("तुमचा RTI अर्ज यशस्वीपणे तयार झाला आहे!")
                
                # तयार झालेला अर्ज दाखवणे
                st.subheader("📄 तयार झालेला RTI मसुदा:")
                st.text_area("अर्ज इथे कॉपी करा:", value=response.text, height=350)
                
                # डाउनलोड बटण
                st.download_button(
                    label="📥 RTI अर्ज (.txt फाईल) डाउनलोड करा",
                    data=response.text,
                    file_name=f"RTI_Application_{user_name}.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"काहीतरी त्रुटी आली: {e}")
