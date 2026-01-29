let currentTutor = null;

// Initialize with embedded data
function loadData() {
    populateTutorSelect();
}

function populateTutorSelect() {
    const select = document.getElementById('tutor-select');
    const names = Object.keys(tutorData);

    names.forEach(name => {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
    });

    select.addEventListener('change', e => loadTutor(e.target.value));

    if (names.length > 0) loadTutor(names[0]);
}

// Generate contextual greeting based on metrics
function getAdaptiveGreeting(firstName, m) {
    const hasPraise = m.praise_count >= 5;
    const hasGoodBalance = m.talk_ratio_tutor_pct < 60;
    const hasPatience = m.avg_think_time_seconds >= 5;
    const hasQuestions = m.question_count >= 15;
    const shortSession = m.total_minutes < 10;
    const noStudents = m.students === 0;

    // Determine greeting level
    let spaced, compact;

    if (noStudents || shortSession) {
        // Minimal session - neutral greeting
        spaced = `Here's your week, ${firstName}`;
        compact = `Your week, ${firstName} 📊`;
    } else if (hasPraise && hasGoodBalance) {
        // Excellent - full celebration
        spaced = `Great week, ${firstName}!`;
        compact = `Great week, ${firstName}! 🎉`;
    } else if (hasPraise || hasPatience || hasQuestions) {
        // Good in some areas
        spaced = `Nice work, ${firstName}!`;
        compact = `Nice work, ${firstName}! 👍`;
    } else if (hasGoodBalance) {
        // Good listener but needs more praise
        spaced = `Week in review, ${firstName}`;
        compact = `Your week, ${firstName} 📋`;
    } else {
        // Neutral - room to grow
        spaced = `Your week, ${firstName}`;
        compact = `Your week, ${firstName} 📝`;
    }

    return { spaced, compact };
}


function loadTutor(name) {
    const t = tutorData[name];
    if (!t) return;
    currentTutor = t;

    const m = t.metrics;
    const firstName = t.tutor_name.split(' ')[0];

    // Week dates
    document.getElementById('week-dates').textContent = t.week_dates_display || '—';
    document.getElementById('week-compact').textContent = t.week_dates_display || '—';

    // Greetings - adaptive based on performance
    const greeting = getAdaptiveGreeting(firstName, m);
    document.getElementById('greeting-spaced').textContent = greeting.spaced;
    document.getElementById('greeting-compact').textContent = greeting.compact;

    // Session badge
    document.getElementById('session-badge').textContent = `📹 Based on ${m.sessions} recording${m.sessions !== 1 ? 's' : ''}`;

    // Archetype - from JSON, show null state if missing
    const archetype = t.archetype;
    const archetypeBadge = document.getElementById('archetype-badge');
    if (archetype) {
        archetypeBadge.textContent = archetype;
        archetypeBadge.classList.remove('null-state');
    } else {
        archetypeBadge.textContent = '— Awaiting LLM';
        archetypeBadge.classList.add('null-state');
    }

    // Hero praise
    document.getElementById('hero-praise').textContent = m.praise_count;

    // Mini stats
    document.getElementById('mini-sessions').textContent = m.sessions;
    document.getElementById('mini-students').textContent = m.students;
    document.getElementById('mini-minutes').textContent = m.total_minutes;

    // Circles with varied sizes
    renderCircles(m);

    // Ratio
    document.getElementById('ratio-tutor').textContent = m.talk_ratio_tutor_pct;
    document.getElementById('ratio-student').textContent = m.talk_ratio_student_pct;
    document.getElementById('ratio-bar').style.width = m.talk_ratio_tutor_pct + '%';

    const talkBadge = m.talk_ratio_tutor_pct > 70 ? ['Room to grow', 'badge-yellow'] : ['Good balance', 'badge-green'];
    const talkEl = document.getElementById('talk-badge');
    talkEl.textContent = talkBadge[0];
    talkEl.className = 'badge ' + talkBadge[1];

    // Think time
    document.getElementById('think-time').textContent = m.avg_think_time_seconds;
    const thinkBadge = m.avg_think_time_seconds < 3 ? ['Try waiting longer', 'badge-yellow'] : ['On target', 'badge-green'];
    const thinkEl = document.getElementById('think-badge');
    thinkEl.textContent = thinkBadge[0];
    thinkEl.className = 'badge ' + thinkBadge[1];

    // Insights (compact)
    renderInsights(m);

    // Students
    renderStudents(t.student_goals);

    // Quote - from JSON
    const quote = t.highlight_quote;
    const quoteLabel = t.highlight_label;

    const quoteSpaced = document.getElementById('quote-spaced');
    const quoteLabelSpaced = document.getElementById('quote-label-spaced');
    const quoteCompact = document.getElementById('quote-compact');

    if (quote) {
        quoteSpaced.textContent = `"${quote}"`;
        quoteSpaced.classList.remove('null-state');
        quoteCompact.textContent = quote;
        quoteCompact.classList.remove('null-state');
    } else {
        quoteSpaced.textContent = '[Awaiting LLM extraction]';
        quoteSpaced.classList.add('null-state');
        quoteCompact.textContent = '[Awaiting LLM extraction]';
        quoteCompact.classList.add('null-state');
    }

    if (quoteLabel) {
        quoteLabelSpaced.textContent = quoteLabel;
    } else {
        quoteLabelSpaced.textContent = '—';
    }

    // Tip - from JSON
    const tip = t.coaching_tip;
    const tipSpaced = document.getElementById('tip-spaced');
    const tipCompact = document.getElementById('tip-compact');
    const tipReason = document.getElementById('tip-reason-spaced');

    if (tip) {
        tipSpaced.textContent = tip;
        tipSpaced.classList.remove('null-state');
        tipCompact.textContent = tip;
        tipCompact.classList.remove('null-state');
    } else {
        tipSpaced.textContent = '[Awaiting LLM suggestion]';
        tipSpaced.classList.add('null-state');
        tipCompact.textContent = '[Awaiting LLM suggestion]';
        tipCompact.classList.add('null-state');
    }
    tipReason.textContent = 'Based on your session metrics';

    // Hide empty sections
    hideEmptySections(t, m);
}

// Hide sections when no meaningful data exists
function hideEmptySections(t, m) {
    // Students section - hide if no students
    const studentsSection = document.getElementById('section-students');
    if (m.students === 0) {
        studentsSection.style.display = 'none';
    } else {
        studentsSection.style.display = '';
    }

    // Quote sections - hide if no highlight quote
    const quoteSpaced = document.getElementById('section-quote-spaced');
    const quoteCompact = document.getElementById('section-quote-compact');
    if (!t.highlight_quote) {
        quoteSpaced.style.display = 'none';
        quoteCompact.style.display = 'none';
    } else {
        quoteSpaced.style.display = '';
        quoteCompact.style.display = '';
    }

    // Tip sections - hide if no coaching tip
    const tipSpaced = document.getElementById('section-tip-spaced');
    const tipCompact = document.getElementById('section-tip-compact');
    if (!t.coaching_tip) {
        tipSpaced.style.display = 'none';
        tipCompact.style.display = 'none';
    } else {
        tipSpaced.style.display = '';
        tipCompact.style.display = '';
    }
}


function renderCircles(m) {
    const container = document.getElementById('circles-container');

    // Determine sizes and accents based on actual values
    // Only accent metrics that are worth celebrating
    const praiseGood = m.praise_count >= 5;
    const questionsGood = m.question_count >= 15;
    const minutesGood = m.total_minutes >= 20;

    const metrics = [
        { label: 'Praise<br>Moments', value: m.praise_count, tip: 'Positive phrases detected', accent: praiseGood, muted: m.praise_count === 0, size: 'lg' },
        { label: 'Questions<br>Asked', value: m.question_count, tip: 'Tutor questions', accent: questionsGood, muted: m.question_count === 0, size: 'lg' },
        { label: 'Minutes', value: m.total_minutes, tip: 'Total duration', accent: minutesGood, muted: m.total_minutes < 5, size: 'md' },
        { label: 'Students', value: m.students, tip: 'Unique students', accent: false, muted: m.students === 0, size: 'sm' },
        { label: 'Sessions', value: m.sessions, tip: 'Zoom recordings', accent: false, muted: false, size: 'sm' }
    ];

    container.innerHTML = metrics.map(met => {
        let circleClass = `stat-circle size-${met.size}`;
        let numberStyle = '';

        if (met.accent) {
            circleClass += ' accent';
            numberStyle = 'style="color: var(--teal-dark);"';
        } else if (met.muted) {
            circleClass += ' muted';
            numberStyle = 'style="color: var(--text-muted);"';
        }

        return `
            <div class="${circleClass}" data-tip="${met.tip}">
                <span class="stat-number" ${numberStyle}>${met.value}</span>
                <span class="stat-label">${met.label}</span>
            </div>
        `;
    }).join('');
}

function renderInsights(m) {
    const container = document.getElementById('insights-row');

    // Edge case: No students or very short session
    if (m.students === 0 || m.total_minutes < 5) {
        container.innerHTML = `
            <div class="insight-block strength">
                <div class="insight-icon">📹</div>
                <div class="insight-title">Session Logged</div>
                <div class="insight-text"><span class="insight-metric">${m.total_minutes} minutes</span> recorded this week.</div>
            </div>
            <div class="insight-block growth">
                <div class="insight-icon">🚀</div>
                <div class="insight-title">Ready to go</div>
                <div class="insight-text">System is tracking your sessions correctly.</div>
            </div>
        `;
        return;
    }

    // Determine actual strength based on metrics
    let strengthIcon = '💪';
    let strengthTitle = '';
    let strengthText = '';

    if (m.praise_count >= 5) {
        // High praise - celebrate it
        strengthTitle = 'You celebrated a lot';
        strengthText = `<span class="insight-metric">${m.praise_count} encouraging moments</span> — your students feel supported.`;
    } else if (m.talk_ratio_tutor_pct < 50) {
        // Great student voice - that's a strength!
        strengthIcon = '👂';
        strengthTitle = 'Great listener';
        strengthText = `Students talked <span class="insight-metric">${m.talk_ratio_student_pct}%</span> of the time — you gave them space to think.`;
    } else if (m.question_count >= 20) {
        // Lots of questions - different strength
        strengthIcon = '❓';
        strengthTitle = 'Question pro';
        strengthText = `You asked <span class="insight-metric">${m.question_count} questions</span> — keeping students engaged.`;
    } else if (m.avg_think_time_seconds >= 5) {
        // Patience is a strength
        strengthIcon = '⏳';
        strengthTitle = 'Patient pauses';
        strengthText = `<span class="insight-metric">${m.avg_think_time_seconds}s</span> avg think time — students had room to process.`;
    } else {
        // Fallback: find something neutral
        strengthIcon = '📊';
        strengthTitle = 'Session tracked';
        strengthText = `<span class="insight-metric">${m.total_minutes} minutes</span> of tutoring logged this week.`;
    }

    // Determine growth area based on metrics
    let growthIcon = '🌱';
    let growthTitle = '';
    let growthText = '';

    if (m.praise_count === 0 && m.talk_ratio_tutor_pct <= 50) {
        // Low praise but good talk balance - focus on encouragement
        growthTitle = 'Add encouragement';
        growthText = `Try specific praise like <span class="insight-metric">"Great job checking your work!"</span>`;
    } else if (m.talk_ratio_tutor_pct > 70) {
        // Too much tutor talk
        growthTitle = 'Let them talk more';
        growthText = `You talked <span class="insight-metric">${m.talk_ratio_tutor_pct}%</span> of the time. Try "What do you think?"`;
    } else if (m.avg_think_time_seconds < 3 && m.question_count > 5) {
        // Fast responses after questions
        growthTitle = 'More wait time';
        growthText = `<span class="insight-metric">${m.avg_think_time_seconds}s</span> think time is quick. Count to 5 after questions.`;
    } else if (m.praise_count < 5 && m.praise_count > 0) {
        // Some praise but could add more
        growthTitle = 'Keep celebrating';
        growthText = `<span class="insight-metric">${m.praise_count} praise moments</span> this week. More helps build confidence.`;
    } else {
        // Everything looks good
        growthTitle = 'Keep it up';
        growthText = `You talked <span class="insight-metric">${m.talk_ratio_tutor_pct}%</span> of the time. Great balance!`;
    }

    container.innerHTML = `
        <div class="insight-block strength">
            <div class="insight-icon">${strengthIcon}</div>
            <div class="insight-title">${strengthTitle}</div>
            <div class="insight-text">${strengthText}</div>
        </div>
        <div class="insight-block growth">
            <div class="insight-icon">${growthIcon}</div>
            <div class="insight-title">${growthTitle}</div>
            <div class="insight-text">${growthText}</div>
        </div>
    `;
}

function renderStudents(goals) {
    const spacedCont = document.getElementById('students-spaced');
    const compactCont = document.getElementById('students-compact');

    if (!goals || goals.length === 0) {
        spacedCont.innerHTML = '<p class="null-state">No student data available</p>';
        compactCont.innerHTML = '<p class="null-state">No student data available</p>';
        return;
    }

    // Spaced style
    spacedCont.innerHTML = goals.slice(0, 3).map(s => {
        const progOffset = 226 * (1 - s.progress_pct / 100);
        const effOffset = 163 * (1 - s.effort_pct / 100);
        return `
            <div class="student-card">
                <div class="student-name">${s.name}</div>
                <div style="display: flex; justify-content: center;">
                    <svg width="80" height="80" viewBox="0 0 80 80" style="transform: rotate(-90deg);">
                        <circle cx="40" cy="40" r="36" fill="none" stroke="var(--border)" stroke-width="6"/>
                        <circle cx="40" cy="40" r="36" fill="none" stroke="var(--green)" stroke-width="6" 
                            stroke-dasharray="226" stroke-dashoffset="${progOffset}" stroke-linecap="round"/>
                        <circle cx="40" cy="40" r="26" fill="none" stroke="var(--border)" stroke-width="5"/>
                        <circle cx="40" cy="40" r="26" fill="none" stroke="var(--yellow)" stroke-width="5" 
                            stroke-dasharray="163" stroke-dashoffset="${effOffset}" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="student-pcts">
                    <span class="progress">${s.progress_pct}%</span> / <span class="effort">${s.effort_pct}%</span>
                </div>
            </div>
        `;
    }).join('');

    // Compact style
    compactCont.innerHTML = goals.slice(0, 4).map(s => {
        const circumference = 94.2;
        const progOffset = circumference * (1 - s.progress_pct / 100);
        const effOffset = circumference * (1 - s.effort_pct / 100);
        return `
            <div class="student">
                <div class="student-goals">
                    <div class="goal-ring">
                        <svg viewBox="0 0 36 36">
                            <circle class="ring-bg" cx="18" cy="18" r="15"/>
                            <circle class="ring-fill green" cx="18" cy="18" r="15" stroke-dasharray="94.2" stroke-dashoffset="${progOffset}"/>
                        </svg>
                        <span class="ring-pct">${s.progress_pct}%</span>
                    </div>
                    <div class="goal-ring">
                        <svg viewBox="0 0 36 36">
                            <circle class="ring-bg" cx="18" cy="18" r="15"/>
                            <circle class="ring-fill yellow" cx="18" cy="18" r="15" stroke-dasharray="94.2" stroke-dashoffset="${effOffset}"/>
                        </svg>
                        <span class="ring-pct">${s.effort_pct}%</span>
                    </div>
                </div>
                <div class="student-name">${s.name}</div>
            </div>
        `;
    }).join('');
}

function setStyle(style) {
    document.body.className = 'style-' + style;
    document.getElementById('btn-spaced').classList.toggle('active', style === 'spaced');
    document.getElementById('btn-compact').classList.toggle('active', style === 'compact');
}

// Init
loadData();
