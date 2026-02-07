"""
وكيل تحليل البيانات — لجنة الفعاليات
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


DATA_ANALYSIS_SYSTEM_PROMPT = """أنت وكيل تحليل البيانات المتخصص في نظام لجنة الفعاليات.

مهامك الرئيسية:
١. تحليل بيانات الفعاليات المستلمة من المدن المستهدفة
٢. إنتاج تقارير تحليلية وإحصائية
٣. تحديد الأنماط والتوزيعات في البيانات
٤. تقديم رؤى قابلة للتنفيذ

المدن المستهدفة:
- الرياض
- جدة
- العلا
- عسير
- حاضرة الدمام

أبعاد التحليل:
- التوزيع حسب المدينة
- التوزيع حسب التصنيف (Marquee, Tier 1, Tier 2, Tier 3)
- التوزيع حسب النوع (أعمال, ترفيه)
- التوزيع حسب الجهة المسؤولة
- حالة التضمين (تضمن, لن تضمن, تحسب بدون تضمين)
- الفترة الزمنية والمدة

أسلوب التحليل:
- استخدم الجداول للمقارنات
- قدم الأرقام والنسب المئوية
- صنف الفعاليات حسب النوع والجهة والمدينة
- حدد الفجوات في البيانات

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- استخدم البيانات الفعلية فقط — لا تخترع أرقاماً
- إذا لم تتوفر معلومة، قل ذلك صراحة
- لا تستخدم رموز تعبيرية مطلقاً

شكل المخرجات:
- عناوين واضحة
- جداول منظمة
- ملخص تنفيذي في البداية
- توصيات في النهاية"""


class DataAnalysisAgent(BaseAgent):
    """وكيل تحليل البيانات — متخصص في تحليل بيانات الفعاليات"""

    def __init__(self):
        super().__init__(
            name="وكيل تحليل البيانات",
            name_en="وكيل تحليل البيانات",
            description="تحليل بيانات الفعاليات وإنتاج التقارير التحليلية",
            temperature=0.3
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return DATA_ANALYSIS_SYSTEM_PROMPT

    def _get_events_summary(self) -> str:
        """Get a summary of events data for analysis."""
        events = self.knowledge_base.get_all_events()

        total = len(events)
        by_city = {}
        by_type = {}
        by_tier = {}
        by_org = {}
        by_inclusion = {}
        incomplete = []

        for event in events:
            city = event.get('city', 'غير محدد')
            by_city[city] = by_city.get(city, 0) + 1

            event_type = event.get('type', 'غير محدد')
            if event_type:
                by_type[event_type] = by_type.get(event_type, 0) + 1

            tier = event.get('tier', 'غير محدد')
            if tier:
                by_tier[tier] = by_tier.get(tier, 0) + 1

            org = event.get('responsible_org', 'غير محدد')
            if org:
                by_org[org] = by_org.get(org, 0) + 1

            inclusion = event.get('inclusion_status', 'غير محدد')
            if inclusion:
                by_inclusion[inclusion] = by_inclusion.get(inclusion, 0) + 1

            required_fields = ['name', 'start_date', 'city', 'responsible_org', 'tier', 'type']
            missing = [f for f in required_fields if not event.get(f)]
            if missing:
                incomplete.append({
                    'name': event.get('name', 'بدون اسم'),
                    'city': city,
                    'missing': missing
                })

        summary = f"""## ملخص بيانات الفعاليات

### الإجمالي: {total} فعالية

### التوزيع حسب المدينة:
| المدينة | العدد | النسبة |
|---------|-------|--------|
"""
        for city, count in sorted(by_city.items(), key=lambda x: x[1], reverse=True):
            pct = count * 100 // total if total > 0 else 0
            summary += f"| {city} | {count} | {pct}% |\n"

        summary += f"""
### التوزيع حسب التصنيف:
| التصنيف | العدد |
|---------|-------|
"""
        for tier, count in sorted(by_tier.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {tier} | {count} |\n"

        summary += f"""
### التوزيع حسب النوع:
| النوع | العدد |
|-------|-------|
"""
        for event_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {event_type} | {count} |\n"

        summary += f"""
### التوزيع حسب حالة التضمين:
| الحالة | العدد |
|--------|-------|
"""
        for status, count in sorted(by_inclusion.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {status} | {count} |\n"

        summary += f"""
### أبرز الجهات المسؤولة (أعلى ١٠):
| الجهة | العدد |
|-------|-------|
"""
        for org, count in sorted(by_org.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary += f"| {org} | {count} |\n"

        if incomplete:
            summary += f"""
### فعاليات تحتاج استكمال ({len(incomplete)}):
"""
            for item in incomplete[:10]:
                summary += f"- **{item['name']}** ({item['city']})"
                if item['missing']:
                    summary += f" — حقول ناقصة: {', '.join(item['missing'])}"
                summary += "\n"

        return summary

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Analyze event data and produce reports."""
        self._clear_thinking()
        self._log_thinking("تحليل بيانات الفعاليات...")

        events_summary = self._get_events_summary()
        self._log_thinking("اكتمل تحليل البيانات — الملخص جاهز")

        enhanced_message = f"""طلب المستخدم: {user_message}

البيانات المتاحة للتحليل:
{events_summary}"""

        if context and context.get('uploaded_data'):
            enhanced_message += f"""

بيانات إضافية محمّلة:
{context['uploaded_data']}"""
            self._log_thinking("تم تضمين بيانات CSV المحمّلة في التحليل")

        enhanced_message += "\n\nقدم تحليلاً شاملاً بناءً على هذه البيانات وطلب المستخدم."

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("إعداد التقرير التحليلي...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتمل إعداد التقرير التحليلي")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "analysis_type": "events_data"
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
                content=f"حدث خطأ أثناء التحليل: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
