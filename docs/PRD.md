# Weekly Wrap: Product Requirements Document

**Version:** 1.0  
**Last Updated:** January 2025  
**Owner:** PLUS Engineering

---

## 1. Overview

**The Goal:** Create an automated weekly email for tutors that celebrates their impact and reinforces best practices using data extracted from tutoring session recordings via the **TACT Pipeline**.

**Core Philosophy:**
- **Grounded in Reality:** All insights must be derived from the actual TACT pipeline output. If the information is not present in the transcript, we do not invent it.
- **Celebration First, Coaching Second:** The tone is encouraging and positive—like "Spotify Wrapped" for your tutoring week. It is NOT a performance review.

---

## 2. User Stories

### Primary User: Tutor
> "As a tutor, I want to receive a weekly summary of my tutoring sessions so I can see what I'm doing well and how I can improve."

### Secondary User: Program Manager
> "As a program manager, I want tutors to receive automated feedback so they feel supported and continuously develop their skills."

---

## 3. Feature Scope

### MVP (v1.0)
| Feature | Priority | Status |
|---------|----------|--------|
| Hero greeting with personalized headline | P0 | ✅ |
| Week-at-a-glance metrics (sessions, students, minutes) | P0 | ✅ |
| Talk ratio visualization | P0 | ✅ |
| Praise count detection | P0 | ✅ |
| Question count detection | P0 | ✅ |
| Think time analysis | P0 | ✅ |
| Tutor archetype assignment | P1 | ✅ |
| Highlight quote extraction | P1 | ✅ |
| Coaching tip generation | P1 | ✅ |
| Student goal progress rings | P2 | ✅ |
| Feedback poll | P2 | ✅ |

### Future Considerations (v2.0+)
- Week-over-week comparison
- Peer benchmarking (anonymized)
- Deep links to training resources
- Goal setting interface

---

## 4. Data Sources

### Input: TACT Pipeline
The TACT (Transcript Analysis for Coaching Tutors) pipeline processes multi-modal recordings and produces structured JSON output.

**Available Data Points:**
- Session metadata: filename, timestamp, tutor, school
- Events array: timestamped utterances with speaker labels
- Duration and silence/inactivity periods

### Derived Metrics
| Metric | Source | Method |
|--------|--------|--------|
| Session count | File count | Algorithmic |
| Student count | Unique speaker names | Algorithmic |
| Talk ratio | Sum of duration by speaker | Algorithmic |
| Praise count | Pattern matching | Algorithmic |
| Question count | Utterances ending with "?" | Algorithmic |
| Think time | Avg pause after questions | Algorithmic |
| Highlight quote | Best praise/empowerment moment | Algorithmic/LLM |
| Coaching tip | Based on metrics | Algorithmic/LLM |

### Mock Data (Not from TACT for MVP)
- Zoom metadata (session dates, recording count)
- Student goal progress (from APPS Goal Performance API)

---

## 5. Success Metrics

### Tier 1: Technical Validation
- **Reliability:** Generate Weekly Wrap for 95%+ active tutors
- **Accuracy:** Spot-check 10 reports against raw transcripts

### Tier 2: Engagement
- **Open Rate:** Target > 40%
- **CTR:** Target > 10%

### Tier 3: Usefulness
- **Feedback Poll:** "Was this useful?" (Yes / Somewhat / No)
- **User Interviews:** 5-10 tutors post-launch

---

## 6. Constraints & Dependencies

### Technical Constraints
- Must render correctly in major email clients (Gmail, Outlook, Apple Mail)
- Maximum email size: 102KB
- No JavaScript execution in email

### Dependencies
- TACT Pipeline v0.0.7+ for transcript data
- PLUS Database for tutor profiles
- APPS API for student goal data (future)

---

## 7. Content Sections

1. **Hero Greeting** — Personalized adaptive headline
2. **At a Glance** — Volume metrics in circles (with adaptive styling)
3. **Your Tutoring Style** — Talk ratio, think time with badges
4. **Insights** — Strength + Growth area (compact view)
5. **Student Goal Progress** — Dual-ring charts (hidden if no students)
6. **Highlight Moment** — Verbatim quote (hidden if none)
7. **Try This Week** — Coaching suggestion (hidden if none)
8. **Feedback** — 3-option poll

---

## 8. Design Principles

1. **Celebrate, don't evaluate** — Tone is encouraging, not punitive
2. **Ground in data** — Every insight links to a measurable metric
3. **Adapt to edge cases** — Handle zeros, short sessions, missing data gracefully
4. **Respect time** — Can be scanned in 30 seconds
5. **Delight** — "Spotify Wrapped" energy, not corporate memo

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2025 | Initial specification |
