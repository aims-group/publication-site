$( document ).ready(function() {
    year_sort_toggle = true;
    author_sort_toggle = false;
    title_sort_toggle = false;
    last_sort = 'year';
    $('#year-heading').addClass('descending');
    $('#search-toggle').click(function(){
        $('#search-container').slideToggle('fast');
    });

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
      url = "/ajax/citation/" + id
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
                    citation.append('<a target="_blank" href="http://dx.doi.org/'+ data.doi +'">doi:' + data.doi + '.' +'</a>');
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
                        citation.append('<a target="_blank" href="http://dx.doi.org/'+ data.doi +'">' + ('http://dx.doi.org/'+data.doi) + '.' +'</a>');
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
      url = "/ajax/moreinfo/" + id
      $.ajax({
        type: "GET",
        url: url,
        data: {},
        dataType: 'json',
        success: function(data){
          output = data.key;
          var data = ""
          if (output === '|||'){
            data = "<p><em>Additional information not provided</em></p>"
          }
          else{
              output = output.replace(/,/g, '<br/>');
              metadata = output.split("|");
              var exp = "";
              var model = "";
              var variable = "";
              var keyword = "";
              var arr = metadata[0].split("<br/>");
              for (var i = 0, len = arr.length; i < len; i++){
                var link = arr[i].replace(' ', '%20')
                exp += "<a href=\"/search?type=experiment&option=" + link + "\">" + arr[i] + "<a/><br/>";
              }
              arr = metadata[1].split("<br/>");
              for (var i = 0, len = arr.length; i < len; i++){
                var link = arr[i].replace(' ', '%20')
                model += "<a href=\"/search?type=model&option=" + link + "\">" + arr[i] + "<a/><br/>";
              }
              arr = metadata[2].split("<br/>");
              for (var i = 0, len = arr.length; i < len; i++){
                var link = arr[i].replace(' ', '%20')
                variable += "<a href=\"/search?type=variable&option=" + link + "\">" + arr[i] + "<a/><br/>";
              }
              arr = metadata[3].split("<br/>");
              for (var i = 0, len = arr.length; i < len; i++){
                var link = arr[i].replace(' ', '%20')
                keyword += "<a href=\"/search?type=keyword&option=" + link + "\">" + arr[i] + "<a/><br/>";
              }
              data =  "<table class=\"table\">" +
                      "<th>Experiments</th><th>Models</th><th>Variables</th><th>Keywords</th><tr>" +
                      "<td>" + exp + "</td>" +
                      "<td>" + model + "</td>" +
                      "<td>" + variable + "</td>" +
                      "<td>" + keyword + "</td>" +
                      "</tr></table>";
          }
          $("div #more_info"+id).html(data);
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
      url = "/ajax/abstract/" + id + "/";
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
      url = "/ajax/citation/" + id
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
                authorstring += author;
            }
            else{
                authorstring += (', ' + author);
            }
        });

        if (data.type == 'Journal'){
            bibtex = "@Article{       " + data.authors[0] + ",\n" +
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
            if(data.year){
                bibtex += ",\n  year         = {" + data.year + "}";
            }
            if(data.month){
                bibtex += ",\n  month        = {" + data.month + "}";
            }
            if (data.doi.indexOf('doi:') === 0){
                data.doi = data.doi.slice(4,data.doi.length).trim();
            }
            if (data.doi.indexOf('doi.org/') > -1){
                data.doi = data.doi.split('doi.org/')[1]
            }
            if(data.doi){
                bibtex += ',\n  doi          = {' + '<a target="_blank" href="http://dx.doi.org/'+ data.doi +'">' + data.doi + '</a>}';
            }
        }
            else if (data.type == 'Book'){
                bibtex = "BibTex not yet available for this publication type";
            }
            else {
                bibtex = "BibTex not yet available for this publication type";
            }
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
    var bottom = $('div.jscroll-next-parent').detach();
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
    $(jq).appendTo('.publication-container .jscroll-inner');
    $(bottom).appendTo('.publication-container .jscroll-inner');
    last_sort = 'year';
};

function author_sort(){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {author: $(this).find('.authors').text(), elem: $(this).detach()};
        array.push(obj);
    });
    var bottom = $('div.jscroll-next-parent').detach();
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
    $(jq).appendTo('.publication-container .jscroll-inner');
    $(bottom).appendTo('.publication-container .jscroll-inner');
    last_sort = 'author';
};

function title_sort(){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {title: $(this).find('.titles').text().trim(), elem: $(this).detach()};
        array.push(obj);
    });
    var bottom = $('div.jscroll-next-parent').detach();
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
    $(jq).appendTo('.publication-container .jscroll-inner');
    $(bottom).appendTo('.publication-container .jscroll-inner');
    last_sort = 'title';
};