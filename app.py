import streamlit as st
import google.generativeai as genai
from datetime import datetime

# १. पेज कॉन्फिगरेशन
st.set_page_config(
    page_title="RTI व लीगल AI सहाय्यक (ChatGPT स्टाईल)",
    page_icon="⚖️",
    layout="wide"
)

# कस्टाईल UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700&display=swap');
* { font-family: 'Mukta', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stChatMessage { border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# २. API की कॉन्फिगरेशन
api_key = st.sidebar.text_input("🔑 Gemini API Key प्रविष्ट करा:", type="password")
if not api_key:
    api_key = st.secrets.get("GEMINI_API_KEY", "")

# AI मॉडेल सेटअप
SYSTEM_INSTRUCTION = """
तुम्ही एक उच्च दर्जाचे मराठी कायदेतज्ज्ञ व RTI सल्लागार AI आहात.
वापरकर्त्याला RTI (जोडपत्र अ, ब, क), ग्राहक मंच, न्यायालयीन याचिका किंवा शासकीय तक्रार अर्जांचे अचूक कायदेशीर मसुदे तयार करून द्या.
कायद्याची सुसंगत कलमे (उदा. RTI कलम ६(१), १९(१), १९(३), कलम २०, ग्राहक संरक्षण कायदा २०१९) वापरून परिपूर्ण मसुदा तयार करा.
"""

def get_ai_response(messages_history):
    if not api_key:
        return "कृपया आधी डाव्या बाजूला तुमची Gemini API Key टाका."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        # चॅट फॉरमॅट तयार करणे
        formatted_history = []
        for msg in messages_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})
        
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(messages_history[-1]["content"])
        return response.text
    except Exception as e:
        return f"त्रुटी: {str(e)}"

# ३. सेशन स्टेट (चॅट हिस्ट्री)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "नमस्कार! मी तुमचा RTI व न्यायालयीन AI सहाय्यक आहे. तुम्हाला कोणत्या विषयावर RTI अर्ज, प्रथम अपील किंवा तक्रार मसुदा बनवून हवा आहे?"
        }
    ]

# ४. साइडबार - क्विक अ‍ॅक्शन बटने
with st.sidebar:
    st.title("⚖️ लीगल टूल्स")
    st.markdown("खालीलपैकी कोणताही पर्याय निवडून त्वरित मसुदा मागू शकता:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 जोडपत्र 'अ'", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "मला माहितीचा अधिकार अधिनियम २००५ च्या कलम ६(१) नुसार जोडपत्र 'अ' चा संपूर्ण कायदेशीर नमुना तयार करून द्या."})
            st.rerun()
    with col2:
        if st.button("🔵 जोडपत्र 'ब'", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "माहिती वेळेत न मिळाल्यामुळे कलम १९(१) नुसार प्रथम अपील (जोडपत्र 'ब') चा मसुदा तयार करून द्या."})
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("🟠 जोडपत्र 'क'", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "राज्य माहिती आयोगाकडे दाखल करण्यासाठी कलम १९(३) नुसार द्वितीय अपील (जोडपत्र 'क') तयार करून द्या. कलम २० नुसार दंडाची मागणी समाविष्ट करा."})
            st.rerun()
    with col4:
        if st.button("🔴 शासकीय तक्रार", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "शासकीय कामातील दिरंगाई आणि गैरव्यवहाराबाबत जिल्हाधिकाऱ्यांना सादर करण्यासाठी कडक तक्रार अर्जाचा मसुदा तयार करा."})
            st.rerun()

    if st.button("🗑️ चॅट साफ करा (Clear Chat)", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "चॅट रीसेट केले आहे. नवीन विषयाचा तपशील सांगा."}
        ]
        st.rerun()

# ५. मुख्य चॅट इंटरफेस
st.title("💬 RTI व लीगल AI चॅट असिस्टंट")
st.caption("ChatGPT प्रमाणे थेट प्रश्न विचारा किंवा अर्जाचा कच्चा तपशील देऊन पक्का मसुदा मिळवा.")

# सर्व मागील मेसेज दाखवणे
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# वापरकर्त्याचे इनपुट
if prompt := st.chat_input("येथे तुमचा प्रश्न किंवा अर्जाचा तपशील लिहा..."):
    # १. युझर मेसेज UI मध्ये दाखवणे
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # २. AI कडून उत्तर मिळवणे
    with st.chat_message("assistant"):
        with st.spinner("कायदेशीर मसुदा तयार होत आहे..."):
            response_text = get_ai_response(st.session_state.messages)
            st.markdown(response_text)
            
    # ३. AI उत्तर हिस्ट्रीमध्ये सेव्ह करणे
    st.session_state.messages.append({"role": "assistant", "content": response_text})
