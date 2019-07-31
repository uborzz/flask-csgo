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
    console.log( "document ready!" )

    $('#boxes').on('change', function(){
        var selected = []

        $.each($("input[name='names']:checked"), function(){
            console.log($(this).val())
            selected.push($(this).val());
        });

        document.string_members = selected.join("|")
        $('#cont').val(document.string_members)
        console.log(document.string_members)
        filterByNames()
    });

    $('#boxes_comp').on('change', function(){
        var selected = []

        $.each($("input[name='names_comp']:checked"), function(){
            console.log($(this).val())
            selected.push($(this).val());
        });

        document.string_members = selected.join("|")
        $('#cont').val(document.string_members)
        console.log(document.string_members)
    });

    $('#boxes_maps').on('change', function(){
        var selected = []

        $.each($("input[name='names_maps']:checked"), function(){
            console.log($(this).val())
            selected.push($(this).val());
        });

        document.string_members = selected.join("|")
        $('#maps').val(document.string_members)
        console.log(document.string_members)
    });

    var chart = new CanvasJS.Chart("chartContainer", {
        theme: "light2",
        animationEnabled: false,
        title: {
            text: "Total",
            fontSize: 22
        },
//        subtitles: [{
//            text: "United Kingdom, 2016",
//            fontSize: 16
//        }],
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
                    { y: 42, label: "Win" },
                    { y: 21, label: "Loss"},
                    { y: 24.5, label: "Tie" }
                ]
    }

});
