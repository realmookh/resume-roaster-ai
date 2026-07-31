import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from models import ResumeAnalysisResult

load_dotenv()
logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("مفتاح OPENROUTER_API_KEY غير موجود.")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=45.0
        )
        self.model_name = "openai/gpt-4o-mini"

    def analyze_and_improve(self, resume_text: str, job_description: str, ats_context: str, original_word_count: int) -> ResumeAnalysisResult:
        
        system_prompt = f"""
        You are a STRICT Data Extractor and ATS (Applicant Tracking System - نظام تتبع المتقدمين) Resume Optimizer.
        Your job is to read the Original Resume Text, extract the ACTUAL facts, and ONLY inject keywords into the summary and bullet points.

        CRITICAL RULES (قواعد حرجة):
        1. STRICT EXTRACTION: Extract the applicant's REAL name, email, phone, and links from the provided text.
        2. ZERO HALLUCINATION (لا للتأليف أبدًا): DO NOT invent companies, universities, job titles, projects, or dates. If the user does not have an Education section, return an empty list [] for education. If they have no Experience, return [].
        3. ENHANCEMENT LIMITS: You may ONLY rewrite the `summary` and `achievements` to include missing keywords from the JD (Job Description - الوصف الوظيفي). You may categorize and add missing skills to the skills lists.
        4. MUST OUTPUT a valid JSON (JavaScript Object Notation - تدوين كائن جافا سكريبت) matching the schema exactly.

        ATS RULES TO FOLLOW:
        {ats_context}
        
        EXPECTED JSON FORMAT (Follow the instructions inside the values):
        {{
          "match_score": 100,
          "missing_keywords": ["keyword1"],
          "contact_info": {{
              "name": "EXTRACT_REAL_NAME_ONLY",
              "email": "EXTRACT_REAL_EMAIL_OR_LEAVE_EMPTY",
              "phone": "EXTRACT_REAL_PHONE_OR_LEAVE_EMPTY",
              "location": "EXTRACT_REAL_LOCATION_OR_LEAVE_EMPTY",
              "linkedin": "EXTRACT_REAL_LINKEDIN_OR_LEAVE_EMPTY"
          }},
          "summary": "Rewrite existing summary to include keywords, or leave empty if no summary exists.",
          "experience": [
            {{
              "job_title": "EXTRACT_ACTUAL_TITLE",
              "company_name": "EXTRACT_ACTUAL_COMPANY",
              "start_date": "ACTUAL_START",
              "end_date": "ACTUAL_END",
              "achievements": ["Enhanced achievement 1", "Enhanced achievement 2"]
            }}
          ],
          "education": [
            {{
              "degree": "EXTRACT_ACTUAL_DEGREE",
              "institution": "EXTRACT_ACTUAL_UNIVERSITY",
              "graduation_date": "ACTUAL_YEAR",
              "details": "ACTUAL_GPA_OR_RANKING"
            }}
          ],
          "projects": [
            {{
              "title": "EXTRACT_ACTUAL_PROJECT_NAME",
              "description": "EXTRACT_ACTUAL_DESCRIPTION"
            }}
          ],
          "courses": [
            {{
              "title": "EXTRACT_ACTUAL_COURSE_NAME",
              "institution": "EXTRACT_ACTUAL_PROVIDER",
              "date": "ACTUAL_DATE",
              "description": "EXTRACT_ACTUAL_DESCRIPTION"
            }}
          ],
          "soft_skills": ["Actual Skill 1", "Added JD Skill"],
          "technical_skills": ["Actual Tech Skill 1", "Added JD Tech Skill"],
          "languages": ["Actual Language"]
        }}
        """
        
        user_prompt = f"""
        Job Description:
        {job_description}
        
        Original Resume Text:
        {resume_text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0 # تم ضبط الحرارة على الصفر لمنع الإبداع والتأليف تماماً
            )
            
            raw_response = response.choices[0].message.content.strip()
            logger.info(f"AI Response Snippet: {raw_response[:300]}...") 
            
            validated_data = ResumeAnalysisResult.model_validate_json(raw_response)
            return validated_data
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {e}")
            raise