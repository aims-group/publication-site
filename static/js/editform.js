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
    emptyform = $('tr.author:last');
});

$('#id_form-TOTAL_FORMS').val($('tr.author').length);
var count = parseInt($('#id_form-TOTAL_FORMS').val());
for(i=0; i < count; i++) {
    $('#id_form-' + i + '-DELETE').closest('td').hide();
}

$('#add_author').click(function( event ) {
    event.preventDefault();
    cloneMore(emptyform);
});

$('#author-form').on('click', '.author-delete', function( event ) {
    event.preventDefault();
    var total = $('#id_form-TOTAL_FORMS').val();
    if(total > 1) {
        if ($(event.target).closest('td').next().val()) {
            elem = $(event.target).closest('tr');
            $(elem).hide();
            $(elem).find('td input:checkbox').prop('checked', true);
        }
        else {
            var form = $(event.target).closest('.author');
            $('#id_form-TOTAL_FORMS').val(total-1);
            $(form).remove();
        }
    }
    else {
        alert('Publications must have at least 1 author.');
    }
});