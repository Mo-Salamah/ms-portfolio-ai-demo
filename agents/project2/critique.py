"""
Critique Agent for Project 2 - Major Celebrations Planning

Reviews outputs and provides constructive feedback.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse


CRITIQUE_SYSTEM_PROMPT = """You are a Critique and Review Agent specialized in evaluating strategic outputs.

IMPORTANT: Always respond in English.

Your role:
1. Review content with a critical and constructive eye
2. Identify strengths and areas of excellence
3. Discover gaps and weaknesses
4. Provide specific suggestions for improvement
5. Ensure consistency and accuracy

Review Criteria:
- Completeness: Does the content cover all required aspects?
- Accuracy: Is the information correct and supported?
- Clarity: Are the ideas clear and organized?
- Actionability: Are the recommendations practical and realistic?
- Relevance: Is the content appropriate for the local context?

Review Structure:
1. General summary of content
2. Strengths (3-5 points)
3. Areas for Improvement (3-5 points)
4. Specific suggestions
5. Overall assessment

Critique Style:
- Constructive and professional
- Specific and actionable
- Balanced between positive and negative
- Supported with examples"""


class CritiqueAgent(BaseAgent):
    """
    Critique specialist for Project 2.
    """

    def __init__(self):
        super().__init__(
            name="Critique Agent",
            name_en="Critique Agent",
            description="Review outputs and provide constructive feedback",
            temperature=0.4
        )

    def get_system_prompt(self) -> str:
        return CRITIQUE_SYSTEM_PROMPT

    def review(
        self,
        content_to_review: str,
        source_agent: str = None,
        original_request: str = None
    ) -> AgentResponse:
        """
        Review content and provide feedback.

        Args:
            content_to_review: The content to be reviewed
            source_agent: Name of the agent that produced the content
            original_request: The original user request

        Returns:
            AgentResponse with critique
        """
        self._clear_thinking()
        self._log_thinking("Reviewing content...")

        review_request = f"""## Review Request

**Content to review:**
{content_to_review}

"""
        if source_agent:
            review_request += f"**Source:** {source_agent}\n"
        if original_request:
            review_request += f"**Original Request:** {original_request}\n"

        review_request += """
---
Provide a comprehensive review including:
1. Content summary
2. Strengths
3. Areas for improvement
4. Specific suggestions
5. Overall assessment"""

        return self.invoke(review_request)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Provide critique based on user request."""
        self._clear_thinking()
        self._log_thinking("Preparing critical review...")

        messages = self._build_messages(user_message, context, conversation_history)

        try:
            self._log_thinking("Analyzing content...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("Review prepared successfully")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "analysis_type": "critique"
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
                content=f"Sorry, an error occurred during review: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )


    def quick_review(self, content: str) -> AgentResponse:
        """Provide a quick review focusing on key points."""
        request = f"""Provide a quick and focused review of the following content:

{content}

Focus on:
1. Top 3 strengths
2. Top 3 areas for improvement
3. One key recommendation"""

        return self.invoke(request)
