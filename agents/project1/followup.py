"""
وكيل المتابعة والتواصل — لجنة الفعاليات
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


FOLLOWUP_SYSTEM_PROMPT = """أنت وكيل المتابعة والتواصل المتخصص في نظام لجنة الفعاليات.

مهامك الرئيسية:
١. تحديد المعلومات الناقصة من كل مدينة وجهة مسؤولة
٢. صياغة رسائل متابعة رسمية ومهنية
٣. ترتيب أولويات المتابعة حسب الأهمية والموعد النهائي
٤. اقتراح قنوات التواصل المناسبة

المدن المستهدفة:
- الرياض
- جدة
- العلا
- عسير
- حاضرة الدمام

أسلوب كتابة الرسائل:
- رسمي ومؤسسي
- واضح ومحدد في الطلبات
- يتضمن المواعيد النهائية
- يشكر الجهة على تعاونها
- يوضح أهمية استكمال البيانات

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- استخدم البيانات الفعلية فقط — لا تخترع أرقاماً
- إذا لم تتوفر معلومة، قل ذلك صراحة
- لا تستخدم رموز تعبيرية مطلقاً

شكل المخرجات:
- قائمة بالمعلومات الناقصة لكل مدينة/جهة
- مسودات رسائل جاهزة للإرسال
- جدول زمني مقترح للمتابعة"""


class FollowupAgent(BaseAgent):
    """وكيل المتابعة والتواصل — متخصص في تحديد الفجوات وصياغة رسائل المتابعة"""

    def __init__(self):
        super().__init__(
            name="وكيل المتابعة والتواصل",
            name_en="وكيل المتابعة والتواصل",
            description="تحديد المعلومات الناقصة وصياغة رسائل المتابعة",
            temperature=0.5
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return FOLLOWUP_SYSTEM_PROMPT

    def _identify_missing_info(self) -> Dict[str, List[Dict]]:
        """Identify missing information by city."""
        events = self.knowledge_base.get_all_events()

        missing_by_city = {}

        required_fields = {
            'name': 'اسم الفعالية',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'city': 'المدينة',
            'responsible_org': 'الجهة المسؤولة',
            'description': 'وصف الفعالية',
            'tier': 'التصنيف',
            'type': 'النوع',
        }

        for event in events:
            city = event.get('city', 'غير محدد')
            if city not in missing_by_city:
                missing_by_city[city] = []

            missing_fields = []
            for field, label in required_fields.items():
                if not event.get(field):
                    missing_fields.append(label)

            if missing_fields:
                missing_by_city[city].append({
                    'event_name': event.get('name', 'بدون اسم'),
                    'responsible_org': event.get('responsible_org', 'غير محدد'),
                    'missing_fields': missing_fields,
                    'inclusion_status': event.get('inclusion_status', 'غير محدد')
                })

        return missing_by_city

    def _format_missing_info_report(self, missing_by_city: Dict) -> str:
        """Format the missing info into a report."""
        report = "## تقرير المعلومات الناقصة\n\n"

        for city, events in sorted(missing_by_city.items()):
            report += f"### {city}\n"
            if not events:
                report += "جميع البيانات مكتملة\n\n"
            else:
                report += f"**{len(events)} فعاليات تحتاج استكمال:**\n\n"
                for event in events[:5]:
                    report += f"- **{event['event_name']}** ({event['responsible_org']})\n"
                    if event['missing_fields']:
                        report += f"  - حقول ناقصة: {', '.join(event['missing_fields'])}\n"
                    report += f"  - حالة التضمين: {event['inclusion_status']}\n"
                if len(events) > 5:
                    report += f"\n  *و{len(events) - 5} فعاليات أخرى...*\n"
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
        self._log_thinking("تحديد المعلومات الناقصة...")

        missing_by_city = self._identify_missing_info()
        missing_report = self._format_missing_info_report(missing_by_city)

        self._log_thinking("تم تحديد المعلومات الناقصة لكل مدينة")

        enhanced_message = f"""طلب المستخدم: {user_message}

تقرير المعلومات الناقصة:
{missing_report}

بناءً على هذه البيانات:
١. لخص الوضع الحالي
٢. رتب أولويات المتابعة
٣. صغ رسائل متابعة رسمية للجهات التي تحتاج استكمال بياناتها"""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("صياغة رسائل المتابعة...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتملت صياغة رسائل المتابعة")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cities_needing_followup": sum(1 for e in missing_by_city.values() if e)
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
