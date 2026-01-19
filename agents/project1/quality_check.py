"""
Quality Check Agent for Project 1 - Events Oversight

Validates data completeness and quality.
"""

from typing import Optional, Dict, List
from ..base_agent import BaseAgent, AgentResponse
from utils.knowledge_base import KnowledgeBase


QUALITY_CHECK_SYSTEM_PROMPT = """You are a Quality Check Agent specialized in the National Events Planning Oversight project.

IMPORTANT: Always respond in English.

Your main tasks:
1. Verify data completeness for each event
2. Verify data accuracy and logic
3. Identify inconsistencies and errors
4. Classify data quality for each implementing entity
5. Provide recommendations for data quality improvement

Quality Criteria:
1. Completeness: All required fields are filled
2. Accuracy: Data is logical and consistent
3. Timeliness: Dates are correct and in the future
4. Formatting: Data is in the correct format

Required Fields:
- Event Name
- Date
- City
- Venue
- Implementing Entity
- Expected Attendance
- Budget (preferred)
- Description (preferred)

Quality Classification:
- 🟢 Excellent: 90%+ completeness
- 🟡 Good: 70-89% completeness
- 🟠 Average: 50-69% completeness
- 🔴 Poor: Less than 50% completeness

Output Style:
- Clear and organized report
- Use colors and symbols for classification
- Details of issues discovered
- Specific recommendations for improvement"""


class QualityCheckAgent(BaseAgent):
    """
    Quality Check specialist for Project 1.
    """

    def __init__(self):
        super().__init__(
            name="Quality Check Agent",
            name_en="Quality Check Agent",
            description="Verify data completeness and quality",
            temperature=0.2
        )
        self.knowledge_base = KnowledgeBase()

    def get_system_prompt(self) -> str:
        return QUALITY_CHECK_SYSTEM_PROMPT

    def _check_data_quality(self) -> Dict:
        """Perform comprehensive data quality check."""
        events = self.knowledge_base.get_all_events()

        required_fields = ['name', 'date', 'city', 'venue', 'organizing_entity', 'expected_attendance']
        optional_fields = ['budget', 'description', 'category']

        quality_report = {
            'total_events': len(events),
            'by_entity': {},
            'issues': [],
            'overall_score': 0
        }

        entity_scores = {}

        for event in events:
            entity = event.get('organizing_entity', 'Unspecified')

            if entity not in entity_scores:
                entity_scores[entity] = {
                    'total': 0,
                    'complete': 0,
                    'issues': []
                }

            entity_scores[entity]['total'] += 1

            # Check required fields
            missing_required = []
            for field in required_fields:
                if not event.get(field) or event.get(field) == 'Unspecified':
                    missing_required.append(field)

            # Check optional fields
            missing_optional = []
            for field in optional_fields:
                if not event.get(field):
                    missing_optional.append(field)

            # Calculate completeness
            total_fields = len(required_fields) + len(optional_fields)
            filled_fields = total_fields - len(missing_required) - len(missing_optional)
            completeness = filled_fields / total_fields

            if completeness >= 0.9:
                entity_scores[entity]['complete'] += 1

            # Record issues
            if missing_required:
                issue = {
                    'event': event.get('name', 'Unnamed'),
                    'entity': entity,
                    'type': 'Missing required fields',
                    'details': missing_required,
                    'severity': 'High'
                }
                quality_report['issues'].append(issue)
                entity_scores[entity]['issues'].append(issue)

            # Check for logical issues
            if event.get('expected_attendance'):
                try:
                    attendance = int(str(event['expected_attendance']).replace(',', ''))
                    if attendance > 100000:
                        issue = {
                            'event': event.get('name'),
                            'entity': entity,
                            'type': 'Unrealistic value',
                            'details': f'Expected attendance too high: {attendance}',
                            'severity': 'Medium'
                        }
                        quality_report['issues'].append(issue)
                except:
                    pass

        # Calculate entity scores
        for entity, data in entity_scores.items():
            if data['total'] > 0:
                score = data['complete'] * 100 // data['total']
                if score >= 90:
                    grade = '🟢 Excellent'
                elif score >= 70:
                    grade = '🟡 Good'
                elif score >= 50:
                    grade = '🟠 Average'
                else:
                    grade = '🔴 Poor'

                quality_report['by_entity'][entity] = {
                    'total': data['total'],
                    'complete': data['complete'],
                    'score': score,
                    'grade': grade,
                    'issues_count': len(data['issues'])
                }

        # Overall score
        if entity_scores:
            total_complete = sum(d['complete'] for d in entity_scores.values())
            total_events = sum(d['total'] for d in entity_scores.values())
            quality_report['overall_score'] = total_complete * 100 // total_events if total_events > 0 else 0

        return quality_report

    def _format_quality_report(self, report: Dict) -> str:
        """Format quality report for display."""
        output = f"""## Quality Check Report

### Overall Score: {report['overall_score']}%

### Implementing Entity Assessment:
| Entity | Events | Complete | Percentage | Grade | Issues |
|--------|--------|----------|------------|-------|--------|
"""
        for entity, data in report['by_entity'].items():
            output += f"| {entity} | {data['total']} | {data['complete']} | {data['score']}% | {data['grade']} | {data['issues_count']} |\n"

        if report['issues']:
            output += f"\n### Issues Discovered ({len(report['issues'])}):\n\n"
            for i, issue in enumerate(report['issues'][:10], 1):
                output += f"**{i}. {issue['event']}** ({issue['entity']})\n"
                output += f"   - Type: {issue['type']}\n"
                output += f"   - Details: {issue['details']}\n"
                output += f"   - Severity: {issue['severity']}\n\n"

            if len(report['issues']) > 10:
                output += f"*and {len(report['issues']) - 10} more issues...*\n"

        return output

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Perform quality check and provide recommendations."""
        self._clear_thinking()
        self._log_thinking("Checking data quality...")

        # Perform quality check
        quality_report = self._check_data_quality()
        formatted_report = self._format_quality_report(quality_report)

        self._log_thinking(f"Checked {quality_report['total_events']} events")
        self._log_thinking(f"Overall score: {quality_report['overall_score']}%")

        # Build enhanced message
        enhanced_message = f"""User request: {user_message}

Quality check results:
{formatted_report}

Provide a comprehensive analysis and recommendations for improving data quality."""

        messages = self._build_messages(enhanced_message, context, conversation_history)

        try:
            self._log_thinking("Preparing recommendations...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.get_system_prompt(),
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("Quality report prepared successfully")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "quality_score": quality_report['overall_score'],
                "issues_found": len(quality_report['issues'])
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
                content=f"Sorry, an error occurred during quality check: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )
