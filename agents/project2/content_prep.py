"""
Content Preparation Agent for Project 2 - Major Celebrations Planning
وكيل إعداد المحتوى للمشروع الثاني

Formats content for professional presentations.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from config import PRESENTATION_GUIDELINES


CONTENT_PREP_SYSTEM_PROMPT = f"""أنت وكيل إعداد المحتوى المتخصص في تحويل المحتوى إلى عروض تقديمية احترافية.

{PRESENTATION_GUIDELINES}

مهامك الرئيسية:
1. تحويل المحتوى إلى شرائح عرض منظمة
2. صياغة عناوين تنفيذية قوية
3. تبسيط المحتوى دون فقدان الجوهر
4. إضافة ملاحظات للمقدم

هيكل الشريحة المثالي:
```
## [العنوان التنفيذي - جملة كاملة تلخص الرسالة]

- النقطة الأولى (مدعومة ببيانات)
- النقطة الثانية
- النقطة الثالثة
- النقطة الرابعة

---
*ملاحظة للمقدم: [توجيهات إضافية]*
```

الجمهور المستهدف:
- قيادات حكومية عليا
- لجان إشرافية
- صناع قرار

أسلوب المحتوى:
- رسمي واحترافي
- مباشر ومركز
- مدعوم بالأرقام
- قابل للعرض في 2-3 دقائق لكل شريحة"""


class ContentPrepAgent(BaseAgent):
    """
    Content Preparation specialist for Project 2.
    وكيل إعداد المحتوى للمشروع الثاني
    """

    def __init__(self):
        super().__init__(
            name="وكيل إعداد المحتوى",
            name_en="Content Preparation Agent",
            description="تنسيق المحتوى للعروض التقديمية",
            temperature=0.5
        )

    def get_system_prompt(self) -> str:
        return CONTENT_PREP_SYSTEM_PROMPT

    def format_for_slides(
        self,
        content: str,
        num_slides: Optional[int] = None,
        target_audience: str = "قيادات حكومية"
    ) -> AgentResponse:
        """
        Format content into presentation slides.

        Args:
            content: The content to format
            num_slides: Optional target number of slides
            target_audience: Description of the audience

        Returns:
            AgentResponse with slide-formatted content
        """
        self._clear_thinking()
        self._log_thinking("تحليل المحتوى لتحويله إلى شرائح عرض...")

        format_request = f"""## المحتوى المطلوب تحويله لعرض تقديمي

**الجمهور المستهدف:** {target_audience}
"""
        if num_slides:
            format_request += f"**عدد الشرائح المستهدف:** {num_slides}\n"

        format_request += f"""
**المحتوى الأصلي:**
{content}

---

يرجى تحويل هذا المحتوى إلى شرائح عرض احترافية مع:
1. عناوين تنفيذية قوية (جمل كاملة)
2. نقاط موجزة ومباشرة (4-6 لكل شريحة)
3. بيانات داعمة حيث أمكن
4. ملاحظات للمقدم"""

        self._log_thinking(f"إعداد محتوى لـ {target_audience}")

        return self.invoke(format_request)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Prepare content for presentations."""
        self._clear_thinking()
        self._log_thinking("بدء تحويل المحتوى إلى تنسيق العرض التقديمي...")

        messages = self._build_messages(user_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ تصميم هيكل الشرائح...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد محتوى العرض التقديمي بنجاح")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "format": "presentation_slides"
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
                content=f"عذراً، حدث خطأ أثناء تنسيق المحتوى: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )


    def create_executive_summary(
        self,
        content: str,
        max_slides: int = 5
    ) -> AgentResponse:
        """Create an executive summary presentation."""
        self._clear_thinking()
        self._log_thinking("إعداد ملخص تنفيذي...")

        summary_request = f"""أعد ملخصاً تنفيذياً من {max_slides} شرائح كحد أقصى للمحتوى التالي:

{content}

الملخص التنفيذي يجب أن يشمل:
1. شريحة العنوان
2. الرسائل الرئيسية (1-2 شرائح)
3. التوصيات الأساسية (1-2 شرائح)
4. الخطوات التالية (1 شريحة)

ركز على أهم النقاط فقط للقيادة العليا."""

        return self.invoke(summary_request)
