"""
Login Page for MS Portfolio AI Agent Demo
"""

import streamlit as st
from config import THEME


def render_login_page():
    """Render the login page with professional styling."""

    # Custom CSS for login page
    st.markdown(f"""
    <style>
        /* Center the login form */
        .login-container {{
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}

        .login-header {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .login-logo {{
            font-size: 64px;
            margin-bottom: 16px;
        }}

        .login-title {{
            color: {THEME['primary']};
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 8px;
        }}

        .login-subtitle {{
            color: #666;
            font-size: 0.9em;
        }}

        .demo-notice {{
            background-color: #fef3c7;
            border: 1px solid {THEME['accent']};
            border-radius: 8px;
            padding: 12px;
            margin-top: 20px;
            text-align: center;
            font-size: 0.85em;
            color: #92400e;
        }}

        /* Style the form - LTR */
        .stTextInput > div > div > input {{
            direction: ltr;
            text-align: left;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Create centered layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Header with logo
        st.markdown("""
        <div class="login-header">
            <div class="login-logo"></div>
            <div class="login-title">Strategic AI Platform</div>
            <div class="login-subtitle">Multi-Agent System for Strategic Planning</div>
        </div>
        """, unsafe_allow_html=True)

        # Login form
        with st.form("login_form"):
            st.markdown("##### Sign In")

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="username_input"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="password_input"
            )

            submit_button = st.form_submit_button(
                "Sign In",
                use_container_width=True,
                type="primary"
            )

            if submit_button:
                # Accept any credentials for demo
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.current_page = "project_select"
                    st.rerun()
                else:
                    st.error("Please enter both username and password")

        # Demo notice
        st.markdown("""
        <div class="demo-notice">
            <strong>Demo Mode</strong><br/>
            You can use any username and password to sign in
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_login_page()
