var meta = $('.meta-form-list ul li');

$('#meta-filter').keyup(function() {
    var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
    meta.show().filter(function() {
        var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
        console.log(text);
        return !~text.indexOf(val);
    }).hide();
});