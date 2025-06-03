# Narrowcast Content

This repository contains a Flask application with multiple pages to show on a narrowcasting device.

## Pages

These are the pages that are currently here:

### Buienradar Graph

`/buienradar_graph?lat=LATITUDE&lon=LONGITUDE`

This page shows a rain graph of the location given by `LATITUDE` and `LONGITUDE`.
The data is sourced from [Buienradar](https://www.buienradar.nl/).

### Upcoming Activities

`/upcoming_activities`

This page displays a schedule of upcoming activities, grouped by day. Activities are fetched from a configured source and shown with their start and end times, as well as categories if available.

The schedule is automatically refreshed every 5 minutes.

### /Pub Timer

`/pub_timer`

This pages shows when the /Pub will open, when its open, or when it's closed for the day.

It uses the /Pub calendar for this. For this, the calendar and an API key need to be specified in the config.
The values are called `PUB_GOOGLE_CALENDAR_ID` and `PUB_GOOGLE_CALENDAR_API_KEY`, or `FLASK_PUB_GOOGLE_CALENDAR_ID` and `FLASK_PUB_GOOGLE_CALENDAR_API_KEY` when using environment variables.

### Spotify Now Playing

`/spotify_now_playing`

This page shows the song that is currently playing on the connected Spotify account.

To access the Spotify API, an app has to be created on the Spotify developer dashboard.
The client id, client secret and redirect URI have to be configured in the config at `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI`, or at `FLASK_SPOTIPY_CLIENT_ID`, `FLASK_SPOTIPY_CLIENT_SECRET`, and `FLASK_SPOTIPY_REDIRECT_URI` when using environment variables.

After starting the application, you have to connect one Spotify account by going to `/spotify_now_playing/authorize`

### Image

`/image?url=IMAGEURL`

This page displays the images provided full screen.

### Combine

`/combine?url0=URL0&size0=SIZE0&url1=URL1&size1=SIZE1&...`

This page can be used to stack multiple pages vertically. This is done by providing multiple URLs, and for every URL a size.
The size is a personage of the full screen height.

## Tokens

To make sure not everyone can access the application, you need to provide a token when doing your request.
Tokens are added to the URL as a parameter, like: `.../?token=TOKEN`.
Multiple tokens can be added to the `TOKENS` configuration option, or the `FLASK_TOKENS` option when using environment variables.
They have to space seperated.

## Deployment

This flask app can be installed and run using pip, or docker.

### Pip

```bash
git clone https://github.com/WISVCH/narrowcast-content.git
cd narrowcast-content
pip install .
flask --app narrowcast_content run
```

### Docker

```bash
docker run -p 8080:8080 --env-file .env ghcr.io/wisvch/narrowcast-content:latest
```