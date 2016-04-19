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
    data = {
    //publication
        doi: $('#id_doi').val(),
        title: $('#id_title').val(),
        url: $('#id_url').val(),
        status: $('#id_status').val(),
        project_number: $('#id_project_number').val(),
        task_number: $('#id_task_number').val(),
        publication_date: $('#id_publication_date').val(),
        abstract: $('#id_abstract').val()
    //active
    };
    console.log('got here');
    elements = $('#tabs .active input')
    $.each(elements, function(index, elem) {
        console.log(elem.val());
    });

}