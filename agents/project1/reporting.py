"""
Reporting Agent for Project 1 - Events Oversight
وكيل إعداد التقارير للمشروع الأول

Compiles results and prepares committee reports.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


REPORTING_SYSTEM_PROMPT = """أنت وكيل إعداد التقارير المتخصص في مشروع الإشراف على تخطيط الفعاليات الوطنية.

مهامك الرئيسية:
1. تجميع النتائج والتحليلات من مختلف المصادر
2. إعداد تقارير دورية للجنة الإشرافية
3. إعداد ملخصات تنفيذية للقيادة
4. توثيق التقدم والتحديات والمخاطر

الجمهور المستهدف:
- اللجنة الإشرافية العليا
- القيادات الحكومية
- فريق التنسيق والمتابعة

هيكل التقارير:
1. الملخص التنفيذي (أهم النقاط)
2. الوضع الحالي (إحصائيات ونسب الإنجاز)
3. التحديات والمخاطر
4. الإجراءات المتخذة
5. الخطوات القادمة
6. التوصيات

أسلوب الكتابة:
- موجز ومباشر
- استخدام الأرقام والنسب
- تسليط الضوء على النقاط الحرجة
- توصيات قابلة للتنفيذ"""


class ReportingAgent(BaseAgent):
    """
    Reporting specialist for Project 1.
    وكيل إعداد التقارير للمشروع الأول
    """

    def __init__(self):
        super().__init__(
            name="وكيل إعداد التقارير",
            name_en="Reporting Agent",
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
        by_status = {}
        by_entity = {}
        complete = 0

        required_fields = ['name', 'date', 'city', 'venue', 'expected_attendance']

        for event in events:
            # Status
            status = event.get('status', 'غير محدد')
            by_status[status] = by_status.get(status, 0) + 1

            # Entity
            entity = event.get('organizing_entity', 'غير محدد')
            if entity not in by_entity:
                by_entity[entity] = {'total': 0, 'complete': 0}
            by_entity[entity]['total'] += 1

            # Check completeness
            is_complete = all(event.get(f) for f in required_fields)
            if is_complete:
                complete += 1
                by_entity[entity]['complete'] += 1

        return {
            'total_events': total,
            'complete_events': complete,
            'completion_rate': complete * 100 // total if total > 0 else 0,
            'by_status': by_status,
            'by_entity': by_entity
        }

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Prepare reports based on user request."""
        self._clear_thinking()
        self._log_thinking("جارٍ تجميع البيانات لإعداد التقرير...")

        # Get status summary
        status = self._get_status_summary()
        self._log_thinking(f"تم تجميع بيانات {status['total_events']} فعالية")

        # Format status for context
        status_text = f"""## ملخص الوضع الحالي

### الإحصائيات العامة:
- إجمالي الفعاليات: {status['total_events']}
- الفعاليات المكتملة البيانات: {status['complete_events']}
- نسبة الاكتمال: {status['completion_rate']}%

### التوزيع حسب الحالة:
"""
        for s, count in status['by_status'].items():
            status_text += f"- {s}: {count}\n"

        status_text += "\n### التوزيع حسب الجهة المنفذة:\n"
        for entity, data in status['by_entity'].items():
            rate = data['complete'] * 100 // data['total'] if data['total'] > 0 else 0
            status_text += f"- {entity}: {data['total']} فعاليات ({rate}% مكتملة)\n"

        # Build enhanced message
        enhanced_message = f"""طلب المستخدم: {user_message}

البيانات المتاحة:
{status_text}

أعد تقريراً مناسباً للجنة الإشرافية بناءً على هذه البيانات وطلب المستخدم."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ صياغة التقرير...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد التقرير بنجاح")

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
                content=f"عذراً، حدث خطأ أثناء إعداد التقرير: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )

    def prepare_committee_report(self) -> AgentResponse:
        """Prepare a standard committee report."""
        return self.invoke("أعد تقرير الوضع الحالي للجنة الإشرافية")

    def prepare_executive_summary(self) -> AgentResponse:
        """Prepare an executive summary."""
        return self.invoke("أعد ملخصاً تنفيذياً موجزاً للقيادة يتضمن أهم النقاط والتوصيات")
