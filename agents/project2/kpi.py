"""
KPI Agent for Project 2 - Major Celebrations Planning
وكيل مؤشرات الأداء للمشروع الثاني

Recommends KPIs and measurement methods for the celebration.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


KPI_SYSTEM_PROMPT = """أنت وكيل مؤشرات الأداء المتخصص في قياس نجاح الاحتفاليات الوطنية الكبرى.

خبراتك تشمل:
1. تصميم مؤشرات الأداء الرئيسية (KPIs)
2. تحديد طرق القياس والمتابعة
3. وضع المستهدفات الواقعية
4. ربط المؤشرات بالأهداف الاستراتيجية

فئات المؤشرات:
- الأثر الاقتصادي (الإنفاق، التوظيف، الاستثمارات)
- المشاركة المجتمعية (الزوار، المتطوعين، الرضا)
- التغطية الإعلامية (الوصول، التفاعل، السمعة)
- الإرث والاستدامة (البنية التحتية، القدرات، الثقافة)
- الكفاءة التشغيلية (الالتزام بالميزانية والجدول)

منهجية التصميم:
1. فهم الأهداف الاستراتيجية
2. تحديد المؤشرات الرئيسية والفرعية
3. تحديد طريقة القياس ومصدر البيانات
4. وضع المستهدفات والحدود
5. تحديد تكرار القياس والمسؤول

معايير المؤشر الجيد (SMART):
- محدد (Specific)
- قابل للقياس (Measurable)
- قابل للتحقيق (Achievable)
- ذو صلة (Relevant)
- محدد بزمن (Time-bound)"""


class KPIAgent(BaseAgent):
    """
    KPI specialist for Project 2.
    وكيل مؤشرات الأداء للمشروع الثاني
    """

    def __init__(self):
        super().__init__(
            name="وكيل مؤشرات الأداء",
            name_en="KPI Agent",
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

        # Group by category
        by_category = {}
        for kpi in kpis:
            cat = kpi.get('category', 'أخرى')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(kpi)

        for cat, cat_kpis in by_category.items():
            context += f"### {cat}\n\n"
            for kpi in cat_kpis:
                context += f"**{kpi.get('name', 'غير مسمى')}**\n"
                context += f"- الوصف: {kpi.get('description', 'لا يوجد')}\n"
                context += f"- الوحدة: {kpi.get('unit', 'غير محدد')}\n"
                context += f"- طريقة القياس: {kpi.get('measurement_method', 'غير محدد')}\n"
                context += f"- التكرار: {kpi.get('frequency', 'غير محدد')}\n"
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
        self._log_thinking("جارٍ تحليل طلب مؤشرات الأداء...")

        # Determine relevant category
        category_keywords = {
            "اقتصاد": "الأثر الاقتصادي",
            "مالي": "الأثر الاقتصادي",
            "مجتمع": "المشاركة المجتمعية",
            "زوار": "المشاركة المجتمعية",
            "إعلام": "التغطية الإعلامية",
            "تواصل": "التغطية الإعلامية",
            "إرث": "الإرث والاستدامة",
            "استدامة": "الإرث والاستدامة",
            "تشغيل": "الكفاءة التشغيلية",
            "ميزانية": "الكفاءة التشغيلية"
        }

        specific_category = None
        for keyword, category in category_keywords.items():
            if keyword in user_message:
                specific_category = category
                break

        kpi_context = self._get_kpi_context(specific_category)
        self._log_thinking(f"تم تحميل مؤشرات الأداء من قاعدة المعرفة")

        enhanced_message = f"""طلب المستخدم: {user_message}

مؤشرات الأداء المتاحة:
{kpi_context}

قدم توصيات مؤشرات أداء مناسبة مع شرح طريقة القياس والمستهدفات المقترحة."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ إعداد توصيات المؤشرات...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد توصيات المؤشرات بنجاح")

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
                content=f"عذراً، حدث خطأ: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )


    def design_kpi_framework(self, objectives: List[str]) -> AgentResponse:
        """Design a complete KPI framework for given objectives."""
        request = f"""صمم إطار مؤشرات أداء شامل للأهداف التالية:
{chr(10).join(f'- {obj}' for obj in objectives)}

يجب أن يشمل الإطار:
1. المؤشرات الرئيسية لكل هدف
2. طرق القياس ومصادر البيانات
3. المستهدفات المقترحة
4. آلية المتابعة والتقييم"""

        return self.invoke(request)
