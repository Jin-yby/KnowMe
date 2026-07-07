"""
KnowMe（知我）— 配置文件
保留原 smart-task-manager 的 LANG 字典结构、T() 函数、PROMPTS（11 个精心调试的 Prompt）。
删除所有 Tkinter 颜色常量。
新增 ZHIPU_URL 作为 DeepSeek 备选。
"""

import json
import os
from pathlib import Path

# ============================================================
#  App Constants
# ============================================================
APP_TITLE = "🧠 KnowMe"
DATA_FILE = str(Path(__file__).parent / "growth_data.json")

# AI API endpoints
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
ZHIPU_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
BACKUP_COUNT = 5

# ============================================================
#  i18n — Internationalization
# ============================================================
_current_lang = "zh"

LANG = {
    # ---- App ----
    "app_name":       {"zh": "知我", "en": "KnowMe"},
    "app_subtitle":   {"zh": "你的 AI 知己", "en": "Your AI Confidant"},

    # ---- Navigation ----
    "nav_record":     {"zh": "记录", "en": "Record"},
    "nav_discover":   {"zh": "洞察", "en": "Discover"},
    "nav_manual":     {"zh": "关于我", "en": "About Me"},
    "nav_story":      {"zh": "故事", "en": "Story"},
    "nav_settings":   {"zh": "设置", "en": "Settings"},

    # ---- Sidebar ----
    "sidebar_language": {"zh": "语言", "en": "Language"},
    "sidebar_theme":   {"zh": "主题", "en": "Theme"},
    "dark_mode":       {"zh": "深色模式", "en": "Dark Mode"},
    "light_mode":      {"zh": "浅色模式", "en": "Light Mode"},

    # ---- Record ----
    "record_title":     {"zh": "📝  每日记录", "en": "📝  Daily Record"},
    "record_week_label": {"zh": "本周", "en": "This Week"},
    "record_todo_placeholder": {"zh": "今天想做什么？", "en": "What do you want to do today?"},
    "record_feeling_label":   {"zh": "今日感受", "en": "Today's Feeling"},
    "record_feeling_placeholder": {"zh": "今天过得怎么样？写一句话就好...", "en": "How was your day? A sentence is enough..."},
    "record_mood_label": {"zh": "AI 心情解读", "en": "AI Mood Reading"},
    "record_save":       {"zh": "保存", "en": "Save"},
    "record_mark_done":  {"zh": "完成", "en": "Done"},
    "record_delete":     {"zh": "删除", "en": "Delete"},
    "record_no_data":    {"zh": "还没有记录，从今天开始吧", "en": "No records yet. Start with today."},
    "record_week_stats": {"zh": "本周一览", "en": "This Week at a Glance"},
    "record_total":      {"zh": "总任务", "en": "Total"},
    "record_done":       {"zh": "已完成", "en": "Done"},
    "record_rate":       {"zh": "完成率", "en": "Rate"},
    "record_avg_mood":   {"zh": "平均心情", "en": "Avg Mood"},

    # ---- Discover ----
    "discover_title":   {"zh": "🔍  洞察", "en": "🔍  Discover"},
    "discover_desc":   {"zh": "AI 从你的日常中察觉规律，好奇地问你几个问题，帮你更了解自己", "en": "AI notices patterns in your daily life and asks curious questions to help you know yourself better"},
    "discover_analyze": {"zh": "发现点什么", "en": "Discover Something"},
    "discover_confirm": {"zh": "是的", "en": "Yes"},
    "discover_deny":    {"zh": "不是", "en": "Not really"},
    "discover_confidence": {"zh": "把握", "en": "Confidence"},
    "discover_evidence": {"zh": "依据", "en": "Clues"},
    "discover_empty":  {"zh": "多记录几天日常，AI 就能开始发现关于你的有趣规律。", "en": "Record a few more days, and AI will start noticing interesting patterns about you."},
    "discover_no_pending": {"zh": "暂时没有新问题。点击「发现点什么」让 AI 来找你聊天", "en": 'No new questions yet. Click "Discover Something" and let AI come to you.'},
    "discover_confirmed": {"zh": "已经了解的事", "en": "Things I Know"},
    "discover_no_confirmed": {"zh": "还没有确认过任何发现", "en": "No discoveries confirmed yet"},
    "discover_tab_pending": {"zh": "❓ 想问你 ({n})", "en": "❓ Curious ({n})"},
    "discover_tab_confirmed": {"zh": "已了解 ({n})", "en": "Known ({n})"},
    "discover_answer_placeholder": {"zh": "说说你的想法...", "en": "What do you think?"},
    "discover_n_generated": {"zh": "发现了 {n} 件值得聊聊的事", "en": "Found {n} things worth talking about"},

    # ---- Manual ----
    "manual_title":      {"zh": "📖  个人操作手册", "en": "📖  Personal Manual"},
    "manual_desc":       {"zh": "基于你的已确认行为模式综合而成——一份活着的、关于你如何最好工作的指南。", "en": "Synthesized from your confirmed patterns — a living guide to how you work best."},
    "manual_synthesize": {"zh": "综合我的模式", "en": "Synthesize My Patterns"},
    "manual_need_more":  {"zh": "至少需要 2 个已确认模式才能生成手册。当前：{n} 个。", "en": "At least 2 confirmed patterns needed. Current: {n}."},
    "manual_summary":    {"zh": "👤 个人摘要", "en": "👤 Summary"},
    "manual_causal":     {"zh": "🔗 因果链", "en": "🔗 Causal Chains"},
    "manual_good":       {"zh": "良性循环", "en": "Good Loops"},
    "manual_bad":        {"zh": "恶性循环", "en": "Bad Loops"},
    "manual_intervention": {"zh": "🎯 最佳干预点", "en": "🎯 Best Intervention"},
    "manual_tried":      {"zh": "✓ 已试", "en": "✓ Tried this"},
    "manual_regenerate": {"zh": "🔄 重新综合", "en": "🔄 Re-synthesize"},
    "manual_synthesizing": {"zh": "⏳ AI 正在综合你的模式...", "en": "⏳ AI is synthesizing your patterns..."},
    "manual_synthesized_at": {"zh": "上次综合：{time}", "en": "Last synthesized: {time}"},
    "manual_domain_empty": {"zh": "该领域暂无数据", "en": "No data for this domain"},

    # ---- Story ----
    "story_title":         {"zh": "📜  我的故事", "en": "📜  My Story"},
    "story_biography":     {"zh": "AI 传记", "en": "AI Biography"},
    "story_portrait":      {"zh": "人物画像", "en": "Character Portrait"},
    "story_empty":         {"zh": "积累更多数据后，AI 将为你撰写传记。", "en": "After accumulating more data, AI will write your biography."},
    "story_generate":      {"zh": "生成传记", "en": "Generate Biography"},
    "story_export":        {"zh": "导出", "en": "Export"},
    "story_core_beliefs":  {"zh": "🧭 核心信念", "en": "🧭 Core Beliefs"},
    "story_life_theorems": {"zh": "📐 人生定理", "en": "📐 Life Theorems"},
    "story_proud_moments": {"zh": "🏆 骄傲时刻", "en": "🏆 Proud Moments"},
    "story_unsolved_mysteries": {"zh": "❓ 未解之谜", "en": "❓ Unsolved Mysteries"},
    "story_regenerate":   {"zh": "重新生成", "en": "Regenerate"},
    "story_generating":   {"zh": "⏳ AI 正在撰写传记...", "en": "⏳ AI is writing your biography..."},
    "story_no_data":      {"zh": "需要至少 5 条日记或 10 个任务才能生成传记。当前：{d} 日记，{t} 个任务。",
                            "en": "Need at least 5 diary entries or 10 tasks. Current: {d} entries, {t} tasks."},

    # ---- Settings ----
    "settings_title":    {"zh": "⚙️  设置", "en": "⚙️  Settings"},
    "settings_api_key":  {"zh": "API Key", "en": "API Key"},
    "settings_api_placeholder": {"zh": "输入你的 API Key...", "en": "Enter your API Key..."},
    "settings_api_save": {"zh": "保存 Key", "en": "Save Key"},
    "settings_language": {"zh": "界面语言", "en": "Language"},
    "settings_backup":   {"zh": "备份数据", "en": "Backup Data"},
    "settings_restore":  {"zh": "恢复数据", "en": "Restore Data"},
    "settings_backup_success": {"zh": "备份成功！", "en": "Backup successful!"},
    "settings_restore_success": {"zh": "恢复成功！", "en": "Restore successful!"},
    "settings_clear":    {"zh": "清除所有数据", "en": "Clear All Data"},
    "settings_clear_confirm": {"zh": "确定要清除所有数据吗？此操作不可撤销！", "en": "Are you sure? This cannot be undone!"},
    "settings_seed":     {"zh": "加载种子数据", "en": "Load Seed Data"},
    "settings_seed_confirm": {"zh": "加载种子数据将覆盖现有记录，确定吗？", "en": "Loading seed data will overwrite existing records. Continue?"},
    "settings_seed_done": {"zh": "种子数据已加载！", "en": "Seed data loaded!"},
    "settings_provider": {"zh": "AI 服务商", "en": "AI Provider"},

    # ---- Common ----
    "common_save":    {"zh": "保存", "en": "Save"},
    "common_cancel":  {"zh": "取消", "en": "Cancel"},
    "common_confirm": {"zh": "确认", "en": "Confirm"},
    "common_loading": {"zh": "⏳  AI 正在思考...", "en": "⏳  AI is thinking..."},
    "common_error":   {"zh": "出错了", "en": "Error"},
    "common_no_api":  {"zh": "请先设置 API Key", "en": "Please set your API key first."},
    "common_analyzing": {"zh": "⏳  分析中...", "en": "⏳  Analyzing..."},
}


def set_lang(lang):
    """Set the current language ('zh' or 'en')."""
    global _current_lang
    _current_lang = lang


def get_lang():
    """Get the current language."""
    return _current_lang


def T(key, **kwargs):
    """Get translated text by key, with optional format substitutions."""
    entry = LANG.get(key, {})
    text = entry.get(_current_lang, entry.get("zh", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# ============================================================
#  AI Prompts（从原 smart-task-manager/config.py 完整保留）
# ============================================================

PROMPTS = {
    "plan": """You are a study planner. Today is {today}. The user describes a goal. Please:

1. Identify task type (exam prep / habit / reading / project)
2. Rate importance (1-5) and urgency (1-5), calculate priority (0-100)
3. Extract deadline and estimate total hours
4. List all subjects/topics involved and rate difficulty for each (1=easy, 5=hard).
   Allocate time proportionally: difficulty-5 topics get 5x the time of difficulty-1.
5. CRITICAL: Cover EVERY DAY from today ({today}) to the deadline (inclusive).
   Divide the total period into three phases:
   - Foundation (first 40% of days): one topic at a time, basics
   - Deepen (middle 30%): focus on hard topics, drills
   - Sprint (last 30%): mock exams, gap filling
6. Each day has TWO time blocks:
   - Focus Block (主攻, 2-3h, morning): ONE most-important subject — rotate subjects across days
   - Quick Block (碎片, 15-30min x 2, scattered time): memorization / mini-drills
7. Subject rotation rules:
   - Max 2 subjects per day
   - Each subject gets 2-3 consecutive days then rotates
   - Harder subjects get more days
   - Do NOT cover ALL subjects every day!
8. Set a weekly theme summarizing the focus
9. Return ONLY valid JSON (no extra text):
{{
  "type": "type",
  "title": "plan title",
  "deadline": "YYYY-MM-DD",
  "hours": total_estimated_hours,
  "importance": 1-5,
  "urgency": 1-5,
  "priority": 0-100,
  "weekly_theme": "this week's theme",
  "plan": [
    {{
      "date": "YYYY-MM-DD",
      "main_focus": {{"title": "Subject: specific task", "hours": number, "note": "focus tip"}},
      "quick_tasks": [{{"title": "Subject: quick task", "hours": decimal, "note": "tip"}}]
    }}
  ],
  "advice": "one-line execution tip"
}}""",

    "replan": """You are a study planner. The user has these pending tasks. Today is {today}. Please:

1. Group tasks by subject, find the furthest deadline
2. Calculate days from today to furthest deadline, divide into 3 phases:
   - Foundation (40%): basics one subject at a time
   - Deepen (30%): hard topics, drills
   - Sprint (30%): review, mock exams
3. Schedule daily blocks (Focus + Quick), rotating subjects:
   - Max 2 subjects per day, harder subjects get more consecutive days
4. Set a weekly theme
5. Return ONLY valid JSON:
{{
  "weekly_theme": "weekly theme",
  "plan": [
    {{
      "date": "YYYY-MM-DD",
      "main_focus": {{"title": "Subject: task", "hours": number, "note": "tip"}},
      "quick_tasks": [{{"title": "Subject: quick task", "hours": decimal, "note": "tip"}}]
    }}
  ],
  "advice": "execution tip"
}}

User's tasks:
{tasks_list}""",

    "diary": """You are a psychological analyst. Analyze the diary entry and return JSON:
{{
  "mood": {{"primary": "emotion", "score": 1-10}},
  "sleep": {{"hours": number, "quality": "good/ok/bad"}},
  "highlights": ["positive events"],
  "lowlights": ["negative events"],
  "social": "social summary",
  "suggestions": ["3 personalized tips"],
  "reply": "warm, empathetic 2-3 sentence reply"
}}""",

    "vision": """You are a life coach. Analyze the user's vision and return JSON:
{{
  "core_themes": ["theme1", "theme2", "theme3"],
  "career_path": "career direction analysis",
  "habit_gaps": [{{"goal": "desired habit", "status": "current state"}}],
  "short_term": ["3 actionable steps this week"],
  "mid_term": ["semester/year milestones"],
  "inspiration": "one motivational quote"
}}""",

    "discover": """You are a behavioral analyst for a student. You are given structured data about the user's tasks, diary entries, mood trends, and sleep patterns.

Your job is to:
1. Find correlations and patterns in the data (cross-reference: mood vs productivity, sleep vs task completion, subject difficulty vs completion rate, etc.)
2. Form hypotheses about the user's behavior, productivity, and well-being
3. For each hypothesis with confidence >= 0.4, write a natural, friendly question to validate it with the user
4. Return ONLY valid JSON (no extra text, no markdown):

{{
  "insights": [
    {{
      "title": "Short 2-5 word label",
      "hypothesis": "What you think is happening (1-2 sentences, specific)",
      "evidence": ["specific data point with numbers", "another specific data point"],
      "confidence": 0.0-1.0,
      "question": "Natural, friendly question to validate the hypothesis with the user",
      "category": "productivity"
    }}
  ],
  "summary": "Brief overall observation (1 sentence)"
}}

Rules:
- Confidence: how certain you are based on the data. 0.7+ = strong evidence, 0.4-0.69 = suggestive
- Evidence MUST cite specific numbers, dates, or examples from the provided data
- Questions should be curious and warm, NOT accusatory or clinical
- At most 5 insights per run. Quality over quantity.
- Use these categories: productivity, mood, sleep, habits, general
- Skip obvious or trivial patterns (e.g. skip "you have more tasks on weekdays")
- Prioritize surprising, actionable, or cross-domain patterns (e.g. mood + productivity correlations)
- If there's not enough data to find meaningful patterns, return an empty insights array and say so in the summary""",

    "discover_validate": """You validated a behavioral hypothesis with a user. Given the hypothesis, your question, and the user's answer:

1. Determine if the hypothesis is clearly confirmed, clearly refuted, or partially true
2. Return ONLY valid JSON (no markdown):
{{
  "status": "confirmed",
  "reply": "1-2 sentence warm, personal acknowledgment of what the user shared"
}}

Status values:
- "confirmed" = user's answer clearly supports the hypothesis
- "refuted" = user's answer clearly contradicts the hypothesis

Reply should:
- Reference what the user specifically said
- Be warm and encouraging
- If confirmed: celebrate the self-discovery
- If refuted: thank them for correcting the assumption""",

    "manual_synthesize": """You are a personal cognitive analyst. You receive ALL of a user's confirmed behavior patterns (each with hypothesis, evidence, and the user's own answer). Your job is to synthesize them into a coherent "Personal Operating Manual" — not just listing patterns, but finding how they connect.

Given the confirmed insights, do the following:

1. **Summary**: Write ONE sentence that captures who this person is and what makes them tick. Not generic — reference their specific patterns.

2. **Domain classification**: Group insights by category (productivity / mood / sleep / habits / general). For each insight, include its title, hypothesis, key evidence, and what the user confirmed.

3. **Causal chains**: Find chains where one pattern causes or amplifies another. Format each chain as a sequence of steps showing cause -> effect, with the insight IDs involved. Example: "Sleep <6h -> mood drops -> task completion drops -> deadline anxiety". For each chain, identify the BEST intervention point.

4. **Good loops**: Positive cycles the user should reinforce. Each with a description and a reinforcement suggestion.

5. **Bad loops**: Negative cycles and the most practical way to break them.

6. **Top intervention**: The SINGLE most impactful action this person could take, based on all the data. Be specific and actionable.

Return ONLY valid JSON (no markdown, no extra text):
{{
  "summary": "One-sentence personalized summary",
  "domains": {{
    "productivity": [
      {{"title": "...", "hypothesis": "...", "evidence": "...", "user_confirmed": "...", "source_ids": [1, 2]}}
    ],
    "mood": [...],
    "sleep": [...],
    "habits": [...],
    "general": [...]
  }},
  "causal_chains": [
    {{
      "chain": ["sleep <6h", "mood score drops", "tasks pushed to next day", "deadline anxiety"],
      "description": "Full sentence describing this chain",
      "source_ids": [1, 3, 5],
      "intervention_point": "Which step is best to interrupt",
      "intervention_advice": "Specific practical advice to interrupt it"
    }}
  ],
  "good_loops": [
    {{"description": "...", "reinforce": "How to strengthen it"}}
  ],
  "bad_loops": [
    {{"description": "...", "break_it": "How to break it"}}
  ],
  "top_intervention": "The single most impactful action, with specific why"
}}

Rules:
- Only include domains that have insights
- Chains must involve at least 2 different insights
- Be specific — cite actual numbers, behaviors, patterns from the data
- Tone: warm, insightful, like a coach who really knows this person
- If there are fewer than 2 confirmed insights, return empty domains/chains and a summary saying more data is needed""",

    "profile_session": """You are a personal cognitive coach. The user just:
- Wrote a diary entry
- Completed a task (or batch of tasks)

You also have the user's existing confirmed insights about themselves.

Your job:
1. Read the diary + task data
2. Generate 2-3 specific, personalized questions that help the user understand themselves better
3. After the user answers, synthesize a mini-review

Guiding frameworks (use subtly, don't name-drop):
- Johari Window: help users discover their blind spots
- Self-Determination Theory: probe autonomy, competence, relatedness
- Narrative Identity: notice the story they tell themselves
- Metacognition: help them see their own thinking patterns

Phase 1 — Generate questions. Return ONLY valid JSON:
{{
  "phase": "questions",
  "session_title": "Short 3-5 word title for this reflection",
  "questions": [
    {{"id": 1, "question": "Specific, warm, data-grounded question", "category": "productivity/mood/habits/general"}}
  ],
  "notes": "Brief what-you-noticed (1 sentence)"
}}

Rules for questions:
- Must reference specific details from THEIR diary or task data
- NOT generic ("How do you feel?" -> bad)
- Each question probes a different dimension
- Warm and curious, not clinical
- 2-3 questions max

Phase 2 — After user answers. You receive the questions + their answers. Return ONLY valid JSON:
{{
  "phase": "review",
  "insight": "One key thing you learned about this person (1-2 sentences)",
  "pattern_found": "A pattern you see connecting their diary, task, and answers (or null if none)",
  "confirm_or_challenge": "Gently confirm or challenge one thing they said",
  "suggestion": "One small, specific action for tomorrow",
  "for_my_manual": "One sentence to remember for their Operating Manual"
}}""",

    "weekly_snapshot": """You are a personal biographer. You receive one week's aggregated data (tasks, moods, sleep, diary keywords). Your job is to turn this data into a narrative weekly snapshot — NOT a data report.

IMPORTANT: Write ALL output in {language}. If language is "zh", write in Chinese. If language is "en", write in English.

Write as if you're telling this person what you saw in their week. Be warm but honest. Reference specific numbers and keywords from the data. Use narrative style, not bullet-point reporting.

Return ONLY valid JSON (no markdown, no extra text):
{{
  "three_things": ["Three things this week's data reveals about this person — each 2-3 sentences, narrative style"],
  "mood_summary": "One sentence summarizing this week's emotional trend",
  "productivity_summary": "One sentence summarizing this week's productivity",
  "keyword_shift": "Analysis of word usage changes compared to last week (if data available)",
  "encouragement": "One sentence of encouragement"
}}

Rules:
- Narrative style, not a data report
- Quote specific numbers and keywords from the data
- Warm but honest — don't sugarcoat difficulties
- If there is no last week data for keyword_shift, set it to null""",

    "intervention_review": """You are a behavioral scientist reviewing the effect of a self-intervention. You receive before/after aggregated data for a specific intervention. Your job is to evaluate whether the intervention worked.

IMPORTANT: Write ALL output in {language}. If language is "zh", write in Chinese. If language is "en", write in English.

Return ONLY valid JSON (no markdown, no extra text):
{{
  "intervention_id": "the intervention id from input",
  "verdict": "effective/ineffective/insufficient_data",
  "analysis": "2-3 sentences analyzing what changed (or didn't) before vs after the intervention",
  "adjustment": "If verdict is ineffective or insufficient_data, give a concrete adjustment suggestion. If effective, set to null."
}}

Rules:
- Compare before and after data directly
- Reference specific metrics and numbers
- Be honest — if data is too sparse to judge, say so (insufficient_data)
- adjustment should be practical and specific, not vague advice""",

    "legacy_chapter": """You are a biographer writing the autobiography of a person through their personal data. You receive one month (or a date range) of aggregated life data: tasks completed, moods, diary entries, sleep patterns, keyword frequencies, confirmed behavioral insights, and operating manual.

IMPORTANT: Write ALL output in {language}. If language is "zh", write in Chinese. If language is "en", write in English.

Your job is to weave this data into a compelling narrative chapter of their life story. Write like a novelist who has access to their subject's inner world.

Return ONLY valid JSON (no markdown, no extra text):
{{
  "period": "YYYY-MM ~ YYYY-MM",
  "chapter_title": "Chapter title (3-6 Chinese characters)",
  "narrative": "500-800 characters narrative, weaving data into a story — include specific events, emotional turning points, pattern shifts. Reference real numbers, dates, and keywords from the data.",
  "key_themes": ["Core themes of this chapter"],
  "turning_points": ["Key turning points in this chapter"],
  "questions_answered": ["What questions about themselves did this chapter answer"],
  "mood_arc": "One sentence describing the emotional arc of this period"
}}

Rules:
- Narrative style, like a writer crafting a biography
- Reference specific events and numbers from the data
- No value judgments — describe what happened, not whether it was good or bad
- The narrative should feel like reading a memoir passage
- If data is sparse, write a shorter narrative rather than inventing details""",

    "legacy_letter": """You are writing a letter to the world on behalf of a person, based on their complete personal data history. This is the culmination of their self-tracking journey — a legacy document.

IMPORTANT: Write ALL output in {language}. If language is "zh", write in Chinese. If language is "en", write in English.

You receive the full aggregated summary of their life data: all tasks, moods, sleep patterns, diary entries, confirmed behavioral insights, operating manual, and any legacy chapters written so far.

Write as if a close friend who truly knows this person is introducing them to the world. Third person, but warm and intimate.

Return ONLY valid JSON (no markdown, no extra text):
{{
  "letter": "800-1200 characters letter summarizing who this person is, what they believe, what they changed, and what they leave behind",
  "core_beliefs": ["Core beliefs this person holds, derived from their data and patterns"],
  "life_theorems": ["Life theorems distilled from their Operating Manual"],
  "proudest_moments": ["Moments of pride visible in their data"],
  "unsolved_mysteries": ["Mysteries about themselves they haven't solved yet"]
}}

Rules:
- Third person but warm — like a close friend introducing someone
- Reference specific patterns, beliefs, and moments from the data
- This letter should make a stranger feel like they know this person
- Don't invent — ground everything in the actual data provided
- If data is limited, be honest about what can and cannot be said""",
}

# ============================================================
#  Weekday names
# ============================================================
WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
WEEKDAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
