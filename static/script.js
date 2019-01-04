$(document).ready(function() {
    $('#principal').DataTable({
        "paging": false
    })
})

document.all_members = null
document.selected_members = []
document.string_members = ""

function myFunc(vars) {
    document.all_members = vars
    return vars
}

$( document ).ready(function() {
    console.log( "ready!" )

    // SEGUIR AKI
    $('#boxes').on('change', function(){
        document.selected_members = []
        $("#boxes").each(function(){
            console.log($(this).val())
            document.selected_members.push($(this).val());
        });
        document.string_members = document.selected_members.toString()
        $('#cont').val(document.string_members)
        console.log(document.string_members)
    });
});


console.log("CARAPOLLA")