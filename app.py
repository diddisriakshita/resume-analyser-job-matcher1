from flask import Flask, render_template, request, redirect, url_for
import os
import re
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# --------------------------------------------------
# UPLOAD CONFIGURATION
# --------------------------------------------------

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


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
# SKILL DICTIONARY
# No external skills.json required
# --------------------------------------------------

skill_dictionary = {

    "Python": [
        "python",
        "py"
    ],

    "Machine Learning": [
        "machine learning",
        "ml"
    ],

    "Deep Learning": [
        "deep learning",
        "neural network",
        "neural networks"
    ],

    "TensorFlow": [
        "tensorflow"
    ],

    "PyTorch": [
        "pytorch"
    ],

    "Scikit-learn": [
        "scikit-learn",
        "sklearn"
    ],

    "NLP": [
        "nlp",
        "natural language processing"
    ],

    "Transformers": [
        "transformers",
        "hugging face"
    ],

    "Generative AI": [
        "generative ai",
        "genai",
        "generative artificial intelligence"
    ],

    "LLM": [
        "llm",
        "large language model",
        "large language models"
    ],

    "Prompt Engineering": [
        "prompt engineering",
        "prompt design"
    ],

    "RAG": [
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation"
    ],

    "Vector Database": [
        "vector database",
        "vector db",
        "vectordb"
    ],

    "Computer Vision": [
        "computer vision"
    ],

    "OpenCV": [
        "opencv",
        "open cv"
    ],

    "SQL": [
        "sql"
    ],

    "MySQL": [
        "mysql"
    ],

    "PostgreSQL": [
        "postgresql",
        "postgres"
    ],

    "Oracle": [
        "oracle",
        "oracle database"
    ],

    "Database Administration": [
        "database administration",
        "database administrator",
        "dba"
    ],

    "Backup and Recovery": [
        "backup and recovery",
        "database backup"
    ],

    "Performance Tuning": [
        "performance tuning",
        "query optimization"
    ],

    "Java": [
        "java",
        "core java"
    ],

    "OOP": [
        "oop",
        "object oriented programming",
        "object-oriented programming"
    ],

    "Data Structures": [
        "data structures",
        "data structure",
        "dsa"
    ],

    "REST API": [
        "rest api",
        "restful api",
        "rest api development"
    ],

    "Spring Boot": [
        "spring boot"
    ],

    "HTML": [
        "html",
        "html5"
    ],

    "CSS": [
        "css",
        "css3"
    ],

    "JavaScript": [
        "javascript",
        "js"
    ],

    "TypeScript": [
        "typescript",
        "ts"
    ],

    "React": [
        "react",
        "reactjs",
        "react.js"
    ],

    "Node.js": [
        "node.js",
        "nodejs",
        "node"
    ],

    "Kotlin": [
        "kotlin"
    ],

    "Android": [
        "android",
        "android development"
    ],

    "Flutter": [
        "flutter"
    ],

    "React Native": [
        "react native"
    ],

    "UI Design": [
        "ui design",
        "user interface design",
        "user interface"
    ],

    "Responsive Design": [
        "responsive design",
        "responsive web design"
    ],

    "AWS": [
        "aws",
        "amazon web services"
    ],

    "Azure": [
        "azure",
        "microsoft azure"
    ],

    "GCP": [
        "gcp",
        "google cloud platform"
    ],

    "Cloud": [
        "cloud",
        "cloud computing"
    ],

    "Linux": [
        "linux",
        "ubuntu"
    ],

    "Networking": [
        "networking",
        "computer networks",
        "network administration"
    ],

    "Docker": [
        "docker"
    ],

    "Kubernetes": [
        "kubernetes",
        "k8s"
    ],

    "Jenkins": [
        "jenkins"
    ],

    "CI/CD": [
        "ci/cd",
        "continuous integration",
        "continuous deployment",
        "continuous delivery"
    ],

    "Terraform": [
        "terraform"
    ],

    "MLflow": [
        "mlflow"
    ],

    "Monitoring": [
        "monitoring",
        "system monitoring",
        "application monitoring"
    ],

    "Cybersecurity": [
        "cybersecurity",
        "cyber security",
        "information security"
    ],

    "Network Security": [
        "network security"
    ],

    "Cloud Security": [
        "cloud security"
    ],

    "Firewalls": [
        "firewall",
        "firewalls"
    ],

    "SIEM": [
        "siem"
    ],

    "Splunk": [
        "splunk"
    ],

    "Incident Response": [
        "incident response",
        "security incident response"
    ],

    "Risk Management": [
        "risk management",
        "security risk management"
    ],

    "Software Testing": [
        "software testing",
        "software test"
    ],

    "Manual Testing": [
        "manual testing",
        "manual software testing"
    ],

    "Test Cases": [
        "test cases",
        "test case"
    ],

    "Jira": [
        "jira"
    ],

    "API Testing": [
        "api testing"
    ],

    "Selenium": [
        "selenium"
    ],

    "Test Automation": [
        "test automation",
        "automated testing",
        "automation testing"
    ],

    "ETL": [
        "etl",
        "extract transform load",
        "extract, transform, load"
    ],

    "Apache Spark": [
        "apache spark",
        "spark"
    ],

    "Data Warehousing": [
        "data warehousing",
        "data warehouse"
    ],

    "Statistics": [
        "statistics",
        "statistical analysis"
    ],

    "Pandas": [
        "pandas"
    ],

    "NumPy": [
        "numpy",
        "numpy library"
    ],

    "Data Visualization": [
        "data visualization",
        "data visualisation"
    ],

    "Excel": [
        "excel",
        "microsoft excel"
    ],

    "Power BI": [
        "power bi",
        "powerbi"
    ],

    "Tableau": [
        "tableau"
    ],

    "Business Analysis": [
        "business analysis",
        "business analyst"
    ],

    "Requirements Gathering": [
        "requirements gathering",
        "requirements analysis"
    ],

    "Communication": [
        "communication",
        "communication skills"
    ],

    "Agile": [
        "agile",
        "agile methodology"
    ],

    "Scrum": [
        "scrum"
    ],

    "Figma": [
        "figma"
    ],

    "UX Design": [
        "ux design",
        "user experience design",
        "user experience"
    ],

    "Wireframing": [
        "wireframing",
        "wireframes"
    ],

    "Prototyping": [
        "prototyping",
        "prototype design"
    ],

    "User Research": [
        "user research",
        "user research methods"
    ],

    "Adobe XD": [
        "adobe xd"
    ],

    "Product Management": [
        "product management",
        "product manager"
    ],

    "Product Strategy": [
        "product strategy"
    ],

    "Market Research": [
        "market research"
    ],

    "Analytics": [
        "analytics",
        "data analytics"
    ],

    "Problem Solving": [
        "problem solving",
        "problem-solving"
    ],

    "Git": [
        "git",
        "github",
        "gitlab"
    ]
}


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
# CREATE JOB DATA
# --------------------------------------------------

jobs = []

for role, required_skills in ROLE_REQUIREMENTS.items():

    for company in COMPANIES:

        skills = list(required_skills)

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

    try:

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

    except Exception as e:

        print("Resume extraction error:", e)
        return ""

    return text.lower()


# --------------------------------------------------
# EXTRACT SKILLS
# --------------------------------------------------

def extract_skills(text):

    detected_skills = []

    text_lower = text.lower()

    for skill, keywords in skill_dictionary.items():

        for keyword in keywords:

            pattern = r"(?<!\w)" + re.escape(
                keyword.lower()
            ) + r"(?!\w)"

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

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        vectors = vectorizer.fit_transform([
            resume_text,
            job_text
        ])

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(similarity * 100, 2)

    except Exception as e:

        print("TF-IDF error:", e)
        return 0


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def index():

    return render_template("index.html")


# --------------------------------------------------
# ROLE SELECTION PAGE
# --------------------------------------------------

@app.route("/roles")
def roles():

    roles_list = sorted(
        ROLE_REQUIREMENTS.keys()
    )

    return render_template(
        "roles.html",
        roles=roles_list
    )


# --------------------------------------------------
# RESUME ANALYSIS PAGE
# --------------------------------------------------

@app.route("/analyze")
def analyze():

    selected_role = request.args.get("role")

    if selected_role not in ROLE_REQUIREMENTS:

        return redirect(
            url_for("roles")
        )

    return render_template(
        "analyze.html",
        selected_role=selected_role
    )


# --------------------------------------------------
# ANALYZE RESUME
# --------------------------------------------------

@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():

    selected_role = request.form.get("role")

    if selected_role not in ROLE_REQUIREMENTS:

        return redirect(
            url_for("roles")
        )

    resume = request.files.get("resume")

    if resume is None:

        return "Please upload a resume."

    if resume.filename == "":

        return "Please select a resume."

    if not allowed_file(resume.filename):

        return "Only PDF and DOCX files are supported."

    filename = secure_filename(
        resume.filename
    )

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    resume.save(filepath)

    # ----------------------------------------------
    # Extract resume text
    # ----------------------------------------------

    resume_text = extract_resume_text(
        filepath
    )

    if not resume_text.strip():

        return (
            "Could not extract text from the resume. "
            "Please upload a text-based PDF or DOCX file."
        )

    # ----------------------------------------------
    # Detect skills
    # ----------------------------------------------

    detected_skills = extract_skills(
        resume_text
    )

    # ----------------------------------------------
    # Get jobs for selected role
    # ----------------------------------------------

    selected_jobs = [
        job for job in jobs
        if job["role"] == selected_role
    ]

    results = []

    # ----------------------------------------------
    # Compare resume with every company
    # ----------------------------------------------

    for job in selected_jobs:

        required_skills = job["skills"]

        matched_skills = [
            skill
            for skill in required_skills
            if skill in detected_skills
        ]

        missing_skills = [
            skill
            for skill in required_skills
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

        # Job text for TF-IDF
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

    # ----------------------------------------------
    # Sort by score
    # ----------------------------------------------

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
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(413)
def file_too_large(error):

    return (
        "Resume file is too large. "
        "Maximum size is 10 MB."
    ), 413


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

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
