"""
洞察页 — AI 发现行为模式，以提问方式验证
"""

import json
from datetime import datetime
import streamlit as st
from services import DataManager, AIClient
import config


# ── 辅助函数（必须在调用前定义） ──

def _validate_and_update(dm, iid, insight, answer, api_key="confirm"):
    """调用 AI 验证用户回答，更新 insight 状态。"""
    provider = dm.data.get("provider", "deepseek")
    key = dm.get_api_key()

    validate_input = json.dumps({
        "hypothesis": insight.get("hypothesis", ""),
        "question": insight.get("question", ""),
        "user_answer": answer,
    }, ensure_ascii=False)

    result = AIClient.ask("discover_validate", validate_input, key, provider=provider)

    if "error" in result:
        st.error(result["error"])
        return

    status = result.get("status", "confirmed" if api_key == "confirm" else "refuted")
    reply = result.get("reply", "")

    # 如果用户点了"不是这样"，无论 AI 怎么说都标记为 refuted
    if api_key == "refute":
        status = "refuted"

    dm.update_insight(
        iid,
        status=status,
        user_answer=answer,
        follow_up=reply,
        confirmed_at=datetime.now().strftime("%Y-%m-%d") if status == "confirmed" else None,
    )
    st.rerun()


# ── 初始化 ──
dm = DataManager()
lang = config.get_lang()

st.title(config.T("discover_title"))
st.caption(config.T("discover_desc"))


# ============================================================
#  数据充足性检查
# ============================================================
total_tasks = len(dm.data.get("tasks", []))
total_diary = len(dm.data.get("diary", []))

if total_tasks == 0 and total_diary == 0:
    st.markdown(
        "<div class='km-empty-state'><span class='emoji'>🔍</span>"
        "记录一周日常后，<br>AI 会在这里向你提问</div>",
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
#  1. 分析按钮
# ============================================================
st.markdown("---")

if st.button(config.T("discover_analyze"), type="primary", use_container_width=True):
    dm.set_discover_last_run()
    st.session_state["analyzing"] = True

if st.session_state.get("analyzing"):
    with st.spinner(config.T("common_loading")):
        agg = dm.aggregate_for_discover()
        api_key = dm.get_api_key()
        provider = dm.data.get("provider", "deepseek")

        result = AIClient.ask("discover", json.dumps(agg, ensure_ascii=False), api_key, provider=provider)

        if "error" in result:
            st.error(result["error"])
            st.session_state["analyzing"] = False
        else:
            insights = result.get("insights", [])
            if not insights:
                st.warning(result.get("summary", "No patterns found"))
                st.session_state["analyzing"] = False
            else:
                saved = 0
                for item in insights:
                    dm.add_insight({
                        "type": "hypothesis",
                        "title": item.get("title", ""),
                        "hypothesis": item.get("hypothesis", ""),
                        "evidence": item.get("evidence", []),
                        "confidence": item.get("confidence", 0.5),
                        "status": "pending",
                        "question": item.get("question", ""),
                        "category": item.get("category", "general"),
                    })
                    saved += 1
                st.session_state["analyzing"] = False
                st.success(config.T("discover_n_generated", n=saved))
                st.rerun()


# ============================================================
#  2. 洞察列表 — 待回答 / 已确认
# ============================================================
st.markdown("---")

pending = dm.get_insights("pending")
confirmed = dm.get_insights("confirmed")

tab_pending, tab_confirmed = st.tabs([
    config.T("discover_tab_pending", n=len(pending)),
    config.T("discover_tab_confirmed", n=len(confirmed)),
])


# ── 待回答 Tab ──
with tab_pending:
    if not pending:
        st.info(config.T("discover_no_pending"))
    else:
        for insight in pending:
            iid = insight["id"]
            confidence = insight.get("confidence", 0.5)

            # 卡片 — 使用设计系统 km-insight-card
            st.markdown(
                "<div class='km-insight-card pending'>",
                unsafe_allow_html=True,
            )

            # 标题 + 置信度
            col_head, col_conf = st.columns([3, 1])
            with col_head:
                st.markdown(f"**{insight.get('title', '')}**")
            with col_conf:
                conf_pct = int(confidence * 100)
            st.markdown(
                f"<div style='font-size:12px;color:#9CA3AF;'>"
                f"{config.T('discover_confidence')}: {conf_pct}%</div>"
                f"<div class='km-confidence-bar'>"
                f"<div class='km-confidence-fill' style='width:{conf_pct}%;'></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # 假设描述
            st.markdown(insight.get("hypothesis", ""))

            # 证据（待回答卡片）
            evidence = insight.get("evidence", [])
            if evidence:
                st.markdown(f"**{config.T('discover_evidence')}**")
                st.markdown(
                    "<ul class='km-evidence-list'>"
                    + "".join(f"<li>{e}</li>" for e in evidence)
                    + "</ul>",
                    unsafe_allow_html=True,
                )

            # AI 提问
            question = insight.get("question", "")
            if question:
                st.info(question)

            # 用户回答输入框
            user_answer = st.text_input(
                "Your answer",
                key=f"answer_{iid}",
                label_visibility="collapsed",
                placeholder=config.T("discover_answer_placeholder"),
            )

            if user_answer.strip():
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button(
                        config.T("discover_confirm"),
                        key=f"confirm_{iid}",
                        use_container_width=True,
                        type="primary",
                    ):
                        _validate_and_update(dm, iid, insight, user_answer.strip(), api_key="confirm")
                with col_no:
                    if st.button(
                        config.T("discover_deny"),
                        key=f"deny_{iid}",
                        use_container_width=True,
                    ):
                        _validate_and_update(dm, iid, insight, user_answer.strip(), api_key="refute")

            st.markdown("</div>", unsafe_allow_html=True)


# ── 已确认 Tab ──
with tab_confirmed:
    if not confirmed:
        st.info(config.T("discover_no_confirmed"))
    else:
        for insight in confirmed:
            st.markdown(
                "<div class='km-insight-card confirmed'>",
                unsafe_allow_html=True,
            )

            col_head, col_cat = st.columns([4, 1])
            with col_head:
                st.markdown(f"**{insight.get('title', '')}**")
            with col_cat:
                cat = insight.get("category", "")
                if cat:
                    st.caption(f"`{cat}`")

            st.markdown(insight.get("hypothesis", ""))

            # 用户回答
            ua = insight.get("user_answer", "")
            if ua:
                st.markdown(f"<small>{ua}</small>", unsafe_allow_html=True)

            # AI follow_up
            follow_up = insight.get("follow_up", "")
            if follow_up:
                st.success(follow_up)

            # 证据（已确认卡片）
            evidence = insight.get("evidence", [])
            if evidence:
                st.markdown(f"**{config.T('discover_evidence')}**")
                st.markdown(
                    "<ul class='km-evidence-list'>"
                    + "".join(f"<li>{e}</li>" for e in evidence)
                    + "</ul>",
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

