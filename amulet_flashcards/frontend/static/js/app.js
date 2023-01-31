/* Display card image when a card name is clicked. Next click hides it. */

function show_autocard(card_image_url) {
    document.getElementById("autocard").src = card_image_url;
    document.getElementById("autocard-backdrop").style.display = "block";
}

function hide_autocard() {
    document.getElementById("autocard-backdrop").style.display = "none";
}


/* Disable the "play it out" button while working on a request */

htmx.on('htmx:beforeRequest', function(evt) {
    document.getElementById("play-button").toggleAttribute("disabled");
    });


htmx.on('htmx:afterRequest', function(evt) {
    document.getElementById("play-button").removeAttribute("disabled");
    maybe_show_stats();
});

/* Load config JSON and plug it into a Google Chart */

google.charts.load("current", {packages:['corechart']});

function maybe_show_stats() {
    var elt = document.getElementById("stats-target");
    if (elt == null) {
        return;
    }
    try {
        chart_config = JSON.parse(elt.innerHTML);
    } catch (Exception) {
        return;
    }
    var data = google.visualization.arrayToDataTable(chart_config["data_arr"]);
    var view = new google.visualization.DataView(data);
    var chart = new google.visualization.ColumnChart(elt);
    chart.draw(view, chart_config["options"]);
}




