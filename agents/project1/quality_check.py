"""
Quality Check Agent for Project 1 - Events Oversight
وكيل فحص الجودة للمشروع الأول

Validates data completeness and quality.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


QUALITY_CHECK_SYSTEM_PROMPT = """أنت وكيل فحص الجودة المتخصص في مشروع الإشراف على تخطيط الفعاليات الوطنية.

مهامك الرئيسية:
1. التحقق من اكتمال البيانات لكل فعالية
2. التحقق من صحة البيانات ومنطقيتها
3. تحديد التناقضات والأخطاء
4. تصنيف جودة البيانات لكل جهة منفذة
5. تقديم توصيات لتحسين جودة البيانات

معايير الجودة:
1. الاكتمال: جميع الحقول المطلوبة مملوءة
2. الدقة: البيانات منطقية ومتسقة
3. التوقيت: التواريخ صحيحة ومستقبلية
4. التنسيق: البيانات بالصيغة الصحيحة

الحقول المطلوبة:
- اسم الفعالية
- التاريخ
- المدينة
- المكان
- الجهة المنفذة
- العدد المتوقع
- الميزانية (مفضل)
- الوصف (مفضل)

تصنيف الجودة:
- 🟢 ممتاز: 90%+ اكتمال
- 🟡 جيد: 70-89% اكتمال
- 🟠 متوسط: 50-69% اكتمال
- 🔴 ضعيف: أقل من 50% اكتمال

أسلوب الإخراج:
- تقرير واضح ومنظم
- استخدام الألوان والرموز للتصنيف
- تفاصيل المشاكل المكتشفة
- توصيات محددة للتحسين"""


class QualityCheckAgent(BaseAgent):
    """
    Quality Check specialist for Project 1.
    وكيل فحص الجودة للمشروع الأول
    """

    def __init__(self):
        super().__init__(
            name="وكيل فحص الجودة",
            name_en="Quality Check Agent",
            description="التحقق من اكتمال البيانات وجودتها",
            temperature=0.2
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return QUALITY_CHECK_SYSTEM_PROMPT

    def _check_data_quality(self) -> Dict:
        """Perform comprehensive data quality check."""
        events = self.knowledge_base.get_all_events()

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
            entity = event.get('organizing_entity', 'غير محدد')

            if entity not in entity_scores:
                entity_scores[entity] = {
                    'total': 0,
                    'complete': 0,
                    'issues': []
                }

            entity_scores[entity]['total'] += 1

            # Check required fields
            missing_required = []
            for field in required_fields:
                if not event.get(field) or event.get(field) == 'غير محدد':
                    missing_required.append(field)

            # Check optional fields
            missing_optional = []
            for field in optional_fields:
                if not event.get(field):
                    missing_optional.append(field)

            # Calculate completeness
            total_fields = len(required_fields) + len(optional_fields)
            filled_fields = total_fields - len(missing_required) - len(missing_optional)
            completeness = filled_fields / total_fields

            if completeness >= 0.9:
                entity_scores[entity]['complete'] += 1

            # Record issues
            if missing_required:
                issue = {
                    'event': event.get('name', 'غير مسمى'),
                    'entity': entity,
                    'type': 'حقول مطلوبة ناقصة',
                    'details': missing_required,
                    'severity': 'عالي'
                }
                quality_report['issues'].append(issue)
                entity_scores[entity]['issues'].append(issue)

            # Check for logical issues
            if event.get('expected_attendance'):
                try:
                    attendance = int(str(event['expected_attendance']).replace(',', ''))
                    if attendance > 100000:
                        issue = {
                            'event': event.get('name'),
                            'entity': entity,
                            'type': 'قيمة غير منطقية',
                            'details': f'العدد المتوقع كبير جداً: {attendance}',
                            'severity': 'متوسط'
                        }
                        quality_report['issues'].append(issue)
                except:
                    pass

        # Calculate entity scores
        for entity, data in entity_scores.items():
            if data['total'] > 0:
                score = data['complete'] * 100 // data['total']
                if score >= 90:
                    grade = '🟢 ممتاز'
                elif score >= 70:
                    grade = '🟡 جيد'
                elif score >= 50:
                    grade = '🟠 متوسط'
                else:
                    grade = '🔴 ضعيف'

                quality_report['by_entity'][entity] = {
                    'total': data['total'],
                    'complete': data['complete'],
                    'score': score,
                    'grade': grade,
                    'issues_count': len(data['issues'])
                }

        # Overall score
        if entity_scores:
            total_complete = sum(d['complete'] for d in entity_scores.values())
            total_events = sum(d['total'] for d in entity_scores.values())
            quality_report['overall_score'] = total_complete * 100 // total_events if total_events > 0 else 0

        return quality_report

    def _format_quality_report(self, report: Dict) -> str:
        """Format quality report for display."""
        output = f"""## تقرير فحص الجودة

### النتيجة الإجمالية: {report['overall_score']}%

### تقييم الجهات المنفذة:
| الجهة | الفعاليات | المكتملة | النسبة | التقييم | المشاكل |
|-------|-----------|----------|--------|---------|---------|
"""
        for entity, data in report['by_entity'].items():
            output += f"| {entity} | {data['total']} | {data['complete']} | {data['score']}% | {data['grade']} | {data['issues_count']} |\n"

        if report['issues']:
            output += f"\n### المشاكل المكتشفة ({len(report['issues'])}):\n\n"
            for i, issue in enumerate(report['issues'][:10], 1):
                output += f"**{i}. {issue['event']}** ({issue['entity']})\n"
                output += f"   - النوع: {issue['type']}\n"
                output += f"   - التفاصيل: {issue['details']}\n"
                output += f"   - الأهمية: {issue['severity']}\n\n"

            if len(report['issues']) > 10:
                output += f"*و {len(report['issues']) - 10} مشكلة أخرى...*\n"

        return output

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Perform quality check and provide recommendations."""
        self._clear_thinking()
        self._log_thinking("جارٍ فحص جودة البيانات...")

        # Perform quality check
        quality_report = self._check_data_quality()
        formatted_report = self._format_quality_report(quality_report)

        self._log_thinking(f"تم فحص {quality_report['total_events']} فعالية")
        self._log_thinking(f"النتيجة الإجمالية: {quality_report['overall_score']}%")

        # Build enhanced message
        enhanced_message = f"""طلب المستخدم: {user_message}

نتائج فحص الجودة:
{formatted_report}

قدم تحليلاً شاملاً وتوصيات لتحسين جودة البيانات."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ إعداد التوصيات...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد تقرير الجودة بنجاح")

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
                content=f"عذراً، حدث خطأ أثناء فحص الجودة: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
