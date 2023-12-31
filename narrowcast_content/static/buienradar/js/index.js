// Function to make the GET request
async function fetchData() {
    try {
        const response = await fetch('https://graphdata.buienradar.nl/2.0/forecast/geo/RainHistoryForecast?lat=' + lat.toString() + '&lon=' + lon.toString());
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

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

function timeToMoment(time) {
    // Get the current moment
    const currentMoment = moment();

// Extract hours and minutes from the time string
    const [hours, minutes] = time.split(':');

// Set the time on the current moment
    const transformedMoment = currentMoment.clone().set({
        hour: parseInt(hours, 10),
        minute: parseInt(minutes, 10),
        second: 0,
        milliseconds: 0
    });

    const options = [transformedMoment.clone().add(1, 'day'), transformedMoment.clone(), transformedMoment.clone().subtract(1, 'day')]

    const closestMoment = findClosestMoment(options)

    return closestMoment;
}

async function get_data() {
    const data = await fetchData();

    // console.log(data)

    const graph_data = [];

    data.forecasts.forEach(forecast => {
        graph_data.push({
            x: moment(forecast.datetime),
            y: forecast.value,
        })
    });
    return graph_data;
}

let myChart;

async function updateChart() {
    const graph_data = await get_data();

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

// Function to parse the data and create the chart
async function createChart() {
    const graph_data = await get_data();

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
            aspectRatio: 2.5,
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
                            size: 8,
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