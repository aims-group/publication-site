$( document ).ready(function() {
    year_sort_toggle = false;
    author_sort_toggle = false;
    title_sort_toggle = false;
    last_sort = 'year';
    $('#year-heading').addClass('descending');
    $('#search-toggle').click(function(){
        $('#search-container').slideToggle('fast');
    });

    try{
        $(".publication-container").jscroll({
            nextSelector: 'a.jscroll-next:last',
            callback: function(){
                $('.jscroll-added div').first().unwrap();
                if (last_sort === 'year'){
                    year_sort_toggle = !year_sort_toggle;
                    year_sort();
                }
                else if (last_sort === 'author'){
                    author_sort_toggle = !author_sort_toggle;
                    author_sort();
                }
                else if (last_sort === 'title'){
                    title_sort_toggle = !title_sort_toggle;
                    title_sort();
                }
            },
        });
    }
    catch(e){
        //jscroll might not be loaded. just move on if it is not present
    }
});

$('#facet-links-container input.radio-sort').change(function(){
    if(this.value == 'alphabetical'){
        var array = []
        $('#facet-links-container table tr').each(function(ind){
            var obj = {name: $(this).find('td:nth-child(1)').text(), elem: $(this).detach()};
            array.push(obj);
        });
        array.sort(function(a, b){
            return a.name.localeCompare(b.name);
        });
        var jq = $();
        array.forEach(function(obj){
             jq = $(jq).push(obj.elem);
        });
        $(jq).appendTo('#facet-links-container table');
    }
    else{ // value == 'count'
        var array = []
        $('#facet-links-container table tr').each(function(ind){
            var obj = {count: parseInt($(this).find('td:nth-child(2)').text()), elem: $(this).detach()};
            array.push(obj);
        });
        array.sort(function(a, b){
            return b.count - a.count;
        });
        var jq = $();
        array.forEach(function(obj){
             jq = $(jq).push(obj.elem);
        });
        $(jq).appendTo('#facet-links-container table');
    }
});

  function show_citation(id){
    if ($("div #citation"+id).html() == "empty"){
      url = "ajax/citation/" + id
      $.ajax({
        type: "GET",
        url: url,
        data: {},
        dataType: 'json',
        success: function(data){
        var authorstring = ''
            $.each(data.authors, function(index, author){
                if(index == 0){
                    authorstring += author;
                }
                else{
                    authorstring += (', ' + author);
                }
            });
            if (data.type == 'Journal'){
                var citation = $('<p/>')
                    .append($('<span/>').text(authorstring + ', ' + data.year + ': ' + data.title + '. '))
                    .append('<span class="citation-italic">' + data.journal_name + '</span>, ');
                if (data.volume_number){
                    citation.append('<span class="citation-bold">'+ data.volume_number + '</span>, ');
                }
                if (data.start_page && data.end_page){
                    citation.append('<span>' + data.start_page + '-' + data.end_page + ', ' + '</span>');
                }
                else if (data.start_page) {
                    citation.append('<span>' + data.start_page + ', ' +'</span>');
                }
                if (data.doi.indexOf('doi:') === 0){
                    data.doi = data.doi.slice(4,data.doi.length).trim();
                }
                if (data.doi.indexOf('doi.org/') > -1){
                    data.doi = data.doi.split('doi.org/')[1]
                }
                if (data.doi !== ''){
                    citation.append('<a target="_blank" href="https://dx.doi.org/'+ data.doi +'">doi:' + data.doi + '.' +'</a>');
                }
            }
            else if (data.type == 'Book'){
                var citation = $('<span/>')
                    .append($('<span/>').text(authorstring + ', ' + data.year + ': ' ))
                if(data.chapter_title){
                    citation.append(data.chapter_title + '. ');
                }
                if(data.book_name){
                    citation.append('<span class="citation-italic">'+ data.book_name + '</span>, ');
                }
                if(data.editor){
                    citation.append(data.editor + ', ');
                }
                if(data.publisher){
                    citation.append(data.publisher + ', ');
                }
                if(data.start_page && data.end_page){
                    citation.append('<span>' + data.start_page + '-' + data.end_page + '.' + '</span>');
                }
                else if (data.start_page) {
                    citation.append('<span>' + data.start_page + ', ' +'</span>');
                }
            }
            else {
                var citation = $('<span/>')
                .append($('<span/>').text(authorstring + ': ' + data.title + '. ' + data.year + '. '))
                if (data.url){
                    citation.append($('<a/>').text(data.url).attr('href', data.url).attr('target', '_blank'));
                }
                if (!data.url && data.doi){
                    if (data.doi.indexOf('doi:') === 0){
                    data.doi = data.doi.slice(4,data.doi.length).trim();
                    }
                    if (data.doi.indexOf('doi.org/') > -1){
                        data.doi = data.doi.split('doi.org/')[1]
                    }
                    if (data.doi !== ''){
                        citation.append('<a target="_blank" href="https://dx.doi.org/'+ data.doi +'">' + ('https://dx.doi.org/'+data.doi) + '.' +'</a>');
                    }
                }
            }
          $("div #citation"+id).html(citation);
          $("div #citation"+id).toggle();
        },
        error: function(request, status, error){
          alert(request + " | " +  status + " | " +  error);
        }
      });
    }
    else{
       $("div #citation"+id).toggle();
    }
  }
  function show_more_info(id){
    if ($("div #more_info"+id).html() == "empty"){
      url = "ajax/moreinfo/" + id
      $.ajax({
        type: "GET",
        url: url,
        data: {},
        dataType: 'json',
        success: function(data){
          var output = "";
          if (data.activities.length == 0 && data.experiments.length == 0 && data.models.length == 0 && data.frequency.length == 0){
            output = "<p><em>Additional information not provided</em></p>";
          }
          else{
              var info_titles = "";
              var info_columns = "";
              if(data.activities.length > 0){
                var rows = "";
                for (var i = 0, len = data.activities.length; i < len; i++){
                    var link = data.activities[i].replace(' ', '%20')
                    rows += "<a href=\"?type=activity&option=" + link + "\">" + data.activities[i] + "<a/><br/>";
                }
                info_titles += "<th>Activities</th>";
                info_columns += "<td>" + rows + "</td>";
              }
              if(data.experiments.length > 0){
                var rows = "";
                for (var i = 0, len = data.experiments.length; i < len; i++){
                    var link = data.experiments[i].replace(' ', '%20')
                    rows += "<a href=\"?type=experiment&option=" + link + "\">" + data.experiments[i] + "<a/><br/>";
                }
                info_titles += "<th>Experiments</th>";
                info_columns += "<td>" + rows + "</td>";
              }
              if(data.models.length > 0){
                var rows = "";
                for (var i = 0, len = data.models.length; i < len; i++){
                    var link = data.models[i].replace(' ', '%20')
                    rows += "<a href=\"?type=model&option=" + link + "\">" + data.models[i] + "<a/><br/>";
                }
                info_titles += "<th>Sources</th>";
                info_columns += "<td>" + rows + "</td>";
              }
              if(data.frequency.length > 0){
                var rows = "";
                for (var i = 0, len = data.frequency.length; i < len; i++){
                    var link = data.frequency[i].replace(' ', '%20')
                    rows += "<a href=\"?type=frequency&option=" + link + "\">" + data.frequency[i] + "<a/><br/>";
                }
                info_titles += "<th>Frequency</th>";
                info_columns += "<td>" + rows + "</td>";
              }
              output =  "<table class=\"table\">" +
                        info_titles +
                        "<tr>" + info_columns + "</tr>" +
                        "</table>";
          }
          $("div #more_info"+id).html(output);
          $("div #more_info"+id).toggle();
        },
        error: function(request, status, error){
          alert(request + " | " +  status + " | " +  error);
        }
      });
    }
    else{
      $("div #more_info"+id).toggle();
    }
  }

  function show_abstract(id){
    if ($("div #abstract"+id).html() == "empty"){
      url = "ajax/abstract/" + id + "/";
      $.ajax({
        type: "GET",
        url: url,
        data: {},
        dataType: 'json',
        success: function(data){
        if(data.abstract) {
            var abstract = "<p><em>Abstract:</em> " + data.abstract + "</p>";
        }
        else {
            var abstract = "<p><em>Abstract not Supplied</em></p>"
        }
          $("div #abstract"+id).html(abstract);
          $("div #abstract"+id).toggle();
        },
        error: function(request, status, error){
          alert(request + " | " +  status + " | " +  error);
        }
      });
    }
    else{
      $("div #abstract"+id).toggle();
    }
  }

function show_bibtex(id){
    if ($("div #bibtex"+id).html() == "empty"){
        url = "ajax/citation/" + id;
        $.ajax({
            type: "GET",
            url: url,
            data: {},
            dataType: 'json',
            success: function(data){
                var authorstring = '';
                var bibtex = '';
                $.each(data.authors, function(index, author){
                    if(index == 0){
                        authorstring = authorstring.concat(author);
                    }
                    else{
                        authorstring = authorstring.concat(' and ', author);
                    }
                });
                if (data.type == 'Journal'){
                    bibtex = "@article{" + data.authors[0].split(',')[0] + ",\n" +
                                "  title        = {{" + data.title + "}},\n" +
                                "  author       = {" + authorstring + "}";
                    if(data.url){
                        bibtex += ',\n  url          = {' + '<a target="_blank" href="' + data.url + '">' + data.url + '</a>}';
                    }
                    if(data.journal_name){
                        bibtex += ",\n  journal      = {" + data.journal_name + "}";
                    }
                    if(data.volume_number){
                        bibtex += ",\n  volume       = {" + data.volume_number + "}";
                    }
                    if(data.article_number){
                        bibtex += ",\n  number       = {" + data.article_number + "}";
                    }
                    if(data.start_page && data.end_page){
                        bibtex += ",\n  pages        = {" + data.start_page + "-" + data.end_page + "}";
                    }
                }
                else if (data.type == 'Book'){
                    bibtex = "@book{" + data.authors[0].split(',')[0] + ",\n" +
                            "  title        = {" + data.title + "},\n" +
                            "  author       = {" + authorstring + "}";
                    if(data.url){
                        bibtex += ',\n  url          = {' + '<a target="_blank" href="' + data.url + '">' + data.url + '</a>}';
                    }
                    if(data.book_name){
                        bibtex += ",\n  title        = {" + data.book_name + "}";
                    }
                    if(data.chapter_title){
                        bibtex += ",\n  chaptertitle = {" + data.chapter_title + "}";
                    }
                    if(data.editor){
                        bibtex += ",\n  editor       = {" + data.editor + "}";
                    }
                    if(data.start_page && data.end_page){
                        bibtex += ",\n  pages        = {" + data.start_page + "-" + data.end_page + "}";
                    }
                    if(data.year){
                        bibtex += ",\n  year         = {" + data.year + "}";
                    }
                    if(data.month){
                        bibtex += ",\n  month        = {" + data.month + "}";
                    }
                    if(data.publisher){
                        bibtex += ",\n  publisher    = {" + data.publisher + "}";
                    }
                    if(data.city_of_publication){
                        bibtex += ",\n  address      = {" + data.city_of_publication + "}";
                    }
                }
                else if (data.type == 'Technical Report'){
                    bibtex = "@techreport{" + data.authors[0].split(',')[0] + ",\n" +
                            "  author       = {" + authorstring + "},\n" +
                            "  title        = {" + data.title + "}"; 
                    if(data.number){
                        bibtex += ",\n  number       = {" + data.number + "}";
                    }
                    if(data.editor){
                        bibtex += ",\n  editor       = {" + data.editor + "}";
                    }
                    if(data.year){
                        bibtex += ",\n  year         = {" + data.year + "}";
                    }
                    if(data.month){
                        bibtex += ",\n  month        = {" + data.month + "}";
                    }
                }
                else if (data.type == 'Conference'){
                    bibtex = "@conference{" + data.authors[0].split(',')[0] + ",\n" +
                            "  author       = {" + authorstring + "},\n" +
                            "  title        = {" + data.title + "}"; 
                    if(data.number){
                        bibtex += ",\n  number       = {" + data.number + "}";
                    }
                    if(data.editor){
                        bibtex += ",\n  editor       = {" + data.editor + "}";
                    }
                    if(data.year){
                        bibtex += ",\n  year         = {" + data.year + "}";
                    }
                    if(data.month){
                        bibtex += ",\n  month        = {" + data.month + "}";
                    }
                }
                else {
                    bibtex = "@misc{" + data.authors[0].split(',')[0] + ",\n" +
                            "  author       = {" + authorstring + "},\n" +
                            "  title        = {" + data.title + "}";
                    if(data.year){
                        bibtex += ",\n  year         = {" + data.year + "}";
                    }
                }
                if (data.doi.indexOf('doi:') === 0){
                        data.doi = data.doi.slice(4,data.doi.length).trim();
                    }
                if (data.doi.indexOf('doi.org/') > -1){
                    data.doi = data.doi.split('doi.org/')[1]
                }
                if(data.doi){
                    bibtex += ',\n  doi          = {' + '<a target="_blank" href="https://dx.doi.org/'+ data.doi +'">' + data.doi + '</a>}';
                }
                bibtex += '\n}'
                $("div #bibtex"+id).html($('<pre/>').append(bibtex));
                $("div #bibtex"+id).toggle();
            },
            error: function(request, status, error){
                alert(request + " | " +  status + " | " +  error);
            }
        });
    }
    else{
       $("div #bibtex"+id).toggle();
    }
}

$.fn.push = function(selector) {
    Array.prototype.push.apply(this, $.makeArray($(selector)));
    return this;
    //jquery .add does not preserve order so we make jquery use an array push
};
$('#year-heading').click(function(){
    year_sort();
});
$('#author-heading').click(function(){
    author_sort();
});
$('#title-heading').click(function(){
    title_sort();
});
function year_sort(){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {year: parseInt($(this).find('.dates').text()), elem: $(this).detach()};
        array.push(obj);
    });
    var bottom = $('div.jscroll-next-parent')
    if(bottom.length != 0){
        bottom.detach(); //if we are on a jscroll page, detatch the jscroll container at the bottom of the page
    }
    if (!year_sort_toggle){
        array.sort(function(a, b){
            return a.year - b.year;
        });
        year_sort_toggle = !year_sort_toggle;
        $('.ascending').removeClass('ascending');
        $('.descending').removeClass('descending');
        $('#year-heading').addClass('ascending');
    }
    else {
        array.sort(function(a, b){
            return b.year - a.year;
        });
        $('.ascending').removeClass('ascending');
        $('.descending').removeClass('descending');
        $('#year-heading').addClass('descending');
        year_sort_toggle = !year_sort_toggle;
    }
    jq = $();
    array.forEach(function(obj){
         jq = $(jq).push(obj.elem);
    });
    if($(".publication-container .jscroll-inner").length == 0){
        $(jq).appendTo('.publication-container');
    }
    else{
        $(jq).appendTo('.publication-container .jscroll-inner');
        $(bottom).appendTo('.publication-container .jscroll-inner');
    }
    last_sort = 'year';
};

function author_sort(){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {author: $(this).find('.authors').text(), elem: $(this).detach()};
        array.push(obj);
    });
    var bottom = $('div.jscroll-next-parent')
    if(bottom.length != 0){
        bottom.detach(); //if we are on a jscroll page, detatch the jscroll container at the bottom of the page
    }
    if (!author_sort_toggle){
        array.sort(function(a, b){
            return a.author.localeCompare(b.author);
        });
        author_sort_toggle = !author_sort_toggle;
        $('.ascending').removeClass('ascending');
        $('.descending').removeClass('descending');
        $('#author-heading').addClass('ascending');
    }
    else {
        array.sort(function(a, b){
            return b.author.localeCompare(a.author);
        });
        $('.ascending').removeClass('ascending');
        $('.descending').removeClass('descending');
        $('#author-heading').addClass('descending');
        author_sort_toggle = !author_sort_toggle;
    }
    jq = $();
    array.forEach(function(obj){
         jq = $(jq).push(obj.elem);
    });
    if($(".publication-container .jscroll-inner").length == 0){
        $(jq).appendTo('.publication-container');
    }
    else{
        $(jq).appendTo('.publication-container .jscroll-inner');
        $(bottom).appendTo('.publication-container .jscroll-inner');
    }
    last_sort = 'author';
};

function title_sort(){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {title: $(this).find('.titles').text().trim(), elem: $(this).detach()};
        array.push(obj);
    });
    var bottom = $('div.jscroll-next-parent')
    if(bottom.length != 0){
        bottom.detach(); //if we are on a jscroll page, detatch the jscroll container at the bottom of the page
    }
    if (!title_sort_toggle){
        array.sort(function(a, b){
            return a.title.localeCompare(b.title);
        });
        title_sort_toggle = !title_sort_toggle;
        $('.ascending').removeClass('ascending');
        $('.descending').removeClass('descending');
        $('#title-heading').addClass('ascending');
    }
    else {
        array.sort(function(a, b){
            return b.title.localeCompare(a.title);
        });
        $('.ascending').removeClass('ascending');
        $('.descending').removeClass('descending');
        $('#title-heading').addClass('descending');
        title_sort_toggle = !title_sort_toggle;
    }
    jq = $();
    array.forEach(function(obj){
         jq = $(jq).push(obj.elem);
    });
    if($(".publication-container .jscroll-inner").length == 0){
        $(jq).appendTo('.publication-container');
    }
    else{
        $(jq).appendTo('.publication-container .jscroll-inner');
        $(bottom).appendTo('.publication-container .jscroll-inner');
    }
    last_sort = 'title';
};