$(document).ready(function(){

    var meta = $('.meta-form-list ul li');
    $('#meta-filter').keyup(function() {
        var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
        meta.show().filter(function() {
            var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
            return !~text.indexOf(val);
        }).hide();
    });

    //https://github.com/uxsolutions/bootstrap-datepicker/
    $( "#id_date_start" ).datepicker({
        changeMonth: true,
        changeYear: true
    });
    $( "#id_date_end" ).datepicker({
        changeMonth: true,
        changeYear: true
    });
    if($('#result-count').length != 0){
        updateSearchCount();
    }

    $('i.help-tooltip').tooltip(); //initialize all tolltips on the page
     
});

$("form").on("change", '.search-input', function(event){
    //if the user has changed an input and blur fires, report number of results
    updateSearchCount();
});

function updateSearchCount(){
    var form = $('form').serialize()
    form = form.concat("&ajax=true"); 
    $.ajax({
        type: 'POST',
        url: '/advanced_search',
        data: form,
        success: function(result){
            $('#result-count').text(result.count);
        },
    }).fail(function($xhr) {
        //Failed to get search count due to server error
    });
}


