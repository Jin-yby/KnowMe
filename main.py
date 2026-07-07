"""
KnowMe（知我）— Streamlit 入口页
全局 CSS（Notion 极简设计系统）+ 侧边栏导航 + 语言/主题切换。
pages/ 目录下的文件会被 Streamlit 自动识别为子页面。
"""

import streamlit as st
import config


# ── 页面配置 ──
st.set_page_config(
    page_title="KnowMe",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局状态 ──
if "lang" not in st.session_state:
    st.session_state.lang = "zh"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False  # 默认浅色（Notion 风格）

lang = st.session_state.lang

# ── 全局设计系统 CSS ──
DESIGN_CSS = """
<style>
/* ── Design System: KnowMe Notion-minimal ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* 全局基础 */
.stApp {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* 主区域容器 */
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF;
    padding-top: 2rem;
}

/* 侧边栏 */
[data-testid="stSidebar"] {
    background-color: #FAFAFA;
    border-right: 1px solid #EBEBEB;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1A1A1A;
}

/* ── 标题层级 ── */
h1, .stTitle {
    font-size: 24px !important;
    font-weight: 600 !important;
    color: #1A1A1A !important;
    letter-spacing: -0.01em;
}

h2 {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #1A1A1A !important;
}

h3, h4, .stSubheader {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #1A1A1A !important;
}

h5, h6 {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #1A1A1A !important;
}

/* ── 正文文字 ── */
.stMarkdown p, .stMarkdown li, .stMarkdown span,
.stCaption, .caption {
    font-size: 14px !important;
    font-weight: 400 !important;
    color: #1A1A1A !important;
    line-height: 1.6;
}

.stCaption, .caption {
    color: #9CA3AF !important;
    font-size: 12px !important;
}

/* ── Metric 卡片 ── */
[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 500 !important;
    font-variant-numeric: tabular-nums;
    color: #1A1A1A !important;
}

[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #6B7280 !important;
    text-transform: none !important;
}

/* ── 按钮 ── */
/* 主要按钮 — 紫色 */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stFormSubmitButton"] {
    background-color: #7C5EE0 !important;
    border-color: #7C5EE0 !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem;
    transition: all 0.15s ease;
}

.stButton > button[kind="primary"]:hover {
    background-color: #6D4FD0 !important;
    border-color: #6D4FD0 !important;
}

/* 次要按钮 — 白底 + 边框 */
.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid #EBEBEB !important;
    border-radius: 6px !important;
    color: #1A1A1A !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease;
}

.stButton > button[kind="secondary"]:hover {
    border-color: #E0E0E0 !important;
    background-color: #FAFAFA !important;
}

/* 默认按钮 */
.stButton > button {
    border-radius: 6px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

/* ── 输入框 ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1px solid #EBEBEB !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    color: #1A1A1A !important;
    background-color: #FFFFFF !important;
    transition: border-color 0.15s ease;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #7C5EE0 !important;
    box-shadow: 0 0 0 2px rgba(124, 94, 224, 0.1) !important;
}

/* ── Checkbox ── */
.stCheckbox {
    font-size: 14px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #6B7280 !important;
    border-radius: 6px 6px 0 0 !important;
}

.stTabs [aria-selected="true"] {
    color: #1A1A1A !important;
    border-bottom: 2px solid #7C5EE0 !important;
}

/* ── Info / Success / Error / Warning ── */
.stAlert {
    border-radius: 8px !important;
    font-size: 14px !important;
}

[data-testid="stAlert"] {
    border: 1px solid #EBEBEB !important;
}

/* ── Divider ── */
hr, .stDivider {
    border: none !important;
    border-top: 1px solid #EBEBEB !important;
    margin: 32px 0 !important;
}

/* ── Sidebar 导航按钮 ── */
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent !important;
    border: none !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    color: #6B7280 !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    transition: all 0.15s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(124, 94, 224, 0.08) !important;
    color: #7C5EE0 !important;
}

/* ── Radio（语言切换） ── */
[data-testid="stSidebar"] [data-testid="stRadio"] {
    font-size: 13px !important;
}

/* ── 卡片通用 — 用于各页面的 HTML 卡片 ── */
.km-card {
    border: 1px solid #EBEBEB;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 12px;
    background: #FFFFFF;
    transition: border-color 0.15s ease;
}

.km-card:hover {
    border-color: #E0E0E0;
}

/* ── 任务行（记录页专用） ── */
.km-task-row {
    display: flex;
    align-items: center;
    padding: 10px 12px;
    border-radius: 6px;
    transition: background 0.15s ease;
    cursor: pointer;
}

.km-task-row:hover {
    background-color: #F9FAFB;
}

.km-task-row:hover .km-task-delete {
    opacity: 1;
}

.km-task-delete {
    opacity: 0;
    transition: opacity 0.15s ease;
    cursor: pointer;
    color: #9CA3AF;
    font-size: 12px;
    margin-left: auto;
    padding: 2px 6px;
    border-radius: 4px;
}

.km-task-delete:hover {
    color: #6B7280;
    background-color: #F3F4F6;
}

.km-task-title {
    font-size: 14px;
    font-weight: 400;
    color: #1A1A1A;
    flex: 1;
}

.km-task-title.done {
    text-decoration: line-through;
    color: #9CA3AF;
}

.km-task-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 12px;
    flex-shrink: 0;
}

.km-task-dot.done { background-color: #7C5EE0; }
.km-task-dot.pending { background-color: #E5E7EB; }

/* ── 洞察卡片 ── */
.km-insight-card {
    border: 1px solid #EBEBEB;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 12px;
    background: #FFFFFF;
    transition: border-color 0.15s ease;
}

.km-insight-card.confirmed {
    border-left: 3px solid #7C5EE0;
}

.km-insight-card.pending {
    border-left: 3px solid #E5E7EB;
}

/* ── 空状态邀请式提示 ── */
.km-empty-state {
    text-align: center;
    color: #9CA3AF;
    font-size: 18px;
    font-weight: 400;
    padding: 60px 0;
    line-height: 1.8;
}
.km-empty-state .emoji {
    font-size: 36px;
    display: block;
    margin-bottom: 16px;
}

/* ── 任务行 hover 紫色竖条 ── */
.km-task-row {
    position: relative;
    padding-left: 16px;
}
.km-task-row::before {
    content: '';
    position: absolute;
    left: 0;
    top: 6px;
    bottom: 6px;
    width: 3px;
    border-radius: 2px;
    background: transparent;
    transition: background 0.15s ease;
}
.km-task-row:hover::before {
    background: #7C5EE0;
}

/* ── 洞察卡片呼吸感 ── */
.km-insight-card {
    margin-bottom: 20px;
}
.km-confidence-bar {
    height: 4px;
    border-radius: 2px;
    background: #EBEBEB;
    margin-top: 8px;
}
.km-confidence-fill {
    height: 4px;
    border-radius: 2px;
    background: #7C5EE0;
}
.km-evidence-list {
    color: #6B7280;
    font-size: 13px;
    padding-left: 16px;
}
.km-evidence-list li {
    margin-bottom: 4px;
}
</style>
"""

st.markdown(DESIGN_CSS, unsafe_allow_html=True)

# ── 侧边栏 ──
st.sidebar.markdown(
    f"# 🧠 {config.T('app_name')}\n"
    f"##### {config.T('app_subtitle')}\n"
    "---"
)

# 语言切换
lang_options = {"中文": "zh", "English": "en"}
current_lang_label = "中文" if lang == "zh" else "English"
selected_lang_label = st.sidebar.radio(
    config.T("sidebar_language"),
    options=list(lang_options.keys()),
    index=list(lang_options.keys()).index(current_lang_label),
    horizontal=True,
)

new_lang = lang_options[selected_lang_label]
if new_lang != lang:
    st.session_state.lang = new_lang
    config.set_lang(new_lang)
    st.rerun()

# 主题切换
theme_label = config.T("dark_mode") if st.session_state.dark_mode else config.T("light_mode")
st.sidebar.toggle(theme_label, value=st.session_state.dark_mode, key="theme_toggle")

st.sidebar.divider()

# ── 主页内容 ──
st.title(f"🧠 {config.T('app_name')}")
st.caption(config.T("app_subtitle"))

st.markdown("""
### KnowMe — AI 自我认知引擎

> 不是任务管理器，不是 AI 规划师。
> 你记录日常，AI 帮你发现自己都不知道的行为模式，建立一份活的「个人使用说明书」。

通过左侧导航栏访问各个页面：
- **记录** — 周历 + 每日 TodoList + 感受日记
- **洞察** — AI 发现行为模式，向你提问验证
- **手册** — AI 综合模式，生成个人操作手册
- **故事** — AI 生成传记 + 人物画像
- **设置** — API Key、语言切换、备份恢复
""")
