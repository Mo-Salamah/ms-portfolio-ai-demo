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
٤. تصنيف جودة البيانات لكل هيئة تطوير
٥. تقديم توصيات لتحسين جودة البيانات

معايير الجودة:
١. الاكتمال: جميع الحقول المطلوبة معبأة
٢. الدقة: البيانات منطقية ومتسقة
٣. الحداثة: التواريخ صحيحة ومستقبلية
٤. التنسيق: البيانات بالشكل الصحيح

الحقول المطلوبة:
- اسم الفعالية
- التاريخ
- المدينة
- الموقع
- هيئة التطوير
- الحضور المتوقع
- الميزانية (مفضل)
- الوصف (مفضل)

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

        entity_map = {
            "Implementing Entity A": "هيئة التطوير (أ)",
            "Implementing Entity B": "هيئة التطوير (ب)",
            "Implementing Entity C": "هيئة التطوير (ج)",
        }

        required_fields = ['name', 'date', 'city', 'venue', 'organizing_entity', 'expected_attendance']
        optional_fields = ['budget', 'description', 'category']

        quality_report = {
            'total_events': len(events),
            'by_entity': {},
            'issues': [],
            'overall_score': 0
        }

        entity_scores = {}

        for event in events:
            entity_raw = event.get('organizing_entity', 'غير محدد')
            entity = entity_map.get(entity_raw, entity_raw)

            if entity not in entity_scores:
                entity_scores[entity] = {
                    'total': 0,
                    'complete': 0,
                    'issues': []
                }

            entity_scores[entity]['total'] += 1

            missing_required = []
            for field in required_fields:
                if not event.get(field) or event.get(field) == 'Unspecified':
                    missing_required.append(field)

            missing_optional = []
            for field in optional_fields:
                if not event.get(field):
                    missing_optional.append(field)

            total_fields = len(required_fields) + len(optional_fields)
            filled_fields = total_fields - len(missing_required) - len(missing_optional)
            completeness = filled_fields / total_fields

            if completeness >= 0.9:
                entity_scores[entity]['complete'] += 1

            if missing_required:
                issue = {
                    'event': event.get('name', 'بدون اسم'),
                    'entity': entity,
                    'type': 'حقول مطلوبة ناقصة',
                    'details': missing_required,
                    'severity': 'عالية'
                }
                quality_report['issues'].append(issue)
                entity_scores[entity]['issues'].append(issue)

            if event.get('expected_attendance'):
                try:
                    attendance = int(str(event['expected_attendance']).replace(',', ''))
                    if attendance > 100000:
                        issue = {
                            'event': event.get('name'),
                            'entity': entity,
                            'type': 'قيمة غير واقعية',
                            'details': f'الحضور المتوقع مرتفع جداً: {attendance}',
                            'severity': 'متوسطة'
                        }
                        quality_report['issues'].append(issue)
                except:
                    pass

        for entity, data in entity_scores.items():
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

                quality_report['by_entity'][entity] = {
                    'total': data['total'],
                    'complete': data['complete'],
                    'score': score,
                    'grade': grade,
                    'issues_count': len(data['issues'])
                }

        if entity_scores:
            total_complete = sum(d['complete'] for d in entity_scores.values())
            total_events = sum(d['total'] for d in entity_scores.values())
            quality_report['overall_score'] = total_complete * 100 // total_events if total_events > 0 else 0

        return quality_report

    def _format_quality_report(self, report: Dict) -> str:
        """Format quality report for display."""
        output = f"""## تقرير فحص الجودة

### النتيجة الإجمالية: {report['overall_score']}%

### تقييم هيئات التطوير:
| الجهة | الفعاليات | مكتملة | النسبة | التصنيف | المشكلات |
|-------|----------|--------|--------|---------|----------|
"""
        for entity, data in report['by_entity'].items():
            output += f"| {entity} | {data['total']} | {data['complete']} | {data['score']}% | {data['grade']} | {data['issues_count']} |\n"

        if report['issues']:
            output += f"\n### المشكلات المكتشفة ({len(report['issues'])}):\n\n"
            for i, issue in enumerate(report['issues'][:10], 1):
                output += f"**{i}. {issue['event']}** ({issue['entity']})\n"
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
