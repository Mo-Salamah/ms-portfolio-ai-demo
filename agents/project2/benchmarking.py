"""
وكيل المقارنة المعيارية — احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


BENCHMARKING_SYSTEM_PROMPT = """أنت وكيل المقارنة المعيارية المتخصص في دراسة تجارب الاحتفاليات الدولية الكبرى.

خبراتك تشمل:
١. تحليل تجارب الاحتفاليات الوطنية الكبرى
٢. استخلاص الدروس المستفادة (للاعتماد، للتكييف، للتجنب)
٣. تحديد عوامل النجاح والتحديات
٤. تقديم توصيات قابلة للتطبيق في السياق المحلي

التجارب الدولية المتاحة في قاعدة المعرفة:
- احتفالية سانت بطرسبرغ بمرور ٣٠٠ عام (روسيا ٢٠٠٣)
- يوبيل روما ٢٠٠٠ (إيطاليا ٢٠٠٠)
- المئوية الأولمبية لبرشلونة (إسبانيا ١٩٩٢)

منهجية التحليل:
١. السياق والأهداف
٢. الهيكل التنظيمي
٣. الميزانية والتمويل
٤. المخرجات والإنجازات
٥. التحديات والدروس المستفادة
٦. التوصيات للسياق المحلي

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- استخدم البيانات الفعلية فقط — لا تخترع أرقاماً
- إذا لم تتوفر معلومة، قل ذلك صراحة
- لا تستخدم رموز تعبيرية مطلقاً"""


class BenchmarkingAgent(BaseAgent):
    """وكيل المقارنة المعيارية — متخصص في دراسة التجارب الدولية"""

    def __init__(self):
        super().__init__(
            name="وكيل المقارنة المعيارية",
            name_en="وكيل المقارنة المعيارية",
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

        benchmarks = self.knowledge_base.get_all_benchmarks()
        context = "## التجارب الدولية المتاحة:\n\n"
        for b in benchmarks:
            context += self._format_single_benchmark(b) + "\n---\n"
        return context

    def _format_single_benchmark(self, benchmark: Dict) -> str:
        """Format a single benchmark for context."""
        output = f"""### {benchmark.get('name', 'بدون اسم')}

**الموقع:** {benchmark.get('location', 'غير محدد')}
**السنة:** {benchmark.get('year', 'غير محدد')}
**المدة:** {benchmark.get('duration', 'غير محدد')}

**الوصف:**
{benchmark.get('description', 'لا يوجد وصف')}

**الأهداف:**
"""
        for obj in benchmark.get('objectives', []):
            output += f"- {obj}\n"

        output += f"\n**النتائج الرئيسية:**\n"
        for outcome in benchmark.get('key_outcomes', []):
            output += f"- {outcome}\n"

        output += f"\n**المؤشرات:**\n"
        metrics = benchmark.get('metrics', {})
        for key, value in metrics.items():
            output += f"- {key}: {value}\n"

        output += f"\n**الدروس المستفادة:**\n"
        lessons = benchmark.get('lessons_learned', {})
        if lessons.get('adopt'):
            output += "\n*للاعتماد:*\n"
            for lesson in lessons['adopt']:
                output += f"  - {lesson}\n"
        if lessons.get('adapt'):
            output += "\n*للتكييف:*\n"
            for lesson in lessons['adapt']:
                output += f"  - {lesson}\n"
        if lessons.get('avoid'):
            output += "\n*للتجنب:*\n"
            for lesson in lessons['avoid']:
                output += f"  - {lesson}\n"

        return output

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Provide benchmarking analysis."""
        self._clear_thinking()
        self._log_thinking("تحليل طلب المقارنة المعيارية...")

        case_keywords = {
            "سانت بطرسبرغ": "St. Petersburg",
            "بطرسبرغ": "St. Petersburg",
            "روسيا": "St. Petersburg",
            "st. petersburg": "St. Petersburg",
            "petersburg": "St. Petersburg",
            "روما": "Rome",
            "إيطاليا": "Rome",
            "rome": "Rome",
            "برشلونة": "Barcelona",
            "إسبانيا": "Barcelona",
            "barcelona": "Barcelona"
        }

        specific_case = None
        message_lower = user_message.lower()
        for keyword, case in case_keywords.items():
            if keyword in message_lower:
                specific_case = case
                break

        benchmark_context = self._get_benchmark_context(specific_case)
        self._log_thinking("تم تحميل بيانات المقارنة من قاعدة المعرفة")

        enhanced_message = f"""طلب المستخدم: {user_message}

البيانات المتاحة من قاعدة المعرفة:
{benchmark_context}

قدم تحليلاً مقارناً شاملاً بناءً على الطلب والبيانات المتاحة."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("إعداد التحليل المقارن...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("اكتمل التحليل المقارن")

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
                content=f"حدث خطأ أثناء التحليل: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
