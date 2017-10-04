var projectSelectedCount = 0;

$(document).ready(function(){
    $('#loading').hide();
    var JOURNAL = 2;
    //The variable indicates which tab should be set as the "active" tab on page load
    setUpForm(JOURNAL);
    var batchDoi = document.getElementById("batch_doi").value;
    if(batchDoi){
        document.getElementById("doi-field").setAttribute("value", batchDoi);
        doisearch()
    }

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

$( "#publication-form-wrapper" ).on('change', '.project-checkbox', function(event) {
    var metaTab = $('#'.concat(this.value, "-tab"))[0];
    if(this.checked){
        $(metaTab).show();
        if(projectSelectedCount == 0){ //then since there will only be one tab, make it active
            var tabNumber = parseInt(metaTab.firstElementChild.getAttribute("href").split('-')[2]); //href holds a string "meta-tabs-x" where x is a number
            $('#meta-tabs').tabs("option", "active", tabNumber-1); //Off by one. id starts at one, but jquery-ui starts at 0
        }
        ++projectSelectedCount;
    }
    else{
        if($('#meta-tabs .panel-heading .ui-tabs-active')[0].id === "".concat(this.value, "-tab")){ //if the deselected project was the active meta tab, hide the content 
            $('#meta-tabs').tabs("option", "active", -1); //set active to an invalid index so nothing is active
        }
        $(metaTab).hide();
        --projectSelectedCount;
    }
    
});


var meta = $('.meta-form-list ul li');
$("#meta-filter").keyup(function() {
    var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
    meta.show().filter(function() {
        var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
        return !~text.indexOf(val);
    }).hide();
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
    $('.project-checkbox:not(:checked)').each(function(index, element){
        var name = element.value; //Grab the name of the unchecked box
        var tab = $("#".concat(name, "-tab")); //find the meta form tab it refers to
        var link = $("#".concat(name, "-tab a")).attr("href"); //grab the link from the tab itself
        $(link).remove(); //Remove the element the link points to. 
        //This prevents meta data from being sent for unrelated projects. 
        //i.e. If CMIP5 is not selected as a project, we don't want to send meta data about it 
    });
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: $('form').serialize(),
        success: function(result){
            if(result.batch_doi){
                document.getElementById("doi-field").setAttribute("value", result.batch_doi);
                document.getElementById("batch-alert-text").innerText = result.batch_doi;
                doisearch();
                window.scrollTo(0, 0);
            }
            else{
                window.location.replace("/review");
            }
        },
    }).fail(function($xhr) {
        $("#publication-form-wrapper").html($xhr.responseText);
        setUpForm(active, metaActive);
        window.scrollTo(0, 0);
    });
}

function setUpForm() {
    //Grab the active tab numbers from arguments or default to 0
    var active = arguments[0] === undefined ? 0 : arguments[0];
    $('#publication-optional-inputs').accordion({
      collapsible: true, active: false
    });
    $('.optional-inputs').accordion({
      collapsible: true, active: false
    });
    $('.project-checkbox').each(function(index, checkbox){
        if(checkbox.checked){
            $("#".concat(checkbox.value, "-tab")).show() //find corresponding meta tab and show it
            ++projectSelectedCount;
        }
        else{
            $("#".concat(checkbox.value, "-tab")).hide() //find corresponding meta tab and hide it
        }
    });
    $( "#tabs" ).tabs({ active: active });
    $( "#meta-tabs" ).tabs();
    isDoiRequired();
    var count = parseInt($('#id_form-TOTAL_FORMS').val());
    for(i=0; i < count; i++) {
        $('#id_form-' + i + '-DELETE').closest('td').remove();
    }
    $.each($('.meta-form-list ul'), function(index, element) {
        if($(element).html() === "")
        {
            //Check each meta form to see if it is empty. if so, hide it
            $(element).parent().hide();
        }
    });
}

function showForm(){
//    https://bugs.jqueryui.com/ticket/3905
    $("#publication-form-wrapper").removeClass("hidden");
    $('#publication-optional-inputs').accordion( "refresh" );
    $('.optional-inputs').accordion( "refresh" );
}
