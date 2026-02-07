"""
صفحة مساحة العمل — منصة الذكاء الاصطناعي للمحفظة (أ)
"""

import csv
import io
import streamlit as st
from config import THEME, PROJECT_1_CONFIG, PROJECT_2_CONFIG
from components.settings_panel import render_settings_panel


# أسماء حالات الاستخدام
PROJECT_NAMES = {
    "project1": {
        "name": "لجنة الفعاليات",
        "description": "برنامج ذكاء اصطناعي يمكّن فريق عمل لجنة الفعاليات من الإشراف على هيئات التطوير في إطار تطوير تقاويم المدن"
    },
    "project2": {
        "name": "احتفالية مرور ٣٠٠ عام على تأسيس الدولة السعودية",
        "description": "تطوير الرؤية والإطار الاستراتيجي لاحتفالية وطنية تاريخية من خلال دراسة التجارب الدولية المشابهة واستخلاص الدروس المستفادة"
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
    """Render the workspace header."""
    project_id = st.session_state.get('selected_project', 'project1')
    project_info = PROJECT_NAMES.get(project_id, PROJECT_NAMES["project1"])

    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("رجوع", key="back_btn"):
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


def render_info_dashboard():
    """Render the info dashboard panel showing system knowledge, files, and capabilities."""
    project_config = get_current_project_config()
    project_id = st.session_state.get('selected_project', 'project1')

    # ذاكرة النظام
    st.markdown(f"""
    <div class="info-dashboard">
        <h4>ذاكرة النظام</h4>
        <div class="info-dashboard-item">
            <span style="color: #374151; font-size: 0.9em;">{project_config.get('system_knowledge', 'غير متاح')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # الملفات المتاحة
    available_files = list(project_config.get('available_files', []))

    # Add uploaded CSV files
    uploaded_names = st.session_state.get('uploaded_csv_names', {}).get(project_id, [])
    if uploaded_names:
        available_files.extend(uploaded_names)

    files_html = ""
    if available_files:
        for f in available_files:
            files_html += f'<div style="background: white; border: 1px solid #e5e7eb; border-radius: 6px; padding: 8px 12px; margin-bottom: 4px; font-size: 0.85em; color: #374151;">{f}</div>'
    else:
        files_html = '<div style="color: #9ca3af; font-size: 0.85em;">لا توجد ملفات محمّلة حالياً</div>'

    st.markdown(f"""
    <div class="info-dashboard">
        <h4>الملفات المتاحة</h4>
        {files_html}
    </div>
    """, unsafe_allow_html=True)

    # القدرات
    capabilities = project_config.get('capabilities', [])
    caps_html = ""
    for cap in capabilities:
        caps_html += f'<div style="color: #374151; font-size: 0.85em; margin-bottom: 4px; padding-right: 8px;">- {cap}</div>'

    st.markdown(f"""
    <div class="info-dashboard">
        <h4>القدرات</h4>
        {caps_html}
    </div>
    """, unsafe_allow_html=True)


def render_csv_upload():
    """Render CSV upload section for project1."""
    project_id = st.session_state.get('selected_project', 'project1')

    if project_id != 'project1':
        return

    st.markdown("---")
    st.markdown("**تحميل ملفات البيانات**")

    uploaded_files = st.file_uploader(
        "اختر ملفات CSV",
        type=["csv"],
        accept_multiple_files=True,
        key="csv_uploader",
        label_visibility="collapsed"
    )

    if uploaded_files:
        csv_data_key = 'uploaded_csv_data'
        csv_names_key = 'uploaded_csv_names'

        if csv_data_key not in st.session_state:
            st.session_state[csv_data_key] = {}
        if csv_names_key not in st.session_state:
            st.session_state[csv_names_key] = {}

        if project_id not in st.session_state[csv_data_key]:
            st.session_state[csv_data_key][project_id] = {}
        if project_id not in st.session_state[csv_names_key]:
            st.session_state[csv_names_key][project_id] = []

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            if file_name not in st.session_state[csv_names_key][project_id]:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    reader = csv.DictReader(io.StringIO(content))
                    rows = list(reader)
                    st.session_state[csv_data_key][project_id][file_name] = {
                        'headers': reader.fieldnames,
                        'rows': rows,
                        'raw': content
                    }
                    st.session_state[csv_names_key][project_id].append(file_name)
                    st.success(f"تم تحميل: {file_name} ({len(rows)} سجل)")
                except Exception as e:
                    st.error(f"خطأ في قراءة {file_name}: {str(e)}")


def render_chat_message(message: dict, index: int):
    """Render a single chat message."""
    role = message["role"]

    with st.chat_message(role):
        st.markdown(message["content"])

        # Show thinking trace if available and enabled
        if (role == "assistant" and
            st.session_state.get('show_thinking', True) and
            message.get("thinking")):

            with st.expander("تفكير الوكيل", expanded=False):
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 12px;
                    border-radius: 8px;
                    border-right: 4px solid {THEME['accent']};
                    margin: 8px 0;
                    white-space: pre-wrap;
                    color: #333;
                    font-size: 0.9em;
                    direction: rtl;
                    text-align: right;
                ">
                {message['thinking'].replace(chr(10), '<br/>')}
                </div>
                """, unsafe_allow_html=True)

        # Show agent name
        if role == "assistant" and message.get("agent"):
            agent_name = message.get("agent", "وكيل")
            st.markdown(f"""
            <span style="
                background-color: {THEME['primary']};
                color: white;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 12px;
                display: inline-block;
                margin-top: 8px;
            ">{agent_name}</span>
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
        direction: rtl;
        text-align: right;
    ">
        <h2 style="color: {THEME['accent']}; margin-bottom: 12px;">
            {project_info['name']}
        </h2>
        <p>{project_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick action buttons
    if project_id == 'project1':
        examples = [
            "حلل بيانات الفعاليات المتاحة",
            "ما المعلومات الناقصة؟",
            "أعد تقريراً للجنة",
            "افحص جودة البيانات",
        ]
    else:
        examples = [
            "أحتاج دراسة مقارنة عن تجربة سانت بطرسبرغ",
            "ما مؤشرات الأداء المقترحة؟",
            "راجع التحليل السابق",
            "حوّل المحتوى لعرض تقديمي",
        ]

    st.markdown("#### أمثلة سريعة")
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                pending_key = f"pending_message_{project_id}"
                st.session_state[pending_key] = example
                st.rerun()


def render_sidebar():
    """Render the sidebar."""

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 16px 0;">
            <h3 style="color: {THEME['primary']}; font-size: 1.1em;">لوحة التحكم</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Info dashboard
        render_info_dashboard()

        # CSV upload for project1
        render_csv_upload()

        st.markdown("---")

        # Settings section
        st.markdown("### الإعدادات")
        st.session_state.show_thinking = st.checkbox(
            "عرض تفكير الوكيل",
            value=st.session_state.get('show_thinking', True),
            help="عرض خطوات تفكير الوكيل"
        )

        st.markdown("---")

        # Settings panel
        render_settings_panel()

        st.markdown("---")

        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("مسح المحادثة", use_container_width=True):
                project_id = st.session_state.get('selected_project', 'project1')
                messages_key = f"messages_{project_id}"
                st.session_state[messages_key] = []
                orchestrator_key = f"orchestrator_{project_id}"
                if orchestrator_key in st.session_state:
                    del st.session_state[orchestrator_key]
                st.rerun()
        with col2:
            if st.button("تسجيل الخروج", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.current_page = "login"
                st.rerun()


def process_user_message(prompt: str, messages_key: str):
    """Process a user message and generate response."""
    project_id = st.session_state.get('selected_project', 'project1')

    # Add user message to history
    st.session_state[messages_key].append({
        "role": "user",
        "content": prompt
    })

    # Build context with uploaded CSV data
    context = {}
    csv_data = st.session_state.get('uploaded_csv_data', {}).get(project_id, {})
    if csv_data:
        csv_context_parts = []
        for fname, fdata in csv_data.items():
            csv_context_parts.append(f"ملف: {fname}\nالأعمدة: {', '.join(fdata['headers'])}\nعدد السجلات: {len(fdata['rows'])}\n")
            # Include sample data
            sample_rows = fdata['rows'][:20]
            for row in sample_rows:
                csv_context_parts.append(str(row))
            if len(fdata['rows']) > 20:
                csv_context_parts.append(f"... و{len(fdata['rows']) - 20} سجلاً إضافياً")
        context['uploaded_data'] = '\n'.join(csv_context_parts)

    # Get response from orchestrator
    try:
        orchestrator = get_orchestrator()
        response = orchestrator.invoke(prompt, context=context if context else None)

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
        error_message = f"حدث خطأ أثناء المعالجة: {str(e)}"
        st.session_state[messages_key].append({
            "role": "assistant",
            "content": error_message,
            "agent": "النظام"
        })


def render_chat_interface():
    """Render the main chat interface."""
    project_id = st.session_state.get('selected_project', 'project1')
    messages_key = f"messages_{project_id}"

    # Initialize messages if needed
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Check for pending message
    pending_key = f"pending_message_{project_id}"
    if pending_key in st.session_state and st.session_state[pending_key]:
        prompt = st.session_state[pending_key]
        st.session_state[pending_key] = None

        with st.spinner("جارٍ المعالجة..."):
            process_user_message(prompt, messages_key)

    # Show welcome message if no messages
    if not st.session_state[messages_key]:
        render_welcome_message()

    # Display chat history
    for i, message in enumerate(st.session_state[messages_key]):
        render_chat_message(message, i)

    # Chat input
    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        st.session_state[pending_key] = prompt
        st.rerun()


def render_workspace_page():
    """Render the complete workspace page."""

    # Render sidebar
    render_sidebar()

    # Main content area
    render_workspace_header()

    st.markdown("---")

    # Chat interface
    st.markdown(f"""
    <h3 style="color: {THEME['primary']};">المحادثة</h3>
    """, unsafe_allow_html=True)

    render_chat_interface()


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_workspace_page()
