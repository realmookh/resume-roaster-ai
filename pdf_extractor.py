import fitz  # PyMuPDF library for PDF processing (مكتبة لمعالجة ملفات المستندات المحمولة)
import base64
from typing import Optional

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    تستخرج جميع النصوص من ملف المستند المحمول (PDF).
    
    Args:
        pdf_bytes (bytes): البيانات الثنائية لملف السيرة الذاتية (The raw bytes of the PDF file).
        
    Returns:
        str: النص الكامل المستخرج من جميع الصفحات (The complete extracted text).
    """
    # فتح ملف الـ PDF من البيانات الثنائية (Bytes) مباشرة في الذاكرة دون حفظه على القرص الصلب
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    
    # المرور على جميع الصفحات واستخراج النص منها
    for page in doc:
        full_text += page.get_text()
        
    doc.close()
    return full_text

def extract_first_page_as_base64_image(pdf_bytes: bytes, zoom_factor: float = 2.0) -> str:
    """
    تقوم بتحويل الصفحة الأولى من المستند إلى صورة عالية الدقة وتشفيرها بصيغة Base64.
    سنرسل هذه الصورة المشفرة لاحقاً إلى نموذج الرؤية (Vision Model) لاستنساخ التصميم.
    
    Args:
        pdf_bytes (bytes): البيانات الثنائية لملف السيرة الذاتية (The raw bytes of the PDF).
        zoom_factor (float): معامل التكبير لزيادة دقة الصورة (Zoom factor to increase DPI/resolution).
        
    Returns:
        str: سلسلة نصية تمثل الصورة بتشفير Base64 (A Base64 encoded string of the image).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    if len(doc) == 0:
        doc.close()
        raise ValueError("ملف السيرة الذاتية فارغ ولا يحتوي على صفحات (The PDF document is empty).")
    
    # نأخذ الصفحة الأولى فقط لأنها عادة تحتوي على الهيكل والتصميم الأساسي
    page = doc[0]
    
    # نستخدم المصفوفة (Matrix) لتكبير الصفحة وزيادة جودة الصورة المنتجة
    matrix = fitz.Matrix(zoom_factor, zoom_factor)
    
    # التقاط صورة الصفحة (Pixmap)
    pix = page.get_pixmap(matrix=matrix)
    
    # تحويل الصورة إلى بيانات ثنائية بصيغة PNG (Portable Network Graphics - رسوميات الشبكة المحمولة)
    image_bytes = pix.tobytes("png")
    doc.close()
    
    # تشفير البيانات الثنائية إلى صيغة Base64 لتكون جاهزة للإرسال عبر واجهة برمجة التطبيقات (API)
    base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
    
    return base64_encoded