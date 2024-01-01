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
    :return:
    """
    now = datetime.now()
    start_of_yesterday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = (now + timedelta(days=20)).replace(hour=23, minute=59, second=59, microsecond=999999)

    url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(current_app.config['PUB_GOOGLE_CALENDAR_ID'])}/events?key={current_app.config['PUB_GOOGLE_CALENDAR_API_KEY']}&timeMin={urllib.parse.quote(start_of_yesterday.astimezone().isoformat())}&timeMax={urllib.parse.quote(end_of_tomorrow.astimezone().isoformat())}&singleEvents=true&maxResults=30"
    print(url)
    try:
        # Make a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Decode the JSON response
            json_data = response.json()
        else:
            # Print an error message if the request was not successful
            abort(500, f"Error: Unable to fetch URL. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
        abort(500, f"Internal error")

    pub_evening_times = [
        {"start": item["start"]["dateTime"], "end": item["end"]["dateTime"]}
        for item in json_data["items"]
        if item.get("summary", "").lower() == "/pub evening"
    ]

    pub_evening_times = [
        {"start": datetime.fromisoformat(item["start"]), "end": datetime.fromisoformat(item["end"])}
        for item in pub_evening_times
    ]

    pub_evening_times_today = [item for item in pub_evening_times if
                               item['start'].date() == datetime.today().date()]
    pub_evening_times_today.sort(key=lambda item: item["start"])

    if len(pub_evening_times_today) > 0:
        return render_template('pub_timer/index.jinja2', open_today=True,
                               start=pub_evening_times_today[0]['start'].isoformat(), end=pub_evening_times_today[0]['end'].isoformat())
    else:
        return render_template('pub_timer/index.jinja2', open_today=False, start=None, end=None)
