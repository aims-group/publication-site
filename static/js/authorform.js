$(function() {
    emptyform = $('tr.author:last');
    authors = new Bloodhound({
    datumTokenizer: function(datum) {
        var nameTokens = Bloodhound.tokenizers.whitespace(datum.name);
        var instTokens = Bloodhound.tokenizers.whitespace(datum.institution);

        return nameTokens.concat(instTokens);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
        url: '../ajax/data/prefetch_authors/',
        cache: false
        }
    });


    $('.typeahead-a').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: 'authors',
        source: authors,
        displayKey: 'name',
        templates: {
            suggestion: function(data){
                return '<p>' + data.name + ' - <em>' + data.institution + '</em></p>';
            }
        }
    });
});

$('#author-form').on('typeahead:select', '.author-name', function(obj, datum, name) {
    console.log($(this));
    $(this).closest('td').next('').find(':input').val(datum.institution);
});

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



//var institutions = new Bloodhound({
//datumTokenizer: Bloodhound.tokenizers.whitespace,
//queryTokenizer: Bloodhound.tokenizers.whitespace,
//prefetch: '../ajax/data/institutions/'
//});
//
//$('.typeahead-i').typeahead({
//    hint: true,
//    highlight: true,
//    minLength: 1
//},
//{
//    name: 'institutions',
//    source: institutions
//});