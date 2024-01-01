let show_confetti = false;

document.addEventListener('DOMContentLoaded', function () {
    function updateTimer() {
        var now = moment();
        var duration;

        if (now.isBefore(start)) {
            //Countdown
            duration = moment.duration(start.diff(now));
            document.querySelector('.countdown').innerHTML = moment.utc(duration.asMilliseconds()).format("-HH:mm:ss");
            document.querySelector('.countdown').style.display = 'block';
            document.querySelector('.open').style.display = 'none';
            document.querySelector('.closed').style.display = 'none';
            show_confetti = false
        } else if (now.isBetween(start, end)) {
            // Opem
            document.querySelector('.countdown').style.display = 'none';
            document.querySelector('.open').style.display = 'block';
            document.querySelector('.closed').style.display = 'none';
            show_confetti = true
        } else {
            // Closed
            document.querySelector('.countdown').style.display = 'none';
            document.querySelector('.open').style.display = 'none';
            document.querySelector('.closed').style.display = 'block';
            show_confetti = false
        }
    }

    // Update the timer every second
    setInterval(updateTimer, 1000);

    // Initial update
    updateTimer();
});

async function do_confetti() {
    const canvas = document.querySelector("canvas");

    var img = document.querySelector('.logo img')
    var rect = img.getBoundingClientRect();
    var centerXPercent = (rect.left + rect.width / 2) / window.innerWidth * 100;
    var centerYPercent = (rect.top + rect.height / 2) / window.innerHeight * 100;

    canvas.confetti =
        canvas.confetti || (await confetti.create(canvas, {resize: true}));

    if (show_confetti) {
        canvas.confetti({
            spread: 360,
            count: 20,
            ticks: 800,
            gravity: 0,
            decay: 0.90,
            startVelocity: 30,
            position: {x: centerXPercent, y: centerYPercent},
            flat: true,
            scalar: 5,
            colors: ['#ffffff'],
            shapes: ['square']
        });
    }
}

setInterval(do_confetti, 100);