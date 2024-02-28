import re
from datetime import timezone

import pytz
from flask import Blueprint, render_template, request

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
    start_of_today = now.replace(hour=0, minute=0)
    end_of_week = (now + timedelta(days=n-1)).replace(hour=23, minute=0)

    return [
        event
        for event in events
        if start_of_today <= event['start'] < end_of_week
    ]


# Function to organize events by day
def organize_events_by_day(events, n):
    organized_events = {}

    today = datetime.now()

    for event in events:
        event_date = event['start'].strftime('%Y-%m-%d')

        if event_date not in organized_events:
            organized_events[event_date] = []

        # Check if it is a multiple day event
        if event['end'].date() > event['start'].date() and event['end'].hour >= 6:
            # Add event for each day until the end date, or n days (excluding events ending before 9:00AM the next day)
            current_date = event['start'].date()
            while current_date <= event['end'].date() and current_date < (today + timedelta(days=n)).date():
                if current_date.strftime('%Y-%m-%d') not in organized_events:
                    organized_events[current_date.strftime('%Y-%m-%d')] = []
                current_date_str = current_date.strftime('%Y-%m-%d')
                organized_events[current_date_str].append({
                    'summary': event['summary'],
                    'start': (event['start'].replace(tzinfo=pytz.utc) + event['start'].utcoffset()).isoformat(),
                    'end': (event['end'].replace(tzinfo=pytz.utc) + event['end'].utcoffset()).isoformat(),
                    'categories': event['categories'],
                })
                current_date += timedelta(days=1)
        else:
            organized_events[event_date].append({
                'summary': event['summary'],
                'start': (event['start'].replace(tzinfo=pytz.utc) + event['start'].utcoffset()).isoformat(),
                'end': (event['end'].replace(tzinfo=pytz.utc) + event['end'].utcoffset()).isoformat(),
                'categories': event['categories'],
            })

    for i in range(n):
        current_date = today + timedelta(days=i)
        current_date_str = current_date.strftime('%Y-%m-%d')
        if current_date_str not in organized_events:
            organized_events[current_date_str] = []

    return organized_events


@upcoming_activities.route('/')
def show():
    return render_template('upcoming_activities/index.jinja2')


@upcoming_activities.route('/events')
@cache.cached(timeout=4 * 60, query_string=True)
def events():
    days = request.args.get('days')
    if not days:
        days = 14
    else:
        days = int(days)

    # Fetch and parse ICS data, then organize events
    ics_events = fetch_and_parse_ics(ics_url)
    filtered_events = filter_events_for_next_n_days(ics_events, days)
    organized_events = organize_events_by_day(filtered_events, days)
    # Print the result
    return organized_events
