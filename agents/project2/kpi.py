"""
وكيل مؤشرات الأداء — احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


KPI_SYSTEM_PROMPT = """أنت وكيل مؤشرات الأداء المتخصص في قياس نجاح الاحتفاليات الوطنية الكبرى.

خبراتك تشمل:
١. تصميم مؤشرات الأداء الرئيسية (KPIs)
٢. تحديد طرق القياس والمتابعة
٣. وضع مستهدفات واقعية
٤. ربط المؤشرات بالأهداف الاستراتيجية

فئات المؤشرات:
- الأثر الاقتصادي (الإنفاق، التوظيف، الاستثمارات)
- المشاركة المجتمعية (الزوار، المتطوعون، الرضا)
- التغطية الإعلامية (الوصول، التفاعل، السمعة)
- الإرث والاستدامة (البنية التحتية، القدرات، الثقافة)
- الكفاءة التشغيلية (الالتزام بالميزانية والجدول)

منهجية التصميم:
١. فهم الأهداف الاستراتيجية
٢. تحديد المؤشرات الرئيسية والفرعية
٣. تحديد طريقة القياس ومصدر البيانات
٤. وضع المستهدفات والحدود
٥. تحديد دورية القياس والجهة المسؤولة

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- استخدم البيانات الفعلية فقط — لا تخترع أرقاماً
- إذا لم تتوفر معلومة، قل ذلك صراحة
- لا تستخدم رموز تعبيرية مطلقاً"""


class KPIAgent(BaseAgent):
    """وكيل مؤشرات الأداء — متخصص في توصية المؤشرات وتحديد طرق القياس"""

    def __init__(self):
        super().__init__(
            name="وكيل مؤشرات الأداء",
            name_en="وكيل مؤشرات الأداء",
            description="توصية مؤشرات الأداء وتحديد طرق القياس",
            temperature=0.4
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return KPI_SYSTEM_PROMPT

    def _get_kpi_context(self, category: str = None) -> str:
        """Get KPI data from knowledge base."""
        if category:
            kpis = self.knowledge_base.get_kpis_by_category(category)
        else:
            kpis = self.knowledge_base.get_all_kpis()

        context = "## مؤشرات الأداء المتاحة في قاعدة المعرفة:\n\n"

        by_category = {}
        for kpi in kpis:
            cat = kpi.get('category', 'أخرى')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(kpi)

        for cat, cat_kpis in by_category.items():
            context += f"### {cat}\n\n"
            for kpi in cat_kpis:
                context += f"**{kpi.get('name', 'بدون اسم')}**\n"
                context += f"- الوصف: {kpi.get('description', 'غير متاح')}\n"
                context += f"- الوحدة: {kpi.get('unit', 'غير محدد')}\n"
                context += f"- طريقة القياس: {kpi.get('measurement_method', 'غير محدد')}\n"
                context += f"- الدورية: {kpi.get('frequency', 'غير محدد')}\n"
                if kpi.get('benchmark_value'):
                    context += f"- القيمة المرجعية: {kpi['benchmark_value']}\n"
                context += "\n"

        return context

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Provide KPI recommendations."""
        self._clear_thinking()
        self._log_thinking("تحليل طلب مؤشرات الأداء...")

        category_keywords = {
            "اقتصاد": "Economic Impact",
            "مالي": "Economic Impact",
            "economic": "Economic Impact",
            "مجتمع": "Community Engagement",
            "زوار": "Community Engagement",
            "community": "Community Engagement",
            "إعلام": "Media Coverage",
            "تواصل": "Media Coverage",
            "media": "Media Coverage",
            "إرث": "Legacy and Sustainability",
            "استدامة": "Legacy and Sustainability",
            "legacy": "Legacy and Sustainability",
            "تشغيل": "Operational Efficiency",
            "ميزانية": "Operational Efficiency",
            "operation": "Operational Efficiency"
        }

        specific_category = None
        message_lower = user_message.lower()
        for keyword, category in category_keywords.items():
            if keyword in message_lower:
                specific_category = category
                break

        kpi_context = self._get_kpi_context(specific_category)
        self._log_thinking("تم تحميل مؤشرات الأداء من قاعدة المعرفة")

        enhanced_message = f"""طلب المستخدم: {user_message}

مؤشرات الأداء المتاحة:
{kpi_context}

قدم توصيات مؤشرات أداء مناسبة مع شرح طرق القياس والمستهدفات المقترحة."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("إعداد توصيات مؤشرات الأداء...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتملت توصيات مؤشرات الأداء")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "analysis_type": "kpi_recommendation",
                "category": specific_category
            }

            return AgentResponse(
                content=response_text,
                thinking=self._get_thinking_trace(),
                metadata=metadata,
                agent_name=self.name,
                agent_name_en=self.name_en
            )

        except Exception as e:
            self._log_thinking(f"حدث خطأ: {str(e)}")
            return AgentResponse(
                content=f"حدث خطأ أثناء المعالجة: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
