import logging
from jinja2 import Environment, BaseLoader
from xhtml2pdf import pisa
from io import BytesIO
from models import ResumeAnalysisResult

logger = logging.getLogger(__name__)

class TemplateBuilder:
    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())
        self.templates = {
            "abdulaziz_cv": self._get_abdulaziz_template()
        }

    def _get_abdulaziz_template(self) -> str:
        """
        قالب مطابق للتصميم المرجعي مع بيانات تواصل متغيرة وديناميكية.
        """
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <style>
            @page {
                size: a4 portrait;
                margin: 0.8cm 1.2cm;
            }
            body { 
                font-family: 'Helvetica', 'Arial', sans-serif; 
                font-size: 9.5pt; 
                line-height: 1.15; 
                color: #000; 
            }
            
            .header { text-align: center; margin-bottom: 10px; }
            .name { font-size: 14pt; font-weight: bold; margin-bottom: 4px; text-transform: uppercase; }
            .contact-info { font-size: 9pt; color: #222; }
            
            a { color: #000; text-decoration: none; border-bottom: 1px solid #000; }
            
            .section-title {
                font-size: 11pt;
                font-weight: bold;
                text-transform: uppercase;
                border-bottom: 1px solid #000;
                margin-top: 8px;
                margin-bottom: 4px;
                padding-bottom: 2px;
                page-break-after: avoid;
            }
            
            table { width: 100%; border-collapse: collapse; page-break-inside: avoid; }
            td { padding: 0; vertical-align: top; }
            .left-col { text-align: left; font-weight: bold;}
            .right-col { text-align: right; width: 150px; font-size: 9pt; }
            
            p { margin: 2px 0; text-align: justify; }
            ul { margin: 2px 0 2px 18px; padding: 0; }
            li { margin-bottom: 2px; text-align: justify; }
        </style>
        </head>
        <body>
            <!-- معلومات الاتصال الديناميكية -->
            <div class="header">
                <div class="name">{{ contact_info.name }}</div>
                <div class="contact-info">
                    {% if contact_info.email %}{{ contact_info.email }}{% endif %}
                    {% if contact_info.phone %} | {{ contact_info.phone }}{% endif %}
                    {% if contact_info.location %} | {{ contact_info.location }}{% endif %}
                    {% if contact_info.linkedin %} | <a href="https://{{ contact_info.linkedin }}">LinkedIn</a>{% endif %}
                </div>
            </div>

            <!-- الهدف (OBJECTIVE) -->
            {% if summary %}
            <div class="section-title">OBJECTIVE</div>
            <p>{{ summary }}</p>
            {% endif %}

            <!-- التعليم (EDUCATION) -->
            {% if education %}
            <div class="section-title">EDUCATION</div>
            {% for edu in education %}
            <table>
                <tr>
                    <td class="left-col">{{ edu.degree }}</td>
                    <td class="right-col">{% if edu.graduation_date %}Graduated: {{ edu.graduation_date }}{% endif %}</td>
                </tr>
                <tr>
                    <td colspan="2" style="font-style: italic;">{{ edu.institution }}</td>
                </tr>
                {% if edu.details %}
                <tr>
                    <td colspan="2" style="font-size: 9pt; padding-top: 2px; color: #333;">{{ edu.details }}</td>
                </tr>
                {% endif %}
            </table>
            {% endfor %}
            {% endif %}

            <!-- الخبرات (EXPERIENCE) -->
            {% if experience %}
            <div class="section-title">EXPERIENCE</div>
            {% for exp in experience %}
            <table>
                <tr>
                    <td class="left-col">{{ exp.job_title }}{% if exp.company_name %}, {{ exp.company_name }}{% endif %}</td>
                    <td class="right-col">{{ exp.start_date }} - {{ exp.end_date }}</td>
                </tr>
            </table>
            <ul>
                {% for bullet in exp.achievements %}
                <li>{{ bullet }}</li>
                {% endfor %}
            </ul>
            {% endfor %}
            {% endif %}

            <!-- المشاريع (PROJECTS) -->
            {% if projects %}
            <div class="section-title">PROJECTS</div>
            {% for proj in projects %}
            <table>
                <tr>
                    <td class="left-col">{{ proj.title }}</td>
                </tr>
            </table>
            <p>{{ proj.description }}</p>
            {% endfor %}
            {% endif %}

            <!-- الدورات (COURSES) -->
            {% if courses %}
            <div class="section-title">COURSES</div>
            {% for course in courses %}
            <table>
                <tr>
                    <td class="left-col">{{ course.title }}</td>
                    <td class="right-col">{{ course.date }}</td>
                </tr>
                {% if course.institution %}
                <tr>
                    <td colspan="2" style="font-style: italic; font-size: 9pt; color: #333;">{{ course.institution }}</td>
                </tr>
                {% endif %}
            </table>
            <p>{{ course.description }}</p>
            {% endfor %}
            {% endif %}

            <!-- المهارات (SKILLS) -->
            {% if soft_skills or technical_skills %}
            <div class="section-title">SKILLS</div>
            {% if soft_skills %}
            <p><strong>Soft skills:</strong> {{ soft_skills | join(' | ') }}</p>
            {% endif %}
            {% if technical_skills %}
            <p><strong>Technical Skills:</strong> {{ technical_skills | join(' | ') }}</p>
            {% endif %}
            {% endif %}

            <!-- اللغات (LANGUAGES) -->
            {% if languages %}
            <div class="section-title">LANGUAGES</div>
            <p>{{ languages | join(' | ') }}</p>
            {% endif %}
        </body>
        </html>
        """

    def build_pdf(self, resume_data: ResumeAnalysisResult, template_name: str = "abdulaziz_cv") -> bytes:
        try:
            html_template_str = self.templates.get("abdulaziz_cv")
            data_dict = resume_data.model_dump()
            
            template = self.jinja_env.from_string(html_template_str)
            rendered_html = template.render(**data_dict)
            
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_buffer)
            
            if pisa_status.err:
                raise Exception("حدث خطأ داخلي في مكتبة xhtml2pdf أثناء إنشاء الملف.")
            
            logger.info("تم إنشاء ملف PDF بنجاح باستخدام القالب المطور.")
            return pdf_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"حدث خطأ أثناء بناء القالب: {e}")
            raise