function update_player(data) {
    if (data.authorized === false) {
        document.querySelector('.song').style.display = 'none';
        document.querySelector('.unauthorized').style.display = 'grid';
        document.querySelector('.not_playing').style.display = 'none';
    } else if (data.anything_playing === false) {
        document.querySelector('.song').style.display = 'none';
        document.querySelector('.unauthorized').style.display = 'none';
        document.querySelector('.not_playing').style.display = 'grid';
    } else {
        document.querySelector('.song').style.display = 'grid';
        document.querySelector('.unauthorized').style.display = 'none';
        document.querySelector('.not_playing').style.display = 'none';
        document.querySelector('.title').textContent = data.title;
        document.querySelector('.artist').textContent = data.artist;
        document.querySelector('.album_cover img').src = data["album_cover"];
        if (data.is_playing === true) {
            document.querySelector('.playing_symbol').classList.add('playing');
        } else {
            document.querySelector('.playing_symbol').classList.remove('playing');
        }
    }
}

// Function to update the now playing information
function updateNowPlaying() {
    fetch('currently_playing',)
        .then(response => response.json())
        .then(data => {
            update_player(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Call updateNowPlaying every 5 seconds
setInterval(updateNowPlaying, 5000);

update_player(initial_data)