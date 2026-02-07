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
- التقاطعات: المدينة × التصنيف، المدينة × النوع، المدينة × حالة التضمين، الجهة × المدينة

مهم جداً: البيانات المقدمة لك تتضمن جداول تقاطعية كاملة (مدينة × تصنيف، مدينة × نوع، إلخ). استخدم هذه البيانات مباشرة في تحليلك — لا تقل إن التقاطعات غير متوفرة.

أسلوب التحليل:
- استخدم الجداول للمقارنات
- قدم الأرقام والنسب المئوية
- صنف الفعاليات حسب النوع والجهة والمدينة
- حدد الفجوات في البيانات
- استخدم الجداول التقاطعية للتحليل المعمق

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
        """Get a comprehensive summary of events data including cross-tabulations."""
        events = self.knowledge_base.get_all_events()

        total = len(events)
        by_city = {}
        by_type = {}
        by_tier = {}
        by_org = {}
        by_inclusion = {}
        # Cross-tabulations
        city_tier = {}
        city_type = {}
        city_inclusion = {}
        city_org = {}
        incomplete = []

        for event in events:
            city = event.get('city', '') or 'غير محدد'
            by_city[city] = by_city.get(city, 0) + 1

            event_type = event.get('type', '') or 'غير محدد'
            by_type[event_type] = by_type.get(event_type, 0) + 1

            tier = event.get('tier', '') or 'غير محدد'
            by_tier[tier] = by_tier.get(tier, 0) + 1

            org = event.get('responsible_org', '') or 'غير محدد'
            by_org[org] = by_org.get(org, 0) + 1

            inclusion = event.get('inclusion_status', '') or 'غير محدد'
            by_inclusion[inclusion] = by_inclusion.get(inclusion, 0) + 1

            # Cross-tabulations
            city_tier.setdefault(city, {})
            city_tier[city][tier] = city_tier[city].get(tier, 0) + 1

            city_type.setdefault(city, {})
            city_type[city][event_type] = city_type[city].get(event_type, 0) + 1

            city_inclusion.setdefault(city, {})
            city_inclusion[city][inclusion] = city_inclusion[city].get(inclusion, 0) + 1

            city_org.setdefault(city, {})
            city_org[city][org] = city_org[city].get(org, 0) + 1

            required_fields = ['name', 'start_date', 'city', 'responsible_org', 'tier', 'type']
            missing = [f for f in required_fields if not event.get(f)]
            if missing:
                incomplete.append({
                    'name': event.get('name', 'بدون اسم'),
                    'city': city,
                    'missing': missing
                })

        # === Build summary ===
        summary = f"""## ملخص بيانات الفعاليات

### الإجمالي: {total} فعالية

### التوزيع حسب المدينة:
| المدينة | العدد | النسبة |
|---------|-------|--------|
"""
        for city, count in sorted(by_city.items(), key=lambda x: x[1], reverse=True):
            pct = count * 100 // total if total > 0 else 0
            summary += f"| {city} | {count} | {pct}% |\n"

        summary += "\n### التوزيع حسب التصنيف:\n| التصنيف | العدد |\n|---------|-------|\n"
        for tier, count in sorted(by_tier.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {tier} | {count} |\n"

        summary += "\n### التوزيع حسب النوع:\n| النوع | العدد |\n|-------|-------|\n"
        for event_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {event_type} | {count} |\n"

        summary += "\n### التوزيع حسب حالة التضمين:\n| الحالة | العدد |\n|--------|-------|\n"
        for status, count in sorted(by_inclusion.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {status} | {count} |\n"

        # === Cross-tabulation: City × Tier ===
        all_tiers = sorted(by_tier.keys())
        summary += f"\n### التقاطع: المدينة × التصنيف\n| المدينة | {' | '.join(all_tiers)} | المجموع |\n|---------|{'|'.join([' ------- ' for _ in all_tiers])}|---------|\n"
        for city in sorted(city_tier.keys(), key=lambda c: by_city.get(c, 0), reverse=True):
            vals = [str(city_tier[city].get(t, 0)) for t in all_tiers]
            summary += f"| {city} | {' | '.join(vals)} | {by_city.get(city, 0)} |\n"

        # === Cross-tabulation: City × Type ===
        all_types = sorted(by_type.keys())
        summary += f"\n### التقاطع: المدينة × النوع\n| المدينة | {' | '.join(all_types)} | المجموع |\n|---------|{'|'.join([' ------- ' for _ in all_types])}|---------|\n"
        for city in sorted(city_type.keys(), key=lambda c: by_city.get(c, 0), reverse=True):
            vals = [str(city_type[city].get(t, 0)) for t in all_types]
            summary += f"| {city} | {' | '.join(vals)} | {by_city.get(city, 0)} |\n"

        # === Cross-tabulation: City × Inclusion Status ===
        all_statuses = sorted(by_inclusion.keys())
        summary += f"\n### التقاطع: المدينة × حالة التضمين\n| المدينة | {' | '.join(all_statuses)} | المجموع |\n|---------|{'|'.join([' ------- ' for _ in all_statuses])}|---------|\n"
        for city in sorted(city_inclusion.keys(), key=lambda c: by_city.get(c, 0), reverse=True):
            vals = [str(city_inclusion[city].get(s, 0)) for s in all_statuses]
            summary += f"| {city} | {' | '.join(vals)} | {by_city.get(city, 0)} |\n"

        # === Top orgs per city ===
        summary += "\n### أبرز الجهات المسؤولة حسب المدينة:\n"
        for city in sorted(city_org.keys(), key=lambda c: by_city.get(c, 0), reverse=True):
            top_orgs = sorted(city_org[city].items(), key=lambda x: x[1], reverse=True)[:5]
            summary += f"\n**{city}:**\n"
            for org, count in top_orgs:
                if org and org != 'غير محدد':
                    summary += f"- {org}: {count}\n"

        # === Global top orgs ===
        summary += "\n### أبرز الجهات المسؤولة (أعلى ١٥):\n| الجهة | العدد |\n|-------|-------|\n"
        for org, count in sorted(by_org.items(), key=lambda x: x[1], reverse=True)[:15]:
            if org and org != 'غير محدد':
                summary += f"| {org} | {count} |\n"

        # === Incomplete events ===
        if incomplete:
            summary += f"\n### فعاليات تحتاج استكمال ({len(incomplete)} من {total}):\n"
            for item in incomplete[:10]:
                summary += f"- **{item['name']}** ({item['city']})"
                if item['missing']:
                    summary += f" — حقول ناقصة: {', '.join(item['missing'])}"
                summary += "\n"
            if len(incomplete) > 10:
                summary += f"\n*و{len(incomplete) - 10} فعاليات أخرى تحتاج استكمال...*\n"

        # === Raw data sample ===
        summary += "\n### عينة من البيانات الخام (أول ٢٥ فعالية):\n"
        summary += "| الاسم | المدينة | الجهة المسؤولة | التصنيف | النوع | تاريخ البداية | تاريخ النهاية | حالة التضمين |\n"
        summary += "|-------|---------|----------------|---------|-------|---------------|---------------|-------------|\n"
        for event in events[:25]:
            name = (event.get('name', '') or '')[:35]
            org_name = (event.get('responsible_org', '') or '')[:25]
            summary += f"| {name} | {event.get('city', '')} | {org_name} | {event.get('tier', '')} | {event.get('type', '')} | {event.get('start_date', '')} | {event.get('end_date', '')} | {event.get('inclusion_status', '')} |\n"

        summary += f"\nملاحظة: البيانات أعلاه عينة من {total} فعالية. جميع الجداول التقاطعية مبنية على كامل البيانات المتاحة.\n"

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
