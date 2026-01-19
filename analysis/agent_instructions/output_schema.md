# Agent 输出格式规范

## JSON 结构

```json
{
  "period": "2025-09",
  "data_summary": {
    "total_conversations": 121,
    "tools": {"codex": 55, "serena": 66, "claude": 0},
    "total_user_messages": 500,
    "date_range": ["2025-09-14", "2025-09-30"]
  },

  "timeline_rhythm": {
    "dense_periods": [
      {
        "date": "2025-09-17",
        "conversation_count": 8,
        "signal": "可能卡住了",
        "related_files": ["file1.jsonl", "file2.jsonl"],
        "context": "当天在处理什么问题"
      }
    ],
    "gaps": [
      {
        "start": "2025-09-25",
        "end": "2025-09-28",
        "days": 3,
        "possible_reason": "独立探索/休息"
      }
    ],
    "conversation_length_stats": {
      "avg": 25,
      "max": 150,
      "max_file": "xxx.jsonl",
      "long_conversations": [
        {
          "file": "xxx.jsonl",
          "length": 150,
          "topic": "主题"
        }
      ]
    }
  },

  "problem_lifecycle": {
    "recurring": [
      {
        "problem": "问题描述",
        "occurrences": ["file1.jsonl", "file2.jsonl"],
        "status": "resolved/abandoned/ongoing",
        "resolution": "如何解决的（如果解决了）"
      }
    ],
    "thought_solved_but_not": [
      {
        "problem": "问题描述",
        "first_solution": "第一次的解决方案",
        "why_failed": "为什么又出现了",
        "files": ["file1.jsonl", "file2.jsonl"]
      }
    ],
    "cross_session": [
      {
        "problem": "跨会话问题描述",
        "sessions": ["session1", "session2"],
        "evolution": "问题如何演进的"
      }
    ]
  },

  "user_thinking": {
    "question_patterns": {
      "vague_count": 10,
      "precise_count": 30,
      "vague_examples": [
        {
          "quote": "原文",
          "file": "xxx.jsonl",
          "better_way": "更好的提问方式"
        }
      ],
      "precise_examples": [
        {
          "quote": "原文",
          "file": "xxx.jsonl",
          "why_good": "为什么这样问更好"
        }
      ]
    },
    "common_expressions": ["经常用的词汇"],
    "intuition_accuracy": {
      "correct_count": 5,
      "wrong_count": 3,
      "correct_examples": [
        {
          "quote": "用户判断",
          "outcome": "结果",
          "file": "xxx.jsonl"
        }
      ],
      "wrong_examples": [
        {
          "quote": "用户判断",
          "actual": "实际情况",
          "file": "xxx.jsonl"
        }
      ]
    }
  },

  "emotion_decisions": {
    "frustration_points": [
      {
        "file": "xxx.jsonl",
        "quote": "原文片段",
        "context": "背景说明",
        "trigger": "什么触发了挫败感"
      }
    ],
    "breakthrough_points": [
      {
        "file": "xxx.jsonl",
        "quote": "原文片段",
        "what_solved": "解决了什么",
        "how": "如何解决的"
      }
    ],
    "compromises": [
      {
        "file": "xxx.jsonl",
        "quote": "原文片段",
        "what_compromised": "妥协了什么",
        "reason": "为什么妥协"
      }
    ],
    "abandoned": [
      {
        "problem": "放弃的问题",
        "file": "xxx.jsonl",
        "reason": "为什么放弃",
        "workaround": "如何绕过的"
      }
    ]
  },

  "tool_tech_evolution": {
    "tool_usage": {
      "codex": 55,
      "serena": 66,
      "claude": 0
    },
    "tool_switches": [
      {
        "from": "codex",
        "to": "claude",
        "when": "日期",
        "reason": "原因"
      }
    ],
    "tech_changes": [
      {
        "change": "CSV → SQLite",
        "when": "日期",
        "trigger": "触发因素",
        "files": ["相关对话文件"]
      }
    ]
  },

  "blind_spots": {
    "could_have_used": [
      {
        "concept": "概念/工具名",
        "context": "用户在做什么时没想到",
        "evidence_file": "xxx.jsonl",
        "quote": "相关对话片段",
        "benefit": "如果用了会怎样"
      }
    ],
    "detours": [
      {
        "problem": "问题",
        "detour_path": "用户走的弯路",
        "better_path": "更好的路径",
        "time_cost": "估计浪费的时间",
        "files": ["相关文件"]
      }
    ],
    "learned_later": [
      {
        "concept": "后来学到的",
        "when_learned": "什么时候学到的",
        "could_have_helped": "如果早知道能帮到什么",
        "files": ["相关文件"]
      }
    ]
  }
}
```

## 输出文件命名

- 2025年9月：`month_2025_09.json`
- 2025年10月：`month_2025_10.json`
- 2025年11月：`month_2025_11.json`
- 2025年12月前半：`month_2025_12_a.json`
- 2025年12月后半+2026年1月：`month_2025_12_b.json`
- 跨月汇总：`cross_month.json`
- 可读索引：`full_index.md`
