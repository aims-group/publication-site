$(document).ready(function(){
    $('#loading').hide();
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

function doisearch(showform) {
    $('#loading').show();
    var doi = $("#doi-field").val();
    if (showform === true) {
        doi = ''
    }
    $.ajax({
        url: '/finddoi',
        method: 'GET',
        data: {'doi': doi},
        success: function(result){
            $('#loading').hide();
            $("#publication-form-wrapper").html(result);
            setUpForm();
            $.each($('#id_model li label'), function(index, element) {
                newelem = $('<input/>');
                $(newelem).attr('id', 'ensemble_'+index);
                $(newelem).attr('name', 'ensemble');
                $(newelem).attr('type', 'number');
                $(element).after(newelem);
            });
            if (showform === true) {
                $('.alert.alert-warning').hide();
            }
        },
        error: function(jqxhr, status, error){
            $('#loading').hide();
            alert("Ajax Failed");
        }
    });
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
        $.each($('#id_model li label'), function(index, element) {
            newelem = $('<input/>');
            $(newelem).attr('id', 'ensemble_'+index);
            $(newelem).attr('name', 'ensemble');
            $(newelem).attr('type', 'number');
            $(newelem).val(ensemble[index]);
            $(element).after(newelem);
        });
        window.scrollTo(0, 0);
    });
}

function setUpForm(active = 0, metaActive = 0) {
    $('#publication-optional-inputs').accordion({
      collapsible: true, active: false
    });
    $( "#tabs" ).tabs({ active: active });
    $( "#meta-tabs" ).tabs({ active: metaActive });
    var count = parseInt($('#id_form-TOTAL_FORMS').val());
    for(i=0; i < count; i++) {
        $('#id_form-' + i + '-DELETE').closest('td').remove();
    }
}
