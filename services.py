"""
KnowMe（知我）— Backend Services
保留原 smart-task-manager/services.py 的 AIClient + 完整 DataManager。
支持 DeepSeek（默认）+ 智谱（备选）双 AI 服务商。
新增 generate_seed_data() — 2 周模拟数据，供评委一键体验。
"""

import json
import os
import re
import shutil
import requests
from datetime import datetime, timedelta

from config import DATA_FILE, DEEPSEEK_URL, ZHIPU_URL, PROMPTS, BACKUP_COUNT


# ============================================================
#  AI Client — 支持 DeepSeek（主）+ 智谱（备）
# ============================================================
class AIClient:
    """Multi-provider AI client: DeepSeek (default) + Zhipu (fallback)."""

    @staticmethod
    def get_api_key():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    key = data.get("api_key", "")
                    if key:
                        return key
            except Exception:
                pass
        return None

    @staticmethod
    def ask(prompt_type, user_text, api_key, system_prompt=None, provider="deepseek"):
        """
        调用 AI API。
        Args:
            prompt_type: PROMPTS 字典的 key（如 "diary", "discover"）
            user_text: 用户输入文本
            api_key: API 密钥
            system_prompt: 可选覆盖系统提示
            provider: "deepseek"（默认）或 "zhipu"
        """
        if not api_key:
            return {"error": "Please set your API Key first"}

        sp = system_prompt or PROMPTS.get(prompt_type, PROMPTS["diary"])

        # 根据服务商选择 URL 和模型
        if provider == "zhipu":
            url = ZHIPU_URL
            model = "glm-4-flash"
        else:
            url = DEEPSEEK_URL
            model = "deepseek-chat"

        try:
            resp = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": sp},
                        {"role": "user", "content": user_text},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                timeout=30,
            )
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            content = content.strip()
            if content.startswith("```"):
                content = re.sub(r"^```\w*\n?", "", content)
                content = re.sub(r"\n?```$", "", content)
            return json.loads(content)
        except requests.exceptions.Timeout:
            return {"error": "Request timeout — check network"}
        except requests.exceptions.ConnectionError:
            return {"error": f"Cannot connect to {'DeepSeek' if provider == 'deepseek' else 'Zhipu'} — check network"}
        except json.JSONDecodeError:
            return {"error": f"AI response format error: {content[:200]}..."}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}


# ============================================================
#  Data Manager — 完整保留原 CRUD + 聚合分析 + 备份恢复
# ============================================================
class DataManager:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        defaults = {"importance": 3, "urgency": 3, "priority": 50, "task_type": "normal",
                    "weekly_theme": "", "actual_minutes": 0}
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for t in data.get("tasks", []):
                    for k, v in defaults.items():
                        if k not in t:
                            t[k] = v
                # Backward-compat: ensure new fields exist
                for field, default in [
                    ("insights", []), ("discover_last_run", None), ("manual", None),
                    ("weekly_snapshots", []), ("reflect_sessions", []), ("legacy_chapters", []),
                    ("insight_viewed_dates", {}),
                    ("biography", ""), ("portrait", {}),
                    ("provider", "deepseek"), ("language", "zh"),
                ]:
                    if field not in data:
                        data[field] = default
                return data
            except Exception:
                pass
        return {"tasks": [], "next_id": 1, "diary": [], "visions": [],
                "insights": [], "discover_last_run": None, "manual": None,
                "api_key": "", "provider": "deepseek", "language": "zh",
                "weekly_snapshots": [], "reflect_sessions": [], "legacy_chapters": [],
                "insight_viewed_dates": {}, "biography": "", "portrait": {}}

    def save(self):
        self._rotate_backups()
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def set_api_key(self, key):
        self.data["api_key"] = key
        self.save()

    def get_api_key(self):
        return self.data.get("api_key", "")

    # ── Backup / Restore ──────────────────────────────

    def _backup_pattern(self):
        base = os.path.splitext(self.filename)[0]
        return f"{base}.backup.*.json"

    def list_backups(self):
        """Return {index: {path, size, mtime}} for existing backup files."""
        base = os.path.splitext(self.filename)[0]
        results = {}
        for i in range(1, BACKUP_COUNT + 1):
            path = f"{base}.backup.{i}.json"
            if os.path.exists(path):
                stat = os.stat(path)
                results[i] = {
                    "path": path,
                    "size": stat.st_size,
                    "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                }
        return results

    def _rotate_backups(self):
        """Rotate backup files before each save. backup.1 is always newest."""
        if not os.path.exists(self.filename):
            return

        base = os.path.splitext(self.filename)[0]
        backups = self.list_backups()

        if len(backups) >= BACKUP_COUNT:
            oldest = max(backups.keys())
            oldest_path = backups[oldest]["path"]
            if os.path.exists(oldest_path):
                os.remove(oldest_path)

        for idx in sorted(backups.keys(), reverse=True):
            old_path = backups[idx]["path"]
            new_path = f"{base}.backup.{idx + 1}.json"
            if os.path.exists(old_path):
                shutil.move(old_path, new_path)

        backup_path = f"{base}.backup.1.json"
        shutil.copy2(self.filename, backup_path)

    def restore_from_backup(self, backup_index):
        """Restore data from a backup file by index. Returns True on success."""
        base = os.path.splitext(self.filename)[0]
        backup_path = f"{base}.backup.{backup_index}.json"
        if not os.path.exists(backup_path):
            return False

        with open(backup_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        defaults = {"importance": 3, "urgency": 3, "priority": 50, "task_type": "normal",
                    "weekly_theme": "", "actual_minutes": 0}
        for t in data.get("tasks", []):
            for k, v in defaults.items():
                if k not in t:
                    t[k] = v
        _compat = {"insights": [], "discover_last_run": None, "manual": None,
                  "weekly_snapshots": [], "reflect_sessions": [], "legacy_chapters": [],
                  "insight_viewed_dates": {}, "biography": "", "portrait": {},
                  "provider": "deepseek", "language": "zh"}
        for field, default in _compat.items():
            if field not in data:
                data[field] = default

        self.data = data
        self.save()
        return True

    # ── Tasks ──────────────────────────────────────────

    def get_tasks(self, date_str=None):
        tasks = self.data.get("tasks", [])
        return [t for t in tasks if t.get("plan_date") == date_str] if date_str else tasks

    def add_time(self, tid, minutes):
        for t in self.data["tasks"]:
            if t["id"] == tid:
                t["actual_minutes"] = t.get("actual_minutes", 0) + minutes
                self.save()
                return True
        return False

    def add_task(self, title, subject, deadline, plan_date=None, hours=0,
                 importance=3, urgency=3, priority=50, task_type="normal",
                 weekly_theme="", actual_minutes=0, _commit=True):
        t = {
            "id": self.data["next_id"], "title": title, "subject": subject or "Other",
            "deadline": deadline or "", "plan_date": plan_date or datetime.now().strftime("%Y-%m-%d"),
            "estimated_hours": hours, "status": "pending",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "importance": importance, "urgency": urgency, "priority": priority,
            "task_type": task_type, "weekly_theme": weekly_theme,
            "actual_minutes": actual_minutes,
        }
        self.data["tasks"].append(t)
        self.data["next_id"] += 1
        if _commit:
            self.save()
        return t

    def add_tasks_batch(self, items, meta=None):
        for it in items:
            self.add_task(
                it.get("title", ""), it.get("subject", ""), it.get("deadline", ""),
                it.get("plan_date", ""), it.get("hours", 0),
                importance=it.get("importance", meta.get("importance", 3) if meta else 3),
                urgency=it.get("urgency", meta.get("urgency", 3) if meta else 3),
                priority=it.get("priority", meta.get("priority", 50) if meta else 50),
                task_type=it.get("task_type", "normal"),
                weekly_theme=it.get("weekly_theme", meta.get("weekly_theme", "") if meta else ""),
                _commit=False,
            )
        self.save()

    def update_task(self, tid, **kw):
        for t in self.data["tasks"]:
            if t["id"] == tid:
                t.update(kw)
                self.save()
                return True
        return False

    def delete_task(self, tid):
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != tid]
        self.save()

    def delete_tasks_by_subject(self, subject):
        before = len(self.data["tasks"])
        self.data["tasks"] = [t for t in self.data["tasks"] if t.get("subject", "") != subject]
        after = len(self.data["tasks"])
        self.save()
        return before - after

    def get_stats(self):
        tasks = self.data["tasks"]
        total = len(tasks)
        pending = sum(1 for t in tasks if t["status"] == "pending")
        completed = sum(1 for t in tasks if t["status"] == "completed")
        today = datetime.now().strftime("%Y-%m-%d")
        td = self.get_tasks(today)
        td_done = sum(1 for t in td if t["status"] == "completed")
        return {
            "total": total, "pending": pending, "completed": completed,
            "rate": int(completed / total * 100) if total else 0,
            "today_total": len(td), "today_done": td_done,
        }

    def get_month_tasks(self, y, m):
        r = {}
        for t in self.data["tasks"]:
            dl = t.get("deadline", "")
            if dl and dl.startswith(f"{y}-{m:02d}"):
                d = int(dl.split("-")[2])
                r[d] = r.get(d, 0) + 1
        return r

    def get_month_deadline_groups(self, y, m):
        from collections import defaultdict
        r = defaultdict(list)
        for t in self.data["tasks"]:
            dl = t.get("deadline", "")
            if dl and dl.startswith(f"{y}-{m:02d}"):
                d = int(dl.split("-")[2])
                r[d].append({
                    "title": t["title"],
                    "subject": t.get("subject", ""),
                    "status": t.get("status", "pending"),
                })
        return dict(r)

    def get_deadline_tasks(self, date_str):
        return [t for t in self.data.get("tasks", []) if t.get("deadline", "") == date_str]

    def get_weekly_theme(self):
        tasks = self.data.get("tasks", [])
        for t in sorted(tasks, key=lambda x: x.get("created", ""), reverse=True):
            wt = t.get("weekly_theme", "")
            if wt:
                return wt
        return ""

    def get_pending_tasks(self):
        return [t for t in self.data.get("tasks", []) if t["status"] == "pending"]

    # ── Diary ─────────────────────────────────────────

    def add_diary(self, text, analysis):
        e = {"date": datetime.now().strftime("%Y-%m-%d"), "raw": text, "analysis": analysis}
        self.data["diary"].append(e)
        self.save()

    def get_diary(self, limit=30):
        return sorted(self.data.get("diary", []), key=lambda x: x.get("date", ""), reverse=True)[:limit]

    def get_diary_map(self):
        return {d["date"]: d for d in self.data.get("diary", [])}

    # ── Discover / Insights ──────────────────────────

    def add_insight(self, insight_data):
        existing = self.data.get("insights", [])
        iid = max([i.get("id", 0) for i in existing], default=0) + 1
        insight = {
            "id": iid,
            "type": insight_data.get("type", "hypothesis"),
            "title": insight_data.get("title", ""),
            "hypothesis": insight_data.get("hypothesis", ""),
            "evidence": insight_data.get("evidence", []),
            "confidence": insight_data.get("confidence", 0.5),
            "status": insight_data.get("status", "pending"),
            "question": insight_data.get("question", ""),
            "user_answer": insight_data.get("user_answer", None),
            "created": datetime.now().strftime("%Y-%m-%d"),
            "category": insight_data.get("category", "general"),
            "confirmed_at": insight_data.get("confirmed_at", None),
            "follow_up": insight_data.get("follow_up", None),
        }
        self.data.setdefault("insights", []).append(insight)
        self.save()
        return insight

    def update_insight(self, iid, **kw):
        for i in self.data.get("insights", []):
            if i["id"] == iid:
                i.update(kw)
                self.save()
                return True
        return False

    def get_insights(self, status=None):
        insights = self.data.get("insights", [])
        if status:
            return [i for i in insights if i.get("status") == status]
        return sorted(insights, key=lambda x: x.get("id", 0), reverse=True)

    def get_pending_insight_count(self):
        return len(self.get_insights("pending"))

    def set_discover_last_run(self, dt=None):
        self.data["discover_last_run"] = dt or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.save()

    def get_discover_last_run(self):
        return self.data.get("discover_last_run")

    def aggregate_for_discover(self):
        """Aggregate user data into a structured summary for AI pattern analysis."""
        tasks = self.data.get("tasks", [])
        diaries = self.data.get("diary", [])
        from collections import defaultdict

        total_tasks = len(tasks)
        completed = sum(1 for t in tasks if t["status"] == "completed")
        pending = total_tasks - completed

        dow_comp = defaultdict(lambda: {"total": 0, "done": 0})
        for t in tasks:
            pd_date = t.get("plan_date", "")
            if pd_date:
                try:
                    dow = datetime.strptime(pd_date, "%Y-%m-%d").strftime("%A")
                    dow_comp[dow]["total"] += 1
                    if t["status"] == "completed":
                        dow_comp[dow]["done"] += 1
                except Exception:
                    pass

        subj_stats = defaultdict(lambda: {"total": 0, "done": 0})
        for t in tasks:
            subj = t.get("subject", "Other")
            subj_stats[subj]["total"] += 1
            if t["status"] == "completed":
                subj_stats[subj]["done"] += 1

        pbands = {"high (>=80)": {"total": 0, "done": 0},
                  "medium (50-79)": {"total": 0, "done": 0},
                  "low (<50)": {"total": 0, "done": 0}}
        for t in tasks:
            p = t.get("priority", 50)
            band = "high (>=80)" if p >= 80 else ("medium (50-79)" if p >= 50 else "low (<50)")
            pbands[band]["total"] += 1
            if t["status"] == "completed":
                pbands[band]["done"] += 1

        on_time = late = no_deadline = 0
        for t in tasks:
            dl = t.get("deadline", "")
            if not dl:
                no_deadline += 1
                continue
            try:
                if t["status"] == "completed":
                    created = t.get("created", "")[:10]
                    if created and created <= dl:
                        on_time += 1
                    else:
                        late += 1
            except Exception:
                pass

        mood_trend = []
        sleep_trend = []
        for d in sorted(diaries, key=lambda x: x.get("date", ""))[-14:]:
            a = d.get("analysis", {})
            if isinstance(a, dict):
                mood = a.get("mood", {})
                if isinstance(mood, dict):
                    mood_trend.append({
                        "date": d["date"],
                        "score": mood.get("score"),
                        "primary": mood.get("primary"),
                    })
                slp = a.get("sleep", {})
                if isinstance(slp, dict):
                    sleep_trend.append({
                        "date": d["date"],
                        "hours": slp.get("hours"),
                        "quality": slp.get("quality"),
                    })

        est_vs_actual = []
        for t in tasks:
            est = t.get("estimated_hours", 0)
            act = t.get("actual_minutes", 0) / 60.0
            if est > 0:
                est_vs_actual.append({
                    "title": t["title"],
                    "estimated_h": est,
                    "actual_h": round(act, 1),
                })

        recent_highlights = []
        for d in diaries[-7:]:
            a = d.get("analysis", {})
            if isinstance(a, dict):
                for h in a.get("highlights", []):
                    recent_highlights.append(f"{d['date']}: {h}")

        creation_by_hour = defaultdict(int)
        for t in tasks:
            ct = t.get("created", "")
            if ct and len(ct) >= 13:
                try:
                    hour = int(ct.split(" ")[1].split(":")[0])
                    creation_by_hour[hour] += 1
                except Exception:
                    pass

        delay_days_list = []
        early_count = on_time_count = last_min_count = 0
        for t in tasks:
            if t["status"] != "completed":
                continue
            dl = t.get("deadline", "")
            ct = t.get("created", "")[:10]
            if not dl or not ct:
                continue
            try:
                dl_dt = datetime.strptime(dl, "%Y-%m-%d")
                ct_dt = datetime.strptime(ct, "%Y-%m-%d")
                span = (dl_dt - ct_dt).days
                delay_days_list.append(span)
                if span > 3:
                    early_count += 1
                elif span >= 1:
                    on_time_count += 1
                else:
                    last_min_count += 1
            except Exception:
                pass

        active_dates = set()
        for t in tasks:
            pd = t.get("plan_date", "")
            if pd:
                active_dates.add(pd)
        for d in diaries:
            active_dates.add(d.get("date", ""))
        sorted_dates = sorted(active_dates)
        total_active_days = len(sorted_dates)
        max_streak = current_streak = 0
        prev = None
        for ds in sorted_dates:
            try:
                dt = datetime.strptime(ds, "%Y-%m-%d")
                if prev and (dt - prev).days == 1:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
                    max_streak = max(max_streak, current_streak)
                prev = dt
            except Exception:
                pass
        days_since_last = 0
        if sorted_dates:
            try:
                days_since_last = (datetime.now() - datetime.strptime(sorted_dates[-1], "%Y-%m-%d")).days
            except Exception:
                pass

        keyword_freq = defaultdict(int)
        stop_words = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
                      "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看",
                      "好", "自己", "这", "他", "她", "它", "们", "那", "被", "从", "把", "让",
                      "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                      "have", "has", "had", "do", "does", "did", "will", "would", "could",
                      "should", "may", "might", "shall", "can", "to", "of", "in", "for",
                      "on", "with", "at", "by", "from", "as", "into", "through", "during",
                      "before", "after", "above", "below", "between", "out", "off", "over",
                      "under", "again", "further", "then", "once", "and", "but", "or", "nor",
                      "not", "so", "yet", "both", "either", "neither", "each", "every",
                      "i", "me", "my", "we", "our", "you", "your", "he", "him", "his",
                      "she", "her", "they", "them", "their", "this", "that", "these", "those",
                      "what", "which", "who", "when", "where", "why", "how", "all", "each",
                      "few", "more", "most", "other", "some", "such", "no", "only", "own",
                      "same", "than", "too", "very", "just", "because", "if", "about", "up"}
        for d in diaries:
            raw = d.get("raw", "")
            words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]{3,}', raw)
            for w in words:
                if w not in stop_words and len(w) >= 2:
                    keyword_freq[w] += 1
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20]

        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "pending": pending,
            "completion_rate": f"{int(completed / total_tasks * 100)}%" if total_tasks else "N/A",
            "day_of_week_completion": dict(dow_comp),
            "subject_stats": dict(subj_stats),
            "priority_band_completion": dict(pbands),
            "deadline_adherence": {"on_time": on_time, "late": late, "no_deadline": no_deadline},
            "mood_trend_last_14_days": mood_trend,
            "sleep_trend_last_14_days": sleep_trend,
            "time_estimation_samples": est_vs_actual[:10],
            "total_diary_entries": len(diaries),
            "recent_diary_highlights": recent_highlights[:10],
            "creation_hour_distribution": dict(creation_by_hour),
            "completion_delay": {
                "avg_deadline_span_days": round(sum(delay_days_list) / len(delay_days_list), 1) if delay_days_list else None,
                "delay_samples": delay_days_list[:15],
                "early_planners": early_count,
                "on_time_planners": on_time_count,
                "last_minute": last_min_count,
            },
            "usage_streak": {
                "total_active_days": total_active_days,
                "max_streak_days": max_streak,
                "days_since_last_use": days_since_last,
            },
            "diary_top_keywords": top_keywords,
        }

    # ── Manual ───────────────────────────────────────

    def get_manual(self):
        return self.data.get("manual")

    def set_manual(self, manual_data):
        self.data["manual"] = {
            "last_synthesized": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "insight_count_at_synthesis": len(self.get_insights("confirmed")),
            **manual_data,
        }
        self.save()

    def get_confirmed_insight_count(self):
        return len(self.get_insights("confirmed"))

    def needs_resynthesis(self):
        manual = self.get_manual()
        if not manual:
            return self.get_confirmed_insight_count() >= 2
        last_count = manual.get("insight_count_at_synthesis", 0)
        return self.get_confirmed_insight_count() != last_count

    # ── Vision ────────────────────────────────────────

    def add_vision(self, text, analysis):
        v = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "raw": text, "analysis": analysis}
        self.data["visions"].append(v)
        self.save()

    def get_visions(self):
        return sorted(self.data.get("visions", []), key=lambda x: x.get("date", ""), reverse=True)

    # ── Weekly Snapshot ─────────────────────────────

    def aggregate_for_weekly(self):
        from collections import defaultdict
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        week_start = monday.strftime("%Y-%m-%d")
        week_end = today.strftime("%Y-%m-%d")

        tasks = self.data.get("tasks", [])
        diaries = self.data.get("diary", [])
        insights = self.data.get("insights", [])

        week_tasks = [t for t in tasks if week_start <= t.get("plan_date", "") <= week_end]
        week_completed = [t for t in week_tasks if t["status"] == "completed"]
        week_pending = [t for t in week_tasks if t["status"] == "pending"]

        last_monday = (monday - timedelta(days=7)).strftime("%Y-%m-%d")
        last_sunday = (monday - timedelta(days=1)).strftime("%Y-%m-%d")
        last_week_tasks = [t for t in tasks if last_monday <= t.get("plan_date", "") <= last_sunday]
        last_week_completed = sum(1 for t in last_week_tasks if t["status"] == "completed")
        last_week_total = len(last_week_tasks)

        week_diaries = [d for d in diaries if week_start <= d.get("date", "") <= week_end]

        moods = []
        sleeps = []
        for d in week_diaries:
            a = d.get("analysis", {})
            if isinstance(a, dict):
                m = a.get("mood", {})
                if isinstance(m, dict) and m.get("score"):
                    moods.append(m)
                s = a.get("sleep", {})
                if isinstance(s, dict) and s.get("hours"):
                    sleeps.append(s)

        week_insights = [i for i in insights if week_start <= i.get("created", "") <= week_end]

        subj_this = defaultdict(lambda: {"total": 0, "done": 0})
        for t in week_tasks:
            subj_this[t.get("subject", "Other")]["total"] += 1
            if t["status"] == "completed":
                subj_this[t.get("subject", "Other")]["done"] += 1

        last_week_diaries = [d for d in diaries if last_monday <= d.get("date", "") <= last_sunday]
        def _extract_keywords(diary_list):
            freq = defaultdict(int)
            for d in diary_list:
                raw = d.get("raw", "")
                words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]{3,}', raw)
                for w in words:
                    if len(w) >= 2:
                        freq[w] += 1
            return dict(freq)
        this_kw = _extract_keywords(week_diaries)
        last_kw = _extract_keywords(last_week_diaries)

        return {
            "week_label": f"{week_start} ~ {week_end}",
            "this_week": {
                "total_tasks": len(week_tasks),
                "completed": len(week_completed),
                "pending": len(week_pending),
                "completion_rate": f"{int(len(week_completed) / len(week_tasks) * 100)}%" if week_tasks else "N/A",
                "subjects": dict(subj_this),
            },
            "last_week": {
                "total_tasks": last_week_total,
                "completed": last_week_completed,
                "completion_rate": f"{int(last_week_completed / last_week_total * 100)}%" if last_week_total else "N/A",
            },
            "comparison": {
                "task_change": len(week_tasks) - last_week_total,
                "completion_change": len(week_completed) - last_week_completed,
            },
            "diary_count": len(week_diaries),
            "avg_mood": round(sum(m.get("score", 0) for m in moods) / len(moods), 1) if moods else None,
            "mood_details": [{"date": d.get("date", ""), **m} for d, m in zip(week_diaries, moods)] if moods else [],
            "avg_sleep": round(sum(s.get("hours", 0) for s in sleeps) / len(sleeps), 1) if sleeps else None,
            "sleep_details": [{"date": d.get("date", ""), **s} for d, s in zip(week_diaries, sleeps)] if sleeps else [],
            "new_insights_count": len(week_insights),
            "new_insights": [{"title": i.get("title", ""), "status": i.get("status", "pending")} for i in week_insights],
            "this_week_keywords": sorted(this_kw.items(), key=lambda x: x[1], reverse=True)[:15],
            "last_week_keywords": sorted(last_kw.items(), key=lambda x: x[1], reverse=True)[:15],
        }

    def get_weekly_snapshot(self, week_label):
        for s in self.data.get("weekly_snapshots", []):
            if s.get("week_label") == week_label:
                return s
        return None

    def save_weekly_snapshot(self, snapshot_data):
        snapshots = self.data.setdefault("weekly_snapshots", [])
        label = snapshot_data.get("week_label", "")
        for i, s in enumerate(snapshots):
            if s.get("week_label") == label:
                snapshots[i] = snapshot_data
                self.save()
                return
        snapshots.append(snapshot_data)
        self.save()

    def get_latest_weekly_snapshot(self):
        snapshots = self.data.get("weekly_snapshots", [])
        return snapshots[-1] if snapshots else None

    # ── Reflect Sessions ────────────────────────────

    def add_reflect_session(self, session_data):
        session = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), **session_data}
        self.data.setdefault("reflect_sessions", []).append(session)
        self.save()
        return session

    def get_reflect_sessions(self, limit=10):
        sessions = self.data.get("reflect_sessions", [])
        return sorted(sessions, key=lambda x: x.get("date", ""), reverse=True)[:limit]

    # ── Insight Viewed Tracking ───────────────────

    def mark_insights_viewed_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        viewed = self.data.setdefault("insight_viewed_dates", {})
        viewed[today] = True
        self.save()

    def has_viewed_insights_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        viewed = self.data.get("insight_viewed_dates", {})
        return viewed.get(today, False)

    # ── Intervention Tracking ──────────────────────

    def mark_intervention_tried(self, insight_id):
        for i in self.data.get("insights", []):
            if i["id"] == insight_id:
                i["intervention_tried"] = True
                i["intervention_tried_at"] = datetime.now().strftime("%Y-%m-%d")
                self.save()
                return True
        return False

    def get_tried_interventions(self):
        return [i for i in self.data.get("insights", [])
                if i.get("intervention_tried") and i.get("status") == "confirmed"]

    def aggregate_intervention_effects(self):
        tried = self.get_tried_interventions()
        results = []
        for insight in tried:
            tried_date = insight.get("intervention_tried_at", "")
            if not tried_date:
                continue
            category = insight.get("category", "general")
            try:
                tried_dt = datetime.strptime(tried_date, "%Y-%m-%d")
                before_start = (tried_dt - timedelta(days=7)).strftime("%Y-%m-%d")
                after_end = (tried_dt + timedelta(days=7)).strftime("%Y-%m-%d")

                tasks = self.data.get("tasks", [])
                before_tasks = [t for t in tasks if before_start <= t.get("plan_date", "") < tried_date]
                after_tasks = [t for t in tasks if tried_date <= t.get("plan_date", "") <= after_end]

                def _rate(task_list):
                    if not task_list:
                        return 0
                    return int(sum(1 for t in task_list if t["status"] == "completed") / len(task_list) * 100)

                results.append({
                    "insight_id": insight["id"],
                    "insight_title": insight.get("title", ""),
                    "category": category,
                    "tried_date": tried_date,
                    "before_completion_rate": _rate(before_tasks),
                    "after_completion_rate": _rate(after_tasks),
                    "before_task_count": len(before_tasks),
                    "after_task_count": len(after_tasks),
                })
            except Exception:
                continue
        return results

    # ── Legacy / Biography ────────────────────────

    def aggregate_for_legacy(self, start_date, end_date):
        tasks = self.data.get("tasks", [])
        diaries = self.data.get("diary", [])
        visions = self.data.get("visions", [])
        insights = self.data.get("insights", [])
        reflect_sessions = self.data.get("reflect_sessions", [])

        range_tasks = [t for t in tasks if start_date <= t.get("plan_date", "") <= end_date]
        range_diaries = [d for d in diaries if start_date <= d.get("date", "") <= end_date]
        range_insights = [i for i in insights if start_date <= i.get("created", "") <= end_date]
        range_reflects = [r for r in reflect_sessions if start_date <= r.get("date", "")[:10] <= end_date]
        range_visions = [v for v in visions if start_date <= v.get("date", "")[:10] <= end_date]

        completed = [t for t in range_tasks if t["status"] == "completed"]
        subjects = list(set(t.get("subject", "") for t in range_tasks if t.get("subject")))

        mood_list = []
        for d in range_diaries:
            a = d.get("analysis", {})
            if isinstance(a, dict):
                m = a.get("mood", {})
                if isinstance(m, dict) and m.get("score"):
                    mood_list.append({"date": d.get("date", ""), "score": m["score"], "primary": m.get("primary")})

        return {
            "period": f"{start_date} ~ {end_date}",
            "task_summary": {
                "total": len(range_tasks),
                "completed": len(completed),
                "completion_rate": f"{int(len(completed) / len(range_tasks) * 100)}%" if range_tasks else "N/A",
                "subjects": subjects,
                "completed_titles": [t["title"] for t in completed[:20]],
            },
            "diary_entries": [{"date": d.get("date", ""), "raw": d.get("raw", "")[:300]} for d in range_diaries],
            "mood_trend": mood_list,
            "visions": [{"date": v.get("date", ""), "raw": v.get("raw", "")[:200]} for v in range_visions],
            "confirmed_insights": [{"title": i.get("title", ""), "hypothesis": i.get("hypothesis", "")}
                                   for i in range_insights if i.get("status") == "confirmed"],
            "reflect_highlights": [{"date": r.get("date", ""), "insight": r.get("review", {}).get("insight", "")[:200]}
                                   for r in range_reflects if isinstance(r.get("review"), dict)],
        }

    def save_legacy_chapter(self, chapter_data):
        chapters = self.data.setdefault("legacy_chapters", [])
        for i, c in enumerate(chapters):
            if c.get("period") == chapter_data.get("period"):
                chapters[i] = chapter_data
                self.save()
                return
        chapters.append(chapter_data)
        self.save()

    def get_legacy_chapters(self):
        chapters = self.data.get("legacy_chapters", [])
        return sorted(chapters, key=lambda x: x.get("period", ""))

    def get_all_legacy_data(self):
        return {
            "tasks": self.data.get("tasks", []),
            "diary": self.data.get("diary", []),
            "visions": self.data.get("visions", []),
            "insights": self.data.get("insights", []),
            "reflect_sessions": self.data.get("reflect_sessions", []),
            "manual": self.data.get("manual"),
            "legacy_chapters": self.data.get("legacy_chapters", []),
            "weekly_snapshots": self.data.get("weekly_snapshots", []),
        }


# ============================================================
#  Seed Data Generator — 2 周模拟数据
# ============================================================

def generate_seed_data():
    """
    生成 2 周的模拟数据（任务 + 日记 + AI 分析结果 + 洞察）。
    供评委一键体验完整产品链路。
    """
    today = datetime.now()
    start_date = today - timedelta(days=13)  # 14 天前

    data = {
        "tasks": [],
        "next_id": 1,
        "diary": [],
        "visions": [],
        "insights": [],
        "discover_last_run": None,
        "manual": None,
        "api_key": "",
        "provider": "deepseek",
        "language": "zh",
        "weekly_snapshots": [],
        "reflect_sessions": [],
        "legacy_chapters": [],
        "insight_viewed_dates": {},
        "biography": "",
        "portrait": {},
    }

    subjects = ["学习", "运动", "阅读", "项目"]
    task_templates = [
        {"title": "复习算法", "subject": "学习", "hours": 2, "importance": 4, "urgency": 3},
        {"title": "跑步 5km", "subject": "运动", "hours": 1, "importance": 3, "urgency": 2},
        {"title": "读《原子习惯》", "subject": "阅读", "hours": 1, "importance": 3, "urgency": 2},
        {"title": "写项目文档", "subject": "项目", "hours": 2, "importance": 4, "urgency": 4},
        {"title": "练习英语听力", "subject": "学习", "hours": 1, "importance": 3, "urgency": 3},
        {"title": "力量训练", "subject": "运动", "hours": 1, "importance": 3, "urgency": 2},
        {"title": "整理笔记", "subject": "学习", "hours": 1, "importance": 2, "urgency": 3},
        {"title": "冥想 15 分钟", "subject": "运动", "hours": 0.5, "importance": 3, "urgency": 1},
        {"title": "Debug 报错", "subject": "项目", "hours": 3, "importance": 5, "urgency": 4},
        {"title": "写周报", "subject": "项目", "hours": 1, "importance": 4, "urgency": 5},
    ]

    diary_templates = [
        "今天状态不错，完成了所有计划任务，感觉很有成就感。",
        "早上起晚了，匆匆忙忙，只完成了一半的任务，有些焦虑。",
        "下午跑步后心情变好了，但是晚上又刷了一小时手机。",
        "今天效率很高，中午没午休，但精神一直很好。",
        "睡得不好，只有 5 小时，今天明显注意力不集中。",
        "和同学讨论了一个有趣的问题，灵感很多，很兴奋。",
        "今天比较平淡，按部就班完成任务，没什么特别的感觉。",
        "加班到很晚，很累，但项目终于有进展了。",
        "偷懒了一天，什么都没做，有点自责但也很放松。",
        "今天尝试了番茄工作法，感觉比之前专注多了。",
        "压力很大，下周有考试，感觉时间不够用。",
        "运动了一小时，出汗后感觉整个人轻松了。",
        "读了一本好书，对人生有了新的思考。",
        "今天是最有收获的一天，解决了困扰很久的问题。",
    ]

    mood_cycle = [
        {"primary": "positive", "score": 8, "sleep": {"hours": 7.5, "quality": "good"}},
        {"primary": "anxious", "score": 4, "sleep": {"hours": 6, "quality": "bad"}},
        {"primary": "mixed", "score": 6, "sleep": {"hours": 7, "quality": "ok"}},
        {"primary": "positive", "score": 9, "sleep": {"hours": 6.5, "quality": "ok"}},
        {"primary": "negative", "score": 3, "sleep": {"hours": 5, "quality": "bad"}},
        {"primary": "positive", "score": 8, "sleep": {"hours": 7, "quality": "good"}},
        {"primary": "neutral", "score": 5, "sleep": {"hours": 7, "quality": "ok"}},
        {"primary": "tired", "score": 4, "sleep": {"hours": 5.5, "quality": "bad"}},
        {"primary": "relaxed", "score": 7, "sleep": {"hours": 8, "quality": "good"}},
        {"primary": "positive", "score": 8, "sleep": {"hours": 7, "quality": "good"}},
        {"primary": "anxious", "score": 4, "sleep": {"hours": 6, "quality": "bad"}},
        {"primary": "positive", "score": 7, "sleep": {"hours": 7.5, "quality": "good"}},
        {"primary": "thoughtful", "score": 7, "sleep": {"hours": 7, "quality": "good"}},
        {"primary": "positive", "score": 9, "sleep": {"hours": 8, "quality": "good"}},
    ]

    # 生成 14 天的数据
    for i in range(14):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

        # 每天 2-4 个任务
        import random
        random.seed(i)  # 确保可复现
        day_tasks = random.sample(task_templates, k=random.randint(2, 4))
        for t in day_tasks:
            status = random.choices(["completed", "pending"], weights=[0.7, 0.3])[0]
            data["tasks"].append({
                "id": data["next_id"],
                "title": t["title"],
                "subject": t["subject"],
                "deadline": date,
                "plan_date": date,
                "estimated_hours": t["hours"],
                "status": status,
                "created": f"{date} 08:00",
                "importance": t["importance"],
                "urgency": t["urgency"],
                "priority": min(t["importance"] * 20 + t["urgency"] * 5, 100),
                "task_type": "normal",
                "weekly_theme": "",
                "actual_minutes": t["hours"] * 60 * random.uniform(0.7, 1.3) if status == "completed" else 0,
            })
            data["next_id"] += 1

        # 每天一条日记
        mood = mood_cycle[i]
        data["diary"].append({
            "date": date,
            "raw": diary_templates[i],
            "analysis": {
                "mood": {"primary": mood["primary"], "score": mood["score"]},
                "sleep": mood["sleep"],
                "highlights": [diary_templates[i][:20] + "..."],
                "lowlights": [],
                "social": "",
                "suggestions": ["保持当前节奏", "注意休息"],
                "reply": "今天辛苦了！",
            },
        })

    # 预置 3 条已确认的洞察（跳过 AI 调用，评委可直接看到手册）
    data["insights"] = [
        {
            "id": 1,
            "type": "hypothesis",
            "title": "睡眠不足拖累效率",
            "hypothesis": "当睡眠少于 6 小时时，第二天的任务完成率显著下降",
            "evidence": ["6月22日睡眠5小时，当天只完成1/3任务", "6月25日睡眠5.5小时，注意力明显不集中"],
            "confidence": 0.85,
            "status": "confirmed",
            "question": "我发现你睡眠不足的时候效率会明显降低，是这样吗？",
            "user_answer": "是的，确实这样，睡不好那天什么都做不进去。",
            "created": (start_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "category": "sleep",
            "confirmed_at": (start_date + timedelta(days=5)).strftime("%Y-%m-%d"),
        },
        {
            "id": 2,
            "type": "hypothesis",
            "title": "运动改善情绪",
            "hypothesis": "运动日当天的情绪评分普遍比非运动日高 2 分以上",
            "evidence": ["6月21日跑步后 mood=8", "6月26日运动后 mood=7", "6月28日运动后心情变好"],
            "confidence": 0.9,
            "status": "confirmed",
            "question": "你注意到运动之后心情通常会变好吗？",
            "user_answer": "对，跑步完确实感觉整个人轻松了。",
            "created": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            "category": "mood",
            "confirmed_at": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
        },
        {
            "id": 3,
            "type": "hypothesis",
            "title": "番茄工作法有效",
            "hypothesis": "使用时间管理技巧（如番茄工作法）时，当天任务完成率显著提升",
            "evidence": ["7月3日尝试番茄工作法，效率很高，全部完成", "当天完成任务数是平均水平的 1.5 倍"],
            "confidence": 0.75,
            "status": "confirmed",
            "question": "你发现番茄工作法对你确实有帮助吗？",
            "user_answer": "是的，感觉比之前专注多了。",
            "created": (start_date + timedelta(days=10)).strftime("%Y-%m-%d"),
            "category": "productivity",
            "confirmed_at": (start_date + timedelta(days=10)).strftime("%Y-%m-%d"),
        },
    ]

    # 预置一条待回答的洞察
    data["insights"].append({
        "id": 4,
        "type": "hypothesis",
        "title": "周一焦虑症",
        "hypothesis": "每周第一天的任务完成率和情绪评分最低",
        "evidence": ["6月23日（周一）焦虑，只完成一半任务", "6月30日（周一）情绪低落"],
        "confidence": 0.6,
        "status": "pending",
        "question": "你有没有觉得每周一总是最难熬的？",
        "user_answer": None,
        "created": (start_date + timedelta(days=12)).strftime("%Y-%m-%d"),
        "category": "mood",
        "confirmed_at": None,
    })

    return data
