import streamlit as st
import requests
import logging
import base64

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# رابط الواجهة الخلفية (FastAPI Backend URL)
BACKEND_URL = "http://localhost:8000/process-resume"

def main():
    """
    الدالة الرئيسية لتشغيل واجهة Streamlit.
    The main function to run the Streamlit application.
    """
    st.set_page_config(
        page_title="Resume Roaster & Improver",
        page_icon="🔥",
        layout="centered"
    )
    
    st.title("🔥 Resume Roaster & Improver")
    st.markdown("""
    قم برفع سيرتك الذاتية (بصيغة PDF) وأدخل الوصف الوظيفي (Job Description). 
    سيقوم الذكاء الاصطناعي بتحليل الفجوات، استنساخ تصميمك الأصلي، وإعادة صياغة المحتوى لاجتياز أنظمة تتبع المتقدمين (ATS).
    """)
    
    st.divider()
    
    # 1. قسم إدخال البيانات
    uploaded_file = st.file_uploader(
        "رفع السيرة الذاتية (Upload Resume PDF)", 
        type=["pdf"],
        help="تأكد أن الملف يحتوي على نصوص قابلة للتحديد وليس صورة ممسوحة ضوئياً فقط."
    )
    
    job_description = st.text_area(
        "الوصف الوظيفي (Job Description)",
        height=200,
        placeholder="انسخ والصق الوصف الوظيفي هنا..."
    )
    
    # 2. زر بدء المعالجة
    if st.button("🚀 تحليل وتحسين السيرة الذاتية", type="primary"):
        if not uploaded_file or not job_description.strip():
            st.error("الرجاء رفع ملف السيرة الذاتية وإدخال الوصف الوظيفي!")
            return
            
        with st.spinner("جاري استنساخ التصميم وتحليل المحتوى... قد يستغرق هذا بضع ثوانٍ ⏳"):
            try:
                # تجهيز البيانات
                files = {"resume_file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"job_description": job_description}
                
                # إرسال الطلب
                response = requests.post(BACKEND_URL, files=files, data=data)
                
                if response.status_code == 200:
                    # تحويل الرد القادم من الخادم إلى قاموس بيانات JSON
                    response_data = response.json()
                    
                    # استخراج البيانات من الرد
                    match_score = response_data.get("match_score", 0)
                    missing_keywords = response_data.get("missing_keywords", [])
                    pdf_base64 = response_data.get("pdf_base64", "")
                    
                    # فك تشفير الـ PDF لإعادته إلى صيغته الأصلية (Bytes)
                    pdf_bytes = base64.b64decode(pdf_base64)
                    
                    st.success("✅ اكتملت المعالجة بنجاح! تم تصميم سيرتك الذاتية الجديدة.")
                    
                    # --- عرض النتائج في الواجهة الأمامية ---
                    st.subheader("📊 نتائج تحليل السيرة الذاتية (Resume Analysis Results)")
                    
                    # عرض نسبة التوافق
                    st.metric(label="نسبة التوافق (Match Score)", value=f"{match_score}%")
                    
                    # عرض الكلمات المفقودة
                    st.write("🔑 الكلمات المفتاحية المفقودة (Missing Keywords):")
                    if missing_keywords:
                        st.info("، ".join(missing_keywords)) 
                    else:
                        st.success("لا توجد كلمات مفقودة! سيرتك ممتازة.")

                    # --- زر التحميل ---
                    st.download_button(
                        label="📄 تحميل السيرة الذاتية المحسنة",
                        data=pdf_bytes,
                        file_name="Improved_Resume.pdf",
                        mime="application/pdf"
                    )
                else:
                    error_msg = response.json().get("detail", "حدث خطأ غير معروف.")
                    st.error(f"❌ خطأ من الخادم: {error_msg}")
                    logger.error(f"Backend error: {error_msg}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ لا يمكن الاتصال بالخادم. هل تأكدت من تشغيل FastAPI (main.py)؟")
            except Exception as e:
                st.error(f"❌ حدث خطأ غير متوقع: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}")

# تأكد أن هذا السطر هو آخر شيء في الملف، وبدون أي مسافات قبله
if __name__ == "__main__":
    main()