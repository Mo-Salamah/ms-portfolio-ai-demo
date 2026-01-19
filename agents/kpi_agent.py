"""
KPI Agent for MS Portfolio AI Agent Demo
وكيل مؤشرات الأداء لنظام المحفظة الذكي

This agent specializes in KPI recommendations and performance measurement.
"""

from typing import Optional, Dict, List
from .base_agent import BaseAgent, AgentResponse
from prompts.kpi_prompt import KPI_SYSTEM_PROMPT
from utils.knowledge_base import KnowledgeBase


class KPIAgent(BaseAgent):
    """
    Agent specialized in KPI recommendations and performance measurement.
    وكيل متخصص في توصيات مؤشرات الأداء والقياس
    """

    def __init__(self):
        super().__init__(
            name="وكيل مؤشرات الأداء",
            name_en="KPI Agent",
            description="متخصص في مؤشرات الأداء الرئيسية والقياس والمتابعة",
            temperature=0.4  # Lower temperature for more precise recommendations
        )
        self.kb = KnowledgeBase()

    def get_system_prompt(self) -> str:
        """Return the KPI-specific system prompt."""
        return KPI_SYSTEM_PROMPT

    def _identify_relevant_categories(self, query: str) -> List[str]:
        """
        Identify which KPI categories are relevant to the query.

        Args:
            query: User's query in Arabic

        Returns:
            List of relevant category names
        """
        category_keywords = {
            "مؤشرات الحضور والمشاركة": ["حضور", "مشاركة", "زوار", "جمهور", "إشغال"],
            "مؤشرات التغطية الإعلامية": ["إعلام", "تغطية", "صحافة", "تواصل", "رقمي"],
            "مؤشرات الأثر الاقتصادي": ["اقتصاد", "استثمار", "وظائف", "إنفاق", "عائد"],
            "مؤشرات رضا الجمهور": ["رضا", "تجربة", "شكاوى", "NPS", "تقييم"],
            "مؤشرات التنفيذ والتسليم": ["تنفيذ", "جدول", "ميزانية", "أمان", "جودة"],
        }

        relevant = []
        query_lower = query.lower()

        for category, keywords in category_keywords.items():
            if any(kw in query_lower for kw in keywords):
                relevant.append(category)

        # If no specific category identified, return all
        if not relevant:
            relevant = list(category_keywords.keys())

        return relevant

    def _get_kpis_for_categories(self, categories: List[str]) -> List[Dict]:
        """
        Get KPIs for the specified categories.

        Args:
            categories: List of category names

        Returns:
            List of KPI dictionaries
        """
        all_kpis = []
        for category in categories:
            kpis = self.kb.get_kpis_by_category(category)
            for kpi in kpis:
                kpi_with_cat = kpi.copy()
                kpi_with_cat["category_name"] = category
                all_kpis.append(kpi_with_cat)
        return all_kpis

    def _format_kpi_context(self, kpis: List[Dict]) -> str:
        """
        Format KPI data as context for the LLM.

        Args:
            kpis: List of KPI dictionaries

        Returns:
            Formatted string with KPI information
        """
        if not kpis:
            return "لا توجد مؤشرات متاحة"

        # Group by category
        by_category = {}
        for kpi in kpis:
            cat = kpi.get("category_name", "غير مصنف")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(kpi)

        context_parts = []
        for category, cat_kpis in by_category.items():
            kpi_details = []
            for kpi in cat_kpis:
                kpi_details.append(f"""
### {kpi.get('name', 'غير محدد')}
- **التعريف:** {kpi.get('definition', 'غير متاح')}
- **طريقة الحساب:** {kpi.get('measurement_method', 'غير متاح')}
- **مصدر البيانات:** {kpi.get('data_source', 'غير متاح')}
- **تكرار القياس:** {kpi.get('frequency', 'غير متاح')}
- **المستهدف المقترح:** {kpi.get('target_example', 'غير متاح')}
- **المعيار الدولي:** {kpi.get('benchmark', 'غير متاح')}
""")

            context_parts.append(f"""
## {category}
{''.join(kpi_details)}
""")

        return "\n---\n".join(context_parts)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """
        Invoke the KPI agent with knowledge base enrichment.

        Args:
            user_message: The user's query
            context: Optional additional context
            conversation_history: Optional previous messages

        Returns:
            AgentResponse with KPI recommendations
        """
        # Clear thinking log
        self._clear_thinking()
        self._log_thinking("تحليل الطلب لتحديد فئات المؤشرات ذات الصلة...")

        # Identify relevant categories
        relevant_categories = self._identify_relevant_categories(user_message)
        self._log_thinking(f"تم تحديد {len(relevant_categories)} فئة ذات صلة")

        # Get KPIs for those categories
        relevant_kpis = self._get_kpis_for_categories(relevant_categories)
        self._log_thinking(f"تم استرجاع {len(relevant_kpis)} مؤشر أداء")

        # Format KPI context
        kpi_context = self._format_kpi_context(relevant_kpis)

        # Get celebration context
        celebration_info = self.kb.get_celebration_info()
        events_summary = self.kb.get_events_summary()

        # Build enhanced context
        enhanced_context = {
            "مكتبة مؤشرات الأداء المتاحة": kpi_context,
            "معلومات الاحتفالية": f"""
اسم الاحتفالية: {celebration_info.get('name', 'غير متاح')}
السنة: {celebration_info.get('year', 'غير متاح')}
إجمالي الفعاليات: {events_summary.get('total_count', 0)}
توزيع الفعاليات حسب الفئة: {events_summary.get('by_category', {})}
توزيع الفعاليات حسب المستوى: {events_summary.get('by_tier', {})}
"""
        }

        if context:
            enhanced_context.update(context)

        self._log_thinking("جارٍ إعداد توصيات مؤشرات الأداء...")

        # Call the parent invoke with enhanced context
        messages = self._build_messages(user_message, enhanced_context, conversation_history)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد التوصيات بنجاح")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "categories_analyzed": relevant_categories,
                "kpis_considered": len(relevant_kpis),
                "stop_reason": response.stop_reason,
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
                content=f"عذراً، حدث خطأ أثناء إعداد توصيات المؤشرات: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
