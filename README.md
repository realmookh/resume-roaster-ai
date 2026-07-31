Resume Roaster and Improver

Overview
A Full-Stack Application that relies on Artificial Intelligence (AI) to analyze Portable Document Format (PDF) resumes, compare them against a Job Description, and rewrite them to pass Applicant Tracking Systems (ATS). The project extracts the data and reconstructs it into a single, pre-designed, highly professional, and ATS-optimized template.

Key Features
Advanced Text Extraction: Accurate reading and processing of PDF files.
Retrieval-Augmented Generation (RAG): Uses a Vector Database with ChromaDB to store and retrieve resume writing best practices.
AI Analysis: Utilizes Large Language Models (LLMs) via the OpenRouter Application Programming Interface (API) to analyze gaps and add missing keywords with zero hallucination.
Document Reconstruction: Generates a final professional PDF on a predefined template using HyperText Markup Language (HTML) and Cascading Style Sheets (CSS) integrated with the Jinja2 template engine.

Tech Stack
Backend: FastAPI, Python
Frontend: Streamlit
AI and LLMs: OpenRouter API
Vector Database: ChromaDB
Processing Tools: PyMuPDF, Jinja2, xhtml2pdf

Local Setup

1. Clone the repository
git clone https://github.com/realmookh/resume-roaster-ai.git
cd resume-roaster-ai

2. Create Virtual Environment and Install Dependencies
uv venv
uv pip install -r requirements.txt

3. Activate the Virtual Environment
For Windows:
.venv\Scripts\activate

4. Environment Variables
Create a .env file in the main directory and add your API key:
OPENROUTER_API_KEY=your_api_key_here

5. Run the Application
Open two terminals:

First terminal for Backend:
uvicorn main:app --reload

Second terminal for Frontend:
streamlit run app.py

Author
Developed by Mukhtar Alabbadi