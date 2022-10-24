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
                location.href='../../judge/graph/';
            });
            
            break;
    }
}
function gif(mode, taste) {    
    if (mode == 'light' && taste == 'bad') {
        console.log("Light mode insult");
        fs.readFile("../../static/light_mode_gifs/insults.txt", 'utf-8', (err, data) => {
            if (err) throw err;
            console.log(data.toString());

            var fr=new FileReader();
            fr.onload=function() {
                document.getElementById('fvf').appendChild=fr.result;
            }
            fr.readAsText(this.files[0]);
        });
    }
}