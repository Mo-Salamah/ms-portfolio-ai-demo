"""
Critique Agent for Project 2 - Major Celebrations Planning
وكيل المراجعة والنقد للمشروع الثاني

Reviews outputs and provides constructive feedback.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse


CRITIQUE_SYSTEM_PROMPT = """أنت وكيل المراجعة والنقد المتخصص في تقييم المخرجات الاستراتيجية.

دورك:
1. مراجعة المحتوى بعين ناقدة وبناءة
2. تحديد نقاط القوة والتميز
3. اكتشاف الفجوات والنقاط الضعيفة
4. تقديم اقتراحات محددة للتحسين
5. التأكد من الاتساق والدقة

معايير المراجعة:
- الاكتمال: هل يغطي المحتوى جميع الجوانب المطلوبة؟
- الدقة: هل المعلومات صحيحة ومدعومة؟
- الوضوح: هل الأفكار واضحة ومنظمة؟
- القابلية للتنفيذ: هل التوصيات عملية وواقعية؟
- الملاءمة: هل المحتوى مناسب للسياق المحلي؟

هيكل المراجعة:
1. ملخص عام للمحتوى
2. نقاط القوة (3-5 نقاط)
3. نقاط التحسين (3-5 نقاط)
4. اقتراحات محددة
5. التقييم العام

أسلوب النقد:
- بناء ومهني
- محدد وقابل للتنفيذ
- متوازن بين الإيجابي والسلبي
- مدعوم بأمثلة"""


class CritiqueAgent(BaseAgent):
    """
    Critique specialist for Project 2.
    وكيل المراجعة والنقد للمشروع الثاني
    """

    def __init__(self):
        super().__init__(
            name="وكيل المراجعة والنقد",
            name_en="Critique Agent",
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
        """
        Review content and provide feedback.

        Args:
            content_to_review: The content to be reviewed
            source_agent: Name of the agent that produced the content
            original_request: The original user request

        Returns:
            AgentResponse with critique
        """
        self._clear_thinking()
        self._log_thinking("جارٍ مراجعة المحتوى...")

        review_request = f"""## طلب المراجعة

**المحتوى المطلوب مراجعته:**
{content_to_review}

"""
        if source_agent:
            review_request += f"**المصدر:** {source_agent}\n"
        if original_request:
            review_request += f"**الطلب الأصلي:** {original_request}\n"

        review_request += """
---
قدم مراجعة شاملة تتضمن:
1. ملخص المحتوى
2. نقاط القوة
3. نقاط التحسين
4. اقتراحات محددة
5. التقييم العام"""

        return self.invoke(review_request)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Provide critique based on user request."""
        self._clear_thinking()
        self._log_thinking("جارٍ إعداد المراجعة النقدية...")

        messages = self._build_messages(user_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ تحليل المحتوى...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد المراجعة بنجاح")

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
                content=f"عذراً، حدث خطأ أثناء المراجعة: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )


    def quick_review(self, content: str) -> AgentResponse:
        """Provide a quick review focusing on key points."""
        request = f"""قدم مراجعة سريعة ومركزة للمحتوى التالي:

{content}

ركز على:
1. أهم 3 نقاط قوة
2. أهم 3 نقاط تحسين
3. توصية رئيسية واحدة"""

        return self.invoke(request)
