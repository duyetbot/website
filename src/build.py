#!/usr/bin/env python3
"""
Extract OpenClaw metrics for dashboard.

Parses session files and cron runs, aggregates by day,
and outputs data/metrics.json for the build script.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"
OPENCLAW_SESSIONS_DIR = Path("/root/.openclaw/agents/main/sessions")
OPENCLAW_CRON_DIR = Path("/root/.openclaw/cron/runs")

# Output file
METRICS_FILE = DATA_DIR / "metrics.json"

# How many days of history to include
DAYS_OF_HISTORY = 30


def parse_session_file(filepath):
    """Parse a single JSONL session file and extract metrics."""
    total_input = 0
    total_output = 0
    total_cost = 0.0
    message_count = 0
    session_timestamp = None

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Get session timestamp
                if event.get('type') == 'session' and 'timestamp' in event:
                    session_timestamp = event['timestamp']

                # Count messages and aggregate usage
                if event.get('type') == 'message':
                    msg = event.get('message', {})
                    usage = msg.get('usage', {})

                    if usage:
                        total_input += usage.get('input', 0)
                        total_output += usage.get('output', 0)
                        total_cost += usage.get('cost', {}).get('total', 0)
                        message_count += 1

    except Exception as e:
        print(f"  Warning: Error reading {filepath}: {e}")
        return None

    if session_timestamp is None:
        return None

    # Parse timestamp to get date
    try:
        dt = datetime.fromisoformat(session_timestamp.replace('Z', '+00:00'))
        date_str = dt.strftime('%Y-%m-%d')
    except:
        return None

    return {
        'date': date_str,
        'input_tokens': total_input,
        'output_tokens': total_output,
        'total_tokens': total_input + total_output,
        'cost': total_cost,
        'messages': message_count
    }


def aggregate_by_day(session_metrics):
    """Aggregate session metrics by day."""
    daily = defaultdict(lambda: {
        'sessions': 0,
        'input_tokens': 0,
        'output_tokens': 0,
        'total_tokens': 0,
        'cost': 0.0,
        'messages': 0
    })

    for session in session_metrics:
        if session is None:
            continue
        date = session['date']
        daily[date]['sessions'] += 1
        daily[date]['input_tokens'] += session['input_tokens']
        daily[date]['output_tokens'] += session['output_tokens']
        daily[date]['total_tokens'] += session['total_tokens']
        daily[date]['cost'] += session['cost']
        daily[date]['messages'] += session['messages']

    return dict(daily)


def parse_cron_runs():
    """Parse cron run files and extract status."""
    cron_runs = []

    if not OPENCLAW_CRON_DIR.exists():
        return cron_runs

    for filepath in OPENCLAW_CRON_DIR.glob("*.jsonl"):
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        run = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if run.get('action') == 'finished':
                        ts = run.get('ts', 0)
                        dt = datetime.fromtimestamp(ts / 1000)

                        cron_runs.append({
                            'job_id': run.get('jobId', 'unknown'),
                            'status': run.get('status', 'unknown'),
                            'summary': run.get('summary', ''),
                            'duration_ms': run.get('durationMs', 0),
                            'timestamp': dt.strftime('%Y-%m-%d %H:%M:%S'),
                            'timestamp_iso': dt.isoformat()
                        })

        except Exception as e:
            print(f"  Warning: Error reading cron file {filepath}: {e}")
            continue

    # Sort by timestamp descending
    cron_runs.sort(key=lambda x: x['timestamp_iso'], reverse=True)
    return cron_runs[:20]  # Last 20 runs


def get_job_names():
    """Map job IDs to human-readable names."""
    return {
        '82f03d0e-3a34-40b3-a42c-d0f0b69432d1': 'Daily AI Report',
        'bec3a0af-b326-46dd-b6a9-a43d37beb886': 'Config Backup',
        '10addaa3-b3ad-4849-8dbe-e298358e913d': 'Website Watch'
    }


def main():
    print("Extracting OpenClaw metrics...")

    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    # Parse all session files
    print("  Parsing session files...")
    session_metrics = []
    if OPENCLAW_SESSIONS_DIR.exists():
        for filepath in OPENCLAW_SESSIONS_DIR.glob("*.jsonl"):
            metrics = parse_session_file(filepath)
            if metrics:
                session_metrics.append(metrics)

    print(f"  Found {len(session_metrics)} sessions")

    # Aggregate by day
    daily_metrics = aggregate_by_day(session_metrics)

    # Filter to last N days and sort
    today = datetime.now().date()
    start_date = today - timedelta(days=DAYS_OF_HISTORY)

    daily_activity = []
    for i in range(DAYS_OF_HISTORY):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        data = daily_metrics.get(date, {
            'sessions': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
            'cost': 0.0,
            'messages': 0
        })
        daily_activity.append({
            'date': date,
            **data
        })

    # Calculate totals
    total_sessions = len(session_metrics)
    total_tokens = sum(s['total_tokens'] for s in session_metrics if s)
    total_cost = sum(s['cost'] for s in session_metrics if s)

    # Today's stats
    today_str = today.strftime('%Y-%m-%d')
    today_data = daily_metrics.get(today_str, {
        'sessions': 0,
        'total_tokens': 0,
        'cost': 0.0
    })

    # Parse cron runs
    print("  Parsing cron runs...")
    cron_runs = parse_cron_runs()

    # Add job names
    job_names = get_job_names()
    for run in cron_runs:
        run['job_name'] = job_names.get(run['job_id'], run['job_id'][:8])

    # Build output
    output = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_sessions': total_sessions,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'today_sessions': today_data['sessions'],
            'today_tokens': today_data['total_tokens'],
            'today_cost': today_data['cost']
        },
        'daily_activity': daily_activity,
        'cron_runs': cron_runs
    }

    # Write output
    with open(METRICS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"  Written: {METRICS_FILE}")
    print(f"  Total sessions: {total_sessions}")
    print(f"  Total tokens: {total_tokens:,}")
    print(f"  Today: {today_data['sessions']} sessions, {today_data['total_tokens']:,} tokens")


if __name__ == "__main__":
    main()
