$(document).ready(function() {
    $('#principal').DataTable({
        "paging": false
    })
})

document.all_members = null
document.selected_members = [] //pendiente guardar en cookie/local storage la seleccion
document.string_members = ""

function myFunc(vars) {
    document.all_members = vars
    return vars
}

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
});


console.log("CARAPOLLA")