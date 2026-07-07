"""
设置页 — API Key、AI 服务商、备份恢复、种子数据、清除数据
"""

import streamlit as st
import json
from services import DataManager, generate_seed_data
import config


# ── 初始化 DataManager ──
dm = DataManager()

st.title(config.T("settings_title"))


# ============================================================
#  1. API Key 设置
# ============================================================
st.markdown("---")
st.subheader("🔑 " + config.T("settings_api_key"))

current_key = dm.get_api_key()
masked_key = current_key[:6] + "****" if len(current_key) > 6 else ("****" if current_key else "")

col1, col2 = st.columns([4, 1])
with col1:
    new_key = st.text_input(
        config.T("settings_api_placeholder"),
        value=current_key,
        type="password",
        key="api_key_input",
        label_visibility="collapsed",
    )
with col2:
    st.write("")  # 对齐按钮
    st.write("")
    if st.button(config.T("settings_api_save"), use_container_width=True):
        if new_key.strip():
            dm.set_api_key(new_key.strip())
            st.success("Key saved")
            st.rerun()

if masked_key != "****" and masked_key != "":
    st.caption(f"当前: `{masked_key}`")


# ============================================================
#  2. AI 服务商选择
# ============================================================
st.subheader("🤖 " + config.T("settings_provider"))
provider_options = {"DeepSeek": "deepseek", "智谱 GLM (Zhipu)": "zhipu"}
current_provider = dm.data.get("provider", "deepseek")
provider_labels = list(provider_options.keys())
current_label = [k for k, v in provider_options.items() if v == current_provider][0]

selected_label = st.radio(
    "Provider",
    options=provider_labels,
    index=provider_labels.index(current_label),
    horizontal=True,
)
selected_provider = provider_options[selected_label]

if selected_provider != current_provider:
    dm.data["provider"] = selected_provider
    dm.save()
    st.success(f"Provider → {selected_label}")


# ============================================================
#  3. 加载种子数据
# ============================================================
st.markdown("---")
st.subheader("🌱 " + config.T("settings_seed"))

if st.button(config.T("settings_seed"), use_container_width=True, type="secondary"):
    st.session_state["seed_confirm"] = True

if st.session_state.get("seed_confirm"):
    st.warning(config.T("settings_seed_confirm"))
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(config.T("common_confirm"), use_container_width=True, type="primary"):
            seed_data = generate_seed_data()
            dm.data = seed_data
            dm.save()
            st.session_state["seed_confirm"] = False
            st.success(config.T("settings_seed_done"))
            st.rerun()
    with col_b:
        if st.button(config.T("common_cancel"), use_container_width=True):
            st.session_state["seed_confirm"] = False
            st.rerun()


# ============================================================
#  4. 数据备份 / 恢复
# ============================================================
st.markdown("---")
st.subheader("💾 " + config.T("settings_backup") + " · " + config.T("settings_restore"))

# 备份按钮
if st.button(config.T("settings_backup"), use_container_width=True, type="secondary"):
    dm.save()  # save() 会自动轮转备份
    st.success(config.T("settings_backup_success"))

# 备份列表
backups = dm.list_backups()
if backups:
    st.caption(f"共 {len(backups)} 个备份（最多保留 {config.BACKUP_COUNT} 个）")
    for idx in sorted(backups.keys()):
        info = backups[idx]
        size_kb = info["size"] / 1024
        col_idx, col_meta, col_btn = st.columns([1, 3, 1])
        with col_idx:
            st.markdown(f"**#{idx}**")
        with col_meta:
            st.caption(f"{info['mtime']}  ·  {size_kb:.1f} KB")
        with col_btn:
            if st.button(config.T("settings_restore"), key=f"restore_{idx}"):
                if dm.restore_from_backup(idx):
                    st.success(config.T("settings_restore_success"))
                    st.rerun()
                else:
                    st.error("恢复失败")
else:
    st.caption("暂无备份")


# ============================================================
#  5. 清除所有数据（危险操作）
# ============================================================
st.markdown("---")
st.subheader("🗑 " + config.T("settings_clear"))

if st.button(config.T("settings_clear"), use_container_width=True, type="secondary"):
    st.session_state["clear_confirm"] = True

if st.session_state.get("clear_confirm"):
    st.error(config.T("settings_clear_confirm"))
    col_x, col_y = st.columns(2)
    with col_x:
        if st.button(config.T("common_confirm"), use_container_width=True, type="primary"):
            # 重置为空数据
            dm.data = dm._load.__wrapped__(dm) if hasattr(dm._load, '__wrapped__') else {
                "tasks": [], "next_id": 1, "diary": [], "visions": [],
                "insights": [], "discover_last_run": None, "manual": None,
                "api_key": "", "provider": "deepseek", "language": "zh",
                "weekly_snapshots": [], "reflect_sessions": [], "legacy_chapters": [],
                "insight_viewed_dates": {}, "biography": "", "portrait": {},
            }
            dm.save()
            st.session_state["clear_confirm"] = False
            st.success("所有数据已清除")
            st.rerun()
    with col_y:
        if st.button(config.T("common_cancel"), use_container_width=True):
            st.session_state["clear_confirm"] = False
            st.rerun()
