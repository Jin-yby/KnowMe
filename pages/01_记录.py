"""
记录页 — 周历 + 每日 TodoList + 感受日记 + AI 情绪分析
设计系统：Notion 极简风格，km-task-row / km-card CSS 类
"""

import streamlit as st
from datetime import datetime, timedelta
from services import DataManager, AIClient
import config


# ── 初始化 ──
dm = DataManager()
today = datetime.now()
today_str = today.strftime("%Y-%m-%d")
lang = config.get_lang()

st.title(config.T("record_title"))


# ============================================================
#  1. 本周周历
# ============================================================
st.markdown(f"#### {config.T('record_week_label')}")

monday = today - timedelta(days=today.weekday())
week_dates = [(monday + timedelta(days=i)) for i in range(7)]

# 一次性读取本周任务
week_tasks_map = {}
for d in week_dates:
    ds = d.strftime("%Y-%m-%d")
    week_tasks_map[ds] = dm.get_tasks(ds)

cols = st.columns(7)
weekday_names = config.WEEKDAYS_CN if lang == "zh" else config.WEEKDAYS_EN

for i, (col, date) in enumerate(zip(cols, week_dates)):
    ds = date.strftime("%Y-%m-%d")
    is_today = ds == today_str
    tasks = week_tasks_map.get(ds, [])

    # 周历格子样式
    if is_today:
        bg = "background-color:#7C5EE0;border-radius:10px;padding:12px 8px;"
        text_color = "#FFFFFF"
    else:
        bg = "border:1px solid #EBEBEB;border-radius:10px;padding:12px 8px;"
        text_color = "#1A1A1A"

    col.markdown(f"<div style='{bg}color:{text_color};text-align:center;'>",
                 unsafe_allow_html=True)

    day_label = weekday_names[i]
    date_num = date.day
    weight = "600" if is_today else "400"
    col.markdown(f"<div style='font-weight:{weight};font-size:12px;opacity:0.8;'>"
                 f"{day_label}</div>",
                 unsafe_allow_html=True)
    col.markdown(f"<div style='font-size:1.3em;font-weight:{weight};margin:2px 0 8px;'>"
                 f"{date_num}</div>",
                 unsafe_allow_html=True)

    # 任务预览
    if tasks:
        for t in tasks[:3]:
            if is_today:
                icon_color = "rgba(255,255,255,0.9)"
            elif t["status"] == "completed":
                icon_color = "#7C5EE0"
            else:
                icon_color = "#9CA3AF"
            icon = "●" if t["status"] == "completed" else "○"
            col.markdown(
                f"<div style='font-size:11px;color:{icon_color};text-align:left;"
                f"padding:1px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                f"max-width:100%;'>"
                f"{icon} {t['title'][:5]}</div>",
                unsafe_allow_html=True,
            )
        if len(tasks) > 3:
            col.markdown(
                f"<div style='font-size:10px;opacity:0.6;'>+{len(tasks)-3}</div>",
                unsafe_allow_html=True,
            )
    else:
        col.markdown(f"<div style='font-size:11px;opacity:0.3;'>-</div>",
                     unsafe_allow_html=True)

    col.markdown("</div>", unsafe_allow_html=True)


st.divider()


# ============================================================
#  2. 今日 TodoList
# ============================================================
st.markdown(f"#### 📅 {today_str}")

today_tasks = dm.get_tasks(today_str)

# 添加任务
with st.form("add_task_form", clear_on_submit=True):
    new_task = st.text_input(
        config.T("record_todo_placeholder"),
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button(config.T("record_save"), type="primary")
    if submitted and new_task.strip():
        dm.add_task(
            title=new_task.strip(),
            subject="Other",
            plan_date=today_str,
            deadline=today_str,
        )
        st.rerun()

# 任务列表 — HTML 渲染（纯文字 + hover 显示删除）
if today_tasks:
    for t in today_tasks:
        is_done = t["status"] == "completed"
        done_cls = "done" if is_done else ""
        dot_cls = "done" if is_done else "pending"

        col_check, col_display, col_del = st.columns([1, 14, 1])

        with col_check:
            clicked = st.checkbox("", value=is_done, key=f"ck_{t['id']}", label_visibility="collapsed")
            if clicked != is_done:
                dm.update_task(t["id"], status="completed" if clicked else "pending")
                st.rerun()

        with col_display:
            st.markdown(
                f"<div class='km-task-row'>"
                f"<div class='km-task-dot {dot_cls}'></div>"
                f"<div class='km-task-title {done_cls}'>{t['title']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col_del:
            if st.button("✕", key=f"del_{t['id']}",
                         help=config.T("record_delete")):
                dm.delete_task(t["id"])
                st.rerun()
else:
    st.markdown(
        "<div class='km-empty-state'><span class='emoji'>📝</span>"
        "写下你今天的第一件事</div>",
        unsafe_allow_html=True,
    )


st.divider()


# ============================================================
#  3. 今日感受 + AI 情绪分析
# ============================================================
st.markdown(f"#### 💬 {config.T('record_feeling_label')}")

diary_map = dm.get_diary_map()
existing_diary = diary_map.get(today_str)

feeling_text = st.text_area(
    config.T("record_feeling_placeholder"),
    value=existing_diary.get("raw", "") if existing_diary else "",
    height=80,
    key="feeling_input",
)

if feeling_text.strip():
    col_analyze, col_info = st.columns([1, 3])
    with col_analyze:
        analyze_clicked = st.button(
            "AI 分析",
            key="analyze_feeling",
            use_container_width=True,
            type="primary",
        )
    with col_info:
        st.caption(config.T("record_mood_label"))

    if analyze_clicked:
        api_key = dm.get_api_key()
        provider = dm.data.get("provider", "deepseek")
        result = AIClient.ask("diary", feeling_text, api_key, provider=provider)

        if "error" in result:
            st.error(result["error"])
        else:
            analysis = result
            mood = analysis.get("mood", {})
            sleep = analysis.get("sleep", {})

            col_mood, col_sleep = st.columns(2)
            with col_mood:
                if isinstance(mood, dict):
                    score = mood.get("score", 0)
                    primary = mood.get("primary", "?")
                    st.metric("Mood", f"{primary} ({score}/10)")
            with col_sleep:
                if isinstance(sleep, dict):
                    hours = sleep.get("hours", 0)
                    quality = sleep.get("quality", "?")
                    st.metric("Sleep", f"{hours}h ({quality})")

            highlights = analysis.get("highlights", [])
            suggestions = analysis.get("suggestions", [])
            reply = analysis.get("reply", "")

            if highlights:
                st.markdown("**Highlights**" if lang == "en" else "**亮点**")
                for h in highlights:
                    st.markdown(f"- {h}")

            if suggestions:
                st.markdown("**Suggestions**" if lang == "en" else "**建议**")
                for s in suggestions:
                    st.markdown(f"- {s}")

            if reply:
                st.info(reply)

            dm.add_diary(feeling_text.strip(), analysis)
            st.success("Saved")
            st.rerun()

    # 已有分析结果时直接展示
    if existing_diary and not analyze_clicked:
        analysis = existing_diary.get("analysis", {})
        if isinstance(analysis, dict):
            mood = analysis.get("mood", {})
            sleep = analysis.get("sleep", {})

            if mood:
                col_mood, col_sleep = st.columns(2)
                with col_mood:
                    if isinstance(mood, dict):
                        score = mood.get("score", 0)
                        primary = mood.get("primary", "?")
                        st.metric("Mood", f"{primary} ({score}/10)")
                with col_sleep:
                    if isinstance(sleep, dict):
                        hours = sleep.get("hours", 0)
                        quality = sleep.get("quality", "?")
                        st.metric("Sleep", f"{hours}h ({quality})")

            reply = analysis.get("reply", "")
            if reply:
                st.info(reply)


st.divider()


# ============================================================
#  4. 本周统计
# ============================================================
st.markdown("#### 📊 " + config.T("record_week_stats"))

week_total = 0
week_done = 0
for ds in week_tasks_map.values():
    week_total += len(ds)
    week_done += sum(1 for t in ds if t["status"] == "completed")

col_total, col_done, col_rate, col_mood = st.columns(4)
with col_total:
    st.metric(config.T("record_total"), week_total)
with col_done:
    st.metric(config.T("record_done"), week_done)
with col_rate:
    rate = f"{int(week_done / week_total * 100)}%" if week_total else "-"
    st.metric(config.T("record_rate"), rate)
with col_mood:
    week_diaries = dm.get_diary(limit=7)
    mood_scores = []
    for d in week_diaries:
        a = d.get("analysis", {})
        if isinstance(a, dict):
            m = a.get("mood", {})
            if isinstance(m, dict) and m.get("score"):
                mood_scores.append(m["score"])
    avg_mood = f"{sum(mood_scores)/len(mood_scores):.1f}" if mood_scores else "-"
    st.metric(config.T("record_avg_mood"), avg_mood)
