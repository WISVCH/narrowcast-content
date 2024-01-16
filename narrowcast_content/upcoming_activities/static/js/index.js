function autoScroll() {
    var currentIndex = 0;

    function scrollToNext() {
        var items = document.querySelectorAll('.day');
        items[currentIndex].scrollIntoView({behavior: 'smooth', block: 'start'});

        currentIndex++;

        // If reached the last div, go back to the top
        if (currentIndex === items.length) {
            currentIndex = 0;
            setTimeout(scrollToNext, 3000);
        } else if (currentIndex === 1) {
            setTimeout(scrollToNext, 7000);
        } else {
            setTimeout(scrollToNext, 3000);
        }
    }

    // Start the auto-scrolling
    scrollToNext();
}

async function fetchAndParseEventData() {
    try {
        // Fetch data from the API
        const response = await fetch('events',);

        if (!response.ok) {
            throw new Error(`Error fetching data: ${response.status} ${response.statusText}`);
        }

        const eventData = await response.json();

        // Parse the JSON using Moment.js
        const parsedEventData = {};

        for (const date in eventData) {
            const parsedDate = moment.utc(date);

            // Sort events by start time
            const events = eventData[date]
                .map(event => ({
                    end: moment.utc(event.end),
                    start: moment.utc(event.start),
                    summary: event.summary,
                    categories: event.categories,
                }))
                .sort((a, b) => a.start - b.start);

            parsedEventData[parsedDate.format("YYYY-MM-DD")] = events;
        }

        // Return the parsedEventData
        return parsedEventData;
    } catch (error) {
        console.error('Error:', error.message);
        // Return null or another suitable value indicating an error
        return null;
    }
}

async function makeSchedule() {
    let schedule = await fetchAndParseEventData()
    if (schedule != null) {
        var days = [];

        // Iterate through each day in the schedule
        for (var day in schedule) {
            if (schedule.hasOwnProperty(day)) {
                let date = moment.utc(day)
                // Create a div for the day
                var dayDiv = document.createElement('div');
                dayDiv.className = 'day';

                var dateDiv = document.createElement('div');
                dateDiv.className = 'date';

                // Create a div for the day name and date
                var dayNameDiv = document.createElement('div');
                dayNameDiv.className = 'day-name';
                dayNameDiv.textContent = date.format('ddd');

                dateDiv.appendChild(dayNameDiv);

                // Create a div for the day name and date
                var dayDateDiv = document.createElement('div');
                dayDateDiv.className = 'day-date';
                dayDateDiv.textContent = date.format('DD-MM-YY');

                dateDiv.appendChild(dayDateDiv);

                dayDiv.appendChild(dateDiv);

                var activitiesDiv = document.createElement('div');
                activitiesDiv.className = 'activities';

                // Iterate through each activity in the day
                schedule[day].forEach(function (activity) {
                    // Create a div for each activity
                    var activityDiv = document.createElement('div');
                    activityDiv.className = 'activity';

                    if (Array.isArray(activity.categories)) {
                        activity.categories.forEach(function (category) {
                                activityDiv.classList.add('category-' + category)
                            }
                        )
                    } else {
                        activityDiv.classList.add('no-category')
                    }


                    // Create a div for the activity name
                    var activityNameDiv = document.createElement('div');
                    activityNameDiv.className = 'activity-name';
                    activityNameDiv.textContent = activity.summary;

                    // Create a div for the start and end time
                    var timeDiv = document.createElement('div');
                    timeDiv.className = 'activity-time';

                    if(activity.start.isSame(date, "day")) {
                        timeDiv.textContent = activity.start.format("HH:mm");
    
                        if (activity.start.isSame(activity.end, "day")) {
                            timeDiv.textContent += ' - ' + activity.end.format("HH:mm");
                        }
                    }

                    // Append activity name and time to the activity div
                    activityDiv.appendChild(activityNameDiv);
                    activityDiv.appendChild(timeDiv);

                    // Append the activity div to the day div
                    activitiesDiv.appendChild(activityDiv);
                    dayDiv.appendChild(activitiesDiv)
                });

                // Append the day div to the container
                days.push(dayDiv);
            }

            // Get the container element
            var container = document.querySelector('.schedule');
            while (container.firstElementChild) {
                container.firstElementChild.remove();
            }
            days.forEach(function (day) {
                container.appendChild(day)
            })
        }
    }
}

document.addEventListener("DOMContentLoaded", async (event) => {
    await makeSchedule();
    setInterval(makeSchedule, 1000 * 60 * 5);
    setTimeout(autoScroll, 0);
});