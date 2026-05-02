from datetime import datetime


def analyze_mood_trends(mood_logs: list) -> dict:
    if not mood_logs:
        return {'average': 0, 'trend': 'no_data', 'streak_alert': False, 'insights': []}

    scores = [log['score'] for log in mood_logs]
    average = sum(scores) / len(scores)

    # Trend: compare recent 7 vs previous 7
    if len(scores) >= 14:
        recent = sum(scores[-7:]) / 7
        older = sum(scores[-14:-7]) / 7
        trend = 'improving' if recent > older + 0.3 else ('declining' if recent < older - 0.3 else 'stable')
    elif len(scores) >= 3:
        trend = 'improving' if scores[-1] > scores[0] else ('declining' if scores[-1] < scores[0] else 'stable')
    else:
        trend = 'insufficient_data'

    # Alert: 3+ consecutive very low mood days
    streak_alert = len(scores) >= 3 and all(s <= 2 for s in scores[-3:])

    insights = []
    if average >= 4.0:
        insights.append("You've been maintaining a very positive mood! Keep nurturing what's working. 🌟")
    elif average >= 3.0:
        insights.append("Your mood has been moderate. Small daily wins can shift your outlook. 💪")
    else:
        insights.append("It looks like you've been having a tough stretch. You don't have to face it alone. 💙")

    if streak_alert:
        insights.append("You've had several difficult days. Consider reaching out to someone you trust. 🤗")

    if trend == 'improving':
        insights.append("Great news — your mood has been trending upward recently! 📈")
    elif trend == 'declining':
        insights.append("Your mood has been dipping lately. Let's work on some small positive habits. 🌱")

    return {
        'average': round(average, 2),
        'trend': trend,
        'streak_alert': streak_alert,
        'insights': insights,
        'total_entries': len(mood_logs)
    }


def get_emotion_distribution(mood_logs: list) -> dict:
    dist = {}
    for log in mood_logs:
        e = log.get('emotion_tag') or 'neutral'
        dist[e] = dist.get(e, 0) + 1
    return dist


def format_chart_data(mood_logs: list) -> dict:
    labels, data = [], []
    for log in mood_logs:
        raw = log['created_at']
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            dt = datetime.strptime(raw, '%Y-%m-%d %H:%M:%S')
        labels.append(dt.strftime('%b %d'))
        data.append(log['score'])
    return {'labels': labels, 'data': data}
