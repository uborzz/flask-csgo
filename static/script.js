$(document).ready(function() {
    $('#principal').DataTable({
        "paging": false
    })
})

document.all_members = null
document.selected_members = [] //pendiente guardar en cookie/local storage la seleccion
document.string_members = ""

function filterByNames () {
    $('#principal').DataTable().column(0).search($('#cont').val(), true, false).draw();
}

$( document ).ready(function() {
//    console.log( "document ready!" )

    $( "#botones_modo" ).change(function() {
        updateWinLossChart()
    });


    $('#boxes').on('change', function(){
        var selected = []

        $.each($("input[name='names']:checked"), function(){
//            console.log($(this).val())
            selected.push($(this).val());
        });

        document.string_members = selected.join("|")
        $('#cont').val(document.string_members)
//        console.log(document.string_members)
        filterByNames()
    });

    $('#boxes_comp').on('change', function(){
        var selected = []

        $.each($("input[name='names_comp']:checked"), function(){
//            console.log($(this).val())
            selected.push($(this).val());
        });

        document.object_members = selected.slice(0)
        document.string_members = selected.join("|")
        $('#cont').val(document.string_members)

        updateWinLossChart()
    });

    $('#boxes_maps').on('change', function(){
        var selected = []

        $.each($("input[name='names_maps']:checked"), function(){
//            console.log($(this).val())
            selected.push($(this).val());
        });

        document.object_maps = selected.slice(0)
        document.string_maps = selected.join(" - ")
        $('#maps').val(document.string_maps)

        updateWinLossChart()
    });

    var chart = new CanvasJS.Chart("chartContainer", {
        theme: "light2",
        animationEnabled: true,
        title: {
            text: "All matches in system",
            fontSize: 22
        },
        subtitles: [{
            text: "No maps filtered",
            fontSize: 16
        }],
        data: [{
            type: "pie",
            indexLabelFontSize: 18,
            radius: 80,
            indexLabel: "{label} - {y}",
            yValueFormatString: "###0.0\"%\"",
            click: explodePie,
            dataPoints: getDatapoints()
        }]
    });
    chart.render();

    function explodePie(e) {
        for(var i = 0; i < e.dataSeries.dataPoints.length; i++) {
            if(i !== e.dataPointIndex)
                e.dataSeries.dataPoints[i].exploded = false;
        }
    }

    function getDatapoints() {
    // dummy
        console.log(document.partidas)
        return [
                    { y: 21, label: "Loss"},
                    { y: 21, label: "Loss"},
                    { y: 24.5, label: "Tie" }
                ]
    }

    function updateWinLossChart() {
//        console.log(chart)
        if (document.string_maps && document.string_members) {

            var partidas = document.partidas

            // Analisis
            modo_players_all = $("#option_all").is(":checked");
            modo_players_any = $("#option_any").is(":checked");

            // filtro mapas
            var filtradas_mapas = []
            for (var partida of partidas) {
                if (document.object_maps.includes(partida['map'])) {
                    filtradas_mapas.push(partida)
                }
            }

            // filtro players
            var filtradas_players = []
            for (var partida of filtradas_mapas) {

                var team_field = "players_team" + partida.local_team  // ekipo dofitos
                var players_en_partida = []  // saco ids de los jugadores del ekipo dofito

                for (var player of partida[team_field]) {
                    players_en_partida.push(player['steam_id'])
                }
//                console.log("players en partida" + players_en_partida)


                // modo todos los seleccionados deben aperecer en la partida
                if (modo_players_all) {
                    console.log("MODO ALL")
                    var success = true  // tiraremos a false el success si un player de los clickados no esta en la game

                    if (document.object_members.length > 5) {  // mas de 5 seleccionados -> auto fail
                        success = false
                    } else {
                        for (var player of document.object_members) {
                            if (!players_en_partida.includes(player)) {  // de los players clicados en el front busco si alguno no esta en la partida
                                success = false
                                break
                            }
                        }
                    }

                    if (success) {
                        filtradas_players.push(partida)
                    }

                // modo cualquiera de los seleccionados (ANY)
                } else if (modo_players_any) {
                    console.log("MODO ALL")
                    var success = false  // tiraremos a false el success hasta que veamos un player de los clickados en la game

                    for (var player of document.object_members) {
                        if (players_en_partida.includes(player)) {  // de los players clicados en el front busco si alguno SI esta en la partida
                            success = true
                            break
                        }
                    }

                    if (success) {
                        filtradas_players.push(partida)
                    }

                }
            }

            // filtro fechas

            var total = 0
            var wins = 0
            var losses = 0
            var ties = 0
            for (partida of filtradas_players) {
                total++
                if (partida['local_result'] == "W") {
                    wins++
                } else if (partida['local_result'] == "L") {
                    losses++
                } else {
                    ties++
                }
            }

            if (total) {
                chart.options.data[0].dataPoints = [
                        { y: 100*ties/total, label: "Tie"},
                        { y: 100*wins/total, label: "Win"},
                        { y: 100*losses/total, label: "Loss"}
                    ]

                var chart_text = total + " matches"
                var chart_subtitle = "Showing info for maps: " + document.string_maps

            } else {
                var chart_text = "0 matches"
                var chart_subtitle = "No info for that selection."
                chart.options.data[0].dataPoints = [
                        { y: 0, label: "Tie"},
                        { y: 100, label: "Win"},
                        { y: 0, label: "Loss"}
                    ]
            }

        } else {
            var chart_text = "0 matches"
            var chart_subtitle = "No players or maps clicked."
            chart.options.data[0].dataPoints = [
                    { y: 0, label: "Tie"},
                    { y: 100, label: "Win"},
                    { y: 0, label: "Loss"}
                ]
        }

        chart.options.title = {
            text: chart_text,
            fontSize: 22
        }
        chart.options.subtitles[0] = {
            text: chart_subtitle,
            fontSize: 16
        }
        chart.render()
    }

    initializeLists()
    updateWinLossChart()

});

function initializeLists() {
        var selected = []
        $.each($("input[name='names_maps']:checked"), function(){
            selected.push($(this).val());
        });
        document.object_maps = selected.slice(0)
        document.string_maps = selected.join(" - ")

        var selected = []
        $.each($("input[name='names_comp']:checked"), function(){
            selected.push($(this).val());
        });
        document.object_members = selected.slice(0)
        document.string_members = selected.join(", ")
    }

function showIds() {
    var info_div = $("#info_ids")[0]
    if (info_div.style.display === "none") {
        info_div.style.display = "block";
    } else {
    info_div.style.display = "none";
    }
}