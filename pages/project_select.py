"""
Project Selection Page for MS Portfolio AI Agent Demo
"""

import streamlit as st
from config import THEME


# Project card configurations with full English content
PROJECT_CARDS = [
    {
        "id": "project1",
        "title": "National Events Planning Oversight",
        "icon": "",
        "description": """A comprehensive oversight system for coordinating national event planning across multiple implementing entities. This multi-agent project enables systematic collection and analysis of event data, identification of information gaps, automated follow-up communications, and preparation of executive reports for oversight committee meetings. The system ensures all stakeholders maintain visibility into event planning progress while reducing manual coordination overhead.""",
        "agents": [
            {"name": "Coordination (Agent)", "desc": "Routes requests and manages workflow across all sub-agents"},
            {"name": "Data Analysis (Agent)", "desc": "Analyzes event databases and produces statistical summaries"},
            {"name": "Follow-up & Communication (Agent)", "desc": "Drafts professional follow-up emails for missing information"},
            {"name": "Reporting (Agent)", "desc": "Compiles findings into committee-ready executive reports"},
            {"name": "Quality Assurance (Agent)", "desc": "Validates data completeness and flags inconsistencies"},
        ],
        "status": "Demo",
        "status_class": "status-demo",
        "poc": "Project Lead"
    },
    {
        "id": "project2",
        "title": "Major Celebrations Strategic Planning",
        "icon": "",
        "description": """A strategic planning system for large-scale national celebrations and commemorative events. This multi-agent project conducts international benchmarking research, develops KPI frameworks, analyzes positioning options, and produces consulting-quality presentations. The system draws on a knowledge base of global celebration case studies to inform strategic recommendations, ensuring proposed approaches are grounded in proven international practices while adapted for local context.""",
        "agents": [
            {"name": "Strategic Planning (Agent)", "desc": "Orchestrates research and synthesizes strategic recommendations"},
            {"name": "Benchmarking (Agent)", "desc": "Conducts deep-dive analysis of international celebration case studies"},
            {"name": "KPI Development (Agent)", "desc": "Recommends performance indicators with measurement frameworks"},
            {"name": "Critique & Review (Agent)", "desc": "Evaluates outputs against consulting quality standards"},
            {"name": "Content Preparation (Agent)", "desc": "Formats analysis into presentation-ready slide content"},
        ],
        "status": "Demo",
        "status_class": "status-demo",
        "poc": "Project Lead"
    },
    {
        "id": "project3",
        "title": "VP Meeting Preparation Assistant",
        "icon": "",
        "description": """An intelligent preparation system for one-on-one meetings with senior leadership. This multi-agent project reviews documents across multiple active projects, extracts key updates and decision points, identifies potential questions or concerns, and prepares structured talking points. The system helps ensure productive executive conversations by synthesizing relevant information from across the portfolio into concise, actionable briefing materials tailored to the specific meeting context.""",
        "agents": [
            {"name": "Meeting Prep (Agent)", "desc": "Orchestrates preparation workflow and compiles final briefing"},
            {"name": "Document Scanner (Agent)", "desc": "Reviews project documents and extracts key updates"},
            {"name": "Issue Identifier (Agent)", "desc": "Flags potential concerns and anticipated questions"},
            {"name": "Talking Points (Agent)", "desc": "Structures information into clear, concise bullet points"},
            {"name": "Context Builder (Agent)", "desc": "Provides background on topics likely to arise"},
        ],
        "status": "Initial launch in June 2026",
        "status_class": "status-upcoming",
        "poc": "Project Lead"
    },
    {
        "id": "project4",
        "title": "Presentation Review & Feedback System",
        "icon": "",
        "description": """A quality assurance system for reviewing slides and presentations before executive delivery. This multi-agent project evaluates presentations against established standards including action title effectiveness, single-message clarity, visual design principles, and strategic narrative coherence. The system provides structured feedback with specific improvement recommendations, helping teams elevate presentation quality while maintaining consistency with organizational style guidelines.""",
        "agents": [
            {"name": "Review Coordinator (Agent)", "desc": "Manages review workflow and compiles consolidated feedback"},
            {"name": "Structure Analyst (Agent)", "desc": "Evaluates slide structure and action title effectiveness"},
            {"name": "Content Reviewer (Agent)", "desc": "Assesses clarity, accuracy, and strategic alignment"},
            {"name": "Visual Design (Agent)", "desc": "Reviews formatting, layout, and visual consistency"},
            {"name": "Executive Lens (Agent)", "desc": "Evaluates from senior leadership perspective"},
        ],
        "status": "Initial launch in June 2026",
        "status_class": "status-upcoming",
        "poc": "Project Lead"
    }
]


def render_project_card(card: dict, is_enabled: bool = True):
    """Render a single project card using native Streamlit components."""

    # Use a container with custom styling
    with st.container():
        # Header row with title and status
        col_title, col_status = st.columns([4, 1])
        with col_title:
            st.markdown(f"### {card['title']}")
        with col_status:
            status_color = "#10b981" if card["status"] == "Demo" else "#6b7280"
            st.markdown(f'<span style="background-color: {status_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; font-weight: 500;">{card["status"]}</span>', unsafe_allow_html=True)

        st.markdown("---")

        # Description
        st.markdown(f"**Description:**")
        st.markdown(f"{card['description']}")

        st.markdown("---")

        # Agents list
        st.markdown("**Available Agents:**")
        for agent in card["agents"]:
            st.markdown(f"- **{agent['name']}** - {agent['desc']}")

        st.markdown("---")

        # Point of contact
        st.markdown(f"**Point of Contact:** {card['poc']}")

        # Spacer
        st.markdown("")

        # Only show button for enabled projects
        if is_enabled and card["status"] == "Demo":
            if st.button(
                f"Open Project",
                key=f"btn_{card['id']}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state.selected_project = card['id']
                st.session_state.current_page = "workspace"
                st.rerun()
        elif not is_enabled or card["status"] != "Demo":
            st.button(
                "Coming Soon",
                key=f"btn_{card['id']}",
                use_container_width=True,
                disabled=True
            )


def render_project_select_page():
    """Render the project selection page with 4 project cards."""

    # Sign out button at top left
    col_signout, col_spacer = st.columns([1, 5])
    with col_signout:
        if st.button("Sign Out", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.current_page = "login"
            st.rerun()

    # Demo mode badge
    st.markdown("""
    <div style="text-align: center; margin-bottom: 10px;">
        <span class="demo-badge">DEMO MODE</span>
    </div>
    """, unsafe_allow_html=True)

    # Header section
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 30px 0;">
        <h1 style="color: {THEME['primary']}; margin-bottom: 16px;">Strategic AI Platform</h1>
        <p style="color: #666; max-width: 800px; margin: 0 auto; line-height: 1.7; font-size: 1.05em;">
            A multi-agent system designed to enhance team productivity through intelligent task delegation.
            Each team member gains access to a suite of specialized AI agents that can conduct research,
            analyze data, prepare presentations, and provide strategic recommendations - all with
            human-in-the-loop oversight to ensure quality and alignment with organizational standards.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Section header
    st.markdown(f"""
    <h2 style="color: {THEME['primary']}; margin-bottom: 24px;">Projects & Agents</h2>
    """, unsafe_allow_html=True)

    # First row of cards
    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_project_card(PROJECT_CARDS[0], is_enabled=True)

    with col2:
        render_project_card(PROJECT_CARDS[1], is_enabled=True)

    # Second row of cards
    col3, col4 = st.columns(2, gap="large")

    with col3:
        render_project_card(PROJECT_CARDS[2], is_enabled=False)

    with col4:
        render_project_card(PROJECT_CARDS[3], is_enabled=False)


if __name__ == "__main__":
    render_project_select_page()
