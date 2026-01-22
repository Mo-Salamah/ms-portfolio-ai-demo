"""
Agent Network Visualization Component for MS Portfolio AI Agent Demo

Simple, clean agent list display that works reliably.
"""

import streamlit as st
from config import THEME, PROJECT_1_CONFIG, PROJECT_2_CONFIG


# Agent names in English for display
AGENT_NAMES_EN = {
    # Project 1 agents
    "coordinator": "Coordination Agent",
    "data_analysis": "Data Analysis Agent",
    "followup": "Follow-up Agent",
    "reporting": "Reporting Agent",
    "quality_check": "Quality Check Agent",
    # Project 2 agents
    "strategic_planning": "Strategic Planning Agent",
    "benchmarking": "Benchmarking Agent",
    "kpi": "KPI Agent",
    "critique": "Critique Agent",
    "content_prep": "Content Preparation Agent",
}


def get_current_project_config():
    """Get the configuration for the currently selected project."""
    project_id = st.session_state.get('selected_project', 'project1')
    if project_id == 'project1':
        return PROJECT_1_CONFIG
    return PROJECT_2_CONFIG


def get_agent_name_en(agent_id: str, default_name: str = "Agent") -> str:
    """Get English name for an agent."""
    return AGENT_NAMES_EN.get(agent_id, default_name)


def render_agent_network(active_agent_id: str = None):
    """Render a simple agent network display."""
    project_id = st.session_state.get('selected_project', 'project1')
    project_name = "National Events Planning Oversight" if project_id == "project1" else "Major Celebrations Strategic Planning"
    project_config = get_current_project_config()
    agents = project_config['agents']

    st.markdown(f"**Agent Network** - {project_name}")

    # Find orchestrator
    orchestrator = None
    specialists = []
    for agent in agents:
        if agent.get('is_orchestrator', False):
            orchestrator = agent
        else:
            specialists.append(agent)

    # Display orchestrator
    if orchestrator:
        orch_name = get_agent_name_en(orchestrator['id'], orchestrator.get('name_en', 'Orchestrator'))
        is_active = orchestrator['id'] == active_agent_id
        status = "🟢 Active" if is_active else "⚪ Ready"
        st.markdown(f"**Orchestrator:** {orch_name} {status}")

    st.markdown("**Specialist Agents:**")

    # Display specialists in columns
    cols = st.columns(2)
    for i, agent in enumerate(specialists):
        agent_name = get_agent_name_en(agent['id'], agent.get('name_en', 'Agent'))
        is_active = agent['id'] == active_agent_id
        status = "🟢" if is_active else "⚪"
        with cols[i % 2]:
            st.markdown(f"{status} {agent_name}")


def render_compact_agent_network(active_agent_id: str = None):
    """Render a compact version of the agent network for sidebar."""
    project_config = get_current_project_config()
    agents = project_config['agents']

    st.markdown("**Active Agents**")

    for agent in agents:
        is_active = agent['id'] == active_agent_id
        is_orchestrator = agent.get('is_orchestrator', False)
        agent_name = get_agent_name_en(agent['id'], agent.get('name_en', 'Agent'))

        prefix = "🎯" if is_orchestrator else "•"
        status = "🟢" if is_active else ""

        st.markdown(f"{prefix} {agent_name} {status}")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_agent_network(active_agent_id="benchmarking")
