"""
Data Analysis Agent for Project 1 - Events Oversight
وكيل تحليل البيانات للمشروع الأول

Analyzes event data and produces analytical reports.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


DATA_ANALYSIS_SYSTEM_PROMPT = """أنت وكيل تحليل البيانات المتخصص في مشروع الإشراف على تخطيط الفعاليات الوطنية.

مهامك الرئيسية:
1. تحليل بيانات الفعاليات المستلمة من الجهات المنفذة
2. إنتاج تقارير تحليلية وإحصائية
3. تحديد الأنماط والتوزيعات في البيانات
4. تقديم رؤى قابلة للتنفيذ

الجهات المنفذة:
- الجهة المنفذة (أ)
- الجهة المنفذة (ب)
- الجهة المنفذة (ج)

أسلوب التحليل:
- استخدم الجداول للمقارنات
- قدم الأرقام والنسب المئوية
- صنف الفعاليات حسب النوع والجهة والمدينة
- حدد الفجوات في البيانات

تنسيق الإخراج:
- عناوين واضحة
- جداول منظمة
- ملخص تنفيذي في البداية
- توصيات في النهاية"""


class DataAnalysisAgent(BaseAgent):
    """
    Data Analysis specialist for Project 1.
    وكيل تحليل البيانات للمشروع الأول
    """

    def __init__(self):
        super().__init__(
            name="وكيل تحليل البيانات",
            name_en="Data Analysis Agent",
            description="تحليل بيانات الفعاليات وإنتاج التقارير التحليلية",
            temperature=0.3
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return DATA_ANALYSIS_SYSTEM_PROMPT

    def _get_events_summary(self) -> str:
        """Get a summary of events data for analysis."""
        events = self.knowledge_base.get_all_events()

        # Calculate statistics
        total = len(events)
        by_entity = {}
        by_type = {}
        by_city = {}
        by_tier = {}
        incomplete = []

        for event in events:
            # By organizing entity
            entity = event.get('organizing_entity', 'غير محدد')
            by_entity[entity] = by_entity.get(entity, 0) + 1

            # By type
            event_type = event.get('type', 'غير محدد')
            by_type[event_type] = by_type.get(event_type, 0) + 1

            # By city
            city = event.get('city', 'غير محدد')
            by_city[city] = by_city.get(city, 0) + 1

            # By tier
            tier = event.get('tier', 'غير محدد')
            by_tier[tier] = by_tier.get(tier, 0) + 1

            # Check for incomplete data
            required_fields = ['name', 'date', 'city', 'venue', 'organizing_entity']
            missing = [f for f in required_fields if not event.get(f)]
            if missing or event.get('status') == 'قيد التخطيط':
                incomplete.append({
                    'name': event.get('name', 'غير مسمى'),
                    'entity': entity,
                    'missing': missing
                })

        summary = f"""## ملخص بيانات الفعاليات

### الإجمالي: {total} فعالية

### التوزيع حسب الجهة المنفذة:
| الجهة | العدد | النسبة |
|-------|-------|--------|
"""
        for entity, count in sorted(by_entity.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {entity} | {count} | {count*100//total}% |\n"

        summary += f"""
### التوزيع حسب نوع الفعالية:
| النوع | العدد |
|-------|-------|
"""
        for event_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {event_type} | {count} |\n"

        summary += f"""
### التوزيع حسب المدينة:
| المدينة | العدد |
|---------|-------|
"""
        for city, count in sorted(by_city.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {city} | {count} |\n"

        summary += f"""
### التوزيع حسب المستوى:
| المستوى | العدد |
|---------|-------|
"""
        for tier, count in sorted(by_tier.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {tier} | {count} |\n"

        if incomplete:
            summary += f"""
### فعاليات تحتاج استكمال ({len(incomplete)}):
"""
            for item in incomplete[:10]:
                summary += f"- **{item['name']}** ({item['entity']})"
                if item['missing']:
                    summary += f" - ناقص: {', '.join(item['missing'])}"
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
        self._log_thinking("جارٍ تحليل بيانات الفعاليات...")

        # Get events summary
        events_summary = self._get_events_summary()
        self._log_thinking(f"تم تحليل البيانات - إجمالي الفعاليات المسجلة")

        # Build context with data
        enhanced_message = f"""طلب المستخدم: {user_message}

البيانات المتاحة للتحليل:
{events_summary}

قدم تحليلاً شاملاً بناءً على هذه البيانات وطلب المستخدم."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ إعداد التقرير التحليلي...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد التقرير التحليلي بنجاح")

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
                content=f"عذراً، حدث خطأ أثناء التحليل: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
