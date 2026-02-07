"""
صفحة تسجيل الدخول — منصة الذكاء الاصطناعي للمحفظة (أ)
"""

import csv
import os
import streamlit as st
from pathlib import Path
from config import THEME


def _get_users_csv_path() -> Path:
    """Get the path to users.csv, trying multiple possible locations."""
    # Try relative to this file
    path1 = Path(__file__).parent.parent / "users.csv"
    if path1.exists():
        return path1

    # Try relative to current working directory
    path2 = Path(os.getcwd()) / "users.csv"
    if path2.exists():
        return path2

    # Try relative to app root (Streamlit Cloud uses /app or /mount/src)
    for root in ["/app", "/mount/src", "/home/appuser"]:
        for dirpath, dirnames, filenames in os.walk(root):
            if "users.csv" in filenames:
                return Path(dirpath) / "users.csv"

    return path1  # fallback


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user against users.csv file. Returns False if file not found or credentials invalid."""
    users_path = _get_users_csv_path()
    try:
        with open(users_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"].strip() == username and row["password"].strip() == password:
                    return True
    except FileNotFoundError:
        # CSV file not found — do NOT allow login
        return False
    except Exception:
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
