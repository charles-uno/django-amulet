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
    maybe_show_stats();
});

google.charts.load("current", {packages:['corechart']});


function maybe_show_stats() {
    var elt = document.getElementById("stats-target");
    if (elt == null) {
        console.log("no stats to show");
        return;
    }
    vals = elt.innerHTML.split(",");
    n_turn2 = parseInt(vals[1]);
    n_turn3 = parseInt(vals[2]);
    n_turn4 = parseInt(vals[3]);
    n_turn5plus = parseInt(vals[4]);
    n_total = n_turn2 + n_turn3 + n_turn4 + n_turn5plus;

    var data = google.visualization.arrayToDataTable([
        ['Turn', 'Completion Rate'],
        ['2', n_turn2/n_total],
        ['3', n_turn3/n_total],
        ['4', n_turn4/n_total],
        ['5+', n_turn5plus/n_total],
     ]);
     var view = new google.visualization.DataView(data);
     var options = {
        title: "Density of Precious Metals, in g/cm^3",
        width: 600,
        height: 400,
        bar: {groupWidth: "95%"},
        legend: { position: "none" },
      };
     var chart = new google.visualization.ColumnChart(elt);
     chart.draw(view, options);

}




