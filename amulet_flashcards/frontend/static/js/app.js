/* Display card image when a card name is clicked. Next click hides it. */

function show_autocard(card_image_url) {
    document.getElementById("autocard").src = card_image_url;
    document.getElementById("autocard-backdrop").style.display = "block";
}

function hide_autocard() {
    document.getElementById("autocard-backdrop").style.display = "none";
}


htmx.on('htmx:beforeRequest', function(evt) {
    document.getElementById("play-button").toggleAttribute("disabled");
    });


htmx.on('htmx:afterRequest', function(evt) {
    document.getElementById("play-button").removeAttribute("disabled");
});
