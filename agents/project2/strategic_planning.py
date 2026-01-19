"""
Strategic Planning Agent for Project 2 - Major Celebrations Planning
Strategic Planning (Agent) - Main orchestrator for celebrations planning

This is the orchestrator for Project 2, managing strategic workflow.
"""

from typing import Optional, Dict, List, Tuple
from ..base_agent import BaseAgent, AgentResponse
from config import INTENT_KEYWORDS


STRATEGIC_PLANNING_SYSTEM_PROMPT = """You are the Strategic Planning (Agent) for the Major Celebrations Strategic Planning project.

Your role:
- Manage the strategic workflow and coordinate between agents
- Improve and clarify user requests before routing
- Ensure quality of strategic outputs
- Provide comprehensive and integrated vision

Available Agents:
1. Benchmarking (Agent) - Studies international celebration experiences
2. KPI Development (Agent) - Recommends performance indicators
3. Critique & Review (Agent) - Reviews and improves outputs
4. Content Preparation (Agent) - Formats presentations and slides

Context:
- Objective: Develop vision and strategic framework for a historic national celebration
- Duration: 20 weeks
- Expected Deliverables: Benchmarking report, KPI framework, positioning options, leadership presentations

Working Style:
- Carefully analyze requests before routing
- Clarify ambiguous requests
- Ensure output consistency
- Provide comprehensive summaries

When analyzing requests:
- For international comparisons, case studies, or benchmarking -> route to Benchmarking (Agent)
- For KPIs, metrics, or performance indicators -> route to KPI Development (Agent)
- For reviewing or critiquing previous outputs -> route to Critique & Review (Agent)
- For slides, presentations, or content formatting -> route to Content Preparation (Agent)"""


class StrategicPlanningAgent(BaseAgent):
    """
    Strategic Planning/Orchestrator agent for Project 2.
    Strategic Planning (Agent) - Main orchestrator
    """

    def __init__(self):
        super().__init__(
            name="Strategic Planning (Agent)",
            name_en="Strategic Planning (Agent)",
            description="Orchestrates research and synthesizes strategic recommendations",
            temperature=0.3
        )

        # Lazy initialization
        self._benchmarking_agent = None
        self._kpi_agent = None
        self._critique_agent = None
        self._content_prep_agent = None

        self._last_response: Optional[AgentResponse] = None
        self._last_agent: Optional[str] = None

    @property
    def benchmarking_agent(self):
        if self._benchmarking_agent is None:
            from .benchmarking import BenchmarkingAgent
            self._benchmarking_agent = BenchmarkingAgent()
        return self._benchmarking_agent

    @property
    def kpi_agent(self):
        if self._kpi_agent is None:
            from .kpi import KPIAgent
            self._kpi_agent = KPIAgent()
        return self._kpi_agent

    @property
    def critique_agent(self):
        if self._critique_agent is None:
            from .critique import CritiqueAgent
            self._critique_agent = CritiqueAgent()
        return self._critique_agent

    @property
    def content_prep_agent(self):
        if self._content_prep_agent is None:
            from .content_prep import ContentPrepAgent
            self._content_prep_agent = ContentPrepAgent()
        return self._content_prep_agent

    def get_system_prompt(self) -> str:
        return STRATEGIC_PLANNING_SYSTEM_PROMPT

    def _classify_intent(self, message: str) -> Tuple[str, float]:
        """Classify user intent based on keywords."""
        message_lower = message.lower()

        # English keywords for intent classification
        intent_keywords = {
            "benchmarking": ["benchmark", "compare", "comparison", "international", "case study", "st. petersburg", "petersburg", "experience", "best practice"],
            "kpi": ["kpi", "indicator", "metric", "measure", "performance", "target", "goal"],
            "critique": ["review", "critique", "feedback", "improve", "evaluate", "assess", "previous"],
            "slide": ["slide", "presentation", "convert", "format", "content", "powerpoint", "deck"]
        }

        scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[intent] = score

        if not scores:
            return ("general", 0.5)

        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / 3, 1.0)

        return (best_intent, confidence)

    def _get_agent_for_intent(self, intent: str) -> Optional[BaseAgent]:
        """Get the appropriate agent for an intent."""
        agent_map = {
            "benchmarking": self.benchmarking_agent,
            "kpi": self.kpi_agent,
            "critique": self.critique_agent,
            "slide": self.content_prep_agent,
        }
        return agent_map.get(intent)

    def _should_use_critique(self, message: str) -> bool:
        """Check if the message is asking to review previous content."""
        review_keywords = ["review", "critique", "evaluate", "feedback", "improve", "assess"]
        return any(kw in message.lower() for kw in review_keywords) and self._last_response is not None

    def _should_format_slides(self, message: str) -> bool:
        """Check if the message is asking to format for slides."""
        slide_keywords = ["slide", "presentation", "convert", "format", "powerpoint"]
        return any(kw in message.lower() for kw in slide_keywords) and self._last_response is not None

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Route the request to appropriate agents."""
        self._clear_thinking()
        self._log_thinking("Analyzing strategic request...")

        # Check for critique request
        if self._should_use_critique(user_message):
            self._log_thinking("Request relates to reviewing previous content")
            self._log_thinking(f"Routing to: {self.critique_agent.name}")

            response = self.critique_agent.review(
                content_to_review=self._last_response.content,
                source_agent=self._last_agent,
                original_request=user_message
            )

            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking
            return response

        # Check for slide formatting
        if self._should_format_slides(user_message):
            self._log_thinking("Request relates to formatting content for presentation")
            self._log_thinking(f"Routing to: {self.content_prep_agent.name}")

            response = self.content_prep_agent.format_for_slides(
                content=self._last_response.content
            )

            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking
            return response

        # Classify intent
        intent, confidence = self._classify_intent(user_message)
        self._log_thinking(f"Intent classified: {intent} (confidence: {confidence:.0%})")

        # Get appropriate agent
        agent = self._get_agent_for_intent(intent)

        if agent:
            self._log_thinking(f"Routing to: {agent.name}")
            response = agent.invoke(user_message, context, conversation_history)

            self._last_response = response
            self._last_agent = agent.name

            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking
            return response

        # General response
        return self._provide_general_response(user_message)

    def _provide_general_response(self, user_message: str) -> AgentResponse:
        """Provide general strategic guidance."""
        general_guidance = """## Welcome to the Major Celebrations Strategic Planning System

I am the Strategic Planning (Agent). I can help you with:

### International Benchmarking
Study and analyze major international celebration experiences.
**Example:** "I need benchmarking on St. Petersburg 300th Anniversary"

### Key Performance Indicators
Recommendations for measuring celebration success.
**Example:** "What KPIs do you recommend?"

### Review and Critique
Review outputs and provide constructive feedback.
**Example:** "Review the previous analysis"

### Presentation Content
Transform content into professional presentations.
**Example:** "Convert to presentation slides"

---
How can I assist you with strategic planning today?"""

        return AgentResponse(
            content=general_guidance,
            thinking=self._get_thinking_trace(),
            metadata={"type": "general_guidance"},
            agent_name=self.name,
            agent_name_en=self.name_en
        )

    def get_available_agents(self) -> List[Dict]:
        """Get information about available agents."""
        return [
            {
                "name": self.benchmarking_agent.name,
                "name_en": self.benchmarking_agent.name_en,
                "description": self.benchmarking_agent.description,
            },
            {
                "name": self.kpi_agent.name,
                "name_en": self.kpi_agent.name_en,
                "description": self.kpi_agent.description,
            },
            {
                "name": self.critique_agent.name,
                "name_en": self.critique_agent.name_en,
                "description": self.critique_agent.description,
            },
            {
                "name": self.content_prep_agent.name,
                "name_en": self.content_prep_agent.name_en,
                "description": self.content_prep_agent.description,
            },
        ]
