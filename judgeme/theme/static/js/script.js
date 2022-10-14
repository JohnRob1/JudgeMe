function list_choices(buttonName, messageHtml, headingId, type) {
    //create message
    let Id = document.getElementById(headingId);
    Id.innerHTML = messageHtml;

    //loop through and display Spotify elements
    //right now this is dummy button
    let placeholder = document.createElement('button');
    placeholder.innerHTML = buttonName;
    Id.appendChild(placeholder);
    
    switch (type) {
        case 'playlist':
            placeholder.addEventListener("click", function(event) {
                list_choices('friendPlaceholder', '<h3>Choose a Friend</h3>', 'friendsMessage', 'friend')
            });
            break;
        case 'friend':
            placeholder.addEventListener("click", function(event) {
                list_choices('friendPlaylistPlaceholder', '<h3>Choose a Friend\'s Playlist</h3>', 'friendsPlaylistsMessage', 'fPlaylist')
            });
            break;
        case 'fPlaylist':
            //send to compare page for functionality
            placeholder.addEventListener("click", function(event) {
                Id = document.getElementById('graphsTypesMessage');
                Id.innerHTML = "<h3>Choose type of graph output for comparison</h3>"

                let slider = document.createElement('button');
                slider.innerHTML = 'Slider Graph';
                Id.appendChild(slider);

                let bar = document.createElement('button');
                bar.innerHTML = 'Bar Graph';
                Id.appendChild(bar);
                Id.addEventListener("click", function(event) {
                    location.href='../../judge/bar/';
                });

                let line = document.createElement('button');
                line.innerHTML = "Line Graph";
                Id.appendChild(line);
            });
            
            break;
    }
}