"""
Enhanced Settings Panel Component for MS Portfolio AI Agent Demo

Four sections:
1. Project Context (locked, read-only)
2. Agent Memory (editable)
3. Presentation Guidelines (reference)
4. Strategic Control (gold highlight)
"""

import streamlit as st
from datetime import datetime
from config import THEME, PROJECT_1_CONFIG, PROJECT_2_CONFIG


# English content for settings panel
PRESENTATION_GUIDELINES_EN = """Action Title Requirements:
- Every slide must have an action title (conclusion/recommendation)
- Title should convey the key takeaway, not just describe content
- Example: "St. Petersburg leveraged heritage as diplomatic stage" not "Overview of St. Petersburg"

Single Message Per Slide:
- Each slide conveys ONE clear message
- Supporting points reinforce the main message
- Avoid information overload

Content Structure:
- Logical flow from context to analysis to recommendations
- Clear hierarchy of information
- Evidence-based assertions

Visual Formatting:
- Consistent styling throughout
- Appropriate use of charts and graphics
- Clean, professional layout"""

STRATEGIC_CONTROL_EN = """Portfolio Control Scope:

Portfolio Permissions:
- Control over all agent outputs
- Define quality and style standards
- Exclusive access to internal knowledge base
- Manage and update agent memory
- Customize agents per project needs

Outputs Under Full Control:
- Reports and analyses
- Presentations
- Official correspondence
- Performance indicators

Note: All outputs reflect portfolio standards and preferences"""

# Project context in English
PROJECT_CONTEXT_EN = {
    "project1": """Project: National Events Planning Oversight

Objective: Ensure comprehensive event data collection and coordination across implementing entities for the 2027 national events program.

Scope:
- Event data analysis and validation
- Gap identification and follow-up
- Committee reporting and executive summaries
- Quality assurance of submitted information

Key Stakeholders:
- Implementing Entity A
- Implementing Entity B
- Implementing Entity C
- Oversight Committee

Timeline: Committee meeting on September 1st requires all data complete""",

    "project2": """Project: Major Celebrations Strategic Planning

Objective: Develop strategic framework for a major national celebration through international benchmarking and best practice analysis.

Scope:
- International benchmarking studies
- KPI framework development
- Strategic positioning options
- Presentation preparation for leadership

Key Deliverables:
- Benchmarking report
- KPI recommendations
- Strategic options presentation
- Executive briefing materials

Duration: 20-week engagement"""
}

# Default memory entries in English
DEFAULT_MEMORY_EN = {
    "project1": [
        {"date": "January 15, 2027", "entry": "Received event data from Implementing Entity A - initial review pending"},
        {"date": "January 10, 2027", "entry": "Project kickoff meeting held - confirmed September 1st committee deadline"},
    ],
    "project2": [
        {"date": "January 15, 2027", "entry": "St. Petersburg 300th Anniversary selected as primary benchmark case"},
        {"date": "January 12, 2027", "entry": "Engagement commenced - 20 week timeline confirmed"},
    ]
}


def get_current_project_config():
    """Get the configuration for the currently selected project."""
    project_id = st.session_state.get('selected_project', 'project1')
    if project_id == 'project1':
        return PROJECT_1_CONFIG
    return PROJECT_2_CONFIG


def render_project_context_section():
    """Render the locked project context section."""
    project_id = st.session_state.get('selected_project', 'project1')
    context = PROJECT_CONTEXT_EN.get(project_id, PROJECT_CONTEXT_EN["project1"])

    with st.expander("Project Context (Locked)", expanded=False):
        st.markdown(f"""
        <div style="
            background-color: #f3f4f6;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid #9ca3af;
            opacity: 0.9;
        ">
            <div style="
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                color: #6b7280;
            ">
                <small>Managed by administration only - Read only</small>
            </div>
            <div style="
                white-space: pre-wrap;
                font-size: 0.9em;
                line-height: 1.8;
                color: #374151;
            ">{context}</div>
        </div>
        """, unsafe_allow_html=True)


def render_agent_memory_section():
    """Render the editable agent memory section."""
    project_id = st.session_state.get('selected_project', 'project1')
    memory_key = f"memory_{project_id}"

    # Initialize memory in session state if not exists
    if memory_key not in st.session_state:
        st.session_state[memory_key] = DEFAULT_MEMORY_EN.get(project_id, []).copy()

    with st.expander("Agent Memory", expanded=True):
        st.markdown("""
        <div style="margin-bottom: 12px; color: #666; font-size: 0.85em;">
            Record of important events and notes for this project
        </div>
        """, unsafe_allow_html=True)

        # Display existing memory entries
        for i, entry in enumerate(st.session_state[memory_key]):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div style="
                    background-color: white;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    border-left: 3px solid {THEME['accent']};
                ">
                    <div style="color: {THEME['accent']}; font-size: 0.8em; margin-bottom: 4px;">
                        {entry['date']}
                    </div>
                    <div style="color: #333;">
                        {entry['entry']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("X", key=f"delete_memory_{i}", help="Delete"):
                    st.session_state[memory_key].pop(i)
                    st.rerun()

        # Add new entry form
        st.markdown("---")
        st.markdown("**Add New Entry:**")

        new_entry = st.text_input(
            "Entry",
            placeholder="Enter a new note or event...",
            key="new_memory_entry",
            label_visibility="collapsed"
        )

        if st.button("+ Add Entry", key="add_memory_btn"):
            if new_entry:
                today = datetime.now().strftime("%B %d, %Y")
                st.session_state[memory_key].insert(0, {
                    "date": today,
                    "entry": new_entry
                })
                st.rerun()


def render_presentation_guidelines_section():
    """Render the presentation guidelines reference section."""
    with st.expander("Presentation Guidelines", expanded=False):
        st.markdown(f"""
        <div style="
            background-color: #f0f9ff;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid #0ea5e9;
        ">
            <div style="
                white-space: pre-wrap;
                font-size: 0.9em;
                line-height: 1.8;
                color: #0c4a6e;
            ">{PRESENTATION_GUIDELINES_EN}</div>
        </div>
        """, unsafe_allow_html=True)


def render_strategic_control_section():
    """Render the strategic control section with gold highlight."""
    with st.expander("Portfolio Control", expanded=False):
        st.markdown(f"""
        <div class="strategic-control" style="
            background-color: {THEME['control_bg']};
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid {THEME['accent']};
            border: 1px solid {THEME['accent']};
        ">
            <div style="
                white-space: pre-wrap;
                font-size: 0.9em;
                line-height: 1.8;
                color: #92400e;
            ">{STRATEGIC_CONTROL_EN}</div>
        </div>
        """, unsafe_allow_html=True)


def render_settings_panel():
    """Render the complete settings panel with all 4 sections."""

    # Panel header
    st.markdown(f"""
    <div style="
        background-color: white;
        color: {THEME['primary']};
        padding: 16px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
        border: 1px solid #e5e7eb;
        border-bottom: 2px solid {THEME['accent']};
    ">
        <h4 style="margin: 0; color: {THEME['primary']};">
            Settings Panel
        </h4>
    </div>
    """, unsafe_allow_html=True)

    # Render all sections
    render_project_context_section()
    render_agent_memory_section()
    render_presentation_guidelines_section()
    render_strategic_control_section()


if __name__ == "__main__":
    # Test the component
    st.set_page_config(layout="wide")
    render_settings_panel()
