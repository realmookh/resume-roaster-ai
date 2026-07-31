import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# إعداد التسجيل لتتبع الأخطاء
logger = logging.getLogger(__name__)

class LayoutCloner:
    """
    مسؤول عن استنساخ التصميم البصري للسيرة الذاتية باستخدام الذكاء الاصطناعي (Vision AI).
    Responsible for cloning the visual layout of the resume using Vision AI.
    """
    def __init__(self):
        """
        تهيئة عميل OpenRouter (Initialize OpenRouter client).
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("مفتاح OPENROUTER_API_KEY غير موجود في المتغيرات البيئية.")
        
        # تهيئة العميل للتواصل مع OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=120.0
        )
        # تحديد نموذج Gemini 1.5 Pro عبر OpenRouter
        self.model_name = "openai/gpt-4o-mini"

    def clone_layout(self, base64_image: str) -> str:
        """
        يأخذ صورة السيرة الذاتية ويولد كود HTML/CSS مطابق لها مع عناصر Jinja2.
        Takes the resume image (Base64) and generates matching HTML/CSS with Jinja2 placeholders.
        
        Args:
            base64_image (str): الصورة المشفرة للسيرة الذاتية (Base64 Encoded Image).
            
        Returns:
            str: كود HTML/CSS النهائي والخام (Raw HTML/CSS code).
        """
        # هندسة أوامر صارمة جداً لإجبار النموذج على إخراج كود برمجي فقط وبصيغة Jinja2
        # هندسة أوامر صارمة جداً لإجبار النموذج على إخراج كود برمجي فقط وبصيغة Jinja2
        prompt = """
        You are an Expert Front-End Developer. Your task is to precisely recreate the visual layout, colors, typography, and structure of the provided resume image using HTML and inline/internal CSS.
        
        CRITICAL RULES (قواعد حرجة):
        1. Output ONLY raw HTML code. Do NOT wrap the code in markdown formatting (like ```html). Do NOT add any conversational text before or after the code.
        2. Do NOT hardcode the user's personal text. You MUST use the following Jinja2 placeholders exactly as written, corresponding to our backend data models:
           - Profile Summary: {{ profile_summary }}
           - Skills: 
             <ul>
               {% for skill in skills %} <li>{{ skill }}</li> {% endfor %}
             </ul>
           - Experience (Iterate over the list): 
             {% for exp in experience_section %}
               <div class="job-entry">
                 <h3>{{ exp.job_title }} | {{ exp.company_name }}</h3>
                 <span class="duration">{{ exp.duration }}</span>
                 <ul>
                   {% for resp in exp.responsibilities %} <li>{{ resp }}</li> {% endfor %}
                 </ul>
               </div>
             {% endfor %}
           - Education (Iterate over the list):
             {% for edu in education_section %}
                <div class="edu-entry">
                  <h3>{{ edu.degree }}</h3>
                  <span>{{ edu.institution }} | {{ edu.graduation_year }}</span>
                </div>
             {% endfor %}
        3. Ensure the CSS makes it look as close to the original image as possible (margins, fonts, colors, multi-column layouts if present).
        "CRITICAL RULE: The PDF engine (xhtml2pdf) DOES NOT support CSS Flexbox or CSS Grid. To create columns or side-by-side layouts, you MUST use HTML <table>. If you use flexbox, the layout will break into multiple pages."
        """
        
        try:
            # إرسال الطلب عبر واجهة برمجة التطبيقات
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1 # درجة حرارة منخفضة لتقليل الإبداع العشوائي والتركيز على الدقة
            )
            
            html_output = response.choices[0].message.content.strip()
            
            # طبقة حماية إضافية (Fallback): إزالة علامات Markdown إذا عصى النموذج التعليمات
            if html_output.startswith("```"):
                html_output = html_output.split("\n", 1)[1]
                if html_output.endswith("```"):
                    html_output = html_output.rsplit("\n", 1)[0]
            if html_output.lower().startswith("html"):
                html_output = html_output.split("\n", 1)[1]
                
            return html_output.strip()
            
        except Exception as e:
            logger.error(f"حدث خطأ أثناء استنساخ التصميم (Error during layout cloning): {e}")
            raise