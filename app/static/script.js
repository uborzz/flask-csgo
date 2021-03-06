$(document).ready(function () {
    $('#principal').DataTable({
        "paging": false
    })
})


document.all_members = null
document.selected_members = [] //pendiente guardar en cookie/local storage la seleccion
document.string_members = ""

document.match_id_elements = []

function filterByNames() {
    $('#principal').DataTable().column(0).search($('#cont').val(), true, false).draw();
}

document.selected_games = []

function generate_config_hash() {
    let config = take_current_config()
    let jsonified = JSON.stringify(config);
    let encoded = btoa(jsonified)
    return encoded
}

function generate_url_with_config() {
    let config = generate_config_hash()
    let url = window.location.origin + window.location.pathname + '#' + config
    return url
}

$(document).ready(function () {

    // -------------------------------------------------------------------
    // GENERAL STATS PAGE
    // -------------------------------------------------------------------

    $('#boxes').on('change', function () {
        var selected = []

        $.each($("input[name='names']:checked"), function () {
            selected.push($(this).val());
        });

        document.string_members = selected.join(",")
        $('#cont').val(document.string_members)
        filterByNames()
    });

    var date_input=$('input[name="date"]'); //our date input has the name "date"
    var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
    date_input.datepicker({
        format: 'dd/mm/yyyy',
        container: container,
        todayHighlight: true,
        autoclose: true,
    })

    // -------------------------------------------------------------------
    // COMPETITIVES PAGE
    // -------------------------------------------------------------------

    $("#botones_modo").change(function () {
        updateWinLossChart()
    });

    $('#boxes_comp').on('change', function () {
        var selected = []

        $.each($("input[name='names_comp']:checked"), function () {
            selected.push($(this).val());
        });

        document.object_members = selected.slice(0)
        document.string_members = selected.join(",")
        $('#cont').val(document.string_members)

        updateWinLossChart()
    });

    $('#boxes_maps').on('change', function () {
        var selected = []

        $.each($("input[name='names_maps']:checked"), function () {
            selected.push($(this).val());
        });

        document.object_maps = selected.slice(0)
        document.string_maps = selected.join(" - ")
        $('#maps').val(document.string_maps)

        updateWinLossChart()
    });

    $('#start_date').on("change", function () {
        updateWinLossChart()
    })
    $('#end_date').on("change", function () {
        updateWinLossChart()
    })

    // listen everywhere, call vue main close for modals.
    document.onkeydown = function(evt) {
        evt = evt || window.event;
        var isEscape = false;
        if ("key" in evt) {
            isEscape = (evt.key === "Escape" || evt.key === "Esc");
        } else {
            isEscape = (evt.keyCode === 27);
        }
        if (isEscape) {
            vm.close_stuff();
        }
    };

    var chart = createPie("chartContainer")
    chart.render();
    var chart_columns = createColumns("chartContainer2")
    chart_columns.render();


    function updateWinLossChart(update_config=true) {

        // TARTA GRAPHIC
        if (update_config_enabled) { save_config() }
        // window.location.href = generate_url_with_config()

        if (document.string_maps && document.string_members) {
            
            // Aplying filters...
            var partidas = document.partidas

            // filtro mapas
            var filtradas_mapas = filterMaps(partidas)

            // filtro fechas
            var filtradas_fecha = filterDates(filtradas_mapas)

            // filtro players
            var filtradas_players = filterPlayers(filtradas_fecha)

            // sorted by time
            var sorted_games = sort_games_by_date(filtradas_players, ascending=false)

            // GAMES
            // for game results...
            document.selected_games = sorted_games
            // console.log("ON UPDATE", document.selected_games)
            var event = new CustomEvent('changes', { detail: { games: document.selected_games, all_players:document.players, selected_players: document.object_members } });
            document.dispatchEvent(event);


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
                    { y: 100 * ties / total, label: "Tie" },
                    { y: 100 * wins / total, label: "Win" },
                    { y: 100 * losses / total, label: "Loss" }
                ]

                var chart_text = total + " matches"
                var chart_subtitle = "Showing info for maps: " + document.string_maps

            } else {
                var chart_text = "0 matches"
                var chart_subtitle = "No info for that selection."
                chart.options.data[0].dataPoints = [
                    { y: 0, label: "Tie" },
                    { y: 100, label: "Win" },
                    { y: 0, label: "Loss" }
                ]
            }

        } else {
            var chart_text = "0 matches"
            var chart_subtitle = "No players or maps clicked."
            chart.options.data[0].dataPoints = [
                { y: 0, label: "Tie" },
                { y: 100, label: "Win" },
                { y: 0, label: "Loss" }
            ]
        }

        chart.options.title.text = chart_text
        chart.options.subtitles[0].text = chart_subtitle
        chart.render()


        // COLUMN BAR GRAPHIC

        var array_por_mapas = {}
        if (document.string_maps && document.string_members) {
            for (partida of filtradas_players) {
                var mapa = partida['map']
                if (!(mapa in array_por_mapas)) {
                    array_por_mapas[mapa] = {
                        wins: 0,
                        loses: 0,
                        ties: 0
                    }
                }
                if (partida['local_result'] == "W") {
                    array_por_mapas[mapa].wins++
                } else if (partida['local_result'] == "L") {
                    array_por_mapas[mapa].loses++
                } else {
                    array_por_mapas[mapa].ties++
                }
            }
        }

        chart_columns.options.data[0].dataPoints = []
        chart_columns.options.data[1].dataPoints = []
        chart_columns.options.data[2].dataPoints = []

        if (array_por_mapas) {
            for (const [map, results] of Object.entries(array_por_mapas)) {
                chart_columns.options.data[0].dataPoints.push({ y: results.wins, label: capitalize(map) })
                chart_columns.options.data[1].dataPoints.push({ y: results.loses, label: capitalize(map) })
                chart_columns.options.data[2].dataPoints.push({ y: results.ties, label: capitalize(map) })
            }
        }

        chart_columns.render()


        // go create the datatables after html init
        var event_tables = new Event('createtables')
        document.dispatchEvent(event_tables)

    }

    $('#share-button').click(
        function show_prompt_with_url() {
            url = generate_url_with_config()
            window.prompt("Share link. Copy to clipboard: Ctrl+C + Enter", url);
            // }
        }
    )

    // console.log("ON_READY", document.selected_games)

    var update_config_enabled = false
    load_last_config()
    initializeLists()
    updateWinLossChart()
    var update_config_enabled = true

});

function take_current_config() {
    let maps = document.string_maps
    let players = document.string_members
    let dates = [$("#start_date").val(), $("#end_date").val()]
    let filter_mode = $("input[name=radio_modo]:checked").attr('id')
    let control_mode = vm.get_mode();
    let config = { 'players': players, 'maps': maps, 'dates': dates, 'filter': filter_mode, 'control': control_mode };
    return config
}

function save_config() {
    // if (document.string_maps && document.string_members) {
        let config = take_current_config()
        let jsonified = JSON.stringify(config);
        localStorage.setItem('matchinegun_config', jsonified)
    // }
}

function load_last_config() {
    let config_in_url = window.location.hash
    // console.log('CONFIG URL', config_in_url.slice(1))

    if (config_in_url != "") {
        var config = atob(config_in_url.slice(1));
        // console.log('READ URL', config)
    } else {
        var config = localStorage.getItem('matchinegun_config');
        // console.log('LOCAL STRO', config)
    }
    try {
        if (config) {
            config = JSON.parse(config)
    
            $.each($("input[name='names_maps']"), function () {
                if (config.maps.includes($(this).val())) {
                    $(this).prop("checked", true)
                }
            });
    
            $.each($("input[name='names_comp']"), function () {
                if (config.players.includes($(this).val())) {
                    $(this).prop("checked", true)
                }
            });
    
            $("#start_date").val(config.dates[0])
            $("#end_date").val(config.dates[1])
    
            const filter_mode = '#' + config.filter
            $(filter_mode).prop("checked", true)

            vm.set_mode(config.control)
            // var event = new CustomEvent('changes', { control: config.control });
            // document.dispatchEvent(event);
        }
    } catch {
        $.each($("input[name='names_maps']"), function () {
            $(this).prop("checked", true);
        });
        $.each($("input[name='names_comp']"), function () {
            $(this).prop("checked", true);
        });
    }
}

function initializeLists() {
    var selected = []
    $.each($("input[name='names_maps']:checked"), function () {
        selected.push($(this).val());
    });
    document.object_maps = selected.slice(0)
    document.string_maps = selected.join(" - ")

    var selected = []
    $.each($("input[name='names_comp']:checked"), function () {
        selected.push($(this).val());
    });
    document.object_members = selected.slice(0)
    document.string_members = selected.join(",")
}

//function showIds() {
//    var info_div = $("#info_ids")[0]
//    if (info_div.style.display === "none") {
//        info_div.style.display = "block";
//    } else {
//        info_div.style.display = "none";
//    }
//}

function createPie(html_name) {
    var pie = new CanvasJS.Chart(html_name, {
        theme: "light2",
        animationEnabled: true,
        title: {
            fontFamily: "Calibri",
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
            dataPoints: getDummyDatapoints()
        }]
    });
    return pie
}

function explodePie(e) {
    for (var i = 0; i < e.dataSeries.dataPoints.length; i++) {
        if (i !== e.dataPointIndex)
            e.dataSeries.dataPoints[i].exploded = false;
    }
}

function getDummyDatapoints() {
    return [
        { y: 33, label: "Win" },
        { y: 34, label: "Loss" },
        { y: 33, label: "Tie" }
    ]
}




function createColumns(html_name) {

    var chart = new CanvasJS.Chart("chartContainer2", {
        animationEnabled: true,
        title: {
            fontFamily: "Calibri",
            text: "W/L/T by map",
            fontSize: 22,
        },
        //        axisX: {
        //            interval: 1,
        //            intervalType: "date"
        //        },
        axisY: {
            gridColor: "#B6B1A8",
            tickColor: "#B6B1A8"
        },
        toolTip: {
            shared: true,
            content: toolTipContent
        },
        data: [{
            type: "stackedColumn",
            showInLegend: true,
            color: "#009900",
            name: "Wins",
            dataPoints: [
                { y: 6.75, label: "mapa1" },
                { y: 8.57, label: "mapa2" },
                { y: 10.64, label: "mapa3" },
                { y: 13.97, label: "mapa4" }
            ]
        },
        {
            type: "stackedColumn",
            showInLegend: true,
            name: "Loses",
            color: "#990000",
            dataPoints: [
                { y: 6.75, label: "mapa1" },
                { y: 8.57, label: "mapa2" },
                { y: 10.64, label: "mapa3" },
                { y: 13.97, label: "mapa4" }
            ]
        },
        {
            type: "stackedColumn",
            showInLegend: true,
            name: "Ties",
            color: "#999999",
            dataPoints: [
                { y: 6.75, label: "mapa1" },
                { y: 8.57, label: "mapa2" },
                { y: 10.64, label: "mapa3" },
                { y: 13.97, label: "mapa4" }
            ]
        }]
    });

    return chart

}

function toolTipContent(e) {
    var str = "";
    var total = 0;
    var str2, str3;
    for (var i = 0; i < e.entries.length; i++) {
        var str1 = "<span style= \"color:" + e.entries[i].dataSeries.color + "\"> " + e.entries[i].dataSeries.name + "</span>: <strong>" + e.entries[i].dataPoint.y + "</strong><br/>";
        total = e.entries[i].dataPoint.y + total;
        str = str.concat(str1);
    }
    str2 = "<span style = \"color:DodgerBlue;\"><strong>" + e.entries[0].dataPoint.label + "</strong></span><br/>";
    total = Math.round(total * 100) / 100;
    str3 = "<span style = \"color:Tomato\">Total:</span><strong>" + total + "</strong><br/>";
    return (str2.concat(str)).concat(str3);
}





// ------------------------------------------------------------------
// MATCH FILTERS
// ------------------------------------------------------------------

function getFilterMode() {
    var mode
    if ($("#option_all").is(":checked")) {
        mode = "all"
    } else if ($("#option_any").is(":checked")) {
        mode = "any"
    } else if ($("#option_exc").is(":checked")) {
        mode = "exc"
    }
    return mode
}


function filterMaps(partidas) {
    var filtradas = []
    for (var partida of partidas) {
        if (document.object_maps.includes(partida['map'])) {
            filtradas.push(partida)
        }
    }
    return filtradas
}


function dateToTs(date_str, selected_included) {
    myDate = date_str.split("/");
    // console.log(myDate);
    var newDate = myDate[1] + "/" + myDate[0] + "/" + myDate[2];
    ts = new Date(newDate).getTime();
    if (selected_included) {
        ts = ts + 24 * 3600 * 1000
    }
    return ts
}


function filterDates(partidas) {
    var start_date = $("#start_date").val()
    var end_date = $("#end_date").val()
    start_date = dateToTs(start_date)
    end_date = dateToTs(end_date, selected_included = true)

    if (!end_date) {
        end_date = new Date().getTime()
    }
    if (!start_date) {
        start_date = 0
    }
    // console.log("Filter dates:"+start_date+end_date)
    var filtradas = []
    for (var partida of partidas) {
        if (partida['_id'] >= start_date && partida['_id'] < end_date) {
            filtradas.push(partida)
        }
    }
    return filtradas
}

function filterPlayers(partidas, filterMode) {

    var filterMode = getFilterMode()

    var filtradas = []
    for (var partida of partidas) {

        var team_field = "players_team" + partida.local_team  // ekipo dofitos
        var players_en_partida = []  // saco ids de los jugadores del ekipo dofito

        for (var player of partida[team_field]) {
            players_en_partida.push(player['steam_id'])
        }
        // console.log("players en partida" + players_en_partida)

        // modo todos los seleccionados deben aperecer en la partida
        if (filterMode == "all") {
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
                filtradas.push(partida)
            }

            // modo cualquiera de los seleccionados (ANY)
        } else if (filterMode == "any") {
            var success = false  // tiraremos a false el success hasta que veamos un player de los clickados en la game
            for (var player of document.object_members) {
                if (players_en_partida.includes(player)) {  // de los players clicados en el front busco si alguno SI esta en la partida
                    success = true
                    break
                }
            }
            if (success) {
                filtradas.push(partida)
            }
        }
    }
    return filtradas
}

function compare_game_dates_asc( a, b ) {
    return (Number(a._id) - Number(b._id))
}
function compare_game_dates_desc( a, b ) {
    return (Number(b._id) - Number(a._id))
}
function sort_games_by_date(games, ascending=true) {
    if (ascending) {
        return games.sort(compare_game_dates_asc)
    } else {
        return games.sort(compare_game_dates_desc)
    }
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
