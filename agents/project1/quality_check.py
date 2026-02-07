"""
وكيل فحص الجودة — لجنة الفعاليات
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


QUALITY_CHECK_SYSTEM_PROMPT = """أنت وكيل فحص الجودة المتخصص في نظام لجنة الفعاليات.

مهامك الرئيسية:
١. التحقق من اكتمال البيانات لكل فعالية
٢. التحقق من دقة البيانات ومنطقيتها
٣. تحديد التناقضات والأخطاء
٤. تصنيف جودة البيانات لكل مدينة
٥. تقديم توصيات لتحسين جودة البيانات

المدن المستهدفة:
- الرياض
- جدة
- العلا
- عسير
- حاضرة الدمام

معايير الجودة:
١. الاكتمال: جميع الحقول المطلوبة معبأة
٢. الدقة: البيانات منطقية ومتسقة
٣. الحداثة: التواريخ صحيحة
٤. التنسيق: البيانات بالشكل الصحيح

الحقول المطلوبة:
- اسم الفعالية
- الجهة المسؤولة
- وصف الفعالية
- تاريخ البداية وتاريخ النهاية
- التصنيف والنوع
- المدينة
- حالة التضمين

تصنيف الجودة:
- ممتاز: اكتمال ٩٠% فأكثر
- جيد: اكتمال ٧٠-٨٩%
- متوسط: اكتمال ٥٠-٦٩%
- ضعيف: اكتمال أقل من ٥٠%

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- استخدم البيانات الفعلية فقط — لا تخترع أرقاماً
- إذا لم تتوفر معلومة، قل ذلك صراحة
- لا تستخدم رموز تعبيرية مطلقاً"""


class QualityCheckAgent(BaseAgent):
    """وكيل فحص الجودة — متخصص في التحقق من اكتمال البيانات وجودتها"""

    def __init__(self):
        super().__init__(
            name="وكيل فحص الجودة",
            name_en="وكيل فحص الجودة",
            description="التحقق من اكتمال البيانات وجودتها",
            temperature=0.2
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return QUALITY_CHECK_SYSTEM_PROMPT

    def _check_data_quality(self) -> Dict:
        """Perform comprehensive data quality check."""
        events = self.knowledge_base.get_all_events()

        required_fields = ['name', 'responsible_org', 'description', 'start_date', 'end_date', 'tier', 'type']
        optional_fields = ['duration_days', 'subcategory', 'funding', 'communication']

        quality_report = {
            'total_events': len(events),
            'by_city': {},
            'issues': [],
            'overall_score': 0
        }

        city_scores = {}

        for event in events:
            city = event.get('city', 'غير محدد')

            if city not in city_scores:
                city_scores[city] = {
                    'total': 0,
                    'complete': 0,
                    'issues': []
                }

            city_scores[city]['total'] += 1

            missing_required = []
            for field in required_fields:
                if not event.get(field):
                    missing_required.append(field)

            missing_optional = []
            for field in optional_fields:
                if not event.get(field):
                    missing_optional.append(field)

            total_fields = len(required_fields) + len(optional_fields)
            filled_fields = total_fields - len(missing_required) - len(missing_optional)
            completeness = filled_fields / total_fields if total_fields > 0 else 0

            if completeness >= 0.9:
                city_scores[city]['complete'] += 1

            if missing_required:
                field_labels = {
                    'name': 'اسم الفعالية',
                    'responsible_org': 'الجهة المسؤولة',
                    'description': 'وصف الفعالية',
                    'start_date': 'تاريخ البداية',
                    'end_date': 'تاريخ النهاية',
                    'tier': 'التصنيف',
                    'type': 'النوع',
                }
                missing_labels = [field_labels.get(f, f) for f in missing_required]
                issue = {
                    'event': event.get('name', 'بدون اسم'),
                    'city': city,
                    'type': 'حقول مطلوبة ناقصة',
                    'details': ', '.join(missing_labels),
                    'severity': 'عالية'
                }
                quality_report['issues'].append(issue)
                city_scores[city]['issues'].append(issue)

        for city, data in city_scores.items():
            if data['total'] > 0:
                score = data['complete'] * 100 // data['total']
                if score >= 90:
                    grade = 'ممتاز'
                elif score >= 70:
                    grade = 'جيد'
                elif score >= 50:
                    grade = 'متوسط'
                else:
                    grade = 'ضعيف'

                quality_report['by_city'][city] = {
                    'total': data['total'],
                    'complete': data['complete'],
                    'score': score,
                    'grade': grade,
                    'issues_count': len(data['issues'])
                }

        if city_scores:
            total_complete = sum(d['complete'] for d in city_scores.values())
            total_events = sum(d['total'] for d in city_scores.values())
            quality_report['overall_score'] = total_complete * 100 // total_events if total_events > 0 else 0

        return quality_report

    def _format_quality_report(self, report: Dict) -> str:
        """Format quality report for display."""
        output = f"""## تقرير فحص الجودة

### النتيجة الإجمالية: {report['overall_score']}%

### تقييم المدن:
| المدينة | الفعاليات | مكتملة | النسبة | التصنيف | المشكلات |
|---------|----------|--------|--------|---------|----------|
"""
        for city, data in sorted(report['by_city'].items()):
            output += f"| {city} | {data['total']} | {data['complete']} | {data['score']}% | {data['grade']} | {data['issues_count']} |\n"

        if report['issues']:
            output += f"\n### المشكلات المكتشفة ({len(report['issues'])}):\n\n"
            for i, issue in enumerate(report['issues'][:10], 1):
                output += f"**{i}. {issue['event']}** ({issue['city']})\n"
                output += f"   - النوع: {issue['type']}\n"
                output += f"   - التفاصيل: {issue['details']}\n"
                output += f"   - الخطورة: {issue['severity']}\n\n"

            if len(report['issues']) > 10:
                output += f"*و{len(report['issues']) - 10} مشكلات أخرى...*\n"

        return output

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Perform quality check and provide recommendations."""
        self._clear_thinking()
        self._log_thinking("فحص جودة البيانات...")

        quality_report = self._check_data_quality()
        formatted_report = self._format_quality_report(quality_report)

        self._log_thinking(f"تم فحص {quality_report['total_events']} فعالية")
        self._log_thinking(f"النتيجة الإجمالية: {quality_report['overall_score']}%")

        enhanced_message = f"""طلب المستخدم: {user_message}

نتائج فحص الجودة:
{formatted_report}

قدم تحليلاً شاملاً وتوصيات لتحسين جودة البيانات."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("إعداد التوصيات...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتمل تقرير فحص الجودة")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "quality_score": quality_report['overall_score'],
                "issues_found": len(quality_report['issues'])
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
                content=f"حدث خطأ أثناء فحص الجودة: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
