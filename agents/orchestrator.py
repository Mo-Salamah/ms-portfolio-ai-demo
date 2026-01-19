"""
Orchestrator Agent for MS Portfolio AI Agent Demo
وكيل التنسيق الرئيسي لنظام المحفظة الذكي

This agent routes requests to appropriate specialist agents and coordinates workflows.
"""

from typing import Optional, Dict, List, Tuple
from .base_agent import BaseAgent, AgentResponse
from .benchmarking_agent import BenchmarkingAgent
from .kpi_agent import KPIAgent
from .critique_agent import CritiqueAgent
from .media_agent import MediaAgent
from .slide_agent import SlideAgent
from prompts.orchestrator_prompt import ORCHESTRATOR_SYSTEM_PROMPT
from config import INTENT_KEYWORDS, AGENT_NAMES


class OrchestratorAgent(BaseAgent):
    """
    Main orchestrator that routes requests to specialist agents.
    المنسق الرئيسي الذي يوجه الطلبات إلى الوكلاء المتخصصين
    """

    def __init__(self):
        super().__init__(
            name="المنسق",
            name_en="Orchestrator",
            description="المنسق الرئيسي لتوجيه الطلبات والتنسيق بين الوكلاء المتخصصين",
            temperature=0.3  # Lower temperature for consistent routing
        )

        # Initialize specialist agents
        self.benchmarking_agent = BenchmarkingAgent()
        self.kpi_agent = KPIAgent()
        self.critique_agent = CritiqueAgent()
        self.media_agent = MediaAgent()
        self.slide_agent = SlideAgent()

        # Store last response for critique/slide follow-ups
        self._last_response: Optional[AgentResponse] = None
        self._last_agent: Optional[str] = None

    def get_system_prompt(self) -> str:
        """Return the orchestrator-specific system prompt."""
        return ORCHESTRATOR_SYSTEM_PROMPT

    def _classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classify the user's intent based on keywords.

        Args:
            message: User's message in Arabic

        Returns:
            Tuple of (intent_type, confidence_score)
        """
        message_lower = message.lower()

        # Count keyword matches for each intent
        scores = {}
        for intent, keywords in INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[intent] = score

        if not scores:
            return ("general", 0.5)

        # Get the intent with highest score
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / 3, 1.0)  # Normalize confidence

        return (best_intent, confidence)

    def _get_agent_for_intent(self, intent: str) -> BaseAgent:
        """
        Get the appropriate agent for an intent.

        Args:
            intent: The classified intent

        Returns:
            The appropriate specialist agent
        """
        agent_map = {
            "benchmarking": self.benchmarking_agent,
            "kpi": self.kpi_agent,
            "critique": self.critique_agent,
            "media": self.media_agent,
            "slide": self.slide_agent,
        }
        return agent_map.get(intent)

    def _should_use_critique(self, message: str) -> bool:
        """Check if the message is asking to review previous content."""
        review_keywords = ["راجع", "قيم", "حسن", "مراجعة", "تقييم", "ملاحظات على"]
        return any(kw in message for kw in review_keywords) and self._last_response is not None

    def _should_format_slides(self, message: str) -> bool:
        """Check if the message is asking to format for slides."""
        slide_keywords = ["شرائح", "عرض تقديمي", "للعرض", "ملخص للعرض"]
        return any(kw in message for kw in slide_keywords) and self._last_response is not None

    def route_request(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """
        Route the request to the appropriate agent.

        Args:
            user_message: The user's message
            conversation_history: Optional conversation history

        Returns:
            AgentResponse from the appropriate agent
        """
        self._clear_thinking()
        self._log_thinking("تحليل الطلب لتحديد الوكيل المناسب...")

        # Check for follow-up requests
        if self._should_use_critique(user_message):
            self._log_thinking("الطلب يتعلق بمراجعة المحتوى السابق")
            self._log_thinking(f"توجيه إلى: {self.critique_agent.name}")

            response = self.critique_agent.review(
                content_to_review=self._last_response.content,
                source_agent=self._last_agent,
                original_request=user_message
            )

            # Merge thinking traces
            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking

            return response

        if self._should_format_slides(user_message):
            self._log_thinking("الطلب يتعلق بتنسيق المحتوى للعرض")
            self._log_thinking(f"توجيه إلى: {self.slide_agent.name}")

            response = self.slide_agent.format_for_slides(
                content=self._last_response.content
            )

            # Merge thinking traces
            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking

            return response

        # Classify intent
        intent, confidence = self._classify_intent(user_message)
        self._log_thinking(f"تم تصنيف النية: {intent} (ثقة: {confidence:.0%})")

        # Get appropriate agent
        agent = self._get_agent_for_intent(intent)

        if agent:
            self._log_thinking(f"توجيه إلى: {agent.name}")

            # Invoke the specialist agent
            response = agent.invoke(user_message, conversation_history=conversation_history)

            # Store for potential follow-ups
            self._last_response = response
            self._last_agent = agent.name

            # Merge thinking traces
            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking

            return response

        else:
            # No specific agent identified, provide a general response
            self._log_thinking("لم يتم تحديد وكيل محدد، سيتم الرد بشكل عام")
            return self._provide_general_response(user_message)

    def _provide_general_response(self, user_message: str) -> AgentResponse:
        """
        Provide a general response when no specific agent is appropriate.

        Args:
            user_message: The user's message

        Returns:
            General guidance response
        """
        general_guidance = f"""## مرحباً بك في نظام المحفظة الذكي

أنا المنسق الرئيسي لهذا النظام. يمكنني مساعدتك في المجالات التالية:

### 📊 التحليل المقارن والمعايير الدولية
اسأل عن تجارب احتفالات دولية مثل سانت بطرسبرغ أو روما أو برشلونة.
**مثال:** "أريد مقارنة مع تجارب دولية مشابهة"

### 📈 مؤشرات الأداء الرئيسية
احصل على توصيات لمؤشرات قياس نجاح الاحتفالية.
**مثال:** "ما هي مؤشرات الأداء المقترحة لمتابعة التنفيذ؟"

### ✍️ المراجعة والنقد
راجع أي محتوى سابق واحصل على ملاحظات بناءة.
**مثال:** "راجع التحليل السابق وقدم ملاحظاتك"

### 📢 الحملات الإعلامية
احصل على توصيات لاستراتيجيات التغطية الإعلامية.
**مثال:** "ما هي استراتيجية الحملة الإعلامية المقترحة؟"

### 📑 المحتوى التقديمي
حوّل أي محتوى إلى شرائح عرض احترافية.
**مثال:** "حول الإجابة السابقة إلى عرض تقديمي"

---

كيف يمكنني مساعدتك اليوم؟"""

        return AgentResponse(
            content=general_guidance,
            thinking=self._get_thinking_trace(),
            metadata={"type": "general_guidance"},
            agent_name=self.name,
            agent_name_en=self.name_en
        )

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """
        Main invoke method - routes to route_request.

        Args:
            user_message: The user's message
            context: Optional additional context (not used)
            conversation_history: Optional conversation history

        Returns:
            AgentResponse from the appropriate agent
        """
        return self.route_request(user_message, conversation_history)

    def get_available_agents(self) -> List[Dict]:
        """
        Get information about available agents.

        Returns:
            List of agent info dictionaries
        """
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
                "name": self.media_agent.name,
                "name_en": self.media_agent.name_en,
                "description": self.media_agent.description,
            },
            {
                "name": self.slide_agent.name,
                "name_en": self.slide_agent.name_en,
                "description": self.slide_agent.description,
            },
        ]
