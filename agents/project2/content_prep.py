"""
Content Preparation Agent for Project 2 - Major Celebrations Planning

Formats content for professional presentations.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from config import PRESENTATION_GUIDELINES


CONTENT_PREP_SYSTEM_PROMPT = f"""You are a Content Preparation Agent specialized in converting content into professional presentations.

IMPORTANT: Always respond in English.

{PRESENTATION_GUIDELINES}

Your main tasks:
1. Convert content into organized presentation slides
2. Craft strong action titles
3. Simplify content without losing substance
4. Add presenter notes

Ideal Slide Structure:
```
## [Action Title - A complete sentence summarizing the message]

- First point (supported with data)
- Second point
- Third point
- Fourth point

---
*Presenter Note: [Additional guidance]*
```

Target Audience:
- Senior government leadership
- Oversight committees
- Decision makers

Content Style:
- Formal and professional
- Direct and focused
- Supported with numbers
- Presentable in 2-3 minutes per slide"""


class ContentPrepAgent(BaseAgent):
    """
    Content Preparation specialist for Project 2.
    """

    def __init__(self):
        super().__init__(
            name="Content Preparation Agent",
            name_en="Content Preparation Agent",
            description="Format content for presentations",
            temperature=0.5
        )

    def get_system_prompt(self) -> str:
        return CONTENT_PREP_SYSTEM_PROMPT

    def format_for_slides(
        self,
        content: str,
        num_slides: Optional[int] = None,
        target_audience: str = "government leadership"
    ) -> AgentResponse:
        """
        Format content into presentation slides.

        Args:
            content: The content to format
            num_slides: Optional target number of slides
            target_audience: Description of the audience

        Returns:
            AgentResponse with slide-formatted content
        """
        self._clear_thinking()
        self._log_thinking("Analyzing content for slide conversion...")

        format_request = f"""## Content to Convert to Presentation

**Target Audience:** {target_audience}
"""
        if num_slides:
            format_request += f"**Target Number of Slides:** {num_slides}\n"

        format_request += f"""
**Original Content:**
{content}

---

Please convert this content into professional presentation slides with:
1. Strong action titles (complete sentences)
2. Concise and direct points (4-6 per slide)
3. Supporting data where possible
4. Presenter notes"""

        self._log_thinking(f"Preparing content for {target_audience}")

        return self.invoke(format_request)

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Prepare content for presentations."""
        self._clear_thinking()
        self._log_thinking("Starting content conversion to presentation format...")

        messages = self._build_messages(user_message, context, conversation_history)

        try:
            self._log_thinking("Designing slide structure...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("Presentation content prepared successfully")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "format": "presentation_slides"
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
                content=f"Sorry, an error occurred while formatting content: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )


    def create_executive_summary(
        self,
        content: str,
        max_slides: int = 5
    ) -> AgentResponse:
        """Create an executive summary presentation."""
        self._clear_thinking()
        self._log_thinking("Preparing executive summary...")

        summary_request = f"""Create an executive summary of maximum {max_slides} slides for the following content:

{content}

The executive summary should include:
1. Title slide
2. Key messages (1-2 slides)
3. Core recommendations (1-2 slides)
4. Next steps (1 slide)

Focus only on the most important points for senior leadership."""

        return self.invoke(summary_request)
