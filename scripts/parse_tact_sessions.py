#!/usr/bin/env python3
"""
Parse TACT session pydantic JSON files and aggregate metrics by tutor.

Usage:
    python parse_tact_sessions.py --input data/transcriptions/tact-v0.0.7 --output output/weekly_wrap_data.json
"""

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime


# Praise patterns (case-insensitive)
PRAISE_PATTERNS = [
    r'\bnice\b', r'\bgreat\b', r'\bgood\s*job\b', r'\bperfect\b',
    r'\bexcellent\b', r'\bawesome\b', r'\bwell\s*done\b', r'\bcorrect\b',
    r'\bexactly\b', r'\byes\!', r'\byou\s*got\s*it\b', r'\bbravo\b',
    r'\bfantastic\b', r'\bwonderful\b', r'\bimpressive\b', r'\bkeep\s*going\b',
    r'\byou\'re\s*doing\s*great\b', r'\bthat\'s\s*right\b', r'\bgood\s*thinking\b',
    r'\bi\s*like\s*how\s*you\b'
]

# Compile patterns for efficiency
PRAISE_REGEX = re.compile('|'.join(PRAISE_PATTERNS), re.IGNORECASE)


def extract_tutor_name(parent_folder_name: str) -> str:
    """Extract tutor name from parent_folder_name like 'Jefferson_Codding_2025-10-31_16:10_Suhyun_Baik'"""
    if not parent_folder_name:
        return "Unknown"
    
    # Pattern: School_Teacher_Date_Time_Firstname_Lastname
    parts = parent_folder_name.split('_')
    
    # Try to find name parts at the end (usually last two parts are first/last name)
    if len(parts) >= 2:
        # Check if last parts look like names (not dates/numbers)
        last_parts = []
        for part in reversed(parts):
            if not re.match(r'^\d', part) and ':' not in part:
                last_parts.insert(0, part)
                if len(last_parts) == 2:
                    break
            else:
                break
        
        if last_parts:
            return ' '.join(last_parts)
    
    return parent_folder_name


def count_praises(text: str) -> int:
    """Count praise phrases in text."""
    if not text:
        return 0
    matches = PRAISE_REGEX.findall(text)
    return len(matches)


def is_question(text: str) -> bool:
    """Check if utterance is a question (ends with ?)."""
    if not text:
        return False
    # Exclude rhetorical fillers
    rhetorical = ['right?', 'okay?', 'ok?', 'you know?', 'huh?', 'yeah?']
    text_lower = text.strip().lower()
    if any(text_lower.endswith(r) for r in rhetorical):
        return False
    return text.strip().endswith('?')


def parse_session(filepath: Path) -> dict:
    """Parse a single pydantic JSON session file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Extract metadata
    metadata = data.get('metadata', {})
    parent_folder = metadata.get('parent_folder_name', '')
    tutor_name = extract_tutor_name(parent_folder)
    session_id = data.get('filename', filepath.stem)
    
    # Extract date from parent folder or processed_at
    processed_at = metadata.get('processed_at_utc', '')
    session_date = None
    if processed_at:
        try:
            session_date = datetime.fromisoformat(processed_at.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        except:
            pass
    
    # Process events
    events = data.get('events', [])
    
    students = set()
    tutor_talk_seconds = 0.0
    student_talk_seconds = 0.0
    praise_count = 0
    question_count = 0
    
    # For think time calculation
    tutor_questions = []
    
    total_duration_seconds = 0.0
    
    for event in events:
        event_type = event.get('event_type')
        offset = event.get('offset_seconds', 0) or 0
        duration = event.get('duration_seconds', 0) or 0
        
        if event_type == 'spoken_utterance':
            speaker_label = event.get('speaker_label', '')
            speaker_name = event.get('speaker_name', '')
            text = event.get('text', '')
            
            if speaker_label == 'tutor':
                tutor_talk_seconds += duration
                praise_count += count_praises(text)
                
                if is_question(text):
                    question_count += 1
                    tutor_questions.append({
                        'offset': offset,
                        'text': text
                    })
                    
            elif speaker_label == 'student':
                student_talk_seconds += duration
                if speaker_name:
                    students.add(speaker_name)
        
        # Track total session duration
        if offset + duration > total_duration_seconds:
            total_duration_seconds = offset + duration
    
    # Calculate think time (avg gap after tutor question before next utterance)
    think_times = []
    sorted_events = sorted([e for e in events if e.get('event_type') == 'spoken_utterance'], 
                          key=lambda x: x.get('offset_seconds', 0))
    
    for i, q in enumerate(tutor_questions):
        q_end = q['offset']
        # Find next utterance
        for event in sorted_events:
            if event.get('offset_seconds', 0) > q_end + 0.5:  # Allow small gap
                # Check if it's within reasonable time (30s)
                gap = event.get('offset_seconds', 0) - q_end
                if gap < 30:
                    think_times.append(gap)
                break
    
    avg_think_time = sum(think_times) / len(think_times) if think_times else 0.0
    
    return {
        'session_id': session_id,
        'tutor_name': tutor_name,
        'session_date': session_date,
        'students': list(students),
        'tutor_talk_seconds': round(tutor_talk_seconds, 1),
        'student_talk_seconds': round(student_talk_seconds, 1),
        'total_duration_seconds': round(total_duration_seconds, 1),
        'praise_count': praise_count,
        'question_count': question_count,
        'avg_think_time_seconds': round(avg_think_time, 1)
    }


def aggregate_by_tutor(sessions: list) -> dict:
    """Aggregate session data by tutor name."""
    tutor_data = defaultdict(lambda: {
        'sessions': [],
        'all_students': set(),
        'total_tutor_talk_seconds': 0.0,
        'total_student_talk_seconds': 0.0,
        'total_duration_seconds': 0.0,
        'total_praise_count': 0,
        'total_question_count': 0,
        'think_times': []
    })
    
    for session in sessions:
        tutor = session['tutor_name']
        data = tutor_data[tutor]
        
        data['sessions'].append({
            'session_id': session['session_id'],
            'date': session['session_date'],
            'students': session['students'],
            'tutor_talk_seconds': session['tutor_talk_seconds'],
            'student_talk_seconds': session['student_talk_seconds'],
            'praise_count': session['praise_count'],
            'question_count': session['question_count']
        })
        
        data['all_students'].update(session['students'])
        data['total_tutor_talk_seconds'] += session['tutor_talk_seconds']
        data['total_student_talk_seconds'] += session['student_talk_seconds']
        data['total_duration_seconds'] += session['total_duration_seconds']
        data['total_praise_count'] += session['praise_count']
        data['total_question_count'] += session['question_count']
        
        if session['avg_think_time_seconds'] > 0:
            data['think_times'].append(session['avg_think_time_seconds'])
    
    # Build final output
    result = {}
    
    for tutor, data in tutor_data.items():
        total_talk = data['total_tutor_talk_seconds'] + data['total_student_talk_seconds']
        talk_ratio_tutor = round((data['total_tutor_talk_seconds'] / total_talk * 100) if total_talk > 0 else 0)
        talk_ratio_student = 100 - talk_ratio_tutor
        avg_think = round(sum(data['think_times']) / len(data['think_times']), 1) if data['think_times'] else 0.0
        
        result[tutor] = {
            'tutor_name': tutor,
            'week_dates_display': 'Nov 18 – 24, 2025',  # Mock - would come from Zoom API
            'metrics': {
                'sessions': len(data['sessions']),
                'students': len(data['all_students']),
                'total_minutes': round(data['total_duration_seconds'] / 60),
                'talk_ratio_tutor_pct': talk_ratio_tutor,
                'talk_ratio_student_pct': talk_ratio_student,
                'praise_count': data['total_praise_count'],
                'question_count': data['total_question_count'],
                'avg_think_time_seconds': avg_think
            },
            'students_list': sorted(list(data['all_students'])),
            'sessions_detail': data['sessions'],
            # Placeholders for LLM-generated content
            'highlight_quote': None,
            'highlight_label': None,
            'coaching_tip': None,
            'archetype': None,
            # Mock student goal data (would come from APPS API)
            'student_goals': [
                {'name': s.split()[0] + ' ' + (s.split()[1][0] + '.' if len(s.split()) > 1 else ''), 
                 'progress_pct': 75, 'effort_pct': 80}
                for s in sorted(list(data['all_students']))[:3]
            ]
        }
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Parse TACT session files')
    parser.add_argument('--input', '-i', required=True, help='Input directory with pydantic JSON files')
    parser.add_argument('--output', '-o', required=True, help='Output JSON file path')
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_path = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        return 1
    
    # Find all pydantic JSON files
    pydantic_files = list(input_dir.glob('*_pydantic.json'))
    print(f"Found {len(pydantic_files)} pydantic JSON files")
    
    # Parse each session
    sessions = []
    for filepath in pydantic_files:
        try:
            session_data = parse_session(filepath)
            sessions.append(session_data)
            print(f"  Parsed: {filepath.name} -> {session_data['tutor_name']} ({len(session_data['students'])} students)")
        except Exception as e:
            print(f"  Error parsing {filepath.name}: {e}")
    
    # Aggregate by tutor
    tutor_data = aggregate_by_tutor(sessions)
    
    print(f"\nAggregated data for {len(tutor_data)} tutors:")
    for tutor, data in tutor_data.items():
        m = data['metrics']
        print(f"  {tutor}: {m['sessions']} sessions, {m['students']} students, "
              f"{m['total_minutes']} min, {m['praise_count']} praises, {m['question_count']} questions")
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(tutor_data, f, indent=2)
    
    print(f"\nOutput written to: {output_path}")
    return 0


if __name__ == '__main__':
    exit(main())
