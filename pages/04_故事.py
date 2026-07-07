"""
故事页 — AI 生成用户传记 + 人物画像
"""

import json
from datetime import datetime
import streamlit as st
from services import DataManager, AIClient
import config


# ── 初始化 ──
dm = DataManager()
lang = config.get_lang()

st.title(config.T("story_title"))

# ── 数据充足性检查 ──
total_diary = len(dm.data.get("diary", []))
total_tasks = len(dm.data.get("tasks", []))

if total_diary < 5 and total_tasks < 10:
    st.markdown(
        "<div class='km-empty-state'><span class='emoji'>📜</span>"
        f"多记录几天日常，<br>AI 就能为你撰写传记</div>",
        unsafe_allow_html=True,
    )
    st.stop()

st.divider()

# ── 检查已有传记 ──
chapters = dm.get_legacy_chapters()
has_biography = len(chapters) > 0

# ── 生成按钮 ──
btn_label = config.T("story_regenerate") if has_biography else config.T("story_generate")

if st.button(btn_label, type="primary", use_container_width=True):
    st.session_state["generating_story"] = True

if st.session_state.get("generating_story"):
    with st.spinner(config.T("story_generating")):
        all_data = dm.get_all_legacy_data()
        provider = dm.data.get("provider", "deepseek")
        api_key = dm.get_api_key()

        prompt = json.dumps(all_data, ensure_ascii=False)
        result = AIClient.ask("legacy_letter", prompt, api_key, provider=provider)

        st.session_state["generating_story"] = False

        if "error" in result:
            st.error(result["error"])
        else:
            letter = result.get("letter", "")
            portrait = result.get("portrait", {})

            # 保存传记和画像
            dm.data["biography"] = letter
            dm.data["portrait"] = portrait
            dm.save()

            # 同时保存为 legacy_chapter
            today_str = datetime.now().strftime("%Y-%m-%d")
            chapter = {
                "period": f"~ {today_str}",
                "chapter_title": result.get("core_beliefs", ["KnowMe"])[0] if result.get("core_beliefs") else "My Story",
                "narrative": letter,
                "key_themes": result.get("core_beliefs", []),
                "turning_points": [],
                "questions_answered": [],
                "mood_arc": "",
            }
            dm.save_legacy_chapter(chapter)
            st.rerun()

# ── 读取传记 ──
biography = dm.data.get("biography", "")
portrait = dm.data.get("portrait", {})

if not biography:
    st.info(config.T("story_empty"))
    st.stop()

st.divider()

# ============================================================
#  1. 传记正文（大段文字，衬线风格）
# ============================================================
st.markdown(f"#### {config.T('story_biography')}")

st.markdown(
    "<div class='km-card' style='font-size:15px;"
    "line-height:1.8;color:#1A1A1A;'>"
    f"{biography}"
    "</div>",
    unsafe_allow_html=True,
)

st.divider()

# ============================================================
#  2. 人物画像
# ============================================================
st.markdown(f"#### {config.T('story_portrait')}")

if not portrait:
    st.caption(config.T("story_empty"))
    st.stop()

# 画像四象限布局
col_beliefs, col_theorems = st.columns(2)
col_proud, col_mysteries = st.columns(2)

with col_beliefs:
    beliefs = portrait.get("core_beliefs", [])
    st.markdown(f"**{config.T('story_core_beliefs')}**")
    if beliefs:
        for b in beliefs:
            st.markdown(
                "<div class='km-card' style='border-left:3px solid #7C5EE0;padding:12px 16px;'>"
                f"<span style='font-size:13px;'>{b}</span>"
                "</div>",
                unsafe_allow_html=True,
            )

with col_theorems:
    theorems = portrait.get("life_theorems", [])
    st.markdown(f"**{config.T('story_life_theorems')}**")
    if theorems:
        for t in theorems:
            st.markdown(
                "<div class='km-card' style='border-left:3px solid #7C5EE0;padding:12px 16px;'>"
                f"<span style='font-size:13px;'>{t}</span>"
                "</div>",
                unsafe_allow_html=True,
            )

with col_proud:
    proud = portrait.get("proudest_moments", [])
    st.markdown(f"**{config.T('story_proud_moments')}**")
    if proud:
        for p in proud:
            st.markdown(
                "<div class='km-card' style='border-left:3px solid #7C5EE0;padding:12px 16px;'>"
                f"<span style='font-size:13px;'>{p}</span>"
                "</div>",
                unsafe_allow_html=True,
            )

with col_mysteries:
    mysteries = portrait.get("unsolved_mysteries", [])
    st.markdown(f"**{config.T('story_unsolved_mysteries')}**")
    if mysteries:
        for m in mysteries:
            st.markdown(
                "<div class='km-card' style='border-left:3px solid #D1D5DB;padding:12px 16px;'>"
                f"<span style='font-size:13px;'>{m}</span>"
                "</div>",
                unsafe_allow_html=True,
            )
