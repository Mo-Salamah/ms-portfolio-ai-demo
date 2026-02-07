"""
مكتب شؤون المهمات والمبادرات — منصة الذكاء الاصطناعي للمحفظة (أ)
"""

import streamlit as st
from config import THEME

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="منصة الذكاء الاصطناعي للمحفظة (أ)",
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto"
)

# Global CSS for Arabic RTL layout
GLOBAL_CSS = f"""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap');

    /* RTL Layout */
    .stApp {{
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    /* Main content area */
    .main .block-container {{
        direction: rtl;
        text-align: right;
        padding-top: 80px;
    }}

    /* Sidebar - RTL */
    [data-testid="stSidebar"] {{
        direction: rtl;
        text-align: right;
        background-color: #f8f9fa;
        border-left: 1px solid #e5e7eb;
        border-right: none;
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
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    h1 {{
        border-bottom: 3px solid {THEME['accent']};
        padding-bottom: 10px;
    }}

    /* Chat messages */
    .stChatMessage {{
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    /* Input field */
    .stChatInput textarea {{
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    /* Text inputs */
    .stTextInput input {{
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    .streamlit-expanderContent {{
        direction: rtl;
        text-align: right;
    }}

    /* Buttons */
    .stButton button {{
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    /* Select boxes */
    .stSelectbox {{
        direction: rtl;
    }}

    /* Info boxes */
    .stAlert {{
        direction: rtl;
        text-align: right;
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

    /* Gold accent */
    .gold-accent {{
        color: {THEME['accent']};
        font-weight: bold;
    }}

    /* Thinking section styling */
    .thinking-content {{
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-right: 4px solid {THEME['accent']};
        border-left: none;
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
        direction: rtl;
        text-align: right;
    }}

    .welcome-box h2 {{
        color: {THEME['accent']} !important;
        margin-bottom: 12px;
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
        direction: rtl;
    }}

    .header-right {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}

    .header-left {{
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
        font-size: 0.8em;
    }}

    .header-entity {{
        color: white;
        font-family: 'Noto Sans Arabic', sans-serif;
        font-size: 1.05em;
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
        font-family: 'Noto Sans Arabic', sans-serif;
        transition: background-color 0.2s;
    }}

    .signout-btn:hover {{
        background-color: rgba(255,255,255,0.2);
    }}

    /* Hide Streamlit branding */
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
        direction: rtl;
        text-align: right;
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

    .status-active {{
        background-color: #10b981;
        color: white;
    }}

    .status-upcoming {{
        background-color: #6b7280;
        color: white;
    }}

    /* Strategic control section */
    .strategic-control {{
        background-color: #fef3c7;
        border: 1px solid {THEME['accent']};
        border-radius: 8px;
        padding: 16px;
    }}

    .strategic-control h4 {{
        color: #92400e;
    }}

    /* Info dashboard */
    .info-dashboard {{
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        direction: rtl;
        text-align: right;
    }}

    .info-dashboard h4 {{
        color: {THEME['primary']};
        margin-bottom: 8px;
        font-size: 0.95em;
    }}

    .info-dashboard-item {{
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }}

    /* File uploader RTL */
    .stFileUploader {{
        direction: rtl;
    }}

    /* Upload area text */
    [data-testid="stFileUploader"] {{
        direction: rtl;
        text-align: right;
    }}

    /* Override Streamlit English text with Arabic */
    /* File uploader: "Drag and drop file here" → Arabic */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] span:first-child {{
        font-size: 0 !important;
    }}
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] span:first-child::after {{
        content: "اسحب الملفات وأفلتها هنا" !important;
        font-size: 0.9rem !important;
        font-family: 'Noto Sans Arabic', sans-serif !important;
    }}

    /* File uploader: "Browse files" button → Arabic */
    [data-testid="stFileUploaderDropzone"] button {{
        font-size: 0 !important;
    }}
    [data-testid="stFileUploaderDropzone"] button::after {{
        content: "تصفح الملفات" !important;
        font-size: 0.85rem !important;
        font-family: 'Noto Sans Arabic', sans-serif !important;
    }}

    /* File uploader: "Limit XMB per file" → Arabic */
    [data-testid="stFileUploader"] small {{
        font-size: 0 !important;
    }}
    [data-testid="stFileUploader"] small::after {{
        content: "ملفات CSV فقط" !important;
        font-size: 0.75rem !important;
        color: #999 !important;
        font-family: 'Noto Sans Arabic', sans-serif !important;
    }}

    /* Override Streamlit's "Running..." spinner text */
    .stSpinner > div {{
        direction: rtl;
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    /* Tabs RTL */
    .stTabs {{
        direction: rtl;
    }}

    /* Metric RTL */
    [data-testid="stMetric"] {{
        direction: rtl;
        text-align: right;
    }}

    /* Make "Manage app" button hidden */
    .stDeployButton {{
        display: none !important;
    }}

    /* Override Streamlit toast/notification text */
    .stToast {{
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
    }}

    /* Hide the sidebar nav separator */
    [data-testid="stSidebarNavSeparator"] {{
        display: none !important;
    }}
</style>
"""

# CSS to completely hide sidebar on pages that don't need it
HIDE_SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    /* Expand main content to full width when sidebar hidden */
    .main .block-container {
        max-width: 100% !important;
    }
</style>
"""


def render_global_header(show_signout: bool = True):
    """Render the global header bar."""
    st.markdown(f"""
    <div class="global-header">
        <div class="header-right">
            <div class="header-logo">AI</div>
            <span class="header-entity">مكتب شؤون المهمات والمبادرات — منصة الذكاء الاصطناعي للمحفظة (أ)</span>
        </div>
        <div class="header-left">
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

    if "uploaded_csv_data" not in st.session_state:
        st.session_state.uploaded_csv_data = {}

    if "uploaded_csv_names" not in st.session_state:
        st.session_state.uploaded_csv_names = {}


def main():
    """Main application function with page routing."""
    # Apply global CSS
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Page routing
    if not st.session_state.authenticated:
        st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)
        render_global_header(show_signout=False)
        from pages.login import render_login_page
        render_login_page()

    elif st.session_state.current_page == "project_select" or st.session_state.selected_project is None:
        st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)
        render_global_header(show_signout=True)
        from pages.project_select import render_project_select_page
        render_project_select_page()

    elif st.session_state.current_page == "workspace":
        render_global_header(show_signout=True)
        from pages.workspace import render_workspace_page
        render_workspace_page()

    else:
        st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)
        render_global_header(show_signout=True)
        from pages.project_select import render_project_select_page
        render_project_select_page()


if __name__ == "__main__":
    main()
