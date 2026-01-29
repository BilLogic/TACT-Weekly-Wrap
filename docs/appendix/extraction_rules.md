# Weekly Wrap: Extraction & Calculation Rules

**Version:** 1.0  
**Parent Document:** [Development Specification](../dev_spec.md)

---

## 1. Metric Calculation Rules

### `tutor_talk_pct`
- **Definition:** (Tutor word count / Total word count) × 100
- **Calculation:** Count all words in `[TUTOR]` segments, divide by total words
- **Validation:** Must be 0-100, round to nearest integer

### `avg_wait_time_seconds`
- **Definition:** Average duration of silence after tutor asks a question
- **Calculation:** 
  1. Identify tutor utterances ending with `?`
  2. Find subsequent `[SILENCE]` or `[STUDENT_*]` segment
  3. Calculate gap duration
  4. Average all gaps
- **Validation:** Must be 0-60 seconds, round to 1 decimal

### `praise_count`
- **Definition:** Count of encouraging or praising statements
- **Pattern matching (case-insensitive):**
  - Explicit praise: "good job", "great", "excellent", "perfect", "nice", "awesome", "well done", "correct", "exactly", "yes!"
  - Encouragement: "you got this", "keep going", "you're doing great", "that's right"
  - Affirmation: "I like how you...", "good thinking"
- **Validation:** Must be non-negative integer

### `question_count`
- **Definition:** Count of questions asked by tutor
- **Calculation:** Count tutor utterances containing `?`
- **Exclusions:** Rhetorical questions like "right?", "okay?", "you know?"
- **Validation:** Must be non-negative integer

---

## 2. Archetype Classification Rules

Assign archetype based on **most distinctive metric** (highest percentile vs. population norms):

| Archetype | ID | Emoji | Primary Signal | Threshold |
|-----------|-----|-------|----------------|-----------|
| The Encourager | `encourager` | 🎯 | praise_count | ≥ 20 |
| The Patient One | `patient_one` | 🧘 | avg_wait_time_seconds | ≥ 5.0s |
| The Question Master | `question_master` | ❓ | question_count | ≥ 40 |
| The Energizer | `energizer` | ⚡ | questions_per_minute | ≥ 1.5 |
| Balanced | `balanced` | ⭐ | No single standout | Default |

**Priority order** (if multiple thresholds met): patience > praise > questions > energizer

---

## 3. Insight Generation Rules

### Strength Insight
- Select the metric with **best performance** relative to targets
- Target benchmarks:
  - `tutor_talk_pct`: < 50% is excellent
  - `avg_wait_time_seconds`: 3-5s is ideal
  - `praise_count`: > 20 is excellent
  - `question_count`: > 30 is excellent

### Growth Insight
- Select the metric **furthest from target**
- Always frame constructively with specific suggestion
- Never use negative language ("you failed to...", "you didn't...")

### Writing Style
- Use second person ("You", "Your")
- Keep titles ≤ 5 words
- Keep body ≤ 15 words
- Include the specific metric value
- End with actionable suggestion if growth area

---

## 4. Quote Selection Rules

Select a quote that:
1. Demonstrates the tutor's **identified strength** (archetype)
2. Is ≤ 25 words
3. Is complete (not cut off mid-sentence)
4. Does not contain student names or identifying info
5. Is positive or instructional in tone

**Return `null` if no suitable quote found.**

---

## 5. Tip Generation Rules

| Tip Type | When to Use | Tone |
|----------|-------------|------|
| `growth` | Primary metric needs improvement | Encouraging, specific |
| `celebration` | All metrics at or above target | Reinforcing, appreciative |

**Tip format:**
- Start with action verb or context
- Include **one specific, concrete behavior** to try
- Highlight the key action in `highlight` field
- Keep total ≤ 15 words

**Tip bank by metric:**

| Metric | Issue | Tip Template |
|--------|-------|--------------|
| `tutor_talk_pct` | > 70% | "Try asking 'What do you think?' then wait." |
| `avg_wait_time_seconds` | < 2s | "After asking, **count to {3-5}** before speaking." |
| `praise_count` | < 5 | "Add a 'Nice work!' when they get it right." |
| `question_count` | < 15 | "Try turning statements into questions." |

---

## 6. Logic Thresholds Reference

### Ring Color Thresholds

| Percentage | Color | CSS Class |
|------------|-------|-----------|
| ≥ 70% | Green | `.ring-fill.green` |
| 40-69% | Yellow | `.ring-fill.yellow` |
| < 40% | Magenta | `.ring-fill.magenta` |
| Effort goals | Blue | `.ring-fill.blue` |

### Metric Quality Thresholds

| Metric | Excellent | Good | Needs Work |
|--------|-----------|------|------------|
| `tutor_talk_pct` | < 50% | 50-70% | > 70% |
| `avg_wait_time_seconds` | 3-5s | 2-3s or 5-7s | < 2s or > 7s |
| `praise_count` | > 20 | 10-20 | < 10 |
| `question_count` | > 30 | 15-30 | < 15 |
