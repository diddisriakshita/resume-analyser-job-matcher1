from flask import Flask, render_template, request, redirect, url_for
import os
import json
import re
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# --------------------------------------------------
# 15 COMPANIES
# --------------------------------------------------

COMPANIES = [
    "Google",
    "Microsoft",
    "Amazon",
    "IBM",
    "Accenture",
    "TCS",
    "Infosys",
    "Wipro",
    "Deloitte",
    "Cognizant",
    "Capgemini",
    "HCLTech",
    "Tech Mahindra",
    "Oracle",
    "Persistent Systems"
]


# --------------------------------------------------
# LOAD SKILLS
# --------------------------------------------------

with open("data/skills.json", "r", encoding="utf-8") as file:
    skill_dictionary = json.load(file)


# --------------------------------------------------
# ROLE-WISE REQUIREMENTS
# --------------------------------------------------

ROLE_REQUIREMENTS = {

    "AI Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "NLP",
        "SQL",
        "Git"
    ],

    "Machine Learning Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "SQL",
        "Git"
    ],

    "Data Scientist": [
        "Python",
        "Machine Learning",
        "Statistics",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "SQL",
        "Data Visualization"
    ],

    "Data Analyst": [
        "SQL",
        "Excel",
        "Python",
        "Pandas",
        "Statistics",
        "Power BI",
        "Tableau",
        "Data Visualization"
    ],

    "Data Engineer": [
        "Python",
        "SQL",
        "ETL",
        "Apache Spark",
        "Data Warehousing",
        "AWS",
        "Git",
        "Linux"
    ],

    "MLOps Engineer": [
        "Python",
        "Machine Learning",
        "Docker",
        "Kubernetes",
        "AWS",
        "CI/CD",
        "MLflow",
        "Git"
    ],

    "Generative AI Engineer": [
        "Python",
        "Generative AI",
        "LLM",
        "Prompt Engineering",
        "RAG",
        "Vector Database",
        "NLP",
        "Git"
    ],

    "NLP Engineer": [
        "Python",
        "NLP",
        "Deep Learning",
        "Transformers",
        "TensorFlow",
        "PyTorch",
        "Machine Learning",
        "SQL"
    ],

    "Computer Vision Engineer": [
        "Python",
        "Computer Vision",
        "OpenCV",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "Machine Learning",
        "NumPy"
    ],

    "Software Engineer": [
        "Java",
        "Python",
        "OOP",
        "Data Structures",
        "SQL",
        "Git",
        "REST API",
        "Problem Solving"
    ],

    "Full Stack Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "SQL",
        "REST API",
        "Git"
    ],

    "Frontend Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "TypeScript",
        "Git",
        "UI Design",
        "Responsive Design"
    ],

    "Backend Developer": [
        "Java",
        "Python",
        "Node.js",
        "SQL",
        "REST API",
        "Spring Boot",
        "Git",
        "Docker"
    ],

    "Mobile App Developer": [
        "Java",
        "Kotlin",
        "Android",
        "Flutter",
        "React Native",
        "REST API",
        "Git",
        "UI Design"
    ],

    "Cloud Engineer": [
        "AWS",
        "Azure",
        "GCP",
        "Cloud",
        "Linux",
        "Networking",
        "Docker",
        "Kubernetes"
    ],

    "DevOps Engineer": [
        "Linux",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "CI/CD",
        "AWS",
        "Terraform",
        "Git"
    ],

    "Site Reliability Engineer": [
        "Linux",
        "Cloud",
        "Kubernetes",
        "Docker",
        "Monitoring",
        "Python",
        "Networking",
        "CI/CD"
    ],

    "Cybersecurity Engineer": [
        "Cybersecurity",
        "Network Security",
        "Cloud Security",
        "Linux",
        "Firewalls",
        "SIEM",
        "Python",
        "Incident Response"
    ],

    "Security Analyst": [
        "Cybersecurity",
        "SIEM",
        "Splunk",
        "Network Security",
        "Incident Response",
        "Risk Management",
        "Linux",
        "Firewalls"
    ],

    "Database Administrator": [
        "SQL",
        "MySQL",
        "PostgreSQL",
        "Oracle",
        "Database Administration",
        "Backup and Recovery",
        "Performance Tuning",
        "Linux"
    ],

    "QA Engineer": [
        "Software Testing",
        "Manual Testing",
        "Test Cases",
        "Jira",
        "SQL",
        "API Testing",
        "Agile",
        "Git"
    ],

    "Automation Test Engineer": [
        "Selenium",
        "Test Automation",
        "Java",
        "Python",
        "API Testing",
        "SQL",
        "Jenkins",
        "Git"
    ],

    "Business Analyst": [
        "Business Analysis",
        "Requirements Gathering",
        "SQL",
        "Excel",
        "Power BI",
        "Communication",
        "Agile",
        "Jira"
    ],

    "UI/UX Designer": [
        "Figma",
        "UX Design",
        "UI Design",
        "Wireframing",
        "Prototyping",
        "User Research",
        "Adobe XD",
        "Communication"
    ],

    "Product Manager": [
        "Product Management",
        "Product Strategy",
        "Market Research",
        "Analytics",
        "Communication",
        "Agile",
        "Scrum",
        "Business Analysis"
    ]
}


# --------------------------------------------------
# COMPANY-SPECIFIC EXTRA REQUIREMENTS
# --------------------------------------------------

COMPANY_EXTRAS = {

    "Google": ["Problem Solving", "Git"],
    "Microsoft": ["Azure", "Git"],
    "Amazon": ["AWS", "Problem Solving"],
    "IBM": ["Cloud", "Agile"],
    "Accenture": ["Communication", "Agile"],
    "TCS": ["Java", "SQL"],
    "Infosys": ["Java", "SQL"],
    "Wipro": ["Cloud", "Agile"],
    "Deloitte": ["Communication", "Analytics"],
    "Cognizant": ["SQL", "Agile"],
    "Capgemini": ["Cloud", "Git"],
    "HCLTech": ["Linux", "Cloud"],
    "Tech Mahindra": ["Java", "Communication"],
    "Oracle": ["SQL", "Oracle"],
    "Persistent Systems": ["Python", "Git"]
}


# --------------------------------------------------
# CREATE JOB DATA AUTOMATICALLY
# --------------------------------------------------

jobs = []

for role, required_skills in ROLE_REQUIREMENTS.items():

    for company in COMPANIES:

        skills = list(required_skills)

        # Add company-specific skills
        for extra_skill in COMPANY_EXTRAS.get(company, []):
            if extra_skill not in skills:
                skills.append(extra_skill)

        jobs.append({
            "company": company,
            "role": role,
            "skills": skills,
            "description": (
                f"{company} {role} position requiring "
                + ", ".join(skills)
                + "."
            )
        })


# --------------------------------------------------
# EXTRACT RESUME TEXT
# --------------------------------------------------

def extract_resume_text(filepath):

    text = ""

    if filepath.lower().endswith(".pdf"):

        reader = PdfReader(filepath)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    elif filepath.lower().endswith(".docx"):

        document = Document(filepath)

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    return text.lower()


# --------------------------------------------------
# EXTRACT SKILLS
# --------------------------------------------------

def extract_skills(text):

    detected_skills = []

    text_lower = text.lower()

    for skill, keywords in skill_dictionary.items():

        for keyword in keywords:

            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

            if re.search(pattern, text_lower):

                detected_skills.append(skill)
                break

    return detected_skills


# --------------------------------------------------
# TF-IDF SIMILARITY
# --------------------------------------------------

def calculate_similarity(resume_text, job_text):

    if not resume_text.strip() or not job_text.strip():
        return 0

    vectorizer = TfidfVectorizer(stop_words="english")

    vectors = vectorizer.fit_transform([
        resume_text,
        job_text
    ])

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return round(similarity * 100, 2)


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# --------------------------------------------------
# ROLE PAGE
# --------------------------------------------------

@app.route("/roles")
def roles():

    roles_list = sorted(ROLE_REQUIREMENTS.keys())

    selected_role = request.args.get("role")

    companies = []

    if selected_role in ROLE_REQUIREMENTS:

        companies = [
            job for job in jobs
            if job["role"] == selected_role
        ]

    return render_template(
        "roles.html",
        roles=roles_list,
        selected_role=selected_role,
        companies=companies
    )


# --------------------------------------------------
# ANALYZE PAGE
# --------------------------------------------------

@app.route("/analyze")
def analyze():

    selected_role = request.args.get("role")

    companies = [
        job for job in jobs
        if job["role"] == selected_role
    ]

    return render_template(
        "analyze.html",
        selected_role=selected_role,
        companies=companies
    )


# --------------------------------------------------
# RESUME ANALYSIS
# --------------------------------------------------

@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():

    selected_role = request.form.get("role")

    resume = request.files.get("resume")

    if not resume:

        return "Please upload a resume."

    if resume.filename == "":

        return "Please select a resume."

    filename = resume.filename

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    resume.save(filepath)

    # Extract resume text
    resume_text = extract_resume_text(filepath)

    # Detect skills
    detected_skills = extract_skills(resume_text)

    # Get selected role jobs
    selected_jobs = [
        job for job in jobs
        if job["role"] == selected_role
    ]

    results = []

    for job in selected_jobs:

        required_skills = job["skills"]

        matched_skills = [
            skill for skill in required_skills
            if skill in detected_skills
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill not in detected_skills
        ]

        # Skill matching percentage
        if required_skills:

            skill_score = (
                len(matched_skills)
                / len(required_skills)
            ) * 100

        else:

            skill_score = 0

        # Job description
        job_text = (
            job["role"]
            + " "
            + job["description"]
            + " "
            + " ".join(required_skills)
        )

        # NLP similarity
        tfidf_score = calculate_similarity(
            resume_text,
            job_text
        )

        # Final score
        final_score = (
            skill_score * 0.7
            + tfidf_score * 0.3
        )

        final_score = round(
            min(final_score, 100),
            2
        )

        results.append({

            "company": job["company"],

            "role": job["role"],

            "required_skills": required_skills,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "skill_score": round(
                skill_score,
                2
            ),

            "tfidf_score": tfidf_score,

            "final_score": final_score
        })


    # Sort companies according to match score
    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return render_template(
        "results.html",

        role=selected_role,

        detected_skills=detected_skills,

        results=results
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    print("-------------------------------------")
    print("AI Resume Analyzer & Job Matcher")
    print("-------------------------------------")

    print(
        "Total Roles:",
        len(ROLE_REQUIREMENTS)
    )

    print(
        "Companies per Role:",
        len(COMPANIES)
    )

    print(
        "Total Job Records:",
        len(jobs)
    )

    app.run(
        debug=True
    )