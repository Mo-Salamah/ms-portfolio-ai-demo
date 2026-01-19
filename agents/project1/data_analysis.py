"""
Data Analysis Agent for Project 1 - Events Oversight

Analyzes event data and produces analytical reports.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


DATA_ANALYSIS_SYSTEM_PROMPT = """You are a Data Analysis Agent specialized in the National Events Planning Oversight project.

IMPORTANT: Always respond in English.

Your main tasks:
1. Analyze event data received from implementing entities
2. Produce analytical and statistical reports
3. Identify patterns and distributions in the data
4. Provide actionable insights

Implementing Entities:
- Implementing Entity A
- Implementing Entity B
- Implementing Entity C

Analysis Style:
- Use tables for comparisons
- Provide numbers and percentages
- Categorize events by type, entity, and city
- Identify data gaps

Output Format:
- Clear headings
- Organized tables
- Executive summary at the beginning
- Recommendations at the end"""


class DataAnalysisAgent(BaseAgent):
    """
    Data Analysis specialist for Project 1.
    """

    def __init__(self):
        super().__init__(
            name="Data Analysis Agent",
            name_en="Data Analysis Agent",
            description="Analyze event data and produce analytical reports",
            temperature=0.3
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return DATA_ANALYSIS_SYSTEM_PROMPT

    def _get_events_summary(self) -> str:
        """Get a summary of events data for analysis."""
        events = self.knowledge_base.get_all_events()

        # Calculate statistics
        total = len(events)
        by_entity = {}
        by_type = {}
        by_city = {}
        by_tier = {}
        incomplete = []

        for event in events:
            # By organizing entity
            entity = event.get('organizing_entity', 'Unspecified')
            by_entity[entity] = by_entity.get(entity, 0) + 1

            # By type
            event_type = event.get('type', 'Unspecified')
            by_type[event_type] = by_type.get(event_type, 0) + 1

            # By city
            city = event.get('city', 'Unspecified')
            by_city[city] = by_city.get(city, 0) + 1

            # By tier
            tier = event.get('tier', 'Unspecified')
            by_tier[tier] = by_tier.get(tier, 0) + 1

            # Check for incomplete data
            required_fields = ['name', 'date', 'city', 'venue', 'organizing_entity']
            missing = [f for f in required_fields if not event.get(f)]
            if missing or event.get('status') == 'In Planning':
                incomplete.append({
                    'name': event.get('name', 'Unnamed'),
                    'entity': entity,
                    'missing': missing
                })

        summary = f"""## Events Data Summary

### Total: {total} events

### Distribution by Implementing Entity:
| Entity | Count | Percentage |
|--------|-------|------------|
"""
        for entity, count in sorted(by_entity.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {entity} | {count} | {count*100//total}% |\n"

        summary += f"""
### Distribution by Event Type:
| Type | Count |
|------|-------|
"""
        for event_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {event_type} | {count} |\n"

        summary += f"""
### Distribution by City:
| City | Count |
|------|-------|
"""
        for city, count in sorted(by_city.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {city} | {count} |\n"

        summary += f"""
### Distribution by Tier:
| Tier | Count |
|------|-------|
"""
        for tier, count in sorted(by_tier.items(), key=lambda x: x[1], reverse=True):
            summary += f"| {tier} | {count} |\n"

        if incomplete:
            summary += f"""
### Events Requiring Completion ({len(incomplete)}):
"""
            for item in incomplete[:10]:
                summary += f"- **{item['name']}** ({item['entity']})"
                if item['missing']:
                    summary += f" - Missing: {', '.join(item['missing'])}"
                summary += "\n"

        return summary

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Analyze event data and produce reports."""
        self._clear_thinking()
        self._log_thinking("Analyzing event data...")

        # Get events summary
        events_summary = self._get_events_summary()
        self._log_thinking("Data analysis complete - events summary prepared")

        # Build context with data
        enhanced_message = f"""User request: {user_message}

Available data for analysis:
{events_summary}

Provide a comprehensive analysis based on this data and the user's request."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("Preparing analytical report...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("Analytical report prepared successfully")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "analysis_type": "events_data"
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
                content=f"Sorry, an error occurred during analysis: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
