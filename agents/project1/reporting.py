"""
Reporting Agent for Project 1 - Events Oversight

Compiles results and prepares committee reports.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


REPORTING_SYSTEM_PROMPT = """You are a Reporting Agent specialized in the National Events Planning Oversight project.

IMPORTANT: Always respond in English.

Your main tasks:
1. Compile results and analyses from various sources
2. Prepare periodic reports for the oversight committee
3. Prepare executive summaries for leadership
4. Document progress, challenges, and risks

Target Audience:
- Senior Oversight Committee
- Government Leadership
- Coordination and Follow-up Team

Report Structure:
1. Executive Summary (key points)
2. Current Status (statistics and completion rates)
3. Challenges and Risks
4. Actions Taken
5. Next Steps
6. Recommendations

Writing Style:
- Concise and direct
- Use numbers and percentages
- Highlight critical points
- Actionable recommendations"""


class ReportingAgent(BaseAgent):
    """
    Reporting specialist for Project 1.
    """

    def __init__(self):
        super().__init__(
            name="Reporting Agent",
            name_en="Reporting Agent",
            description="Compile results and prepare committee reports",
            temperature=0.4
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return REPORTING_SYSTEM_PROMPT

    def _get_status_summary(self) -> Dict:
        """Get overall status summary."""
        events = self.knowledge_base.get_all_events()

        total = len(events)
        by_status = {}
        by_entity = {}
        complete = 0

        required_fields = ['name', 'date', 'city', 'venue', 'expected_attendance']

        for event in events:
            # Status
            status = event.get('status', 'Unspecified')
            by_status[status] = by_status.get(status, 0) + 1

            # Entity
            entity = event.get('organizing_entity', 'Unspecified')
            if entity not in by_entity:
                by_entity[entity] = {'total': 0, 'complete': 0}
            by_entity[entity]['total'] += 1

            # Check completeness
            is_complete = all(event.get(f) for f in required_fields)
            if is_complete:
                complete += 1
                by_entity[entity]['complete'] += 1

        return {
            'total_events': total,
            'complete_events': complete,
            'completion_rate': complete * 100 // total if total > 0 else 0,
            'by_status': by_status,
            'by_entity': by_entity
        }

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Prepare reports based on user request."""
        self._clear_thinking()
        self._log_thinking("Compiling data for report preparation...")

        # Get status summary
        status = self._get_status_summary()
        self._log_thinking(f"Compiled data for {status['total_events']} events")

        # Format status for context
        status_text = f"""## Current Status Summary

### General Statistics:
- Total Events: {status['total_events']}
- Events with Complete Data: {status['complete_events']}
- Completion Rate: {status['completion_rate']}%

### Distribution by Status:
"""
        for s, count in status['by_status'].items():
            status_text += f"- {s}: {count}\n"

        status_text += "\n### Distribution by Implementing Entity:\n"
        for entity, data in status['by_entity'].items():
            rate = data['complete'] * 100 // data['total'] if data['total'] > 0 else 0
            status_text += f"- {entity}: {data['total']} events ({rate}% complete)\n"

        # Build enhanced message
        enhanced_message = f"""User request: {user_message}

Available data:
{status_text}

Prepare an appropriate report for the oversight committee based on this data and the user's request."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("Drafting report...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("Report prepared successfully")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "report_type": "committee_report",
                "data_summary": status
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
                content=f"Sorry, an error occurred while preparing the report: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )

    def prepare_committee_report(self) -> AgentResponse:
        """Prepare a standard committee report."""
        return self.invoke("Prepare a current status report for the oversight committee")

    def prepare_executive_summary(self) -> AgentResponse:
        """Prepare an executive summary."""
        return self.invoke("Prepare a concise executive summary for leadership including key points and recommendations")
