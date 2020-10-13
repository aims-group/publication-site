var projectSelectedCount = 0;

$(document).ready(function(){
    $('#loading').hide();
    $('#publication-optional-inputs').accordion({
      collapsible: true
    });
    var active_found = false;
    var active_index = 0;
    $('.project-checkbox').each(function(index, checkbox){
        if(checkbox.checked){
            if(!active_found){
                active_index = index;
                active_found = true;
            }
            $("#".concat(checkbox.value, "-tab")).show() //find corresponding meta tab and show it
            ++projectSelectedCount;
        }
        else{
            $("#".concat(checkbox.value, "-tab")).hide() //find corresponding meta tab and hide it
        }
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
    if(active_found){
        $( "#meta-tabs" ).tabs({
            active: active_index,
            collapsible: true
          });
    } else {
        $( "#meta-tabs" ).tabs({
            active: false,
            collapsible: true
          });
    }
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

$( "#project-form" ).on('change', '.project-checkbox', function(event) {
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
        if(projectSelectedCount > 0){
            // find another selected project to make active
            $('.project-checkbox').each(function(index, checkbox){
                if(checkbox.checked){
                    $('#meta-tabs').tabs("option", "active", index);
                    return false;
                }
            });
        } else {
            // hide all tabs if no projects are selected
            $('#meta-tabs').tabs("option", "active", false);
        }
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

function doisearch() {
    $('#loading').show();
    var doi = $("#doi-field").val();
    $.ajax({
        url: 'finddoi',
        method: 'GET',
        data: {'doi': doi},
        success: function(data){
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
                    if(data.missing_journal){
                        var warn = $('<div/>')
                        .html( 'The journal publishing this article, <b>' + data.container_title + '</b>, was not found in the list.'
                             + ' To add this journal, please submit an issue to our <a href="https://github.com/aims-group/publication-site/issues/">GitHub Issues</a> page'
                             + ' with the title: <br> <b>"Please add journal named: ' + data.container_title + '."</b> <br><br>'
                             + ' Currently, your publication will be registered with journal set to "Other".  Once you\'ve submitted the issue,'
                             + ' as described above, and the journal name you requested has been added to the list, please go to the Edit'
                             + ' page, select your publication, and replace "Other" with the actual name of the journal.')
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

function showForm(){
//    https://bugs.jqueryui.com/ticket/3905
    $("#publication-form-wrapper").removeClass("hidden");
    $('#publication-optional-inputs').accordion( "refresh" );
    $('.optional-inputs').accordion( "refresh" );
}
