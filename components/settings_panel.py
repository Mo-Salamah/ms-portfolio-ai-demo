"""
لوحة الإعدادات — منصة الذكاء الاصطناعي للمحفظة (أ)
"""

import streamlit as st
from datetime import datetime
from config import THEME, PROJECT_1_CONFIG, PROJECT_2_CONFIG, PRESENTATION_GUIDELINES, STRATEGIC_CONTROL_TEXT


def get_current_project_config():
    """Get the configuration for the currently selected project."""
    project_id = st.session_state.get('selected_project', 'project1')
    if project_id == 'project1':
        return PROJECT_1_CONFIG
    return PROJECT_2_CONFIG


def render_project_context_section():
    """Render the locked project context section."""
    project_config = get_current_project_config()
    context = project_config.get('context', '')

    with st.expander("سياق المشروع (للقراءة فقط)", expanded=False):
        st.markdown(f"""
        <div style="
            background-color: #f3f4f6;
            padding: 16px;
            border-radius: 8px;
            border-right: 4px solid #9ca3af;
            border-left: none;
            opacity: 0.9;
            direction: rtl;
            text-align: right;
        ">
            <div style="
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                color: #6b7280;
            ">
                <small>يُدار من قبل الإدارة فقط — للقراءة فقط</small>
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
    project_config = get_current_project_config()
    memory_key = f"memory_{project_id}"

    if memory_key not in st.session_state:
        st.session_state[memory_key] = list(project_config.get('memory', []))

    with st.expander("ذاكرة الوكلاء", expanded=True):
        st.markdown("""
        <div style="margin-bottom: 12px; color: #666; font-size: 0.85em; direction: rtl;">
            سجل الأحداث والملاحظات المهمة لهذا المشروع
        </div>
        """, unsafe_allow_html=True)

        for i, entry in enumerate(st.session_state[memory_key]):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div style="
                    background-color: white;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    border-right: 3px solid {THEME['accent']};
                    border-left: none;
                    direction: rtl;
                    text-align: right;
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
                if st.button("X", key=f"delete_memory_{i}", help="حذف"):
                    st.session_state[memory_key].pop(i)
                    st.rerun()

        st.markdown("---")
        st.markdown("**إضافة ملاحظة جديدة:**")

        new_entry = st.text_input(
            "ملاحظة",
            placeholder="أدخل ملاحظة جديدة...",
            key="new_memory_entry",
            label_visibility="collapsed"
        )

        if st.button("+ إضافة", key="add_memory_btn"):
            if new_entry:
                today = datetime.now().strftime("%Y-%m-%d")
                st.session_state[memory_key].insert(0, {
                    "date": today,
                    "entry": new_entry
                })
                st.rerun()


def render_presentation_guidelines_section():
    """Render the presentation guidelines reference section."""
    with st.expander("معايير إعداد الشرائح", expanded=False):
        st.markdown(f"""
        <div style="
            background-color: #f0f9ff;
            padding: 16px;
            border-radius: 8px;
            border-right: 4px solid #0ea5e9;
            border-left: none;
            direction: rtl;
            text-align: right;
        ">
            <div style="
                white-space: pre-wrap;
                font-size: 0.9em;
                line-height: 1.8;
                color: #0c4a6e;
            ">{PRESENTATION_GUIDELINES}</div>
        </div>
        """, unsafe_allow_html=True)


def render_strategic_control_section():
    """Render the strategic control section."""
    with st.expander("صلاحيات المحفظة", expanded=False):
        st.markdown(f"""
        <div class="strategic-control" style="
            background-color: {THEME['control_bg']};
            padding: 16px;
            border-radius: 8px;
            border-right: 4px solid {THEME['accent']};
            border-left: none;
            border: 1px solid {THEME['accent']};
            direction: rtl;
            text-align: right;
        ">
            <div style="
                white-space: pre-wrap;
                font-size: 0.9em;
                line-height: 1.8;
                color: #92400e;
            ">{STRATEGIC_CONTROL_TEXT}</div>
        </div>
        """, unsafe_allow_html=True)


def render_settings_panel():
    """Render the complete settings panel."""

    st.markdown(f"""
    <div style="
        background-color: white;
        color: {THEME['primary']};
        padding: 16px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
        border: 1px solid #e5e7eb;
        border-bottom: 2px solid {THEME['accent']};
        direction: rtl;
        text-align: right;
    ">
        <h4 style="margin: 0; color: {THEME['primary']};">
            إعدادات المشروع
        </h4>
    </div>
    """, unsafe_allow_html=True)

    render_project_context_section()
    render_agent_memory_section()
    render_presentation_guidelines_section()
    render_strategic_control_section()


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_settings_panel()
