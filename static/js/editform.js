$(document).ready(function(){
    $('#loading').hide();
    $('#publication-optional-inputs').accordion({
      collapsible: true
    });
    $.each($('.meta-form-list ul'), function(index, element) {
        if($(element).html() === "")
        {
            //Check each meta form to see if it is empty. if so, hide it
            $(element).parent().hide();
        }
    });
    if($("#id_status option:selected").text() !== "Published"){
        $( "#id_doi" ).parent().removeClass('required');
    }
    $( "#meta-tabs" ).tabs();
});

$('#id_form-TOTAL_FORMS').val($('tr.author').length);
var count = parseInt($('#id_form-TOTAL_FORMS').val());
for(i=0; i < count; i++) {
    $('#id_form-' + i + '-DELETE').closest('td').hide();
}

$( "#id_status" ).change(function() {
    if($("#id_status option:selected").text() === "Published"){
        $( "#id_doi" ).parent().addClass('required');
    }
    else{
        $( "#id_doi" ).parent().removeClass('required');
    }
});

$( '#meta-tabs' ).on( "tabscreate", function( event, ui ) {
    $('#meta-tabs .active').removeClass('active');
    $(ui.tab).addClass('active');
    $('#meta_type').val($(ui.tab).text());
});

$( '#meta-tabs' ).on( "tabsactivate", function( event, ui ) {
        $(ui.oldTab).removeClass('active');
        $(ui.newTab).addClass('active');
        $('#meta_type').val($(ui.newTab).text());
});

var meta = $('.meta-form-list ul li');
$("#meta-filter").keyup(function() {
    console.log("hello");
    var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
    meta.show().filter(function() {
        var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
        return !~text.indexOf(val);
    }).hide();
});

function doisearch() {
    $('#loading').show();
    var doi = $("#doi-field").val();
    $.ajax({
        url: '/finddoi',
        method: 'GET',
        data: {'doi': doi},
        success: function(data){
        console.log(data);
            if(data.success){
                $('.warning-message').removeClass('alert alert-warning').text('');
                if(data.doi) $('#id_doi').val(data.doi);
                if(data.title) $('#id_title').val(data.title);
                if(data.publication_date) $('#id_publication_date').val(data.publication_date);
                if(data.url) $('#id_url').val(data.url);
                if(data.title) $('#id_title').val(data.title);
                if($('#id_book-book_name').length){
                    if(data.book_name) $($('#id_book_name')).val(data.book_name);
                    if(data.book_name) $('#id_book_name').val(data.book_name);
                    if(data.start_page) $('#id_start_page').val(data.start_page);
                    if(data.end_page) $('#id_end_page').val(data.end_page);
                    if(data.publisher) $('#id_publisher').val(data.publisher);
                }
                else if($('id_conf-conference_name').length){
                    if(data.conference_name) $('#id_conference_name').val(data.conference_name);
                    if(data.start_page) $('#id_start_page').val(data.start_page);
                    if(data.end_page) $('#id_end_page').val(data.end_page);
                    if(data.publisher) $('#id_publisher').val(data.publisher);
                }
                else if($('#id_journal-name')){
                    if(data.journal_name) $('#id_journal_name').val(data.journal_index+1);
                    if(data.volume_number) $('#id_volume_number').val(data.volume_number);
                    if(data.article_number) $('#id_article_number').val(data.article_number);
                    if(data.start_page) $('#id_start_page').val(data.start_page);
                    if(data.end_page) $('#id_end_page').val(data.end_page);
                    if(data.guessed_journal){
                        var warn = $('<div/>')
                        .text('Warning: Journal name may not be accurate. Please check that it is correct.')
                        .addClass('alert alert-warning');
                        $('#journal-warning').append(warn);
                    }
                }
                else if($('#id_mag-name')){
                    if(data.mag_name) $('#id_magazine-name').val(data.magazine_name);
                    if(data.volume_number) $('#id_volume_number').val(data.volume_number);
                    if(data.article_number) $('#id_article_number').val(data.article_number);
                    if(data.start_page) $('#id_start_page').val(data.start_page);
                    if(data.end_page) $('#id_end_page').val(data.end_page);
                }
                var authorCount = $('#id_form-TOTAL_FORMS').val();
                while(data.authors_list.length > authorCount){
                    cloneMore(emptyform, num);
                    authorCount = $('#id_form-TOTAL_FORMS').val();
                }
                $.each($('.author-name.tt-input'), function(index, elem){
                    if(data.authors_list.length > index){
                        $(elem).val(data.authors_list[index].name);
                    }
                    else{
                        return false; //break out of loop
                    }
                });
            }
            else{
                $('.warning-message').addClass('alert alert-warning').text(data.message);
            }
            $('#loading').hide();
            showForm();
        },
        error: function(jqxhr, status, error){
            $('.warning-message').removeClass('alert alert-warning').text('');
            $('#loading').hide();
            showForm();
            alert("Ajax Failed");
        }
    });
}