from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import base64
from concurrent.futures import ThreadPoolExecutor
import asyncio
import time 

from pdf_extractor import extract_text_from_pdf
from rag_engine import RAGEngine
from ai_analyzer import AIAnalyzer
from template_builder import TemplateBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Roaster & Improver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGEngine()
rag.seed_initial_data()
analyzer = AIAnalyzer()
builder = TemplateBuilder()
executor = ThreadPoolExecutor(max_workers=2)

@app.post("/process-resume")
async def process_resume_endpoint(
    resume_file: UploadFile = File(..., description="ملف السيرة الذاتية بصيغة PDF"),
    job_description: str = Form(..., description="الوصف الوظيفي (Job Description)"),
    template_name: str = Form("professional", description="اسم القالب (Template Name)") 
):
    if not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="الملف المرفوع يجب أن يكون بصيغة PDF.")
        
    try:
        t0 = time.time() # بداية حساب الوقت الإجمالي
        pdf_bytes = await resume_file.read()
        
        # 1. استخراج النص
        logger.info("جاري استخراج النص من المستند...")
        t_start = time.time()
        resume_text = extract_text_from_pdf(pdf_bytes)
        logger.info(f"استخراج النص استغرق: {time.time() - t_start:.2f} ثانية")
        
        # ------ [طبقة الحماية الجديدة] ------
        # نتحقق مما إذا كان النص المستخرج فارغاً (بسبب أن الملف صورة أو لا يدعم النسخ)
        if not resume_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="عذراً! يبدو أن ملف الـ PDF عبارة عن صورة (Scanned Image) أو لا يحتوي على نصوص قابلة للتحديد. النظام لا يمكنه قراءته. يرجى رفع سيرة ذاتية بنصوص قابلة للنسخ."
            )
        # ------------------------------------

        original_word_count = len(resume_text.split())
        strict_word_limit = int(original_word_count * 1.15) 
        
        # 2. محرك RAG
        logger.info("جاري استرجاع نصائح ATS...")
        t_start = time.time()
        ats_context = rag.get_ats_context(job_description)
        logger.info(f"محرك RAG استغرق: {time.time() - t_start:.2f} ثانية")
        
        # 3. تحليل الذكاء الاصطناعي
        logger.info("جاري تحليل وتحسين النص عبر الذكاء الاصطناعي...")
        t_start = time.time()
        loop = asyncio.get_running_loop()
        improved_resume_data = await loop.run_in_executor(
            executor, 
            analyzer.analyze_and_improve, 
            resume_text, job_description, ats_context, strict_word_limit
        )
        logger.info(f"تحليل الذكاء الاصطناعي استغرق: {time.time() - t_start:.2f} ثانية")
        
        # 4. بناء الـ PDF
        logger.info(f"جاري بناء ملف PDF النهائي باستخدام القالب: {template_name}...")
        t_start = time.time()
        final_pdf_bytes = builder.build_pdf(improved_resume_data, template_name)
        logger.info(f"بناء الـ PDF استغرق: {time.time() - t_start:.2f} ثانية")
        
        pdf_base64_str = base64.b64encode(final_pdf_bytes).decode('utf-8')
        
        logger.info(f"العملية بالكامل استغرقت: {time.time() - t0:.2f} ثانية")
        
        # إرجاع النتيجة النهائية
        return JSONResponse(content={
            "pdf_base64": pdf_base64_str,
            "match_score": improved_resume_data.match_score,
            "missing_keywords": improved_resume_data.missing_keywords
        })
        
    except HTTPException:
        raise # إعادة رمي خطأ التحقق ليظهر للمستخدم في الواجهة
    except Exception as e:
        logger.error(f"فشل في معالجة السيرة الذاتية: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))