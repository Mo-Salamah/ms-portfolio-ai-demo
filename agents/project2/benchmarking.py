"""
Benchmarking Agent for Project 2 - Major Celebrations Planning

Enhanced version for international benchmarking research.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


BENCHMARKING_SYSTEM_PROMPT = """You are a Benchmarking Agent specialized in studying major international celebrations and events.

IMPORTANT: Always respond in English.

Your expertise includes:
1. Analyzing major national celebration experiences
2. Extracting lessons learned (to adopt, to adapt, to avoid)
3. Identifying success factors and challenges
4. Providing recommendations applicable to local context

International experiences available in the knowledge base:
- St. Petersburg 300th Anniversary (Russia 2003)
- Rome Jubilee 2000 (Italy 2000)
- Barcelona Olympic Centennial (Spain 1992)

Analysis methodology:
1. Context and objectives
2. Organizational structure
3. Budget and funding
4. Outputs and achievements
5. Challenges and lessons learned
6. Recommendations for local context

Output style:
- Structured comparative analysis
- Comparison tables
- Clear lesson classification (adopt/adapt/avoid)
- Specific and actionable recommendations"""


class BenchmarkingAgent(BaseAgent):
    """
    Benchmarking specialist for Project 2.
    """

    def __init__(self):
        super().__init__(
            name="Benchmarking Agent",
            name_en="Benchmarking Agent",
            description="Conduct comparative research and analyze international experiences",
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
        context = "## Available International Experiences:\n\n"
        for b in benchmarks:
            context += self._format_single_benchmark(b) + "\n---\n"
        return context

    def _format_single_benchmark(self, benchmark: Dict) -> str:
        """Format a single benchmark for context."""
        output = f"""### {benchmark.get('name', 'Unnamed')}

**Location:** {benchmark.get('location', 'Unspecified')}
**Year:** {benchmark.get('year', 'Unspecified')}
**Duration:** {benchmark.get('duration', 'Unspecified')}

**Description:**
{benchmark.get('description', 'No description')}

**Objectives:**
"""
        for obj in benchmark.get('objectives', []):
            output += f"- {obj}\n"

        output += f"\n**Key Outcomes:**\n"
        for outcome in benchmark.get('key_outcomes', []):
            output += f"- {outcome}\n"

        output += f"\n**Metrics:**\n"
        metrics = benchmark.get('metrics', {})
        for key, value in metrics.items():
            output += f"- {key}: {value}\n"

        output += f"\n**Lessons Learned:**\n"
        lessons = benchmark.get('lessons_learned', {})
        if lessons.get('adopt'):
            output += "\n*To Adopt:*\n"
            for lesson in lessons['adopt']:
                output += f"  ✅ {lesson}\n"
        if lessons.get('adapt'):
            output += "\n*To Adapt:*\n"
            for lesson in lessons['adapt']:
                output += f"  🔄 {lesson}\n"
        if lessons.get('avoid'):
            output += "\n*To Avoid:*\n"
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
        self._log_thinking("Analyzing benchmarking request...")

        # Determine which case studies are relevant
        case_keywords = {
            "st. petersburg": "St. Petersburg",
            "petersburg": "St. Petersburg",
            "russia": "St. Petersburg",
            "rome": "Rome",
            "italy": "Rome",
            "jubilee": "Rome",
            "barcelona": "Barcelona",
            "spain": "Barcelona",
            "olympic": "Barcelona"
        }

        specific_case = None
        message_lower = user_message.lower()
        for keyword, case in case_keywords.items():
            if keyword in message_lower:
                specific_case = case
                break

        benchmark_context = self._get_benchmark_context(specific_case)
        self._log_thinking("Loaded benchmark data from knowledge base")

        enhanced_message = f"""User request: {user_message}

Data available from knowledge base:
{benchmark_context}

Provide a comprehensive comparative analysis based on the request and available data."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("Preparing comparative analysis...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("Comparative analysis prepared successfully")

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
            self._log_thinking(f"Error occurred: {str(e)}")
            return AgentResponse(
                content=f"Sorry, an error occurred during analysis: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )


    def compare_cases(self, cases: List[str]) -> AgentResponse:
        """Compare multiple benchmark cases."""
        request = f"Provide a detailed comparison between the following experiences: {', '.join(cases)}"
        return self.invoke(request)
