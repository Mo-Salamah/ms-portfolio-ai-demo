"""
Demo prompts for systematic testing of the multi-agent system.
Each project has a sequence of prompts that simulate the demo flow.
"""

# =============================================================================
# PROJECT 1: National Events Planning Oversight
# =============================================================================
# Demo scenario: We received an Excel containing event information from
# Implementing Entity A. We want to analyze it and prepare for the committee
# meeting on September 1st (today is Jan 17th).

PROJECT1_PROMPTS = {
    "name": "National Events Planning Oversight",
    "scenario": """
    We have received event data from Implementing Entity A. Today is January 17th,
    and we need to ensure all information is complete before the oversight committee
    meeting on September 1st. The user wants to analyze the data, identify gaps,
    and prepare follow-up communications.
    """,
    "steps": [
        {
            "step_id": "P1_STEP1",
            "step_name": "Initial Data Analysis Request",
            "description": "User requests comprehensive analysis of received event data",
            "prompt": """I need a comprehensive analysis of the event data received from Implementing Entity A. Please provide:
1. Total events and distribution by category and tier
2. Events with missing or incomplete information
3. Timeline analysis - are there any scheduling conflicts or gaps?
4. Summary of events by responsible entity

Note: The committee meeting is on September 1st, and we need all data complete by then.""",
            "expected_agents": ["Coordination (Agent)", "Data Analysis (Agent)", "Quality Assurance (Agent)"],
            "expected_output_contains": ["total events", "distribution", "missing", "incomplete"]
        },
        {
            "step_id": "P1_STEP2",
            "step_name": "Follow-up Email Generation",
            "description": "User requests follow-up emails for entities with incomplete data",
            "prompt": """Based on the previous analysis, prepare formal follow-up emails for each implementing entity that has events with missing information.

The emails should:
- Be professional and courteous
- Clearly specify which events have missing information
- List exactly what information is needed
- Reference the September 1st committee deadline
- Request response within 2 weeks""",
            "expected_agents": ["Coordination (Agent)", "Follow-up & Communication (Agent)"],
            "expected_output_contains": ["Dear", "missing information", "September", "deadline"]
        },
        {
            "step_id": "P1_STEP3",
            "step_name": "Committee Report Preparation",
            "description": "User requests executive summary for oversight committee",
            "prompt": """Prepare an executive summary for the oversight committee meeting that includes:

1. Data Collection Status
   - Overall completion percentage
   - Status by implementing entity

2. Key Findings
   - Total events planned
   - Distribution highlights

3. Risks and Challenges
   - Data gaps that may impact planning
   - Timeline concerns

4. Recommended Next Steps
   - Immediate actions required
   - Escalation items if any

Format this as a professional briefing document suitable for senior leadership.""",
            "expected_agents": ["Coordination (Agent)", "Reporting (Agent)", "Quality Assurance (Agent)"],
            "expected_output_contains": ["Executive Summary", "Status", "Risks", "Recommendations"]
        }
    ]
}


# =============================================================================
# PROJECT 2: Major Celebrations Strategic Planning
# =============================================================================
# Demo scenario: Strategic planning for a major national celebration.
# The demo recreates the benchmarking exercise with St. Petersburg.
#
# DEMO FLOW:
# 1. User submits initial benchmarking request
# 2. Orchestrator refines the request and creates research brief
# 3. Benchmarking Agent acknowledges (at this point, presenter explains
#    "this would take 5-10 minutes, I've pre-run it")
# 4. NEW CHAT: User pastes research results
# 5. Content Agent converts to presentation-ready slides
# 6. Optional: Critique Agent reviews

PROJECT2_PROMPTS = {
    "name": "Major Celebrations Strategic Planning",
    "scenario": """
    We are conducting strategic planning for a major national celebration in a
    historic city. The objective is to benchmark against international experiences
    and produce consulting-quality analysis and presentations.
    """,
    "steps": [
        {
            "step_id": "P2_STEP1",
            "step_name": "Initial Benchmarking Request",
            "description": "User requests benchmarking study for major celebration",
            "prompt": """I need to prepare a benchmarking study for a major national celebration in a historic city. The study should analyze comparable international experiences focusing on:

- Strategic positioning (local, national, international dimensions)
- Programming and activation model
- Governance and delivery structure
- Geographic reach and intensity of activations
- Lessons learned

Start with the St. Petersburg 300th Anniversary (2003) as the primary case study. This was a significant city anniversary that combined heritage celebration with urban regeneration and international diplomatic positioning.""",
            "expected_agents": ["Strategic Planning (Agent)"],
            "expected_output_contains": ["research brief", "Benchmarking", "dimensions", "St. Petersburg"]
        },
        {
            "step_id": "P2_STEP2",
            "step_name": "Benchmarking Agent Acknowledgment",
            "description": "Benchmarking Agent receives brief and acknowledges",
            "prompt": "[SYSTEM: This is the handoff to Benchmarking Agent after orchestrator creates research brief]",
            "expected_agents": ["Benchmarking (Agent)"],
            "expected_output_contains": ["received", "research", "St. Petersburg", "analysis"],
            "note": "At this point in the live demo, presenter explains: 'The agent is now conducting deep research. I've pre-run this to save time. Let me show you the results...'"
        },
        {
            "step_id": "P2_STEP3",
            "step_name": "Content Conversion Request (New Chat with Results)",
            "description": "User provides research results and requests slide conversion",
            "prompt": """Here are the research results from the St. Petersburg 300th Anniversary benchmarking analysis:

---
ST. PETERSBURG 300TH ANNIVERSARY: BENCHMARK ANALYSIS

OVERVIEW & CONTEXT
- Duration: 3-year intensive preparation (2000-2003); 10-day peak jubilee (May 24 - June 3, 2003)
- Investment: Approximately $1.9 billion (60 billion rubles), exceeding the city's entire annual budget
- Attendance: 45+ heads of state; 2 million+ visitors during peak period
- Flagship Project: Konstantinovsky Palace - $300 million restoration from ruins in 18 months

STRATEGIC POSITIONING
- Local: Urban regeneration - restoration of 1,000+ facades, new transport infrastructure
- National: Elevation to "Presidential Capital" - framing St. Petersburg as birthplace of modern Russian statehood
- International: Revival of "Window to Europe" narrative - positioning Russia as sophisticated, stable global partner
- Connection to National Priorities: Consolidation of federal authority; projection of soft power during political transition

GEOGRAPHIC REACH & ACTIVATION INTENSITY
| Location | Intensity | Description |
|----------|-----------|-------------|
| St. Petersburg | Full (10/10) | All physical programming: summits, galas, exhibitions, spectacles. 200+ events in 10 days. $1.9B investment. |
| Moscow | Moderate (4/10) | Official delegation hub, media headquarters. No parallel public programming. |
| Major Regional Cities | Light (2/10) | Synchronized museum exhibitions, school curriculum integration, symbolic contributions (300 Siberian cedars). |
| Broader Russia | Broadcast Only (1/10) | Participation via state television only. No physical activations. |

Key Finding: "Nationalization" of the celebration was achieved through narrative control (state TV), not distributed programming. This minimized coordination complexity but concentrated all benefits in one city.

GOVERNANCE & DELIVERY MODEL
- Top-Down Federalism: Central Organizing Committee with Presidential mandates bypassed local bottlenecks
- Public-Private Partnership: Konstantinovsky Palace 99.9% funded by private "patriotic" donors
- Media Integration: State television used to "nationalize" a local celebration into shared national experience
- Key Stakeholders: Presidential Administration (strategic oversight), City Administration (operations), Cultural Institutions (programming)

LESSONS LEARNED

What to ADOPT:
- Heritage as diplomatic stage: Use historic site as theater for global summitry
- Private capital mobilization: Engage private donors for flagship heritage projects
- Institutional legacy design: Plan for organizing committee to transition into permanent event authority

What to ADAPT:
- Geographic participation model: Consider physical activations in secondary cities, not just broadcast
- Smart security: Replace hard lockdowns with digital crowd management
- Digital layer: 2003 was analog-first; modern celebrations need metaverse/digital twin strategy

What to AVOID:
- "Potemkin" restoration: Avoid cosmetic facade work masking infrastructure deficits
- Elite-only programming: 75% resident dissatisfaction stemmed from VIP-focused benefits
- Governance opacity: Establish single-source budget visibility from Day 1
---

Please convert this content into presentation-ready slides following our established guidelines.

Required: 3-4 slides covering:
1. Overview and strategic positioning
2. Programming model and geographic reach/activation intensity
3. Lessons learned for our national celebration""",
            "expected_agents": ["Strategic Planning (Agent)", "Content Preparation (Agent)"],
            "expected_output_contains": ["Slide 1", "Slide 2", "Slide 3", "action title", "lessons"]
        },
        {
            "step_id": "P2_STEP4",
            "step_name": "Critique and Review Request",
            "description": "User requests critique of the slide content",
            "prompt": """Review the slide content you just prepared and provide structured feedback:

1. Strengths - What works well about this content?
2. Areas for Improvement - What could be enhanced?
3. Specific Recommendations - Concrete suggestions for improvement
4. Overall Assessment - Rating from 1-5 with justification

Evaluate against consulting presentation standards: action titles, single message per slide, supporting evidence, strategic relevance.""",
            "expected_agents": ["Critique & Review (Agent)"],
            "expected_output_contains": ["Strengths", "Improvement", "Recommendations", "Assessment"]
        }
    ]
}


# =============================================================================
# ALL PROMPTS COLLECTION
# =============================================================================

ALL_DEMO_PROMPTS = {
    "project1": PROJECT1_PROMPTS,
    "project2": PROJECT2_PROMPTS
}


def get_project_prompts(project_key: str) -> dict:
    """Get prompts for a specific project."""
    return ALL_DEMO_PROMPTS.get(project_key, {})


def get_all_prompts() -> dict:
    """Get all demo prompts."""
    return ALL_DEMO_PROMPTS


def list_available_projects() -> list:
    """List available project keys."""
    return list(ALL_DEMO_PROMPTS.keys())
