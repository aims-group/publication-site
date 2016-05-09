$('#author-form').on('click', 'a.model-author-delete', function( event ){
    elem = $(event.target).closest('tr');
    $(elem).hide();
    $(elem).find('td input:checkbox').prop('checked', true);
});

$('#author-form').on('click', 'a.model-author-delete', function( event ){
    elem = $(event.target).closest('tr');
    $(elem).hide();
    $(elem).find('td input:checkbox').prop('checked', true);
});


function cloneMore(element, num) {
    var newElement = $(element).clone(true);
    var total = $('#id_form-TOTAL_FORMS').val();
    newElement.find('#id_form-'+ num +'-DELETE').closest('td').remove()
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (num) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (num) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_form-TOTAL_FORMS').val(total);
    $('#author-form tr:last').after(newElement);
}