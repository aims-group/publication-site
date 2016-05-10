$(document).ready(function(){
    $.each($('#id_model li label'), function(index, element) {
        newelem = $('<input/>');
        $(newelem).attr('id', 'ensemble_'+index);
        $(newelem).attr('name', 'ensemble');
        if(ensemble.length > 0 && ensemble[0][0] === index+1) {
            $(newelem).val(ensemble[0][1]);
            ensemble.shift(); //treat the array as a queue. [0] is always the next checked element
        }
        $(element).after(newelem);
    });
});

$('#id_form-TOTAL_FORMS').val($('tr.author').length);
var count = parseInt($('#id_form-TOTAL_FORMS').val());
for(i=0; i < count; i++) {
    $('#id_form-' + i + '-DELETE').closest('td').hide();
}

