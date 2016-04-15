function doisearch() {
    $('#loading').show();
    var doi = $("#doi-field").val();
    console.log("form value: " + doi);
    $.ajax({
        url: '/finddoi/',
        method: 'GET',
        data: {'doi': doi},
        success: function(result){
            $('#loading').hide();
            $("#publication-form-wrapper").html(result);
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
    console.log("Submitting publication");
}