"""
Main Workspace Page for MS Portfolio AI Agent Demo

Combines chat interface, agent network, and settings panel.
"""

import streamlit as st
from config import THEME, PROJECT_1_CONFIG, PROJECT_2_CONFIG
from components.settings_panel import render_settings_panel
from components.agent_network import render_agent_network, render_compact_agent_network


# Project names in English
PROJECT_NAMES = {
    "project1": {
        "name": "National Events Planning Oversight",
        "description": "A comprehensive oversight system for coordinating national event planning across multiple implementing entities."
    },
    "project2": {
        "name": "Major Celebrations Strategic Planning",
        "description": "A strategic planning system for large-scale national celebrations and commemorative events."
    }
}


def get_current_project_config():
    """Get the configuration for the currently selected project."""
    project_id = st.session_state.get('selected_project', 'project1')
    if project_id == 'project1':
        return PROJECT_1_CONFIG
    return PROJECT_2_CONFIG


def get_orchestrator():
    """Get or create the orchestrator for the current project."""
    project_id = st.session_state.get('selected_project', 'project1')
    orchestrator_key = f"orchestrator_{project_id}"

    if orchestrator_key not in st.session_state:
        if project_id == 'project1':
            from agents.project1 import CoordinatorAgent
            st.session_state[orchestrator_key] = CoordinatorAgent()
        else:
            from agents.project2 import StrategicPlanningAgent
            st.session_state[orchestrator_key] = StrategicPlanningAgent()

    return st.session_state[orchestrator_key]


def render_workspace_header():
    """Render the workspace header with project info and navigation."""
    project_id = st.session_state.get('selected_project', 'project1')
    project_info = PROJECT_NAMES.get(project_id, PROJECT_NAMES["project1"])

    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        if st.button("Back", key="back_btn"):
            st.session_state.current_page = "project_select"
            st.rerun()

    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <h2 style="color: {THEME['primary']}; margin-bottom: 4px;">
                {project_info['name']}
            </h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Demo mode badge
        st.markdown("""
        <div class="demo-badge" style="text-align: center;">
            DEMO MODE
        </div>
        """, unsafe_allow_html=True)


def render_chat_message(message: dict, index: int):
    """Render a single chat message."""
    role = message["role"]

    with st.chat_message(role):
        st.markdown(message["content"])

        # Show thinking trace if available and enabled
        if (role == "assistant" and
            st.session_state.get('show_thinking', True) and
            message.get("thinking")):

            with st.expander("Agent Thinking", expanded=False):
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 12px;
                    border-radius: 8px;
                    border-left: 4px solid {THEME['accent']};
                    margin: 8px 0;
                    white-space: pre-wrap;
                    color: #333;
                    font-size: 0.9em;
                ">
                {message['thinking'].replace(chr(10), '<br/>')}
                </div>
                """, unsafe_allow_html=True)

        # Show agent name
        if role == "assistant" and message.get("agent"):
            agent_name_en = message.get("agent_en", message.get("agent", "Agent"))
            st.markdown(f"""
            <span style="
                background-color: {THEME['primary']};
                color: white;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 12px;
                display: inline-block;
                margin-top: 8px;
            ">{agent_name_en}</span>
            """, unsafe_allow_html=True)


def render_welcome_message():
    """Render the welcome message when chat is empty."""
    project_id = st.session_state.get('selected_project', 'project1')
    project_info = PROJECT_NAMES.get(project_id, PROJECT_NAMES["project1"])

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {THEME['primary']} 0%, #2d4a6f 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    ">
        <h2 style="color: {THEME['accent']}; margin-bottom: 12px;">
            Welcome to {project_info['name']}
        </h2>
        <p>{project_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick action buttons based on project - English prompts
    if project_id == 'project1':
        examples = [
            "Analyze the event data we received",
            "What information is missing?",
            "Prepare a committee report",
            "Check data quality",
        ]
    else:
        examples = [
            "I need benchmarking on St. Petersburg",
            "What KPIs do you recommend?",
            "Review the previous analysis",
            "Convert to presentation slides",
        ]

    st.markdown("#### Quick Start Examples")
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                # Use the pending message pattern for consistency
                pending_key = f"pending_message_{project_id}"
                st.session_state[pending_key] = example
                st.rerun()


def render_sidebar():
    """Render the enhanced sidebar with settings and agent info."""

    with st.sidebar:
        # Header
        st.markdown(f"""
        <div style="text-align: center; padding: 16px 0;">
            <h3 style="color: {THEME['primary']}; font-size: 1.1em;">Strategic AI Platform</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Settings section
        st.markdown("### Settings")
        st.session_state.show_thinking = st.checkbox(
            "Show Agent Thinking",
            value=st.session_state.get('show_thinking', True),
            help="Display the agent's reasoning process"
        )

        st.markdown("---")

        # Compact agent network
        render_compact_agent_network(st.session_state.get('active_agent_id'))

        st.markdown("---")

        # Settings panel
        render_settings_panel()

        st.markdown("---")

        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Chat", use_container_width=True):
                project_id = st.session_state.get('selected_project', 'project1')
                messages_key = f"messages_{project_id}"
                st.session_state[messages_key] = []
                orchestrator_key = f"orchestrator_{project_id}"
                if orchestrator_key in st.session_state:
                    del st.session_state[orchestrator_key]
                st.rerun()
        with col2:
            if st.button("Sign Out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.current_page = "login"
                st.rerun()


def process_user_message(prompt: str, messages_key: str):
    """Process a user message and generate response."""
    # Add user message to history
    st.session_state[messages_key].append({
        "role": "user",
        "content": prompt
    })

    # Get response from orchestrator
    try:
        orchestrator = get_orchestrator()
        response = orchestrator.invoke(prompt)

        # Update active agent
        st.session_state.active_agent_id = response.metadata.get('agent_id')

        # Add response to history
        st.session_state[messages_key].append({
            "role": "assistant",
            "content": response.content,
            "thinking": response.thinking,
            "agent": response.agent_name,
            "agent_en": response.agent_name_en,
            "metadata": response.metadata
        })

    except Exception as e:
        error_message = f"Sorry, an error occurred: {str(e)}"
        st.session_state[messages_key].append({
            "role": "assistant",
            "content": error_message,
            "agent": "System"
        })


def render_chat_interface():
    """Render the main chat interface."""
    project_id = st.session_state.get('selected_project', 'project1')
    messages_key = f"messages_{project_id}"

    # Initialize messages if needed
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Check if there's a pending message to process
    pending_key = f"pending_message_{project_id}"
    if pending_key in st.session_state and st.session_state[pending_key]:
        prompt = st.session_state[pending_key]
        st.session_state[pending_key] = None

        # Show processing indicator
        with st.spinner("Thinking..."):
            process_user_message(prompt, messages_key)

    # Show welcome message if no messages
    if not st.session_state[messages_key]:
        render_welcome_message()

    # Display chat history
    for i, message in enumerate(st.session_state[messages_key]):
        render_chat_message(message, i)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Store the message and rerun to process it
        st.session_state[pending_key] = prompt
        st.rerun()


def render_workspace_page():
    """Render the complete workspace page."""

    # Render sidebar
    render_sidebar()

    # Main content area
    render_workspace_header()

    # Layout: Agent network on top, chat below
    with st.expander("Agent Network", expanded=False):
        render_agent_network(st.session_state.get('active_agent_id'))

    st.markdown("---")

    # Chat interface
    st.markdown(f"""
    <h3 style="color: {THEME['primary']};">Conversation</h3>
    """, unsafe_allow_html=True)

    render_chat_interface()


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_workspace_page()
