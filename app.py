import streamlit as st
import PyPDF2
import re
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Resume Parsing & Job Description",
    page_icon="📄",
    layout="centered"
)

# ---------------- APP TITLE ----------------
st.markdown("<h1 style='color:black; font-weight:bold;'>Resume Parsing & Job Description</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:gray;'>ATS-based Resume Screening & Ranking</h3>", unsafe_allow_html=True)

# ---------------- INPUTS ----------------
uploaded_file = st.file_uploader("📤 Upload Resume (PDF only)", type=["pdf"])
job_description = st.text_area("📝 Paste Job Description")

# Skill database
skills_db = [
    "python", "sql", "excel", "power bi", "tableau",
    "seo", "digital marketing", "google ads",
    "data analysis", "machine learning"
]

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(pdf_file):
    """Safely extract text from PDF"""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        except:
            continue
    return text.lower()

def extract_skills(text, skills):
    """Return list of skills found in text"""
    return [skill for skill in skills if re.search(r"\b" + skill + r"\b", text)]

def check_resume_template(text):
    """Check if resume contains at least 3 standard sections"""
    sections = ["education", "skills", "experience", "projects", "certifications"]
    count = sum(1 for section in sections if section in text)
    return count >= 3

# ---------------- ANALYSIS ----------------
if st.button("🔍 Analyze Resume"):
    if not uploaded_file or not job_description.strip():
        st.warning("⚠️ Please upload a resume and enter the job description")

    else:
        try:
            resume_text = extract_text_from_pdf(uploaded_file)
            jd_text = job_description.lower()

            # Card-like layout
            st.markdown("<div style='background-color:white; padding:20px; border-radius:12px; box-shadow:0px 4px 12px rgba(0,0,0,0.1)'>", unsafe_allow_html=True)

            # -------- TEMPLATE VALIDATION --------
            if not check_resume_template(resume_text):
                st.markdown("### ❌ Application Status")
                st.markdown("<p style='color:red; font-weight:bold;'>Rejected – Resume Template Not Standard</p>", unsafe_allow_html=True)
                st.write("Resume must contain sections like Education, Skills, Experience, etc.")

            else:
                # Extract skills
                resume_skills = extract_skills(resume_text, skills_db)
                jd_skills = extract_skills(jd_text, skills_db)

                matched = set(resume_skills) & set(jd_skills)
                missing = set(jd_skills) - set(resume_skills)

                score = int((len(matched) / len(jd_skills)) * 100) if jd_skills else 0

                # -------- RANKING --------
                if score >= 80:
                    st.success("🏆 Rank 1 – Highly Suitable")
                elif score >= 50:
                    st.warning("⭐ Rank 2 – Moderately Suitable")
                else:
                    st.error("⚠️ Rank 3 – Low Match")

                st.markdown("### ✅ Application Status")
                st.markdown("<p style='color:green; font-weight:bold;'>Accepted</p>", unsafe_allow_html=True)

                # -------- BAR CHART --------
                st.markdown("### 📊 ATS Score Analysis")
                chart_data = pd.DataFrame({
                    "Skills": ["Matched Skills", "Missing Skills"],
                    "Count": [len(matched), len(missing)]
                })
                st.bar_chart(chart_data.set_index("Skills"))

                st.write(f"**Final ATS Score:** {score}%")
                st.markdown("### ✅ Matched Skills")
                st.write(list(matched))
                st.markdown("### ❌ Missing Skills")
                st.write(list(missing))

            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error("❌ Error reading resume. Make sure it is a valid PDF.")
            st.write(e)
