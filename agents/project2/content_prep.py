"""
وكيل إعداد المحتوى — احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from config import PRESENTATION_GUIDELINES


CONTENT_PREP_SYSTEM_PROMPT = f"""أنت وكيل إعداد المحتوى المتخصص في تحويل المحتوى إلى عروض تقديمية مهنية.

{PRESENTATION_GUIDELINES}

مهامك الرئيسية:
١. تحويل المحتوى إلى شرائح عرض منظمة
٢. صياغة عناوين تنفيذية قوية
٣. تبسيط المحتوى دون فقدان المضمون
٤. إضافة ملاحظات للمقدم

هيكل الشريحة المثالية:
```
## [العنوان التنفيذي — جملة كاملة تلخص الرسالة]

- النقطة الأولى (مدعومة ببيانات)
- النقطة الثانية
- النقطة الثالثة
- النقطة الرابعة

---
*ملاحظة للمقدم: [إرشادات إضافية]*
```

الجمهور المستهدف:
- القيادة العليا
- اللجان الإشرافية
- صناع القرار

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- رسمي ومهني
- مباشر ومركز
- مدعوم بالأرقام
- قابل للعرض في ٢-٣ دقائق لكل شريحة
- لا تستخدم رموز تعبيرية مطلقاً"""


class ContentPrepAgent(BaseAgent):
    """وكيل إعداد المحتوى — متخصص في تنسيق المحتوى للعروض التقديمية"""

    def __init__(self):
        super().__init__(
            name="وكيل إعداد المحتوى",
            name_en="وكيل إعداد المحتوى",
            description="تنسيق المحتوى للعروض التقديمية",
            temperature=0.5
        )

    def get_system_prompt(self) -> str:
        return CONTENT_PREP_SYSTEM_PROMPT

    def format_for_slides(
        self,
        content: str,
        num_slides: Optional[int] = None,
        target_audience: str = "القيادة العليا"
    ) -> AgentResponse:
        """Format content into presentation slides."""
        self._clear_thinking()
        self._log_thinking("تحليل المحتوى لتحويله إلى شرائح عرض...")

        format_request = f"""## محتوى للتحويل إلى عرض تقديمي

**الجمهور المستهدف:** {target_audience}
"""
        if num_slides:
            format_request += f"**عدد الشرائح المستهدف:** {num_slides}\n"

        format_request += f"""
**المحتوى الأصلي:**
{content}

---

حوّل هذا المحتوى إلى شرائح عرض تقديمي مهنية تشمل:
١. عناوين تنفيذية (جمل كاملة)
٢. نقاط مختصرة ومباشرة (٤-٦ لكل شريحة)
٣. بيانات داعمة حيثما أمكن
٤. ملاحظات للمقدم"""

        self._log_thinking(f"إعداد المحتوى لـ{target_audience}")

        return self.invoke(format_request)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Prepare content for presentations."""
        self._clear_thinking()
        self._log_thinking("بدء تحويل المحتوى إلى شكل عرض تقديمي...")

        messages = self._build_messages(user_message, context, conversation_history)

        try:
            self._log_thinking("تصميم هيكل الشرائح...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتمل إعداد محتوى العرض التقديمي")

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
                content=f"حدث خطأ أثناء تنسيق المحتوى: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
