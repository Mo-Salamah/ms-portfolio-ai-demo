"""
Follow-up Agent for Project 1 - Events Oversight
وكيل المتابعة والتواصل للمشروع الأول

Identifies missing information and drafts follow-up communications.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


FOLLOWUP_SYSTEM_PROMPT = """أنت وكيل المتابعة والتواصل المتخصص في مشروع الإشراف على تخطيط الفعاليات الوطنية.

مهامك الرئيسية:
1. تحديد المعلومات الناقصة من كل جهة منفذة
2. صياغة رسائل متابعة مهنية ومهذبة
3. تحديد أولويات المتابعة حسب الأهمية والموعد النهائي
4. اقتراح آليات التواصل المناسبة

الجهات المنفذة:
- الجهة المنفذة (أ)
- الجهة المنفذة (ب)
- الجهة المنفذة (ج)

الموعد النهائي: اجتماع اللجنة الإشرافية - 1 سبتمبر 2027

أسلوب صياغة الرسائل:
- رسمي ومهني
- واضح ومحدد في الطلبات
- يتضمن المواعيد النهائية
- يشكر الجهة على تعاونها
- يوضح أهمية استكمال البيانات

تنسيق الإخراج:
- قائمة بالمعلومات الناقصة لكل جهة
- مسودات رسائل جاهزة للإرسال
- جدول زمني مقترح للمتابعة"""


class FollowupAgent(BaseAgent):
    """
    Follow-up and Communication specialist for Project 1.
    وكيل المتابعة والتواصل للمشروع الأول
    """

    def __init__(self):
        super().__init__(
            name="وكيل المتابعة والتواصل",
            name_en="Follow-up Agent",
            description="تحديد المعلومات الناقصة وصياغة رسائل المتابعة",
            temperature=0.5
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return FOLLOWUP_SYSTEM_PROMPT

    def _identify_missing_info(self) -> Dict[str, List[Dict]]:
        """Identify missing information by entity."""
        events = self.knowledge_base.get_all_events()

        missing_by_entity = {
            "الجهة المنفذة (أ)": [],
            "الجهة المنفذة (ب)": [],
            "الجهة المنفذة (ج)": [],
        }

        required_fields = {
            'name': 'اسم الفعالية',
            'date': 'التاريخ',
            'city': 'المدينة',
            'venue': 'المكان',
            'expected_attendance': 'العدد المتوقع',
            'budget': 'الميزانية',
            'description': 'الوصف'
        }

        for event in events:
            entity = event.get('organizing_entity', 'غير محدد')
            if entity not in missing_by_entity:
                continue

            missing_fields = []
            for field, label in required_fields.items():
                if not event.get(field) or event.get(field) == 'غير محدد':
                    missing_fields.append(label)

            if missing_fields or event.get('status') == 'قيد التخطيط':
                missing_by_entity[entity].append({
                    'event_name': event.get('name', 'غير مسمى'),
                    'event_id': event.get('id', 'N/A'),
                    'missing_fields': missing_fields,
                    'status': event.get('status', 'غير محدد')
                })

        return missing_by_entity

    def _format_missing_info_report(self, missing_by_entity: Dict) -> str:
        """Format the missing info into a report."""
        report = "## تقرير المعلومات الناقصة\n\n"

        for entity, events in missing_by_entity.items():
            report += f"### {entity}\n"
            if not events:
                report += "✅ جميع البيانات مكتملة\n\n"
            else:
                report += f"⚠️ **{len(events)} فعاليات تحتاج استكمال:**\n\n"
                for event in events[:5]:
                    report += f"- **{event['event_name']}**\n"
                    if event['missing_fields']:
                        report += f"  - الحقول الناقصة: {', '.join(event['missing_fields'])}\n"
                    report += f"  - الحالة: {event['status']}\n"
                if len(events) > 5:
                    report += f"\n  *و {len(events) - 5} فعاليات أخرى...*\n"
                report += "\n"

        return report

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Identify missing info and draft follow-up messages."""
        self._clear_thinking()
        self._log_thinking("جارٍ تحديد المعلومات الناقصة...")

        # Get missing info
        missing_by_entity = self._identify_missing_info()
        missing_report = self._format_missing_info_report(missing_by_entity)

        self._log_thinking("تم تحديد المعلومات الناقصة لكل جهة")

        # Build context
        enhanced_message = f"""طلب المستخدم: {user_message}

تقرير المعلومات الناقصة الحالي:
{missing_report}

بناءً على هذه البيانات، قم بما يلي:
1. تلخيص الوضع الحالي
2. تحديد الأولويات
3. صياغة رسائل متابعة مهنية للجهات التي تحتاج استكمال بيانات"""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ صياغة رسائل المتابعة...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد رسائل المتابعة بنجاح")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "entities_needing_followup": sum(1 for e in missing_by_entity.values() if e)
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


    def draft_email(self, entity: str, specific_requests: List[str] = None) -> AgentResponse:
        """Draft a follow-up email for a specific entity."""
        self._clear_thinking()
        self._log_thinking(f"صياغة رسالة متابعة لـ {entity}...")

        missing_by_entity = self._identify_missing_info()
        entity_missing = missing_by_entity.get(entity, [])

        request = f"""صِغ رسالة متابعة رسمية لـ {entity}.

المعلومات الناقصة:
{self._format_missing_info_report({entity: entity_missing})}

{"الطلبات المحددة: " + ", ".join(specific_requests) if specific_requests else ""}

الرسالة يجب أن تكون:
- رسمية ومهنية
- واضحة في الطلبات
- تتضمن الموعد النهائي (1 سبتمبر 2027)
- مهذبة وتشكر الجهة على تعاونها"""

        return self.invoke(request)
