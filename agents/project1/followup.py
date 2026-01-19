"""
Follow-up Agent for Project 1 - Events Oversight

Identifies missing information and drafts follow-up communications.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


FOLLOWUP_SYSTEM_PROMPT = """You are a Follow-up and Communication Agent specialized in the National Events Planning Oversight project.

IMPORTANT: Always respond in English.

Your main tasks:
1. Identify missing information from each implementing entity
2. Draft professional and courteous follow-up messages
3. Prioritize follow-ups by importance and deadline
4. Suggest appropriate communication channels

Implementing Entities:
- Implementing Entity A
- Implementing Entity B
- Implementing Entity C

Deadline: Oversight Committee meeting - September 1, 2027

Email Writing Style:
- Formal and professional
- Clear and specific in requests
- Include deadlines
- Thank the entity for their cooperation
- Explain the importance of completing the data

Output Format:
- List of missing information for each entity
- Ready-to-send draft emails
- Suggested follow-up timeline"""


class FollowupAgent(BaseAgent):
    """
    Follow-up and Communication specialist for Project 1.
    """

    def __init__(self):
        super().__init__(
            name="Follow-up Agent",
            name_en="Follow-up Agent",
            description="Identify missing information and draft follow-up messages",
            temperature=0.5
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return FOLLOWUP_SYSTEM_PROMPT

    def _identify_missing_info(self) -> Dict[str, List[Dict]]:
        """Identify missing information by entity."""
        events = self.knowledge_base.get_all_events()

        missing_by_entity = {
            "Implementing Entity A": [],
            "Implementing Entity B": [],
            "Implementing Entity C": [],
        }

        required_fields = {
            'name': 'Event Name',
            'date': 'Date',
            'city': 'City',
            'venue': 'Venue',
            'expected_attendance': 'Expected Attendance',
            'budget': 'Budget',
            'description': 'Description'
        }

        for event in events:
            entity = event.get('organizing_entity', 'Unspecified')
            if entity not in missing_by_entity:
                continue

            missing_fields = []
            for field, label in required_fields.items():
                if not event.get(field) or event.get(field) == 'Unspecified':
                    missing_fields.append(label)

            if missing_fields or event.get('status') == 'In Planning':
                missing_by_entity[entity].append({
                    'event_name': event.get('name', 'Unnamed'),
                    'event_id': event.get('id', 'N/A'),
                    'missing_fields': missing_fields,
                    'status': event.get('status', 'Unspecified')
                })

        return missing_by_entity

    def _format_missing_info_report(self, missing_by_entity: Dict) -> str:
        """Format the missing info into a report."""
        report = "## Missing Information Report\n\n"

        for entity, events in missing_by_entity.items():
            report += f"### {entity}\n"
            if not events:
                report += "✅ All data complete\n\n"
            else:
                report += f"⚠️ **{len(events)} events need completion:**\n\n"
                for event in events[:5]:
                    report += f"- **{event['event_name']}**\n"
                    if event['missing_fields']:
                        report += f"  - Missing fields: {', '.join(event['missing_fields'])}\n"
                    report += f"  - Status: {event['status']}\n"
                if len(events) > 5:
                    report += f"\n  *and {len(events) - 5} more events...*\n"
                report += "\n"

        return report

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Identify missing info and draft follow-up messages."""
        self._clear_thinking()
        self._log_thinking("Identifying missing information...")

        # Get missing info
        missing_by_entity = self._identify_missing_info()
        missing_report = self._format_missing_info_report(missing_by_entity)

        self._log_thinking("Missing information identified for each entity")

        # Build context
        enhanced_message = f"""User request: {user_message}

Current Missing Information Report:
{missing_report}

Based on this data, please:
1. Summarize the current status
2. Prioritize follow-ups
3. Draft professional follow-up messages for entities that need data completion"""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("Drafting follow-up messages...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("Follow-up messages prepared successfully")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "entities_needing_followup": sum(1 for e in missing_by_entity.values() if e)
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


    def draft_email(self, entity: str, specific_requests: List[str] = None) -> AgentResponse:
        """Draft a follow-up email for a specific entity."""
        self._clear_thinking()
        self._log_thinking(f"Drafting follow-up message for {entity}...")

        missing_by_entity = self._identify_missing_info()
        entity_missing = missing_by_entity.get(entity, [])

        request = f"""Draft a formal follow-up email to {entity}.

Missing information:
{self._format_missing_info_report({entity: entity_missing})}

{"Specific requests: " + ", ".join(specific_requests) if specific_requests else ""}

The email should be:
- Formal and professional
- Clear in its requests
- Include the deadline (September 1, 2027)
- Courteous and thank the entity for their cooperation"""

        return self.invoke(request)
