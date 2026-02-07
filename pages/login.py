"""
صفحة تسجيل الدخول — منصة الذكاء الاصطناعي للمحفظة (أ)
"""

import csv
import streamlit as st
from pathlib import Path
from config import THEME


# Path to users CSV file
USERS_CSV_PATH = Path(__file__).parent.parent / "users.csv"


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user against users.csv file."""
    try:
        with open(USERS_CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"].strip() == username and row["password"].strip() == password:
                    return True
    except FileNotFoundError:
        return False
    return False


def render_login_page():
    """Render the login page."""

    st.markdown(f"""
    <style>
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
            direction: rtl;
        }}

        .login-title {{
            color: {THEME['primary']};
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 8px;
            font-family: 'Noto Sans Arabic', sans-serif;
        }}

        .login-subtitle {{
            color: #666;
            font-size: 0.9em;
            font-family: 'Noto Sans Arabic', sans-serif;
        }}

        .stTextInput > div > div > input {{
            direction: rtl;
            text-align: right;
        }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"""
        <div class="login-header">
            <div class="login-title">منصة الذكاء الاصطناعي للمحفظة (أ)</div>
            <div class="login-subtitle">مكتب شؤون المهمات والمبادرات</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("##### تسجيل الدخول")

            username = st.text_input(
                "اسم المستخدم",
                placeholder="أدخل اسم المستخدم",
                key="username_input"
            )

            password = st.text_input(
                "كلمة المرور",
                type="password",
                placeholder="أدخل كلمة المرور",
                key="password_input"
            )

            submit_button = st.form_submit_button(
                "دخول",
                use_container_width=True,
                type="primary"
            )

            if submit_button:
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.current_page = "project_select"
                        st.rerun()
                    else:
                        st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
                else:
                    st.error("يرجى إدخال اسم المستخدم وكلمة المرور")


if __name__ == "__main__":
    render_login_page()
