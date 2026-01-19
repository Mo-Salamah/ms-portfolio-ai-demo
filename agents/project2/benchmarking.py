"""
Benchmarking Agent for Project 2 - Major Celebrations Planning
وكيل المقارنة المعيارية للمشروع الثاني

Enhanced version for international benchmarking research.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


BENCHMARKING_SYSTEM_PROMPT = """أنت وكيل المقارنة المعيارية المتخصص في دراسة الاحتفاليات والفعاليات الدولية الكبرى.

خبراتك تشمل:
1. تحليل تجارب الاحتفاليات الوطنية الكبرى
2. استخلاص الدروس المستفادة (للتبني، للتكييف، للتجنب)
3. تحديد عوامل النجاح والتحديات
4. تقديم توصيات قابلة للتطبيق محلياً

التجارب الدولية المتوفرة في قاعدة المعرفة:
- احتفالية سانت بطرسبرغ 300 عام (روسيا 2003)
- يوبيل روما الألفي (إيطاليا 2000)
- المئوية الأولمبية لبرشلونة (إسبانيا 1992)

منهجية التحليل:
1. السياق والأهداف
2. الهيكل التنظيمي
3. الميزانية والتمويل
4. المخرجات والإنجازات
5. التحديات والدروس المستفادة
6. التوصيات للسياق المحلي

أسلوب الإخراج:
- تحليل مقارن منظم
- جداول للمقارنة
- تصنيف واضح للدروس (تبني/تكييف/تجنب)
- توصيات محددة وقابلة للتنفيذ"""


class BenchmarkingAgent(BaseAgent):
    """
    Benchmarking specialist for Project 2.
    وكيل المقارنة المعيارية للمشروع الثاني
    """

    def __init__(self):
        super().__init__(
            name="وكيل المقارنة المعيارية",
            name_en="Benchmarking Agent",
            description="إجراء البحوث المقارنة وتحليل التجارب الدولية",
            temperature=0.5
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return BENCHMARKING_SYSTEM_PROMPT

    def _get_benchmark_context(self, case_name: str = None) -> str:
        """Get benchmark data from knowledge base."""
        if case_name:
            benchmark = self.knowledge_base.get_benchmark_by_name(case_name)
            if benchmark:
                return self._format_single_benchmark(benchmark)

        # Return all benchmarks
        benchmarks = self.knowledge_base.get_all_benchmarks()
        context = "## التجارب الدولية المتوفرة:\n\n"
        for b in benchmarks:
            context += self._format_single_benchmark(b) + "\n---\n"
        return context

    def _format_single_benchmark(self, benchmark: Dict) -> str:
        """Format a single benchmark for context."""
        output = f"""### {benchmark.get('name', 'غير مسمى')}

**الموقع:** {benchmark.get('location', 'غير محدد')}
**السنة:** {benchmark.get('year', 'غير محدد')}
**المدة:** {benchmark.get('duration', 'غير محدد')}

**الوصف:**
{benchmark.get('description', 'لا يوجد وصف')}

**الأهداف:**
"""
        for obj in benchmark.get('objectives', []):
            output += f"- {obj}\n"

        output += f"\n**المخرجات الرئيسية:**\n"
        for outcome in benchmark.get('key_outcomes', []):
            output += f"- {outcome}\n"

        output += f"\n**المقاييس:**\n"
        metrics = benchmark.get('metrics', {})
        for key, value in metrics.items():
            output += f"- {key}: {value}\n"

        output += f"\n**الدروس المستفادة:**\n"
        lessons = benchmark.get('lessons_learned', {})
        if lessons.get('adopt'):
            output += "\n*للتبني:*\n"
            for lesson in lessons['adopt']:
                output += f"  ✅ {lesson}\n"
        if lessons.get('adapt'):
            output += "\n*للتكييف:*\n"
            for lesson in lessons['adapt']:
                output += f"  🔄 {lesson}\n"
        if lessons.get('avoid'):
            output += "\n*للتجنب:*\n"
            for lesson in lessons['avoid']:
                output += f"  ⚠️ {lesson}\n"

        return output

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Provide benchmarking analysis."""
        self._clear_thinking()
        self._log_thinking("جارٍ تحليل طلب المقارنة المعيارية...")

        # Determine which case studies are relevant
        case_keywords = {
            "سانت بطرسبرغ": "سانت بطرسبرغ",
            "بطرسبورغ": "سانت بطرسبرغ",
            "روسيا": "سانت بطرسبرغ",
            "روما": "روما",
            "إيطاليا": "روما",
            "يوبيل": "روما",
            "برشلونة": "برشلونة",
            "إسبانيا": "برشلونة",
            "أولمبي": "برشلونة"
        }

        specific_case = None
        for keyword, case in case_keywords.items():
            if keyword in user_message:
                specific_case = case
                break

        benchmark_context = self._get_benchmark_context(specific_case)
        self._log_thinking(f"تم تحميل بيانات المقارنة المعيارية")

        enhanced_message = f"""طلب المستخدم: {user_message}

البيانات المتاحة من قاعدة المعرفة:
{benchmark_context}

قدم تحليلاً مقارناً شاملاً بناءً على الطلب والبيانات المتاحة."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ إعداد التحليل المقارن...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إعداد التحليل المقارن بنجاح")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "analysis_type": "benchmarking",
                "specific_case": specific_case
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


    def compare_cases(self, cases: List[str]) -> AgentResponse:
        """Compare multiple benchmark cases."""
        request = f"قدم مقارنة تفصيلية بين التجارب التالية: {', '.join(cases)}"
        return self.invoke(request)
