function doisearch() {
    var doi = $("#doi-field").val();
    console.log("form value: " + doi);
    $.ajax({
        url: '/finddoi/',
        method: 'GET',
        data: {'doi': doi},
        success: function(result){
            $("#publication-form-wrapper").html(result);
        },
        error: function(jqxhr, status, error){
            alert("Ajax Failed");
            console.log(jqxhr);
            console.log(status);
            console.log(error);
        }
    });
}