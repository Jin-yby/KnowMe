# 🧠 KnowMe — AI 自我认知引擎

> 你的数据是代码，AI 是编译器，输出的是你从未读过的「自传」。

---

## ⚡ 认知链路

```
📝 记录日常  →  🔍 AI 发现模式  →  📖 综合个人手册  →  📜 生成传记
  tasks+diary    cross-domain       causal chains        narrative
                 pattern detection   intervention        biography
```

传统工具帮你做事。KnowMe 帮你 **读自己**。

---

## ✨ 功能矩阵

### 📅 每日记录

| 能力 | 说明 |
|------|------|
| 周历视图 | 7 天横向排列 · 今日紫色高亮 · 任务预览 |
| TodoList | checkbox 切换 · 一键删除 · 数据持久化 |
| 日记管理 | 每日感受输入 · AI 实时解析情绪/睡眠/关键词 |
| 周统计面板 | 任务完成率 · 平均情绪分数 · 实时 metric |

### 🔍 行为洞察

| 能力 | 说明 |
|------|------|
| 模式引擎 | 聚合全量数据 · 跨维度交叉分析（情绪 vs 效率 · 睡眠 vs 完成率） |
| 假设验证 | AI 提问 → 用户回答 → AI 判断 confirmed / refuted |
| 置信度可视化 | 紫色进度条 · 百分比精确到个位 |
| 证据溯源 | 每条假设附带具体数据点 · 来源可追溯 |

### 📖 个人手册

| 能力 | 说明 |
|------|------|
| 摘要生成 | 一句话概括你的行为画像 |
| 因果链 | 识别深层链路：`sleep <6h → mood ↓ → tasks → deadline anxiety` |
| 循环识别 | 良性循环（reinforce）/ 恶性循环（break it） |
| 干预推荐 | 基于全量数据给出 #1 最高 ROI 行动建议 |

### 📜 我的故事

| 能力 | 说明 |
|------|------|
| AI 传记 | 全量数据叙事性传记 · 衬线排版 · 800-1200 字 |
| 人物画像 | 核心信念 🟢 · 人生定理 🟣 · 骄傲时刻 🟠 · 未解之谜 ⚪ |

### ⚙️ 系统层

| 能力 | 说明 |
|------|------|
| 双 AI 引擎 | DeepSeek（主） / 智谱 GLM-4-Flash（备） · 一键切换 |
| i18n | 80+ 翻译键 · 中英双语实时切换 |
| 种子数据 | 2 周模拟数据一键注入 · 演示/评测零成本 |
| 备份系统 | 自动轮转 5 份快照 · 手动恢复 · 断点回溯 |

---

## 🏗️ 架构

| 层级 | 技术 | 说明 |
|------|------|------|
| Interface | **Streamlit** | 标准多页面架构 · 5 个独立 page |
| AI Engine | **DeepSeek / 智谱 GLM** | 11 个 Prompt 模板 · JSON 结构化输出 |
| Data | **Local JSON** | 自动备份轮转 · 零网络依赖 |
| Design | **Notion-minimal** | Inter 字体 · CSS 变量体系 · km-* 组件类 |
| i18n | **dict-based** | 80+ key · zh/en 双语 · T() 函数 |

```
KnowMe/
├── main.py              # 入口 + 全局 CSS（~350 行设计系统）
├── config.py            # LANG[80+] + PROMPTS[11] + CONSTANTS
├── services.py          # AIClient + DataManager + seed generator
├── pages/
│   ├── 01_记录.py        # 周历 · TodoList · 日记 · 情绪分析
│   ├── 02_洞察.py        # 模式发现 · 假设验证 · 置信度条
│   ├── 03_手册.py        # 因果链 · 循环 · 干预点
│   ├── 04_故事.py        # 传记 · 人物画像
│   └── 05_设置.py        # API Key · provider · backup
├── .gitignore
└── requirements.txt
```

---

## 🚀 启动

```bash
pip install streamlit requests
streamlit run main.py
# → 设置页 → API Key → 种子数据 → 全链路
```

---

## 🎨 Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#FFFFFF` | 页面底色 |
| `--accent` | `#7C5EE0` | 品牌紫 · 主按钮 · 今日高亮 |
| `--success` | `#10B981` | 完成态 · 确认洞察 |
| `--warning` | `#F59E0B` | 待办 · 待验证洞察 |
| `--border` | `#EBEBEB` | 卡片边框 1px · 分割线 |
| `--text` | `#1A1A1A` / `#6B7280` / `#9CA3AF` | 主 / 次 / 辅三级文字 |
| `--font` | Inter 400/500/600 | Notion 同款 · Google Fonts CDN |
| `--radius` | 8px / 6px | 卡片 / 按钮 |
| `--transition` | 0.15s ease | hover 过渡 |

**CSS 组件库**：`.km-card` · `.km-task-row` · `.km-task-dot` · `.km-insight-card` · `.km-confidence-bar` · `.km-evidence-list` · `.km-empty-state`

---

## 📊 数据安全

| 项目 | 策略 |
|------|------|
| 存储 | 本地 `growth_data.json` · 零云端传输 |
| 备份 | 自动轮转 5 份 `.backup.{n}.json` |
| API Key | 仅本地明文 · 不上传 · 不日志 |
