"""
Coordinator Agent for Project 1 - Events Oversight
Coordination (Agent) - Main orchestrator for the Events Oversight project

This is the orchestrator for Project 1, routing requests to specialist agents.
"""

from typing import Optional, Dict, List, Tuple
from ..base_agent import BaseAgent, AgentResponse
from config import INTENT_KEYWORDS


COORDINATOR_SYSTEM_PROMPT = """You are the Coordination (Agent) for the National Events Planning Oversight project.

Your role:
- Route requests to appropriate specialist agents
- Summarize results and coordinate between agents
- Ensure information completeness and quality

Available Agents:
1. Data Analysis (Agent) - Analyzes event data and produces statistical reports
2. Follow-up & Communication (Agent) - Identifies missing information and drafts follow-up messages
3. Reporting (Agent) - Compiles results and prepares committee reports
4. Quality Assurance (Agent) - Verifies data completeness and quality

Context:
- Deadline: Oversight Committee meeting - September 1, 2027
- Three main implementing entities: Implementing Entity A, Entity B, Entity C
- Goal: Ensure information readiness for oversight committees

Response Style:
- Use professional English
- Be concise and professional
- Clearly identify the appropriate agent
- Provide a summary of actions taken

When analyzing requests:
- For data analysis, statistics, or event distribution questions -> route to Data Analysis (Agent)
- For missing information or follow-up needs -> route to Follow-up & Communication (Agent)
- For reports, summaries, or committee documents -> route to Reporting (Agent)
- For quality checks or data validation -> route to Quality Assurance (Agent)"""


class CoordinatorAgent(BaseAgent):
    """
    Coordinator/Orchestrator agent for Project 1.
    Coordination (Agent) - Main orchestrator
    """

    def __init__(self):
        super().__init__(
            name="Coordination (Agent)",
            name_en="Coordination (Agent)",
            description="Routes requests and manages workflow across all sub-agents",
            temperature=0.3
        )

        # Lazy initialization of specialist agents
        self._data_analysis_agent = None
        self._followup_agent = None
        self._reporting_agent = None
        self._quality_check_agent = None

        self._last_response: Optional[AgentResponse] = None
        self._last_agent: Optional[str] = None

    @property
    def data_analysis_agent(self):
        if self._data_analysis_agent is None:
            from .data_analysis import DataAnalysisAgent
            self._data_analysis_agent = DataAnalysisAgent()
        return self._data_analysis_agent

    @property
    def followup_agent(self):
        if self._followup_agent is None:
            from .followup import FollowupAgent
            self._followup_agent = FollowupAgent()
        return self._followup_agent

    @property
    def reporting_agent(self):
        if self._reporting_agent is None:
            from .reporting import ReportingAgent
            self._reporting_agent = ReportingAgent()
        return self._reporting_agent

    @property
    def quality_check_agent(self):
        if self._quality_check_agent is None:
            from .quality_check import QualityCheckAgent
            self._quality_check_agent = QualityCheckAgent()
        return self._quality_check_agent

    def get_system_prompt(self) -> str:
        return COORDINATOR_SYSTEM_PROMPT

    def _classify_intent(self, message: str) -> Tuple[str, float]:
        """Classify user intent based on keywords."""
        message_lower = message.lower()

        # English keywords for intent classification
        intent_keywords = {
            "data_analysis": ["analyze", "analysis", "statistics", "distribution", "data", "events", "total", "count", "summary"],
            "followup": ["missing", "incomplete", "follow-up", "follow up", "email", "contact", "gap", "lacking"],
            "reporting": ["report", "committee", "executive", "briefing", "document", "prepare", "summary"],
            "quality_check": ["quality", "check", "validate", "verify", "complete", "accuracy"]
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
            "data_analysis": self.data_analysis_agent,
            "followup": self.followup_agent,
            "reporting": self.reporting_agent,
            "quality_check": self.quality_check_agent,
        }
        return agent_map.get(intent)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Route the request to appropriate agents."""
        self._clear_thinking()
        self._log_thinking("Analyzing request to determine appropriate agent...")

        # Check for quality check request
        quality_keywords = ["quality", "check", "validate", "verify", "complete"]
        if any(kw in user_message.lower() for kw in quality_keywords):
            self._log_thinking("Routing to: Quality Assurance (Agent)")
            response = self.quality_check_agent.invoke(user_message, context, conversation_history)
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
        """Provide general guidance."""
        general_guidance = """## Welcome to the National Events Planning Oversight System

I am the Coordination (Agent). I can help you with:

### Data Analysis
Analyze event data from implementing entities and produce statistical reports.
**Example:** "Analyze the event data we received"

### Follow-up & Communication
Identify missing information and draft follow-up messages to entities.
**Example:** "What information is missing from Entity B?"

### Committee Reporting
Compile results and prepare reports for the oversight committee.
**Example:** "Prepare a status report for the committee"

### Quality Assurance
Verify data completeness and quality.
**Example:** "Check data quality for received submissions"

---
How can I assist you today?"""

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
                "name": self.data_analysis_agent.name,
                "name_en": self.data_analysis_agent.name_en,
                "description": self.data_analysis_agent.description,
            },
            {
                "name": self.followup_agent.name,
                "name_en": self.followup_agent.name_en,
                "description": self.followup_agent.description,
            },
            {
                "name": self.reporting_agent.name,
                "name_en": self.reporting_agent.name_en,
                "description": self.reporting_agent.description,
            },
            {
                "name": self.quality_check_agent.name,
                "name_en": self.quality_check_agent.name_en,
                "description": self.quality_check_agent.description,
            },
        ]
