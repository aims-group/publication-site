$(document).ready(function(){
    $('#loading').hide();
    setUpForm();
});

$( "#publication-form-wrapper" ).on( "tabscreate", '#tabs', function( event, ui ) {
    $('#tabs .active').removeClass('active');
    $(ui.tab).addClass('active');
    $('#pub_type').val($(ui.tab).text());
});

$( "#publication-form-wrapper" ).on( "tabsactivate", '#tabs', function( event, ui ) {
        $(ui.oldTab).removeClass('active');
        $(ui.newTab).addClass('active');
        $('#pub_type').val($(ui.newTab).text());
        $('.optional-inputs').accordion( "refresh" );
});

$( "#publication-form-wrapper" ).on( "tabscreate", '#meta-tabs', function( event, ui ) {
    $('#meta-tabs .active').removeClass('active');
    $(ui.tab).addClass('active');
    $('#meta_type').val($(ui.tab).text());
});

$( "#publication-form-wrapper" ).on( "tabsactivate", '#meta-tabs', function( event, ui ) {
        $(ui.oldTab).removeClass('active');
        $(ui.newTab).addClass('active');
        $('#meta_type').val($(ui.newTab).text());

});

$( "#id_pub-status" ).change(function() {
    if($("#id_pub-status option:selected").text() === "Published"){
        $( "#id_pub-doi" ).parent().addClass('required');
    }
    else{
        $( "#id_pub-doi" ).parent().removeClass('required');
    }
});


function doisearch(showFormClicked) {
    if (showFormClicked === true) {
        $('.warning-message').removeClass('alert alert-warning').text('');
        showForm();
    }
    else {
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
                    $('#id_pub-doi').val(data.doi);
                    $('#id_pub-title').val(data.title);
                    $('#id_pub-publication_date').val(data.publication_date);
                    $('#id_pub-url').val(data.url);
                    $('#id_pub-title').val(data.title);
                    $('#id_book-book_name').val(data.book_name);
                    $('#id_book-start_page').val(data.start_page);
                    $('#id_book-end_page').val(data.end_page);
                    $('#id_book-publisher').val(data.publisher);
                    $('#id_conf-conference_name').val(data.conference_name);
                    $('#id_conf-start_page').val(data.start_page);
                    $('#id_conf-end_page').val(data.end_page);
                    $('#id_conf-publisher').val(data.publisher);
                    $('#id_journal-name').val(data.journal_name);
                    $('#id_journal-volume_number').val(data.volume_number);
                    $('#id_journal-article_number').val(data.article_number);
                    $('#id_journal-start_page').val(data.start_page);
                    $('#id_journal-end_page').val(data.end_page);
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
}

function submitPublication() {
    var ensemble = []
    var active = $( "#tabs" ).tabs( "option", "active" );
    var metaActive = $( "#meta-tabs" ).tabs( "option", "active" );
    $.each($("#id_model input[name='ensemble']"), function(index, element){
        ensemble[index] = $(element).val()
    });
    $('#meta-tabs .panel-body div[style="display: none;"]').remove(); //remove unused form elements before serializing
    $.ajax({
        type: 'POST',
        url: '/new',
        data: $('form').serialize(),
        success: function(result){
            window.location.replace("/review");
        },
    }).fail(function($xhr) {
        $("#publication-form-wrapper").html($xhr.responseText);
        setUpForm(active, metaActive);
        window.scrollTo(0, 0);
    });
}

function setUpForm(active = 0, metaActive = 0) {
    $('#publication-optional-inputs').accordion({
      collapsible: true, active: false
    });
    $('#journal-optional-inputs').accordion({
      collapsible: true, active: false
    });
    $( "#tabs" ).tabs({ active: active });
    $( "#meta-tabs" ).tabs({ active: metaActive });
    var count = parseInt($('#id_form-TOTAL_FORMS').val());
    for(i=0; i < count; i++) {
        $('#id_form-' + i + '-DELETE').closest('td').remove();
    }
    $.each($('#id_model li label'), function(index, element) {
        newelem = $('<input/>');
        $(newelem).attr('id', 'ensemble_'+index);
        $(newelem).attr('name', 'ensemble');
        $(newelem).attr('type', 'number');
        $(element).after(newelem);
    });
}

function showForm(){
//    https://bugs.jqueryui.com/ticket/3905
    $("#publication-form-wrapper").removeClass("hidden");
    $('#publication-optional-inputs').accordion( "refresh" );
}

