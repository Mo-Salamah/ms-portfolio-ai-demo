"""
Benchmarking Agent for MS Portfolio AI Agent Demo
وكيل المقارنة المعيارية لنظام المحفظة الذكي

This agent specializes in benchmark analysis and international case studies.
"""

import json
from typing import Optional, Dict, List
from .base_agent import BaseAgent, AgentResponse
from prompts.benchmarking_prompt import BENCHMARKING_SYSTEM_PROMPT
from utils.knowledge_base import KnowledgeBase


class BenchmarkingAgent(BaseAgent):
    """
    Agent specialized in benchmark analysis and international comparisons.
    وكيل متخصص في التحليل المقارن والمقارنات الدولية
    """

    def __init__(self):
        super().__init__(
            name="وكيل المقارنة المعيارية",
            name_en="Benchmarking Agent",
            description="متخصص في دراسات الحالة الدولية والمقارنات المعيارية للفعاليات الكبرى",
            temperature=0.5  # Balanced for analytical yet creative output
        )
        self.kb = KnowledgeBase()

    def get_system_prompt(self) -> str:
        """Return the benchmarking-specific system prompt."""
        return BENCHMARKING_SYSTEM_PROMPT

    def _get_relevant_benchmarks(self, query: str) -> List[Dict]:
        """
        Identify and retrieve relevant benchmarks based on the query.

        Args:
            query: User's query in Arabic

        Returns:
            List of relevant benchmark dictionaries
        """
        # Keywords that might indicate specific benchmarks
        benchmark_keywords = {
            "سانت بطرسبرغ": "BM001",
            "روسيا": "BM001",
            "روما": "BM002",
            "إيطاليا": "BM002",
            "برشلونة": "BM003",
            "إسبانيا": "BM003",
        }

        relevant = []

        # Check for specific benchmark mentions
        for keyword, benchmark_id in benchmark_keywords.items():
            if keyword in query:
                benchmark = self.kb.get_benchmark_by_id(benchmark_id)
                if benchmark and benchmark not in relevant:
                    relevant.append(benchmark)

        # If no specific benchmark mentioned, return all for comprehensive analysis
        if not relevant:
            relevant = self.kb.get_all_benchmarks()

        return relevant

    def _format_benchmark_context(self, benchmarks: List[Dict]) -> str:
        """
        Format benchmark data as context for the LLM.

        Args:
            benchmarks: List of benchmark dictionaries

        Returns:
            Formatted string with benchmark information
        """
        context_parts = []

        for b in benchmarks:
            metrics = b.get("key_metrics", {})
            overview = b.get("overview", {})
            lessons = b.get("lessons_learned", {})

            context_parts.append(f"""
## {b.get('name')} ({b.get('year')}) - {b.get('country')}

### نظرة عامة
{overview.get('summary', '')}

### الرؤية الاستراتيجية
{overview.get('strategic_vision', '')}

### المؤشرات الرئيسية
- إجمالي الفعاليات: {metrics.get('total_events', 'غير متاح')}
- الفعاليات الرئيسية: {metrics.get('marquee_events', 'غير متاح')}
- الزوار الدوليون: {metrics.get('international_guests', 'غير متاح')}
- إجمالي الزوار: {metrics.get('total_visitors', 'غير متاح')}
- الأثر الاقتصادي: {metrics.get('economic_impact_usd', 'غير متاح')}
- نمو السياحة: {metrics.get('tourism_increase_percent', 'غير متاح')}%
- الوظائف المستحدثة: {metrics.get('jobs_created', 'غير متاح')}

### عوامل النجاح
{chr(10).join(['- ' + f for f in b.get('success_factors', [])])}

### الدروس المستفادة
**ما يجب تبنيه:**
{chr(10).join(['- ' + l for l in lessons.get('adopt', [])])}

**ما يجب تكييفه:**
{chr(10).join(['- ' + l for l in lessons.get('adapt', [])])}

**ما يجب تجنبه:**
{chr(10).join(['- ' + l for l in lessons.get('avoid', [])])}

### التحديات
{chr(10).join(['- ' + c for c in b.get('challenges_faced', [])])}

### الإرث
{chr(10).join(['- ' + l for l in b.get('legacy', [])])}
""")

        return "\n---\n".join(context_parts)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """
        Invoke the benchmarking agent with knowledge base enrichment.

        Args:
            user_message: The user's query
            context: Optional additional context
            conversation_history: Optional previous messages

        Returns:
            AgentResponse with benchmark analysis
        """
        # Clear thinking log
        self._clear_thinking()
        self._log_thinking("تحليل الطلب للبحث عن دراسات الحالة ذات الصلة...")

        # Get relevant benchmarks
        relevant_benchmarks = self._get_relevant_benchmarks(user_message)
        self._log_thinking(f"تم تحديد {len(relevant_benchmarks)} دراسة حالة ذات صلة")

        # Format benchmark context
        benchmark_context = self._format_benchmark_context(relevant_benchmarks)
        self._log_thinking("تم تجهيز بيانات دراسات الحالة")

        # Get celebration context
        celebration_info = self.kb.get_celebration_info()
        events_summary = self.kb.get_events_summary()

        # Build enhanced context
        enhanced_context = {
            "دراسات الحالة المتاحة": benchmark_context,
            "معلومات الاحتفالية الحالية": f"""
اسم الاحتفالية: {celebration_info.get('name', 'غير متاح')}
السنة: {celebration_info.get('year', 'غير متاح')}
إجمالي الفعاليات: {events_summary.get('total_count', 0)}
الحضور المتوقع: {events_summary.get('total_expected_attendance', 0):,}
"""
        }

        if context:
            enhanced_context.update(context)

        self._log_thinking("جارٍ توليد التحليل المقارن...")

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
            self._log_thinking("تم توليد التحليل بنجاح")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "benchmarks_used": [b.get("name") for b in relevant_benchmarks],
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
                content=f"عذراً، حدث خطأ أثناء إعداد التحليل المقارن: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
