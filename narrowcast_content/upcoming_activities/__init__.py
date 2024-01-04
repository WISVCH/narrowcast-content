import re
from datetime import timezone

import pytz
from flask import Blueprint, render_template

upcoming_activities = Blueprint('upcoming_activities', __name__,
                                template_folder='templates', static_folder='static',
                                url_prefix='/upcoming_activities')

import requests
from icalendar import Calendar
from datetime import datetime, timedelta

from narrowcast_content.cache import cache

# URL of the ICS feed
ics_url = 'https://ch.tudelft.nl/feed/ical/'


# Function to fetch and parse ICS data
def fetch_and_parse_ics(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        cal_data = response.text
        cal = Calendar.from_ical(cal_data)

        return [
            {
                'summary': event.get('summary'),
                'start': event.get('dtstart').dt.replace(tzinfo=timezone.utc),
                'end': event.get('dtend').dt.replace(tzinfo=timezone.utc),
                'categories': re.search(r'Category: (.+?)\.', event.get('description')).group(1).lower().split(
                    ", ") if re.search(r'Category: (.+?)\.', event.get('description')) else None,
            }
            for event in cal.walk('vevent')
        ]
    except Exception as e:
        print(f'Error fetching or parsing ICS data: {e}')
        return []


# Function to filter events for the next 7 days
def filter_events_for_next_n_days(events, n):
    now = datetime.now(timezone.utc)
    end_of_week = now + timedelta(days=n)

    return [
        event
        for event in events
        if now <= event['start'] < end_of_week
    ]


# Function to organize events by day
def organize_events_by_day(events, n):
    organized_events = {}

    for event in events:
        event_date = event['start'].strftime('%Y-%m-%d')

        if event_date not in organized_events:
            organized_events[event_date] = []

        organized_events[event_date].append({
            'summary': event['summary'],
            'start': (event['start'].replace(tzinfo=pytz.utc) + event['start'].utcoffset()).isoformat(),
            'end': (event['end'].replace(tzinfo=pytz.utc) + event['end'].utcoffset()).isoformat(),
            'categories': event['categories'],
        })

    today = datetime.now()

    for i in range(n):
        current_date = today + timedelta(days=i)
        current_date_str = current_date.strftime('%Y-%m-%d')
        if current_date_str not in organized_events:
            organized_events[current_date_str] = []

    return organized_events


@upcoming_activities.route('/')
def show():
    return render_template('upcoming_activities/index.jinja2')


@upcoming_activities.route('/events/')
@cache.cached(timeout=4 * 60)
def events():
    # Fetch and parse ICS data, then organize events
    ics_events = fetch_and_parse_ics(ics_url)
    filtered_events = filter_events_for_next_n_days(ics_events, 14)
    organized_events = organize_events_by_day(filtered_events, 14)
    # Print the result
    return organized_events
