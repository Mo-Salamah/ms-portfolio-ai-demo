"""
وكيل التنسيق — لجنة الفعاليات
"""

from typing import Optional, Dict, List, Tuple
from ..base_agent import BaseAgent, AgentResponse
from config import INTENT_KEYWORDS


COORDINATOR_SYSTEM_PROMPT = """أنت وكيل التنسيق في نظام لجنة الفعاليات.

دورك:
- توجيه الطلبات للوكلاء المتخصصين المناسبين
- تلخيص النتائج والتنسيق بين الوكلاء
- ضمان اكتمال المعلومات وجودتها

الوكلاء المتاحون:
١. وكيل تحليل البيانات — يحلل بيانات الفعاليات وينتج تقارير إحصائية
٢. وكيل المتابعة والتواصل — يحدد المعلومات الناقصة ويصيغ رسائل المتابعة
٣. وكيل إعداد التقارير — يجمّع النتائج ويعد تقارير اللجان
٤. وكيل فحص الجودة — يتحقق من اكتمال البيانات وجودتها

السياق:
- خمس مدن مستهدفة: الرياض، جدة، العلا، عسير، حاضرة الدمام
- بيانات فعلية من قواعد بيانات تقاويم المدن
- الهدف: ضمان جاهزية المعلومات للجان الإشرافية

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
- طلبات تحليل البيانات والإحصائيات -> وكيل تحليل البيانات
- طلبات المعلومات الناقصة والمتابعة -> وكيل المتابعة والتواصل
- طلبات التقارير والملخصات -> وكيل إعداد التقارير
- طلبات فحص الجودة والتحقق -> وكيل فحص الجودة"""


class CoordinatorAgent(BaseAgent):
    """وكيل التنسيق — المنسق الرئيسي للجنة الفعاليات"""

    def __init__(self):
        super().__init__(
            name="وكيل التنسيق",
            name_en="وكيل التنسيق",
            description="توجيه الطلبات وتنسيق سير العمل",
            temperature=0.3
        )

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

        intent_keywords = {
            "data_analysis": ["تحليل", "بيانات", "إحصائيات", "توزيع", "إجمالي", "فعاليات", "تصنيف", "نوع", "جهة", "analyze", "analysis", "statistics", "data", "events", "total", "count", "الرياض", "جدة", "العلا", "عسير", "الدمام", "مدينة", "مدن"],
            "followup": ["متابعة", "رسالة", "بريد", "تواصل", "ناقص", "مطلوب", "استكمال", "إرسال", "missing", "follow-up", "follow up", "email", "gap", "incomplete"],
            "reporting": ["تقرير", "ملخص", "لجنة", "اجتماع", "تنفيذي", "report", "committee", "executive", "briefing", "summary", "prepare"],
            "quality_check": ["جودة", "فحص", "تحقق", "اكتمال", "صحة", "quality", "check", "validate", "verify", "complete", "accuracy"]
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
        self._log_thinking("تحليل الطلب لتحديد الوكيل المناسب...")

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
        """Provide general guidance in Arabic."""
        general_guidance = """نظام لجنة الفعاليات يضم الوكلاء التالية:

وكيل تحليل البيانات — لتحليل بيانات الفعاليات من المدن الخمس (الرياض، جدة، العلا، عسير، حاضرة الدمام) وإنتاج تقارير إحصائية.

وكيل المتابعة والتواصل — لتحديد المعلومات الناقصة وصياغة رسائل المتابعة للجهات المسؤولة.

وكيل إعداد التقارير — لتجميع النتائج وإعداد تقارير اللجنة الإشرافية.

وكيل فحص الجودة — للتحقق من اكتمال البيانات وجودتها.

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
            {"name": self.data_analysis_agent.name, "name_en": self.data_analysis_agent.name_en, "description": self.data_analysis_agent.description},
            {"name": self.followup_agent.name, "name_en": self.followup_agent.name_en, "description": self.followup_agent.description},
            {"name": self.reporting_agent.name, "name_en": self.reporting_agent.name_en, "description": self.reporting_agent.description},
            {"name": self.quality_check_agent.name, "name_en": self.quality_check_agent.name_en, "description": self.quality_check_agent.description},
        ]
