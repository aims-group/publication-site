function doisearch(showform) {
    $('#loading').show();
    var doi = $("#doi-field").val();
    if (showform === true) {
        doi = ''
    }
    $.ajax({
        url: '/finddoi/',
        method: 'GET',
        data: {'doi': doi},
        success: function(result){
            $('#loading').hide();
            $("#publication-form-wrapper").html(result);
            if (showform === true) {
                $('.alert.alert-warning').hide();
            }
        },
        error: function(jqxhr, status, error){
            $('#loading').hide();
            alert("Ajax Failed");
            console.log(jqxhr);
            console.log(status);
            console.log(error);
        }
    });
}

$(document).ready(function(){
    $('#loading').hide();
});

function submitPublication() {
    $.ajax({
        type: 'POST',
        url: '/new',
        data: $('form').serialize(),
    })

}

