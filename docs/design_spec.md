# Weekly Wrap: Design Specification

**Version:** 1.0  
**Last Updated:** January 2025

---

## 1. Layout Options

The Weekly Wrap supports two layout styles:

| Style | Purpose | Use Case |
|-------|---------|----------|
| **Spaced** | Full-featured email layout | Desktop, web preview |
| **Compact** | Mobile-optimized, scannable | Mobile devices, quick reads |

---

## 2. Content Sections

### Hero Section
- Adaptive greeting based on performance
- Week date range
- Archetype badge (if assigned)
- Session count badge

### Week at a Glance
- Metric circles with adaptive styling:
  - **Accent (teal):** Celebrate good metrics (praise ≥5, questions ≥15, minutes ≥20)
  - **Muted (dashed):** De-emphasize zeros or low values
  - **Neutral:** Default styling

### Your Tutoring Style (Spaced only)
- Talk ratio bar (tutor % vs student %)
- Think time with badge
- Badges: "Good balance" (green) / "Room to grow" (yellow)

### Insights (Compact only)
- Two insight cards: Strength + Growth
- Icons and brief descriptions
- Replaces detailed style breakdown in Compact view

### Student Goal Progress
- Dual-ring visualization (Progress + Effort)
- **Hidden if no students**

### Highlight Moment
- Verbatim quote from transcript
- Quote label (context)
- **Hidden if no suitable quote**

### Try This Week
- Coaching suggestion
- **Hidden if no tip available**

### Feedback
- 3-option poll: 👍 Yes / 👎 No / ⚠️ Issue

---

## 3. Adaptive UI Logic

### 3.1 Greeting Headlines

| Condition | Greeting | Emoji |
|-----------|----------|-------|
| No students OR short session (<10 min) | "Here's your week, {name}" | 📊 |
| Good balance but low praise | "Week in review, {name}" | 📋 |
| Has praise OR patience OR questions | "Nice work, {name}!" | 👍 |
| Praise ≥5 AND good balance (<60% talk) | "Great week, {name}!" | 🎉 |

### 3.2 Circle Accents

| Metric | Accent (Celebrate) | Muted (De-emphasize) |
|--------|--------------------|----------------------|
| Praise | ≥ 5 | = 0 |
| Questions | ≥ 15 | = 0 |
| Minutes | ≥ 20 | < 5 |
| Students | — | = 0 |
| Sessions | — | — |

### 3.3 Section Visibility

| Section | Condition to Hide |
|---------|-------------------|
| Student Goal Progress | `students === 0` |
| Highlight Moment | `!highlight_quote` |
| Try This Week | `!coaching_tip` |

### 3.4 Insight Selection (Strength)

Priority order:
1. High praise (≥5) → "You celebrated a lot"
2. Low talk ratio (<50%) → "Great listener" 👂
3. Many questions (≥20) → "Question pro" ❓
4. Long think time (≥5s) → "Patient pauses" ⏳
5. Fallback → "Session tracked" 📊

### 3.5 Insight Selection (Growth)

Priority order:
1. Zero praise + low talk → "Add encouragement"
2. High talk ratio (>70%) → "Let them talk more"
3. Low think time (<3s) + questions → "More wait time"
4. Low praise (1-4) → "Keep celebrating"
5. Fallback → "Keep it up"

---

## 4. Visual Specifications

### Colors (from Style Guide)
| Token | Hex | Usage |
|-------|-----|-------|
| `--teal` | `#00bfcc` | Primary accent, good metrics |
| `--teal-dark` | `#007f89` | Accent text |
| `--green` | `#4cab65` | Progress goals, success badges |
| `--yellow` | `#ffc94b` | Effort goals, warning badges |
| `--magenta` | `#dd2ab0` | Low progress indicator |
| `--ink` | `#1e1f24` | Primary text |
| `--ink-subtle` | `#62636c` | Secondary text |
| `--border` | `#e0e1e6` | Dividers, muted circles |

### Typography
| Role | Font | Weight | Size |
|------|------|--------|------|
| Hero headline | Lato | Black (900) | 36-48px |
| Section headers | Lato | Bold (700) | 18-24px |
| Body text | Merriweather Sans | Regular (400) | 14-16px |
| Labels | Merriweather Sans | SemiBold (600) | 10-12px |

### Circle Sizes
| Size | Dimensions |
|------|------------|
| Large (lg) | 110px |
| Medium (md) | 100px |
| Small (sm) | 90px |

### Circle Styles
| State | Border | Text Color |
|-------|--------|------------|
| Accent | 3px solid teal | teal-dark |
| Muted | 2px dashed border | text-muted |
| Default | 2px solid border | ink |

---

## 5. Responsive Behavior

### Spaced View (≥600px)
- Full section headers
- Expanded cards with descriptions
- Detailed style breakdown (ratio + think time)

### Compact View (<600px)
- Condensed headers
- Insight row (2 cards inline)
- Quote/tip strips instead of cards

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2025 | Initial specification |
