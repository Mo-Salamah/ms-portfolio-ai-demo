"""
وكيل التخطيط الاستراتيجي — احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية
"""

from typing import Optional, Dict, List, Tuple
from ..base_agent import BaseAgent, AgentResponse
from config import INTENT_KEYWORDS


STRATEGIC_PLANNING_SYSTEM_PROMPT = """أنت وكيل التخطيط الاستراتيجي في نظام احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية.

دورك:
- إدارة سير العمل الاستراتيجي والتنسيق بين الوكلاء
- تحسين وتوضيح طلبات المستخدم قبل توجيهها
- ضمان جودة المخرجات الاستراتيجية
- تقديم رؤية شاملة ومتكاملة

الوكلاء المتاحون:
١. وكيل المقارنة المعيارية — يدرس تجارب الاحتفاليات الدولية
٢. وكيل مؤشرات الأداء — يوصي بمؤشرات الأداء
٣. وكيل المراجعة — يراجع المخرجات ويقدم ملاحظات بناءة
٤. وكيل إعداد المحتوى — ينسق المحتوى للعروض التقديمية

السياق:
- الهدف: تطوير الرؤية والإطار الاستراتيجي لاحتفالية وطنية تاريخية
- المدة: ٢٠ أسبوع
- المخرجات المتوقعة: تقرير المقارنة المعيارية وإطار مؤشرات الأداء وخيارات التموضع وعروض تقديمية للقيادة

أسلوب الرد:
- عربي فصيح مؤسسي
- مختصر ومباشر — لا مقدمات طويلة
- لا تستخدم عبارات مثل "بالتأكيد" أو "سعيد بمساعدتك"
- تعامل مع المستخدم كمسؤول رفيع المستوى
- استخدم البيانات الفعلية فقط — لا تخترع أرقاماً
- إذا لم تتوفر معلومة، قل ذلك صراحة
- تجنب النقاط (bullets) إلا للضرورة — استخدم صياغة نثرية
- لا تستخدم رموز تعبيرية مطلقاً

عند تحليل الطلب:
- طلبات المقارنة والدراسات والتجارب الدولية -> وكيل المقارنة المعيارية
- طلبات المؤشرات والقياس والأداء -> وكيل مؤشرات الأداء
- طلبات المراجعة والنقد والتقييم -> وكيل المراجعة
- طلبات العروض التقديمية والشرائح -> وكيل إعداد المحتوى"""


class StrategicPlanningAgent(BaseAgent):
    """وكيل التخطيط الاستراتيجي — المنسق الرئيسي لاحتفالية ٣٠٠ عام"""

    def __init__(self):
        super().__init__(
            name="وكيل التخطيط الاستراتيجي",
            name_en="وكيل التخطيط الاستراتيجي",
            description="إدارة سير العمل الاستراتيجي والتنسيق",
            temperature=0.3
        )

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

        intent_keywords = {
            "benchmarking": ["مقارنة", "معايير", "دراسة حالة", "تجارب دولية", "أفضل الممارسات", "مقارن", "benchmark", "تحليل مقارن", "سانت بطرسبرغ", "روما", "برشلونة", "تجارب عالمية"],
            "kpi": ["مؤشرات", "قياس", "أداء", "KPI", "تقييم", "مؤشر", "قياسات", "متابعة", "رصد", "مقاييس"],
            "critique": ["مراجعة", "نقد", "تحسين", "تقييم", "تحليل نقدي", "راجع", "قيم", "حلل", "ملاحظات", "تعليقات"],
            "slide": ["عرض", "شريحة", "تقديم", "عرض تقديمي", "شرائح", "بوربوينت", "تلخيص", "للعرض", "slide", "presentation", "convert", "format", "powerpoint"]
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
        review_keywords = ["مراجعة", "راجع", "نقد", "تقييم", "review", "critique"]
        return any(kw in message.lower() for kw in review_keywords) and self._last_response is not None

    def _should_format_slides(self, message: str) -> bool:
        """Check if the message is asking to format for slides."""
        slide_keywords = ["عرض تقديمي", "شرائح", "شريحة", "حوّل", "slide", "presentation"]
        return any(kw in message.lower() for kw in slide_keywords) and self._last_response is not None

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Route the request to appropriate agents."""
        self._clear_thinking()
        self._log_thinking("تحليل الطلب الاستراتيجي...")

        # Check for critique request
        if self._should_use_critique(user_message):
            self._log_thinking("الطلب يتعلق بمراجعة محتوى سابق")
            self._log_thinking(f"توجيه إلى: {self.critique_agent.name}")

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
            self._log_thinking("الطلب يتعلق بتنسيق المحتوى للعرض التقديمي")
            self._log_thinking(f"توجيه إلى: {self.content_prep_agent.name}")

            response = self.content_prep_agent.format_for_slides(
                content=self._last_response.content
            )

            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking
            return response

        # Classify intent
        intent, confidence = self._classify_intent(user_message)
        self._log_thinking(f"تصنيف الطلب: {intent} (ثقة: {confidence:.0%})")

        # Get appropriate agent
        agent = self._get_agent_for_intent(intent)

        if agent:
            self._log_thinking(f"توجيه إلى: {agent.name}")
            response = agent.invoke(user_message, context, conversation_history)

            self._last_response = response
            self._last_agent = agent.name

            combined_thinking = self._get_thinking_trace() + "\n\n" + response.thinking
            response.thinking = combined_thinking
            return response

        return self._provide_general_response(user_message)

    def _provide_general_response(self, user_message: str) -> AgentResponse:
        """Provide general strategic guidance in Arabic."""
        general_guidance = """نظام احتفالية مرور ٣٠٠ عام يضم الوكلاء التالية:

وكيل المقارنة المعيارية — لدراسة وتحليل تجارب الاحتفاليات الدولية الكبرى واستخلاص الدروس المستفادة.

وكيل مؤشرات الأداء — لتوصية مؤشرات أداء مناسبة وتحديد طرق القياس والمتابعة.

وكيل المراجعة — لمراجعة المخرجات وتقديم ملاحظات بناءة لتحسين الجودة.

وكيل إعداد المحتوى — لتنسيق المحتوى وتحويله إلى عروض تقديمية جاهزة للقيادة.

يمكنك توجيه طلبك مباشرة وسيتم تحويله للوكيل المناسب."""

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
            {"name": self.benchmarking_agent.name, "name_en": self.benchmarking_agent.name_en, "description": self.benchmarking_agent.description},
            {"name": self.kpi_agent.name, "name_en": self.kpi_agent.name_en, "description": self.kpi_agent.description},
            {"name": self.critique_agent.name, "name_en": self.critique_agent.name_en, "description": self.critique_agent.description},
            {"name": self.content_prep_agent.name, "name_en": self.content_prep_agent.name_en, "description": self.content_prep_agent.description},
        ]
