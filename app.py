"""
MS Portfolio AI Agent Demo - Main Application Entry Point

A multi-agent AI system for strategic planning with English interface.
Supports multiple projects with distinct agent workflows.
"""

import streamlit as st
from config import THEME

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Strategic AI Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS for English LTR layout with green header
GLOBAL_CSS = f"""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap');

    /* LTR Layout */
    .stApp {{
        direction: ltr;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }}

    /* Main content area */
    .main .block-container {{
        direction: ltr;
        text-align: left;
        padding-top: 80px;  /* Space for header */
    }}

    /* Sidebar - Light theme */
    [data-testid="stSidebar"] {{
        direction: ltr;
        text-align: left;
        background-color: #f8f9fa;
        border-right: 1px solid #e5e7eb;
    }}

    [data-testid="stSidebar"] .stMarkdown {{
        color: #333;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {{
        color: {THEME['primary']} !important;
    }}

    /* Headers */
    h1, h2, h3 {{
        color: {THEME['primary']};
        font-family: 'Inter', sans-serif;
    }}

    h1 {{
        border-bottom: 3px solid {THEME['accent']};
        padding-bottom: 10px;
    }}

    /* Chat messages */
    .stChatMessage {{
        direction: ltr;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }}

    /* Input field */
    .stChatInput textarea {{
        direction: ltr;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }}

    /* Text inputs */
    .stTextInput input {{
        direction: ltr;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }}

    /* Expander for thinking */
    .streamlit-expanderHeader {{
        direction: ltr;
        text-align: left;
        font-family: 'Inter', sans-serif;
    }}

    .streamlit-expanderContent {{
        direction: ltr;
        text-align: left;
    }}

    /* Buttons */
    .stButton button {{
        font-family: 'Inter', sans-serif;
    }}

    /* Select boxes */
    .stSelectbox {{
        direction: ltr;
    }}

    /* Info boxes */
    .stAlert {{
        direction: ltr;
        text-align: left;
    }}

    /* Agent badge styling */
    .agent-badge {{
        background-color: {THEME['primary']};
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        display: inline-block;
        margin-top: 8px;
    }}

    /* Gold accent for important elements */
    .gold-accent {{
        color: {THEME['accent']};
        font-weight: bold;
    }}

    /* Thinking section styling */
    .thinking-content {{
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid {THEME['accent']};
        margin: 8px 0;
        color: #333;
    }}

    /* Welcome message styling */
    .welcome-box {{
        background: linear-gradient(135deg, {THEME['primary']} 0%, #2d4a6f 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    }}

    .welcome-box h2 {{
        color: {THEME['accent']} !important;
        margin-bottom: 12px;
    }}

    /* Demo mode badge */
    .demo-badge {{
        background-color: #f59e0b;
        color: #1a1a1a;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
    }}

    /* Global header bar */
    .global-header {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background-color: #1a4d2e;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 24px;
        z-index: 9999;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }}

    .header-left {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}

    .header-right {{
        display: flex;
        align-items: center;
    }}

    .header-logo {{
        width: 36px;
        height: 36px;
        background-color: rgba(255,255,255,0.2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }}

    .header-entity {{
        color: white;
        font-family: 'Noto Sans Arabic', sans-serif;
        font-size: 1.1em;
        font-weight: 500;
        direction: rtl;
    }}

    .signout-btn {{
        background-color: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 6px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9em;
        transition: background-color 0.2s;
    }}

    .signout-btn:hover {{
        background-color: rgba(255,255,255,0.2);
    }}

    /* Hide Streamlit branding for cleaner look */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Streamlit header - hide default */
    header[data-testid="stHeader"] {{
        display: none;
    }}

    /* Form styling */
    .stForm {{
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }}

    /* Checkbox styling in sidebar */
    [data-testid="stSidebar"] .stCheckbox label {{
        color: #333 !important;
    }}

    /* Project card styling */
    .project-card {{
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s, border-color 0.2s;
    }}

    .project-card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-color: {THEME['primary']};
    }}

    .project-card h3 {{
        color: {THEME['primary']};
        margin-bottom: 12px;
    }}

    .project-card .description {{
        color: #666;
        font-size: 0.95em;
        line-height: 1.6;
        margin-bottom: 16px;
    }}

    .project-card .agents-list {{
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 16px;
    }}

    .project-card .status-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 500;
    }}

    .status-demo {{
        background-color: #10b981;
        color: white;
    }}

    .status-upcoming {{
        background-color: #6b7280;
        color: white;
    }}

    /* Strategic control section - gold background */
    .strategic-control {{
        background-color: #fef3c7;
        border: 1px solid {THEME['accent']};
        border-radius: 8px;
        padding: 16px;
    }}

    .strategic-control h4 {{
        color: #92400e;
    }}
</style>
"""


def render_global_header(show_signout: bool = True):
    """Render the global header bar that appears on all pages."""
    signout_html = ""
    if show_signout:
        signout_html = """
        <form action="" method="post" style="margin: 0;">
            <button type="submit" class="signout-btn" name="signout">Sign Out</button>
        </form>
        """

    st.markdown(f"""
    <div class="global-header">
        <div class="header-left">
            <div class="header-logo">AI</div>
        </div>
        <div class="header-right">
            <span class="header-entity">مكتب المهمات الاستشارية</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all required session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"

    if "selected_project" not in st.session_state:
        st.session_state.selected_project = None

    if "show_thinking" not in st.session_state:
        st.session_state.show_thinking = True

    if "active_agent_id" not in st.session_state:
        st.session_state.active_agent_id = None


def main():
    """Main application function with page routing."""
    # Apply global CSS
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Page routing
    if not st.session_state.authenticated:
        # Show login page (no header signout on login)
        render_global_header(show_signout=False)
        from pages.login import render_login_page
        render_login_page()

    elif st.session_state.current_page == "project_select" or st.session_state.selected_project is None:
        # Show project selection page
        render_global_header(show_signout=True)
        from pages.project_select import render_project_select_page
        render_project_select_page()

    elif st.session_state.current_page == "workspace":
        # Show main workspace
        render_global_header(show_signout=True)
        from pages.workspace import render_workspace_page
        render_workspace_page()

    else:
        # Default to project selection
        render_global_header(show_signout=True)
        from pages.project_select import render_project_select_page
        render_project_select_page()


if __name__ == "__main__":
    main()
