import chromadb
from chromadb.config import Settings
import logging

# إعداد التسجيل (Logging) لتتبع الأخطاء أو العمليات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    """
    محرك (RAG) لإدارة قاعدة البيانات المتجهة (Vector Database).
    يقوم بتخزين واسترجاع أفضل ممارسات السير الذاتية وأنظمة تتبع المتقدمين (ATS).
    
    A RAG engine to manage the vector database. It stores and retrieves 
    resume best practices and ATS guidelines.
    """
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        تهيئة قاعدة بيانات ChromaDB المتجهة.
        
        Args:
            persist_directory (str): مسار المجلد الذي سيتم حفظ قاعدة البيانات فيه محلياً.
        """
        try:
            # تهيئة العميل (Client) لإنشاء قاعدة البيانات أو الاتصال بها إذا كانت موجودة
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # إنشاء أو الحصول على المجموعة (Collection) التي ستخزن البيانات
            # Collection تشبه الجداول (Tables) في قواعد البيانات التقليدية
            self.collection = self.client.get_or_create_collection(
                name="ats_best_practices",
                metadata={"description": "قواعد ونصائح لاجتياز أنظمة تتبع المتقدمين"}
            )
            logger.info("تم الاتصال بقاعدة بيانات ChromaDB بنجاح (Successfully connected to ChromaDB).")
        except Exception as e:
            logger.error(f"حدث خطأ أثناء تهيئة قاعدة البيانات: {e}")
            raise

    def seed_initial_data(self):
        """
        دالة مساعدة لإدخال بيانات أولية (Seed Data) إلى قاعدة البيانات المتجهة.
        يجب تشغيلها مرة واحدة فقط عند إعداد النظام.
        """
        # نتحقق إذا كانت المجموعة فارغة لنقوم بإضافة البيانات الأولية
        if self.collection.count() == 0:
            logger.info("المجموعة فارغة، جاري إدخال البيانات الأولية (Seeding initial data)...")
            
            documents = [
                "يجب أن تركز الخبرات العملية على الإنجازات القابلة للقياس باستخدام الأرقام، مثلاً: 'زيادة المبيعات بنسبة 20%'.",
                "يجب تجنب استخدام الكلمات الرنانة (Buzzwords) مثل 'مفكر خارج الصندوق' واستبدالها بمهارات تقنية واضحة.",
                "عند ذكر المهارات التقنية، يجب أن تتطابق تماماً مع الكلمات المفتاحية الموجودة في الوصف الوظيفي (Job Description).",
                "صيغة الفعل في الخبرات السابقة يجب أن تكون في الزمن الماضي (Past Tense)، وفي الوظيفة الحالية في الزمن المضارع.",
                "لا تستخدم جداول أو أعمدة معقدة في السيرة الذاتية لأن بعض أنظمة ATS تفشل في قراءتها."
            ]
            
            # ننشئ معرفات فريدة (IDs) لكل مستند نصي
            ids = [f"doc_{i}" for i in range(len(documents))]
            
            self.collection.add(
                documents=documents,
                ids=ids
            )
            logger.info("تم إضافة البيانات الأولية بنجاح.")
        else:
            logger.info("قاعدة البيانات تحتوي على بيانات مسبقاً، سيتم تخطي عملية الإدخال.")

    def get_ats_context(self, job_description: str, n_results: int = 3) -> str:
        """
        البحث في قاعدة البيانات المتجهة واسترجاع أقرب النصائح التي تناسب الوصف الوظيفي.
        
        Args:
            job_description (str): الوصف الوظيفي الذي نبحث بناءً عليه (Query).
            n_results (int): عدد النتائج (النصائح) المراد استرجاعها.
            
        Returns:
            str: نص مجمع يحتوي على النصائح ليتم تمريره كـ (Context) لنموذج الذكاء الاصطناعي.
        """
        try:
            results = self.collection.query(
                query_texts=[job_description],
                n_results=n_results
            )
            
            # استخراج النصوص من النتائج وتجميعها في نص واحد
            retrieved_docs = results['documents'][0]
            context = "\n".join(f"- {doc}" for doc in retrieved_docs)
            return context
        
        except Exception as e:
            logger.error(f"خطأ أثناء استرجاع البيانات (Error retrieving context): {e}")
            return ""

# كتلة للتجربة السريعة للتحقق من عمل الكود (Testing Block)
if __name__ == "__main__":
    rag = RAGEngine()
    rag.seed_initial_data()
    print("نتائج البحث التجريبي:")
    print(rag.get_ats_context("نبحث عن مهندس برمجيات ذو خبرة في تحسين الأداء"))