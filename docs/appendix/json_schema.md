# Weekly Wrap: Output JSON Schema

**Version:** 1.0  
**Parent Document:** [Development Specification](../dev_spec.md)

---

## Output JSON Schema

### Complete Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WeeklyWrapData",
  "type": "object",
  "required": ["tutor", "week", "sessions", "metrics", "insights", "tip"],
  "properties": {
    "tutor": {
      "type": "object",
      "required": ["id", "name"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" }
      }
    },
    "week": {
      "type": "object",
      "required": ["start_date", "end_date", "recording_count"],
      "properties": {
        "start_date": { "type": "string", "format": "date" },
        "end_date": { "type": "string", "format": "date" },
        "recording_count": { "type": "integer", "minimum": 1 }
      }
    },
    "sessions": {
      "type": "object",
      "required": ["count", "total_minutes", "student_count"],
      "properties": {
        "count": { "type": "integer", "minimum": 1 },
        "total_minutes": { "type": "integer", "minimum": 1 },
        "student_count": { "type": "integer", "minimum": 1 }
      }
    },
    "metrics": {
      "type": "object",
      "required": ["tutor_talk_pct", "avg_wait_time_seconds", "praise_count", "question_count"],
      "properties": {
        "tutor_talk_pct": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Percentage of words spoken by tutor vs students"
        },
        "avg_wait_time_seconds": {
          "type": "number",
          "minimum": 0,
          "maximum": 60,
          "description": "Average silence duration after tutor asks a question"
        },
        "praise_count": {
          "type": "integer",
          "minimum": 0,
          "description": "Count of encouraging/praising statements"
        },
        "question_count": {
          "type": "integer",
          "minimum": 0,
          "description": "Count of questions asked by tutor"
        }
      }
    },
    "archetype": {
      "type": "object",
      "required": ["id", "name", "emoji", "defining_metric"],
      "properties": {
        "id": {
          "type": "string",
          "enum": ["encourager", "patient_one", "question_master", "energizer", "balanced"]
        },
        "name": { "type": "string" },
        "emoji": { "type": "string" },
        "defining_metric": { "type": "string" },
        "defining_value": { "type": ["number", "string"] }
      }
    },
    "insights": {
      "type": "object",
      "required": ["strength", "growth"],
      "properties": {
        "strength": {
          "type": "object",
          "required": ["title", "body", "metric_ref"],
          "properties": {
            "title": { "type": "string", "maxLength": 30 },
            "body": { "type": "string", "maxLength": 100 },
            "metric_ref": { "type": "string" }
          }
        },
        "growth": {
          "type": "object",
          "required": ["title", "body", "metric_ref"],
          "properties": {
            "title": { "type": "string", "maxLength": 30 },
            "body": { "type": "string", "maxLength": 100 },
            "metric_ref": { "type": "string" }
          }
        }
      }
    },
    "highlight_quote": {
      "type": ["object", "null"],
      "properties": {
        "text": { "type": "string", "maxLength": 150 },
        "context": { "type": "string", "maxLength": 50 }
      }
    },
    "tip": {
      "type": "object",
      "required": ["type", "text", "highlight"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["growth", "celebration"]
        },
        "text": { "type": "string", "maxLength": 80 },
        "highlight": { "type": "string", "maxLength": 20 }
      }
    },
    "greeting": {
      "type": "object",
      "required": ["text", "emoji"],
      "properties": {
        "text": { "type": "string" },
        "emoji": { "type": "string" }
      }
    }
  }
}
```

### Example Output

```json
{
  "tutor": {
    "id": "tutor_abc123",
    "name": "Baik"
  },
  "week": {
    "start_date": "2024-11-18",
    "end_date": "2024-11-24",
    "recording_count": 3
  },
  "sessions": {
    "count": 3,
    "total_minutes": 73,
    "student_count": 7
  },
  "metrics": {
    "tutor_talk_pct": 81,
    "avg_wait_time_seconds": 1.6,
    "praise_count": 45,
    "question_count": 32
  },
  "archetype": {
    "id": "encourager",
    "name": "The Encourager",
    "emoji": "🎯",
    "defining_metric": "praise_count",
    "defining_value": 45
  },
  "insights": {
    "strength": {
      "title": "You celebrated a lot",
      "body": "45 encouraging moments — your students feel supported.",
      "metric_ref": "praise_count"
    },
    "growth": {
      "title": "Let them talk more",
      "body": "You talked 81% of the time. Try asking \"What do you think?\"",
      "metric_ref": "tutor_talk_pct"
    }
  },
  "highlight_quote": {
    "text": "You're doing great. Keep sharing your screen and solving the problems.",
    "context": "encouraging a student"
  },
  "tip": {
    "type": "growth",
    "text": "This week, try asking a question then count to 5.",
    "highlight": "count to 5"
  },
  "greeting": {
    "text": "Great week, Baik!",
    "emoji": "🎉"
  }
}
```
