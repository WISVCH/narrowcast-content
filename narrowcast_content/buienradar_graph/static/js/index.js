/**
 * Call the buienradar API to get the rain data
 */
async function fetchGraphData() {
    try {
        const response = await fetch('https://graphdata.buienradar.nl/2.0/forecast/geo/RainHistoryForecast?lat=' + lat.toString() + '&lon=' + lon.toString());
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

/**
 * Call the buienradar API to get the other data
 */
async function fetchWeatherData() {
    try {
        const response = await fetch('https://data.buienradar.nl/2.0/feed/json');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

/**
 * Out of a list of moments, pick the closed to now, either in the future or in the past.
 * @param momentList
 * @returns {*}
 */
function findClosestMoment(momentList) {
    // Get the current moment
    const currentMoment = moment();

    // Initialize variables to track the closest moment and the time difference
    let closestMoment = momentList[0];
    let timeDifference = Math.abs(momentList[0].diff(currentMoment));

    // Iterate through the list of moments
    for (let i = 1; i < momentList.length; i++) {
        const tempDifference = Math.abs(momentList[i].diff(currentMoment));

        // Update the closest moment if the current moment is closer
        if (tempDifference < timeDifference) {
            closestMoment = momentList[i];
            timeDifference = tempDifference;
        }
    }

    return closestMoment;
}

//source: https://www.movable-type.co.uk/scripts/latlong.html
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // metres
    const φ1 = lat1 * Math.PI / 180; // φ, λ in radians
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
        Math.cos(φ1) * Math.cos(φ2) *
        Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    const d = R * c; // in metres

    return d;
}

function findClosestStation(data, targetLat, targetLon) {
    let closestStation = null;
    let minDistance = Infinity;

    for (const station of data.actual.stationmeasurements) {
        const stationLat = station.lat;
        const stationLon = station.lon;
        const distance = calculateDistance(targetLat, targetLon, stationLat, stationLon);
        if (distance < minDistance) {
            minDistance = distance;
            closestStation = station;
        }
    }

    return closestStation;
}

/**
 * Get and parse the data from buienradar
 */
async function getGraphData() {
    const data = await fetchGraphData();

    const graph_data = [];

    data.forecasts.forEach(forecast => {
        graph_data.push({
            x: moment(forecast.datetime),
            y: forecast.value,
        })
    });
    return graph_data;
}

async function updateTemp() {
    const weather_data = await fetchWeatherData()
    const station_measurements = findClosestStation(weather_data, lat, lon)
    document.querySelector(".temp").innerHTML = station_measurements.temperature + "°C"

    const weatherIcon = document.querySelector(".weather_icon");
    weatherIcon.src = station_measurements.iconurl;

    // Fix for mistake in url of icon in buienradar api
    weatherIcon.onerror = function () {
        // Extract filename and convert to uppercase
        weatherIcon.onerror = null; // Prevent infinite loop if the fallback also fails
        weatherIcon.src = station_measurements.iconurl.replace(/\/([a-z])\.png$/, (_, letter) => `/${letter.toUpperCase()}.png`);
    };
}

let myChart;

/**
 * Update the chart with new data from buienradar, and the new time
 */
async function updateChart() {
    const graph_data = await getGraphData();

    myChart.data.datasets[0].data = graph_data
    myChart.options.scales.x.min = graph_data[0]['x'];
    myChart.options.scales.x.max = graph_data[graph_data.length - 1]['x'];

    const now = moment()

    myChart.options.plugins.annotation.annotations.nowLine.xMin = now
    myChart.options.plugins.annotation.annotations.nowLine.xMax = now

    let closestDayChange = now.clone().set({
        hour: 0,
        minute: 0,
        second: 0,
        milliseconds: 0
    })
    closestDayChange = findClosestMoment([closestDayChange.clone().add(1, 'day'), closestDayChange.clone(), closestDayChange.clone().subtract(1, 'day')])

    myChart.options.plugins.annotation.annotations.dayLine.xMin = closestDayChange
    myChart.options.plugins.annotation.annotations.dayLine.xMax = closestDayChange
    myChart.options.plugins.annotation.annotations.dayLine.label.content = closestDayChange.format('dddd')

    myChart.update();
}

/**
 * Parse the data and create the chart
 */
async function createChart() {
    const graph_data = await getGraphData();

    const now = moment()

    let closestDayChange = now.clone().set({
        hour: 0,
        minute: 0,
        second: 0,
        milliseconds: 0
    })
    closestDayChange = findClosestMoment([closestDayChange.clone().add(1, 'day'), closestDayChange.clone(), closestDayChange.clone().subtract(1, 'day')])


    // Create a line chart using Chart.js
    const ctx = document.getElementById('rainfallChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                data: graph_data,
                fill: true,
                showLine: false,
                tension: 0.3,
                pointRadius: 0,
                cubicInterpolationMode: 'default',
                backgroundColor: '#5A9BD3',
            }],
        },
        options: {
            aspectRatio: 3.0,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 130,
                    border: {
                        display: false,
                    },
                    afterBuildTicks: axis => axis.ticks = [40, 70, 100].map(v => ({value: v})),
                    ticks: {
                        callback: function (value, index, ticks) {
                            return ["Light", "Medium", "Heavy"][index]
                        },
                        color: "#aaaaaa",
                        font: {
                            family: "'RTLGraphikTT-Semibold',Arial,Helvetica,sans-serif",
                            weight: "normal",
                            size: 12,
                        },
                        padding: 10,
                    }
                },
                x: {
                    type: 'time',
                    min: graph_data[0]['x'],
                    max: graph_data[graph_data.length - 1]['x'],
                    grid: {
                        display: false,
                        lineWidth: 0,
                    },
                    border: {
                        color: "#aaaaaa",
                    },
                    ticks: {
                        color: "#152B82",
                        font: {
                            family: "'RTLGraphikTT-Semibold',Arial,Helvetica,sans-serif",
                            weight: "bold",
                            size: 16,
                        },
                        // autoSkip: true,
                        // maxTicksLimit: 10,
                        stepSize: 30,
                        maxRotation: 0,
                        minRotation: 0,
                    },
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        },
                    }
                }
            },

            hover: {mode: null},
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    enabled: false,
                },
                annotation: {
                    annotations: {
                        nowLine: {
                            type: 'line',
                            xMin: now,
                            xMax: now,
                            yMax: 120,
                            mode: "vertical",
                            borderColor: "#152B82",
                            borderWidth: 1,
                            borderDash: [5, 5],
                            label: {
                                content: "Now",
                                display: true,
                                backgroundColor: 'rgba(255, 255, 255, 255)',
                                color: "#152B82",
                                font: {
                                    family: "'RTLGraphikTT-Semibold',Arial,Helvetica,sans-serif",
                                    weight: "bold",
                                    size: 16
                                },
                                position: 'end',
                                yAdjust: '',
                            },
                        },
                        dayLine: {
                            type: 'line',
                            xMin: closestDayChange,
                            xMax: closestDayChange,
                            yMax: 120,
                            mode: "vertical",
                            borderColor: "#aaaaaa",
                            borderWidth: 1,
                            label: {
                                content: closestDayChange.format('dddd'),
                                display: true,
                                backgroundColor: 'rgba(255, 255, 255, 255)',
                                color: "#aaaaaa",
                                font: {
                                    family: "'RTLGraphikTT-Semibold',Arial,Helvetica,sans-serif",
                                    weight: "normal",
                                    size: 16,
                                },
                                position: 'end',
                                yAdjust: '',
                            },
                        }
                    }
                },
            }
        },
    });
}

// Call the function to create the chart
createChart();
updateTemp();

setInterval(updateTemp, 60000*5); // Repeat every 5 minutes

// Function to calculate time remaining until the next whole minute
function calculateTimeRemaining() {
    const now = new Date();
    const secondsUntilNextMinute = 60 - now.getSeconds();
    return secondsUntilNextMinute * 1000; // Convert seconds to milliseconds
}

// Call updateChart at the beginning of every whole minute
setTimeout(() => {
    updateChart(); // Call immediately
    setInterval(updateChart, 60000); // Repeat every 1 minute
}, calculateTimeRemaining());