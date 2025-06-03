import urllib
from datetime import datetime, timedelta

import requests
from flask import Blueprint, render_template, abort, request, current_app

pub_timer = Blueprint('pub_timer', __name__,
                      template_folder='templates', static_folder='static',
                      url_prefix='/pub_timer')


@pub_timer.route('/')
def show():
    """
    Get the open pub evening of today, and render it on the page.
    If fetching the calendar fails, fall back to a “this‐week” schedule of
    Wednesday and Thursday from 17:00 to 22:00.
    """
    now = datetime.now()
    # Define a window for the API query: start_of_yesterday → end_of_tomorrow (up to +20d)
    start_of_yesterday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = (now + timedelta(days=20)).replace(hour=23, minute=59, second=59, microsecond=999999)

    # Build the Google Calendar API URL
    url = (
        f"https://www.googleapis.com/calendar/v3/calendars/"
        f"{urllib.parse.quote(current_app.config['PUB_GOOGLE_CALENDAR_ID'])}/events?"
        f"key={current_app.config['PUB_GOOGLE_CALENDAR_API_KEY']}"
        f"&timeMin={urllib.parse.quote(start_of_yesterday.astimezone().isoformat())}"
        f"&timeMax={urllib.parse.quote(end_of_tomorrow.astimezone().isoformat())}"
        f"&singleEvents=true&maxResults=30"
    )

    # Try fetching the calendar; if it fails or returns non-200, we set json_data = None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
        else:
            # Non-200 → fall back
            print(f"Error: Fetch returned status {response.status_code}")
            json_data = None
    except Exception as e:
        # Network/timeout/etc. → fall back
        print(f"Error during HTTP GET: {e}")
        json_data = None

    if json_data:
        # Normal path: parse “/pub” events out of the JSON response
        pub_evening_times = [
            {"start": item["start"]["dateTime"], "end": item["end"]["dateTime"]}
            for item in json_data.get("items", [])
            if "/pub" in item.get("summary", "").lower()
        ]
        # Convert ISO strings → naive datetime objects
        pub_evening_times = [
            {
                "start": datetime.fromisoformat(item["start"]),
                "end":   datetime.fromisoformat(item["end"])
            }
            for item in pub_evening_times
        ]
    else:
        # Fallback path: this week’s Wednesday & Thursday, 17:00–22:00
        pub_evening_times = []

        # Compute the date of “this week’s Monday” at midnight
        # (weekday(): Monday == 0, Tuesday == 1, … Sunday == 6)
        monday_of_this_week = now - timedelta(days=now.weekday())
        # Wednesday = Monday + 2 days, Thursday = Monday + 3 days
        wednesday = monday_of_this_week + timedelta(days=2)
        thursday  = monday_of_this_week + timedelta(days=3)

        # Create two slots: Wed 17:00–22:00 and Thu 17:00–22:00
        for candidate_day in (wednesday, thursday):
            start_dt = candidate_day.replace(hour=17, minute=0, second=0, microsecond=0)
            end_dt   = candidate_day.replace(hour=22, minute=0, second=0, microsecond=0)
            pub_evening_times.append({
                "start": start_dt,
                "end":   end_dt
            })

    # Now, filter out only those “pub” slots that fall on today’s date
    pub_evening_times_today = [
        slot for slot in pub_evening_times
        if slot["start"].date() == now.date()
    ]
    pub_evening_times_today.sort(key=lambda slot: slot["start"])

    # If there’s at least one slot today, render it as “open_today = True”
    if pub_evening_times_today:
        return render_template(
            'pub_timer/index.jinja2',
            open_today=True,
            start=pub_evening_times_today[0]['start'].isoformat(),
            end=  pub_evening_times_today[0]['end'].isoformat()
        )
    else:
        # No slots today → “open_today = False”
        return render_template(
            'pub_timer/index.jinja2',
            open_today=False,
            start=None,
            end=None
        )