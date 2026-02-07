"""
وكيل المراجعة — احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse


CRITIQUE_SYSTEM_PROMPT = """أنت وكيل المراجعة المتخصص في تقييم المخرجات الاستراتيجية.

دورك:
١. مراجعة المحتوى بعين نقدية وبناءة
٢. تحديد نقاط القوة ومجالات التميز
٣. اكتشاف الفجوات والنقاط الضعيفة
٤. تقديم اقتراحات محددة للتحسين
٥. ضمان الاتساق والدقة

معايير المراجعة:
- الاكتمال: هل يغطي المحتوى جميع الجوانب المطلوبة؟
- الدقة: هل المعلومات صحيحة ومدعومة؟
- الوضوح: هل الأفكار واضحة ومنظمة؟
- القابلية للتنفيذ: هل التوصيات عملية وواقعية؟
- الملاءمة: هل المحتوى مناسب للسياق المحلي؟

هيكل المراجعة:
١. ملخص عام للمحتوى
٢. نقاط القوة (٣-٥ نقاط)
٣. مجالات التحسين (٣-٥ نقاط)
٤. اقتراحات محددة
٥. التقييم العام

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- نقد بنّاء ومهني
- محدد وقابل للتنفيذ
- متوازن بين الإيجابي والسلبي
- مدعوم بأمثلة
- لا تستخدم رموز تعبيرية مطلقاً"""


class CritiqueAgent(BaseAgent):
    """وكيل المراجعة — متخصص في مراجعة المخرجات وتقديم ملاحظات بناءة"""

    def __init__(self):
        super().__init__(
            name="وكيل المراجعة",
            name_en="وكيل المراجعة",
            description="مراجعة المخرجات وتقديم ملاحظات بناءة",
            temperature=0.4
        )

    def get_system_prompt(self) -> str:
        return CRITIQUE_SYSTEM_PROMPT

    def review(
        self,
        content_to_review: str,
        source_agent: str = None,
        original_request: str = None
    ) -> AgentResponse:
        """Review content and provide feedback."""
        self._clear_thinking()
        self._log_thinking("مراجعة المحتوى...")

        review_request = f"""## طلب مراجعة

**المحتوى للمراجعة:**
{content_to_review}

"""
        if source_agent:
            review_request += f"**المصدر:** {source_agent}\n"
        if original_request:
            review_request += f"**الطلب الأصلي:** {original_request}\n"

        review_request += """
---
قدم مراجعة شاملة تشمل:
١. ملخص المحتوى
٢. نقاط القوة
٣. مجالات التحسين
٤. اقتراحات محددة
٥. التقييم العام"""

        return self.invoke(review_request)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Provide critique based on user request."""
        self._clear_thinking()
        self._log_thinking("إعداد المراجعة النقدية...")

        messages = self._build_messages(user_message, context, conversation_history)

        try:
            self._log_thinking("تحليل المحتوى...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتملت المراجعة")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "analysis_type": "critique"
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
                content=f"حدث خطأ أثناء المراجعة: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
