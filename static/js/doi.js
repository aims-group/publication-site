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

$( "#publication-form-wrapper" ).on('change', '#id_pub-status', function() {
    isDoiRequired();
});

function isDoiRequired(){
    if($("#id_pub-status option:selected").text() === "Published"){
        $( "#id_pub-doi" ).parent().addClass('required');
    }
    else{
        $( "#id_pub-doi" ).parent().removeClass('required');
    }
}

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
                    $('#journal-warning').empty();
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
                    $('#id_journal-journal_name').val(data.journal_index+1);
                    $('#id_journal-volume_number').val(data.volume_number);
                    $('#id_journal-article_number').val(data.article_number);
                    $('#id_journal-start_page').val(data.start_page);
                    $('#id_journal-end_page').val(data.end_page);

                    if(data.guessed_journal){
                      var warn = $('<div/>')
                      .text('Warning: Journal name may not be accurate. Please check that it is correct.')
                      .addClass('alert alert-warning');
                      $('#journal-warning').append(warn);
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

function setUpForm() {
    var active = arguments[0] === undefined ? 0 : arguments[0];
    var metaActive = arguments[1] === undefined ? 0 : arguments[1];
    $('#publication-optional-inputs').accordion({
      collapsible: true, active: false
    });
    $('.optional-inputs').accordion({
      collapsible: true, active: false
    });
    $( "#tabs" ).tabs({ active: active });
    $( "#meta-tabs" ).tabs({ active: metaActive });
    isDoiRequired();
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
    $('.optional-inputs').accordion( "refresh" );
}

