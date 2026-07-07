"""
手册页 — AI 综合已确认模式，生成个人操作手册
"""

import json
from datetime import datetime
import streamlit as st
from services import DataManager, AIClient
import config


# ── 辅助函数 ──

DOMAIN_ICONS = {
    "productivity": "▸",
    "mood": "▸",
    "sleep": "▸",
    "habits": "▸",
    "general": "▸",
}

DOMAIN_NAMES = {
    "zh": {"productivity": "效率", "mood": "情绪", "sleep": "睡眠", "habits": "习惯", "general": "综合"},
    "en": {"productivity": "Productivity", "mood": "Mood", "sleep": "Sleep", "habits": "Habits", "general": "General"},
}


def _try_intervention(dm, insight_id):
    """标记一个干预点为已尝试。"""
    dm.mark_intervention_tried(insight_id)
    st.success(config.T("manual_tried"))
    st.rerun()


# ── 初始化 ──
dm = DataManager()
lang = config.get_lang()

st.title(config.T("manual_title"))
st.caption(config.T("manual_desc"))

confirmed_count = dm.get_confirmed_insight_count()

# ── 数据充足性检查 ──
if confirmed_count < 2:
    st.markdown(
        "<div class='km-empty-state'><span class='emoji'>📖</span>"
        f"去洞察页确认 2 个模式，<br>然后回来解锁你的个人手册</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ── 获取现有手册 ──
manual = dm.get_manual()
has_manual = manual is not None
needs_update = dm.needs_resynthesis()

st.divider()

# ── 综合按钮 ──
if has_manual:
    # 已有手册：显示"重新综合" + 上次综合时间
    last_time = manual.get("last_synthesized", "")
    if last_time:
        st.caption(config.T("manual_synthesized_at", time=last_time))

    if needs_update:
        btn_label = config.T("manual_synthesize")
    else:
        btn_label = config.T("manual_regenerate")
else:
    btn_label = config.T("manual_synthesize")

if st.button(btn_label, type="primary", use_container_width=True):
    st.session_state["synthesizing"] = True

if st.session_state.get("synthesizing"):
    with st.spinner(config.T("manual_synthesizing")):
        confirmed = dm.get_insights("confirmed")
        provider = dm.data.get("provider", "deepseek")
        api_key = dm.get_api_key()

        prompt = json.dumps([
            {
                "id": i.get("id"),
                "title": i.get("title", ""),
                "hypothesis": i.get("hypothesis", ""),
                "evidence": i.get("evidence", []),
                "user_confirmed": i.get("user_answer", ""),
                "category": i.get("category", "general"),
            }
            for i in confirmed
        ], ensure_ascii=False)

        result = AIClient.ask("manual_synthesize", prompt, api_key, provider=provider)

        st.session_state["synthesizing"] = False

        if "error" in result:
            st.error(result["error"])
        else:
            dm.set_manual(result)
            st.rerun()

# ── 重新读取手册（可能刚刚更新） ──
manual = dm.get_manual()
if not manual:
    st.stop()

st.divider()

# ============================================================
#  展示手册
# ============================================================

# ── 1. 个人摘要（紫色左边框卡片） ──
summary = manual.get("summary", "")
if summary:
    st.markdown(
        "<div class='km-card' style='border-left:3px solid #7C5EE0;'>"
        f"<h4>{config.T('manual_summary')}</h4>"
        f"<p>{summary}</p>"
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── 2. 领域分组（st.expander） ──
domains = manual.get("domains", {})
if domains:
    domain_names = DOMAIN_NAMES.get(lang, DOMAIN_NAMES["zh"])
    for domain_key, items in domains.items():
        if not items:
            continue
        icon = DOMAIN_ICONS.get(domain_key, "📌")
        name = domain_names.get(domain_key, domain_key)

        with st.expander(f"{name} ({len(items)})"):
            for item in items:
                title = item.get("title", "")
                hypothesis = item.get("hypothesis", "")
                evidence = item.get("evidence", "")
                user_confirmed = item.get("user_confirmed", "")

                st.markdown(
                    "<div class='km-card'>"
                    f"<strong>{title}</strong><br>"
                    f"<span style='color:#6B7280;'>{hypothesis}</span>"
                    f"{'<br><small style=color:#6B7280>' + user_confirmed + '</small>' if user_confirmed else ''}"
                    "</div>",
                    unsafe_allow_html=True,
                )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── 3. 因果链 ──
chains = manual.get("causal_chains", [])
if chains:
    st.markdown(f"#### {config.T('manual_causal')}")
    for chain in chains:
        steps = chain.get("chain", [])
        desc = chain.get("description", "")
        intervention = chain.get("intervention_advice", "")

        steps_html = " → ".join(f"<small>{s}</small>" for s in steps)
        st.markdown(
            "<div class='km-card'>"
            f"<div style='color:#6B7280;margin-bottom:8px;'>{steps_html}</div>"
            f"<p>{desc}</p>"
            f"{'<div style=background:#F3F0FF;border-radius:6px;padding:8px 12px;margin-top:8px;font-size:13px;color:#7C5EE0>' + intervention + '</div>' if intervention else ''}"
            "</div>",
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── 4. 良性 / 恶性循环（并排） ──
good_loops = manual.get("good_loops", [])
bad_loops = manual.get("bad_loops", [])

if good_loops or bad_loops:
    col_good, col_bad = st.columns(2)

    with col_good:
        st.markdown(f"#### {config.T('manual_good')}")
        for loop in good_loops:
            desc = loop.get("description", "")
            reinforce = loop.get("reinforce", "")
            st.markdown(
                "<div class='km-card' style='border-left:3px solid #7C5EE0;'>"
                f"<p>{desc}</p>"
                f"{'<small style=color:#6B7280>' + reinforce + '</small>' if reinforce else ''}"
                "</div>",
                unsafe_allow_html=True,
            )

    with col_bad:
        st.markdown(f"#### {config.T('manual_bad')}")
        for loop in bad_loops:
            desc = loop.get("description", "")
            break_it = loop.get("break_it", "")
            st.markdown(
                "<div class='km-card' style='border-left:3px solid #D1D5DB;'>"
                f"<p>{desc}</p>"
                f"{'<small style=color:#6B7280>' + break_it + '</small>' if break_it else ''}"
                "</div>",
                unsafe_allow_html=True,
            )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── 5. 最佳干预点（紫色高亮卡片） ──
top = manual.get("top_intervention", "")
if top:
    st.markdown(
        "<div class='km-card' style='border:1px solid #7C5EE0;background:#F3F0FF;'>"
        f"<h4>{config.T('manual_intervention')}</h4>"
        f"<p style='font-size:15px;'>{top}</p>"
        "</div>",
        unsafe_allow_html=True,
    )
