"""
صفحة اختيار حالة الاستخدام — منصة الذكاء الاصطناعي للمحفظة (أ)
"""

import streamlit as st
from config import THEME


# حالات الاستخدام
USE_CASES = [
    {
        "id": "project1",
        "title": "لجنة الفعاليات",
        "description": "برنامج ذكاء اصطناعي يمكّن فريق عمل لجنة الفعاليات من الإشراف على هيئات التطوير في إطار تطوير تقاويم المدن",
        "status": "متاح",
        "status_class": "status-active",
        "enabled": True,
    },
    {
        "id": "project2",
        "title": "احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية",
        "description": "تطوير الرؤية والإطار الاستراتيجي لاحتفالية وطنية تاريخية من خلال دراسة التجارب الدولية المشابهة واستخلاص الدروس المستفادة",
        "status": "متاح",
        "status_class": "status-active",
        "enabled": True,
    },
    {
        "id": "project3",
        "title": "مراجعة العروض التقديمية",
        "description": "نظام ذكاء اصطناعي مدرّب على المخرجات التاريخية للمحفظة لمراجعة العروض التقديمية وضمان التوافق مع المعايير المعتمدة",
        "status": "قيد التطوير",
        "status_class": "status-upcoming",
        "enabled": False,
    },
    {
        "id": "project4",
        "title": "الرياضات الإلكترونية",
        "description": "نظام ذكاء اصطناعي يدعم فريق الرياضات الإلكترونية في التفاوض مع الناشرين وتخطيط البطولات وإعداد التقارير الدورية",
        "status": "قيد التطوير",
        "status_class": "status-upcoming",
        "enabled": False,
    },
    {
        "id": "project5",
        "title": "المساعد العام للمحفظة",
        "description": "نظام ذكاء اصطناعي يوفر قدرات مشتركة — تطوير الاستراتيجيات والمقارنات المعيارية ومتابعة مؤشرات الأداء — لجميع مسارات العمل",
        "status": "قيد التطوير",
        "status_class": "status-upcoming",
        "enabled": False,
    },
    {
        "id": "project6",
        "title": "مكتب تواصل الوزراء",
        "description": "نظام ذكاء اصطناعي يساهم في عملية المتابعة مع مختلف الوزارات وتطوير التقارير الربعية بشأنها",
        "status": "قيد التطوير",
        "status_class": "status-upcoming",
        "enabled": False,
    },
]


def render_use_case_card(case: dict):
    """Render a single use case card."""
    with st.container():
        col_title, col_status = st.columns([4, 1])
        with col_title:
            st.markdown(f"### {case['title']}")
        with col_status:
            status_color = "#10b981" if case["enabled"] else "#6b7280"
            st.markdown(
                f'<span style="background-color: {status_color}; color: white; padding: 4px 12px; '
                f'border-radius: 12px; font-size: 0.8em; font-weight: 500;">{case["status"]}</span>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown(f"{case['description']}")
        st.markdown("")

        if case["enabled"]:
            if st.button(
                "فتح",
                key=f"btn_{case['id']}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state.selected_project = case['id']
                st.session_state.current_page = "workspace"
                st.rerun()
        else:
            st.button(
                "قيد التطوير",
                key=f"btn_{case['id']}",
                use_container_width=True,
                disabled=True
            )


def render_project_select_page():
    """Render the project selection page."""

    # Sign out button (left side in RTL layout)
    col_spacer, col_signout = st.columns([5, 1])
    with col_signout:
        if st.button("تسجيل الخروج", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.current_page = "login"
            st.rerun()

    # Header section
    st.markdown(f"""
    <div style="text-align: right; padding: 20px 0 30px 0; direction: rtl;">
        <h1 style="color: {THEME['primary']}; margin-bottom: 16px;">منصة الذكاء الاصطناعي للمحفظة (أ)</h1>
        <p style="color: #666; line-height: 1.7; font-size: 1.05em; font-family: 'Noto Sans Arabic', sans-serif;">
            منصة ذكاء اصطناعي متعددة الوكلاء ("Multi-Agent System") مصممة لدعم فرق العمل
            في المحفظة من خلال وكلاء متخصصين يقومون بالبحث وتحليل البيانات وإعداد التقارير
            والتوصيات الاستراتيجية.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Section header
    st.markdown(f"""
    <h2 style="color: {THEME['primary']}; margin-bottom: 24px;">حالات الاستخدام</h2>
    """, unsafe_allow_html=True)

    # First row - enabled use cases
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_use_case_card(USE_CASES[0])
    with col2:
        render_use_case_card(USE_CASES[1])

    # Second row
    col3, col4 = st.columns(2, gap="large")
    with col3:
        render_use_case_card(USE_CASES[2])
    with col4:
        render_use_case_card(USE_CASES[3])

    # Third row
    col5, col6 = st.columns(2, gap="large")
    with col5:
        render_use_case_card(USE_CASES[4])
    with col6:
        render_use_case_card(USE_CASES[5])


if __name__ == "__main__":
    render_project_select_page()
