"""
وكيل إعداد التقارير — لجنة الفعاليات
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


REPORTING_SYSTEM_PROMPT = """أنت وكيل إعداد التقارير المتخصص في نظام لجنة الفعاليات.

مهامك الرئيسية:
١. تجميع النتائج والتحليلات من مصادر متعددة
٢. إعداد التقارير الدورية للجنة الإشرافية
٣. إعداد الملخصات التنفيذية للقيادة
٤. توثيق التقدم والتحديات والمخاطر

المدن المستهدفة:
- الرياض
- جدة
- العلا
- عسير
- حاضرة الدمام

الجمهور المستهدف:
- اللجنة الإشرافية العليا
- القيادة
- فريق التنسيق والمتابعة

هيكل التقرير:
١. الملخص التنفيذي (النقاط الرئيسية)
٢. الوضع الحالي (إحصائيات ونسب الإنجاز)
٣. التحديات والمخاطر
٤. الإجراءات المتخذة
٥. الخطوات التالية
٦. التوصيات

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- استخدم البيانات الفعلية فقط — لا تخترع أرقاماً
- إذا لم تتوفر معلومة، قل ذلك صراحة
- لا تستخدم رموز تعبيرية مطلقاً
- استخدم الأرقام والنسب المئوية
- أبرز النقاط الحرجة
- قدم توصيات قابلة للتنفيذ"""


class ReportingAgent(BaseAgent):
    """وكيل إعداد التقارير — متخصص في تجميع النتائج وإعداد تقارير اللجان"""

    def __init__(self):
        super().__init__(
            name="وكيل إعداد التقارير",
            name_en="وكيل إعداد التقارير",
            description="تجميع النتائج وإعداد تقارير اللجان",
            temperature=0.4
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return REPORTING_SYSTEM_PROMPT

    def _get_status_summary(self) -> Dict:
        """Get overall status summary."""
        events = self.knowledge_base.get_all_events()

        total = len(events)
        by_city = {}
        by_tier = {}
        by_inclusion = {}
        complete = 0

        required_fields = ['name', 'start_date', 'city', 'responsible_org', 'tier', 'type', 'description']

        for event in events:
            city = event.get('city', 'غير محدد')
            if city not in by_city:
                by_city[city] = {'total': 0, 'complete': 0}
            by_city[city]['total'] += 1

            tier = event.get('tier', 'غير محدد')
            by_tier[tier] = by_tier.get(tier, 0) + 1

            inclusion = event.get('inclusion_status', 'غير محدد')
            by_inclusion[inclusion] = by_inclusion.get(inclusion, 0) + 1

            is_complete = all(event.get(f) for f in required_fields)
            if is_complete:
                complete += 1
                by_city[city]['complete'] += 1

        return {
            'total_events': total,
            'complete_events': complete,
            'completion_rate': complete * 100 // total if total > 0 else 0,
            'by_city': by_city,
            'by_tier': by_tier,
            'by_inclusion': by_inclusion
        }

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Prepare reports based on user request."""
        self._clear_thinking()
        self._log_thinking("تجميع البيانات لإعداد التقرير...")

        status = self._get_status_summary()
        self._log_thinking(f"تم تجميع بيانات {status['total_events']} فعالية")

        status_text = f"""## ملخص الوضع الحالي

### الإحصائيات العامة:
- إجمالي الفعاليات: {status['total_events']}
- فعاليات مكتملة البيانات: {status['complete_events']}
- نسبة الاكتمال: {status['completion_rate']}%

### التوزيع حسب المدينة:
| المدينة | إجمالي | مكتمل | نسبة الاكتمال |
|---------|--------|--------|---------------|
"""
        for city, data in sorted(status['by_city'].items()):
            rate = data['complete'] * 100 // data['total'] if data['total'] > 0 else 0
            status_text += f"| {city} | {data['total']} | {data['complete']} | {rate}% |\n"

        status_text += "\n### التوزيع حسب التصنيف:\n"
        for tier, count in sorted(status['by_tier'].items(), key=lambda x: x[1], reverse=True):
            status_text += f"- {tier}: {count}\n"

        status_text += "\n### التوزيع حسب حالة التضمين:\n"
        for inc, count in sorted(status['by_inclusion'].items(), key=lambda x: x[1], reverse=True):
            status_text += f"- {inc}: {count}\n"

        enhanced_message = f"""طلب المستخدم: {user_message}

البيانات المتاحة:
{status_text}

أعد تقريراً مناسباً للجنة الإشرافية بناءً على هذه البيانات وطلب المستخدم."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("إعداد التقرير...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتمل إعداد التقرير")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "report_type": "committee_report",
                "data_summary": status
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
                content=f"حدث خطأ أثناء إعداد التقرير: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
