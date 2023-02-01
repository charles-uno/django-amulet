/* Display card image when a card name is clicked. Next click hides it. */

function show_autocard(card_image_url) {
    document.getElementById("autocard").src = card_image_url;
    document.getElementById("autocard-backdrop").style.display = "block";
}

function hide_autocard() {
    document.getElementById("autocard-backdrop").style.display = "none";
}

/* "About this page" blurb covers cards */

function show_about() {
    document.getElementById("main").style.display = "none";
    document.getElementById("about").style.display = "block";
}

document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.key == "Escape" || evt.key == "Esc") {
        hide_about()
    }
};

function hide_about() {
    document.getElementById("main").style.display = "block";
    document.getElementById("about").style.display = "none";
}

/* Disable the buttons while working on a request */

htmx.on('htmx:beforeRequest', function(evt) {
    document.getElementById("opener-button").toggleAttribute("disabled");
    document.getElementById("play-button").toggleAttribute("disabled");
});


htmx.on('htmx:afterRequest', function(evt) {
    document.getElementById("opener-button").removeAttribute("disabled");
    document.getElementById("play-button").removeAttribute("disabled");
});


