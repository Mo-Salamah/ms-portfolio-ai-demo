"""
Critique Agent for MS Portfolio AI Agent Demo
وكيل النقد والمراجعة لنظام المحفظة الذكي

This agent specializes in reviewing and critiquing outputs from other agents.
"""

from typing import Optional, Dict, List
from .base_agent import BaseAgent, AgentResponse
from prompts.critique_prompt import CRITIQUE_SYSTEM_PROMPT


class CritiqueAgent(BaseAgent):
    """
    Agent specialized in reviewing and critiquing content.
    وكيل متخصص في مراجعة وتقييم المحتوى
    """

    def __init__(self):
        super().__init__(
            name="وكيل النقد والمراجعة",
            name_en="Critique Agent",
            description="متخصص في مراجعة المخرجات وتقديم ملاحظات بناءة للتحسين",
            temperature=0.6  # Balanced for thoughtful critique
        )

    def get_system_prompt(self) -> str:
        """Return the critique-specific system prompt."""
        return CRITIQUE_SYSTEM_PROMPT

    def review(
        self,
        content_to_review: str,
        source_agent: str,
        original_request: Optional[str] = None
    ) -> AgentResponse:
        """
        Review content from another agent.

        Args:
            content_to_review: The content to be reviewed
            source_agent: Name of the agent that produced the content
            original_request: Optional original user request

        Returns:
            AgentResponse with critique and recommendations
        """
        self._clear_thinking()
        self._log_thinking(f"استلام محتوى للمراجعة من: {source_agent}")

        # Build the review request
        review_request = f"""## المحتوى المطلوب مراجعته

**المصدر:** {source_agent}
"""
        if original_request:
            review_request += f"""
**الطلب الأصلي:**
{original_request}
"""

        review_request += f"""
**المحتوى:**
{content_to_review}

---

يرجى مراجعة هذا المحتوى وتقديم تقييم شامل يشمل:
1. نقاط القوة
2. مجالات التحسين
3. توصيات محددة
4. التقييم العام (1-5)
"""

        self._log_thinking("جارٍ تحليل المحتوى وإعداد المراجعة...")

        return self.invoke(review_request)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """
        Invoke the critique agent.

        Args:
            user_message: The review request or content to critique
            context: Optional additional context
            conversation_history: Optional previous messages

        Returns:
            AgentResponse with critique
        """
        self._clear_thinking()
        self._log_thinking("بدء عملية المراجعة والتقييم...")

        # Build messages
        messages = self._build_messages(user_message, context, conversation_history)

        try:
            self._log_thinking("جارٍ تحليل المحتوى...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم إكمال المراجعة بنجاح")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
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
                content=f"عذراً، حدث خطأ أثناء إعداد المراجعة: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )

    def quick_review(self, content: str) -> Dict[str, any]:
        """
        Perform a quick review and return structured feedback.

        Args:
            content: Content to review

        Returns:
            Dictionary with strengths, improvements, and rating
        """
        self._clear_thinking()

        quick_prompt = f"""راجع هذا المحتوى بسرعة وقدم:
1. ثلاث نقاط قوة (في جملة واحدة لكل منها)
2. اثنين من مجالات التحسين (في جملة واحدة لكل منها)
3. تقييم من 1-5

المحتوى:
{content[:2000]}...

قدم الإجابة بتنسيق موجز."""

        response = self.invoke(quick_prompt)

        return {
            "feedback": response.content,
            "agent": self.name,
            "thinking": response.thinking
        }
