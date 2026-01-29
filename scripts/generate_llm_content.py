#!/usr/bin/env python3
"""
Generate LLM content for Weekly Wrap.
Reads TACT transcriptions and produces highlight quotes + coaching tips.
"""

import json
from pathlib import Path
import re

DATA_DIR = Path('/Users/billguo/Desktop/Vibe Coding/TACT-Weekly-Wrap/data/transcriptions/tact-v0.0.7')
OUTPUT_FILE = Path('/Users/billguo/Desktop/Vibe Coding/TACT-Weekly-Wrap/output/weekly_wrap_data.json')

# Patterns for highlight moment selection
EMPOWERMENT_PATTERNS = [
    r"you('ve| have) got this",
    r"try (it|this) (on )?your(self)?",
    r"let you",
    r"you can do (it|this)",
    r"give it a (shot|try)",
    r"believe in you",
    r"i('m| am) going to let you",
    r"keep (it )?up",
    r"keep working",
    r"you're doing (so )?(well|great|good|amazing)",
    r"taking your time",
    r"don't give up",
]

PRAISE_PATTERNS = [
    r"(that's |you're )?(so )?(doing )?(great|good|awesome|amazing|excellent|perfect|wonderful|fantastic)",
    r"nice (work|job|one)",
    r"well done",
    r"good job",
    r"proud of you",
    r"you (got|nailed) (it|this)",
    r"exactly( right)?",
    r"love (that|it|how)",
    r"that's (exactly )?right",
    r"you remembered",
    r"great (work|job|thinking|question)",
    r"i('m)? impressed",
]

# Patterns to EXCLUDE (greetings, questions, mundane)
EXCLUDE_PATTERNS = [
    r"^(hi|hello|hey|how)",
    r"can you hear me",
    r"my name is",
    r"share your screen",
    r"^okay\.?$",
    r"^yeah\.?$",
    r"^um\.?$",
    r"^mhm\.?$",
    r"good\. how",
    r"^good\.$",
    r"what time",
    r"did you sleep",
    r"going to bed",
]

def score_utterance(text: str) -> tuple:
    """Score an utterance for highlight potential. Returns (empowerment_score, praise_score, length)."""
    text_lower = text.lower().strip()
    
    # Skip excluded patterns
    for p in EXCLUDE_PATTERNS:
        if re.search(p, text_lower):
            return (0, 0, 0)
    
    emp_score = sum(1 for p in EMPOWERMENT_PATTERNS if re.search(p, text_lower))
    praise_score = sum(1 for p in PRAISE_PATTERNS if re.search(p, text_lower))
    
    # Penalize very short or very long utterances
    if len(text) < 25:
        return (0, 0, 0)
    
    length_score = 1 if 30 < len(text) < 200 else 0.5
    
    # Bonus for specific, detailed praise
    if len(text) > 50 and (emp_score > 0 or praise_score > 0):
        length_score += 0.5
    
    return (emp_score, praise_score, length_score)

def select_highlight(utterances: list) -> dict:
    """Select the best highlight moment from tutor utterances."""
    if not utterances:
        return {"quote": None, "label": None}
    
    scored = []
    for u in utterances:
        text = u.get('text', '').strip()
        if len(text) < 25:
            continue
        emp, praise, length = score_utterance(text)
        total = emp * 3 + praise * 2 + length  # Weight empowerment higher
        if total > 0:
            scored.append((total, text, emp, praise))
    
    if not scored:
        # Fallback: find any utterance with "good" or similar
        for u in utterances:
            text = u.get('text', '').strip()
            if len(text) > 40 and any(w in text.lower() for w in ['good', 'great', 'nice', 'keep']):
                scored.append((0.5, text, 0, 1))
                break
    
    if not scored:
        return {"quote": None, "label": None}
    
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_text, emp, praise = scored[0]
    
    # Determine label based on what triggered the score
    if emp > 0:
        label = "Empowering Independence"
    elif praise > 0:
        label = "Building Confidence"
    else:
        label = "Clear Guidance"
    
    # Clean up the quote
    quote = best_text.strip()
    if len(quote) > 150:
        quote = quote[:147] + "..."
    
    return {"quote": quote, "label": label}

def generate_coaching_tip(metrics: dict) -> dict:
    """Generate coaching suggestion based on metrics."""
    talk_ratio = metrics.get('talk_ratio_tutor_pct', 50)
    think_time = metrics.get('avg_think_time_seconds', 3.0)
    praise_count = metrics.get('praise_count', 0)
    sessions = metrics.get('sessions', 1)
    
    praise_per_session = praise_count / max(sessions, 1)
    
    # Apply coaching logic from system prompts
    if talk_ratio > 75:
        return {
            "tip": "Try asking 'What do you think?' and waiting for their answer",
            "reason": f"You talked {talk_ratio}% of the time—letting students explain more helps them learn."
        }
    elif think_time < 3.0:
        return {
            "tip": "After asking a question, count to 5 before jumping in",
            "reason": f"Your {think_time:.1f}s think time is below the 3-5s target."
        }
    elif praise_per_session < 5:
        return {
            "tip": "Add specific praise like 'Great job checking your work!'",
            "reason": f"You averaged {praise_per_session:.1f} praise moments per session."
        }
    else:
        # Celebrate what's working
        return {
            "tip": "Keep doing what you're doing—your balance is great!",
            "reason": f"Great talk balance ({talk_ratio}%) and {think_time:.1f}s think time."
        }

def determine_archetype(metrics: dict) -> str:
    """Determine tutor archetype based on metrics."""
    talk_ratio = metrics.get('talk_ratio_tutor_pct', 50)
    think_time = metrics.get('avg_think_time_seconds', 3.0)
    praise_count = metrics.get('praise_count', 0)
    questions = metrics.get('question_count', 0)
    sessions = metrics.get('sessions', 1)
    
    praise_per_session = praise_count / max(sessions, 1)
    questions_per_session = questions / max(sessions, 1)
    
    # Archetype logic
    if questions_per_session > 20:
        return "🎯 The Question Master"
    elif praise_per_session > 15:
        return "💫 The Encourager"
    elif talk_ratio < 50:
        return "👂 The Listener"
    elif think_time > 5:
        return "🧘 The Patient Guide"
    elif talk_ratio > 80:
        return "📚 The Explainer"
    else:
        return "⚡ Steady & Strong"

def main():
    # Load existing data
    with open(OUTPUT_FILE) as f:
        tutor_data = json.load(f)
    
    # Load all transcriptions and group by tutor
    tutor_utterances = {}
    
    for filepath in DATA_DIR.glob('*_pydantic.json'):
        with open(filepath) as f:
            data = json.load(f)
        
        # Extract tutor name from folder name
        folder = data.get('metadata', {}).get('parent_folder_name', '')
        tutor_name = folder.split('_')[-1].replace('_', ' ').strip()
        
        # Map to actual tutor names in our data
        name_map = {
            'Baik': 'Suhyun Baik',
            'Adebayo': 'Oluwatooni Adebayo',
            'Crawford': 'Paisley Crawford',
            'Jones': 'Kathryn Jones',
            'Puja': 'Sumeda Puja',
            'Gandhi': 'Varaun Gandhi',
            'Dalvi': 'Jai Dalvi',
            'Taine': 'Iraine Taine',
            'Keys': 'Marena Keys',
            'Shetty': 'Aditya Shetty',
            'Chen': 'Alicia Chen',
            'Lamberton': 'Kristen Lamberton',
            'Miene': 'Victor Miene',
            'Duncan': 'Riona Duncan',
            'Li': 'Mandy Li',
        }
        
        for surname, full_name in name_map.items():
            if surname in tutor_name:
                tutor_name = full_name
                break
        
        if tutor_name not in tutor_data:
            continue
        
        # Extract tutor utterances
        utterances = []
        for event in data.get('events', []):
            if event.get('event_type') == 'spoken_utterance' and event.get('speaker_label') == 'tutor':
                utterances.append({
                    'text': event.get('text', ''),
                    'offset': event.get('offset_seconds', 0)
                })
        
        if tutor_name not in tutor_utterances:
            tutor_utterances[tutor_name] = []
        tutor_utterances[tutor_name].extend(utterances)
    
    # Generate LLM content for each tutor
    for tutor_name, data in tutor_data.items():
        utterances = tutor_utterances.get(tutor_name, [])
        metrics = data.get('metrics', {})
        
        # Select highlight
        highlight = select_highlight(utterances)
        data['highlight_quote'] = highlight['quote']
        data['highlight_label'] = highlight['label']
        
        # Generate coaching tip
        coaching = generate_coaching_tip(metrics)
        data['coaching_tip'] = coaching['tip']
        
        # Determine archetype
        data['archetype'] = determine_archetype(metrics)
        
        print(f"✓ {tutor_name}")
        print(f"  Quote: {highlight['quote'][:60] if highlight['quote'] else 'N/A'}...")
        print(f"  Archetype: {data['archetype']}")
        print()
    
    # Save updated data
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tutor_data, f, indent=2)
    
    print(f"Updated {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
