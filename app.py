import streamlit as st
import pdfplumber
import docx
import requests
import os

# ---------------- SETTINGS ---------------- #
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

# ---------------- PARSER ---------------- #
def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        st.warning("Unsupported file type. Please upload PDF or DOCX.")
    return text.strip()

# ---------------- GROQ CALL ---------------- #
def analyze_with_groq(prompt):
    if not GROQ_API_KEY:
        return "Error: Missing GROQ API key."
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a professional career coach analyzing LinkedIn profiles."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            },
        )
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error connecting to Groq API: {str(e)}"

# ---------------- STREAMLIT UI ---------------- #
st.set_page_config(page_title="LinkedIn Profile Analyzer", layout="wide")
st.title("🧠 LinkedIn Profile Analyzer")

uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    resume_text = extract_text(uploaded_file)
    st.text_area("Extracted Resume Text", resume_text, height=250)
    
    if st.button("Analyze Resume"):
        with st.spinner("Analyzing resume with AI..."):
            prompt = (
                "Analyze this resume text as a LinkedIn profile. "
                "Extract key skills, summarize professional background, "
                "suggest headline ideas, and recommend improvements.\n\n"
                f"Resume:\n{resume_text}"
            )
            output = analyze_with_groq(prompt)
            st.subheader("💡 AI Analysis & Suggestions")
            st.write(output)
else:
    st.info("Please upload a resume to get started.")
st.markdown(
    """
    <hr style="border:1px solid #999;">
    <div style="text-align:center; color:#888; font-size:14px; margin-top:10px;">
        Made with ❤ by <b>GuruBrahma</b> | Powered by Python  🚀
    </div>
    """,
    unsafe_allow_html=True
)