


function cloneMore(element) {
    var newElement = $(element).clone(true);
    var total = $('#id_form-TOTAL_FORMS').val();
    newElement.find('#id_form-'+ total-1 +'-DELETE').closest('td').remove()
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        console.log($(this).val());
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id, "value": ''}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_form-TOTAL_FORMS').val(total);
    $('#author-form tr:last').after(newElement);
}