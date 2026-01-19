"""
Agent Network Visualization Component for MS Portfolio AI Agent Demo

Displays an interactive network diagram showing:
- Orchestrator agent in the center
- Specialist agents around it
- Active agent highlighting
- Status indicators
"""

import streamlit as st
from config import THEME, PROJECT_1_CONFIG, PROJECT_2_CONFIG


# Agent names in English for display
AGENT_NAMES_EN = {
    # Project 1 agents
    "coordinator": "Coordination (Agent)",
    "data_analysis": "Data Analysis (Agent)",
    "followup": "Follow-up & Communication (Agent)",
    "reporting": "Reporting (Agent)",
    "quality_check": "Quality Assurance (Agent)",
    # Project 2 agents
    "strategic_planning": "Strategic Planning (Agent)",
    "benchmarking": "Benchmarking (Agent)",
    "kpi": "KPI Development (Agent)",
    "critique": "Critique & Review (Agent)",
    "content_prep": "Content Preparation (Agent)",
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


def generate_agent_network_svg(agents: list, active_agent_id: str = None) -> str:
    """
    Generate an SVG visualization of the agent network.

    Args:
        agents: List of agent configurations
        active_agent_id: ID of the currently active agent (optional)

    Returns:
        SVG string
    """
    # Find orchestrator and specialists
    orchestrator = None
    specialists = []
    for agent in agents:
        if agent.get('is_orchestrator', False):
            orchestrator = agent
        else:
            specialists.append(agent)

    # SVG dimensions
    width = 600
    height = 400
    center_x = width // 2
    center_y = height // 2

    # Colors
    primary = THEME['primary']
    accent = THEME['accent']
    active_color = "#10b981"  # Green for active
    inactive_color = "#e5e7eb"

    # Calculate positions for specialists (arranged in a circle)
    import math
    num_specialists = len(specialists)
    radius = 140
    positions = []

    for i in range(num_specialists):
        angle = (2 * math.pi * i / num_specialists) - (math.pi / 2)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions.append((x, y))

    # Start building SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="max-width: 100%; height: auto;">
        <defs>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.2"/>
            </filter>
            <linearGradient id="activeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{active_color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="centerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{primary};stop-opacity:1" />
                <stop offset="100%" style="stop-color:#2d4a6f;stop-opacity:1" />
            </linearGradient>
        </defs>

        <!-- Background -->
        <rect width="{width}" height="{height}" fill="#f8fafc" rx="12"/>

        <!-- Connection lines -->
        <g stroke="{inactive_color}" stroke-width="2" fill="none">'''

    # Draw connection lines from center to each specialist
    for i, (x, y) in enumerate(positions):
        is_active = specialists[i]['id'] == active_agent_id
        line_color = active_color if is_active else inactive_color
        stroke_width = 3 if is_active else 2
        svg += f'''
            <line x1="{center_x}" y1="{center_y}" x2="{x}" y2="{y}"
                  stroke="{line_color}" stroke-width="{stroke_width}"
                  {'stroke-dasharray="5,5"' if not is_active else ''}>
                {'<animate attributeName="stroke-dashoffset" from="10" to="0" dur="0.5s" repeatCount="indefinite"/>' if is_active else ''}
            </line>'''

    svg += '</g>'

    # Draw specialist nodes
    svg += '<g>'
    for i, (x, y) in enumerate(positions):
        agent = specialists[i]
        is_active = agent['id'] == active_agent_id
        agent_en_name = get_agent_name_en(agent['id'], agent.get('name_en', 'Agent'))

        # Node circle
        fill = f"url(#activeGradient)" if is_active else "white"
        stroke = active_color if is_active else primary
        text_color = "white" if is_active else primary

        # Truncate long names for display
        display_name = agent_en_name[:20] if len(agent_en_name) > 20 else agent_en_name

        svg += f'''
        <g transform="translate({x}, {y})">
            <circle r="45" fill="{fill}" stroke="{stroke}" stroke-width="2" filter="url(#shadow)">
                {f'<animate attributeName="r" values="45;48;45" dur="1s" repeatCount="indefinite"/>' if is_active else ''}
            </circle>
            <text y="0" text-anchor="middle" fill="{text_color}" font-size="10" font-weight="bold" font-family="Arial">
                {display_name}
            </text>
            {'<circle r="8" cx="35" cy="-35" fill="' + active_color + '"><animate attributeName="opacity" values="1;0.5;1" dur="1s" repeatCount="indefinite"/></circle>' if is_active else ''}
        </g>'''

    svg += '</g>'

    # Draw orchestrator in center
    if orchestrator:
        orch_name_en = get_agent_name_en(orchestrator['id'], orchestrator.get('name_en', 'Orchestrator'))
        svg += f'''
        <g transform="translate({center_x}, {center_y})">
            <circle r="55" fill="url(#centerGradient)" stroke="{accent}" stroke-width="3" filter="url(#shadow)"/>
            <text y="-5" text-anchor="middle" fill="white" font-size="11" font-weight="bold" font-family="Arial">
                {orch_name_en[:18]}
            </text>
            <text y="15" text-anchor="middle" fill="{accent}" font-size="9" font-family="Arial">
                Orchestrator
            </text>
        </g>'''

    svg += '</svg>'
    return svg


def render_agent_status_panel(active_agent_id: str = None):
    """Render a status panel showing agent activity."""
    project_config = get_current_project_config()
    agents = project_config['agents']

    st.markdown("""
    <div style="margin-top: 16px;">
        <h4 style="color: #374151; margin-bottom: 12px;">Agent Status</h4>
    </div>
    """, unsafe_allow_html=True)

    for agent in agents:
        is_active = agent['id'] == active_agent_id
        status_color = "#10b981" if is_active else "#9ca3af"
        status_text = "Active" if is_active else "Ready"
        bg_color = "#ecfdf5" if is_active else "#f9fafb"
        agent_en_name = get_agent_name_en(agent['id'], agent.get('name_en', 'Agent'))

        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background-color: {bg_color};
            border-radius: 6px;
            margin-bottom: 6px;
            border-left: 3px solid {status_color};
        ">
            <span style="font-size: 0.9em; color: #374151;">
                {'Orchestrator' if agent.get('is_orchestrator') else 'Agent'} - {agent_en_name}
            </span>
            <span style="
                font-size: 0.75em;
                color: {status_color};
                background-color: white;
                padding: 2px 8px;
                border-radius: 10px;
            ">
                {status_text}
            </span>
        </div>
        """, unsafe_allow_html=True)


def render_agent_network(active_agent_id: str = None):
    """
    Render the complete agent network visualization.

    Args:
        active_agent_id: ID of the currently active agent for highlighting
    """
    project_id = st.session_state.get('selected_project', 'project1')
    project_name = "National Events Planning Oversight" if project_id == "project1" else "Major Celebrations Strategic Planning"
    project_config = get_current_project_config()

    # Header
    st.markdown(f"""
    <div style="
        background-color: white;
        color: {THEME['primary']};
        padding: 12px 16px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
        border: 1px solid #e5e7eb;
        border-bottom: 2px solid {THEME['accent']};
    ">
        <h3 style="margin: 0; color: {THEME['primary']}; font-size: 1.1em;">
            Agent Network
        </h3>
        <small style="color: #666;">
            {project_name}
        </small>
    </div>
    """, unsafe_allow_html=True)

    # Network visualization
    svg = generate_agent_network_svg(project_config['agents'], active_agent_id)

    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 16px;
        border-radius: 0 0 8px 8px;
        border: 1px solid #e5e7eb;
        border-top: none;
    ">
        {svg}
    </div>
    """, unsafe_allow_html=True)

    # Status panel
    render_agent_status_panel(active_agent_id)


def render_compact_agent_network(active_agent_id: str = None):
    """Render a compact version of the agent network for sidebar."""
    project_config = get_current_project_config()
    agents = project_config['agents']

    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 16px;
        border: 1px solid #e5e7eb;
    ">
        <h4 style="color: {THEME['primary']}; margin-bottom: 12px; font-size: 0.95em;">
            Active Agents
        </h4>
    """, unsafe_allow_html=True)

    for agent in agents:
        is_active = agent['id'] == active_agent_id
        is_orchestrator = agent.get('is_orchestrator', False)
        agent_en_name = get_agent_name_en(agent['id'], agent.get('name_en', 'Agent'))

        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 6px 8px;
            background-color: {'#ecfdf5' if is_active else '#f9fafb'};
            border-radius: 6px;
            margin-bottom: 4px;
            border-left: 2px solid {'#10b981' if is_active else '#e5e7eb'};
        ">
            <span style="margin-right: 8px;">{'Orch' if is_orchestrator else 'Agent'}</span>
            <span style="color: #333; font-size: 0.85em;">
                {agent_en_name}
            </span>
            {f'<span style="margin-left: auto; font-size: 0.7em; color: #10b981;">Active</span>' if is_active else ''}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    # Test the component
    st.set_page_config(layout="wide")
    render_agent_network(active_agent_id="benchmarking")
