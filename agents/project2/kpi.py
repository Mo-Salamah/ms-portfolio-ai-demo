"""
KPI Agent for Project 2 - Major Celebrations Planning

Recommends KPIs and measurement methods for the celebration.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


KPI_SYSTEM_PROMPT = """You are a KPI Agent specialized in measuring the success of major national celebrations.

IMPORTANT: Always respond in English.

Your expertise includes:
1. Designing Key Performance Indicators (KPIs)
2. Identifying measurement and monitoring methods
3. Setting realistic targets
4. Linking indicators to strategic objectives

Indicator Categories:
- Economic Impact (spending, employment, investments)
- Community Engagement (visitors, volunteers, satisfaction)
- Media Coverage (reach, engagement, reputation)
- Legacy and Sustainability (infrastructure, capabilities, culture)
- Operational Efficiency (budget and schedule adherence)

Design Methodology:
1. Understand strategic objectives
2. Define main and sub-indicators
3. Determine measurement method and data source
4. Set targets and thresholds
5. Define measurement frequency and responsible party

Good Indicator Criteria (SMART):
- Specific
- Measurable
- Achievable
- Relevant
- Time-bound"""


class KPIAgent(BaseAgent):
    """
    KPI specialist for Project 2.
    """

    def __init__(self):
        super().__init__(
            name="KPI Agent",
            name_en="KPI Agent",
            description="Recommend KPIs and define measurement methods",
            temperature=0.4
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return KPI_SYSTEM_PROMPT

    def _get_kpi_context(self, category: str = None) -> str:
        """Get KPI data from knowledge base."""
        if category:
            kpis = self.knowledge_base.get_kpis_by_category(category)
        else:
            kpis = self.knowledge_base.get_all_kpis()

        context = "## KPIs Available in Knowledge Base:\n\n"

        # Group by category
        by_category = {}
        for kpi in kpis:
            cat = kpi.get('category', 'Other')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(kpi)

        for cat, cat_kpis in by_category.items():
            context += f"### {cat}\n\n"
            for kpi in cat_kpis:
                context += f"**{kpi.get('name', 'Unnamed')}**\n"
                context += f"- Description: {kpi.get('description', 'None')}\n"
                context += f"- Unit: {kpi.get('unit', 'Unspecified')}\n"
                context += f"- Measurement Method: {kpi.get('measurement_method', 'Unspecified')}\n"
                context += f"- Frequency: {kpi.get('frequency', 'Unspecified')}\n"
                if kpi.get('benchmark_value'):
                    context += f"- Benchmark Value: {kpi['benchmark_value']}\n"
                context += "\n"

        return context

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Provide KPI recommendations."""
        self._clear_thinking()
        self._log_thinking("Analyzing KPI request...")

        # Determine relevant category
        category_keywords = {
            "economic": "Economic Impact",
            "financial": "Economic Impact",
            "community": "Community Engagement",
            "visitor": "Community Engagement",
            "media": "Media Coverage",
            "communication": "Media Coverage",
            "legacy": "Legacy and Sustainability",
            "sustainability": "Legacy and Sustainability",
            "operation": "Operational Efficiency",
            "budget": "Operational Efficiency"
        }

        specific_category = None
        message_lower = user_message.lower()
        for keyword, category in category_keywords.items():
            if keyword in message_lower:
                specific_category = category
                break

        kpi_context = self._get_kpi_context(specific_category)
        self._log_thinking("Loaded KPIs from knowledge base")

        enhanced_message = f"""User request: {user_message}

Available KPIs:
{kpi_context}

Provide appropriate KPI recommendations with explanation of measurement methods and proposed targets."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("Preparing KPI recommendations...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("KPI recommendations prepared successfully")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "analysis_type": "kpi_recommendation",
                "category": specific_category
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
                content=f"Sorry, an error occurred: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )


    def design_kpi_framework(self, objectives: List[str]) -> AgentResponse:
        """Design a complete KPI framework for given objectives."""
        request = f"""Design a comprehensive KPI framework for the following objectives:
{chr(10).join(f'- {obj}' for obj in objectives)}

The framework should include:
1. Key indicators for each objective
2. Measurement methods and data sources
3. Proposed targets
4. Monitoring and evaluation mechanism"""

        return self.invoke(request)
