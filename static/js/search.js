$( document ).ready(function() {
    year_sort_toggle = false;
    author_sort_toggle = false;
    title_sort_toggle = false;
    $(".publication-container").jscroll({
        nextSelector: 'a.jscroll-next:last'
    });
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
                var citation = $('<span/>')
                    .append($('<span/>').text(authorstring + ', ' + data.year + ': ' + data.title + '. '))
                    .append('<span class="citation-italic">' + data.journal_name + '</span>, ');
                if (data.volume_number){
                    citation.append('<span class="citation-bold">'+ data.volume_number + '</span>, ');
                }
                if(data.start_page && data.end_page){
                    citation.append('<span>' + data.start_page + '-' + data.end_page + ', ' + '</span>');
                }
                else if (data.start_page) {
                    citation.append('<span>' + data.start_page + ', ' +'</span>');
                }
                if(data.doi !== 'doi:' && data.doi !== ''){
                    citation.append('<span>' + data.doi + '.' +'</span>');
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
                    citation.append($('<a/>').text(data.url).attr('href', data.url));
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

$.fn.push = function(selector) {
    Array.prototype.push.apply(this, $.makeArray($(selector)));
    return this;
    //jquery .add does not preserve order so we make jquery use an array push
};

$('#year-heading').click(function(event){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {year: parseInt($(this).find('.dates').text()), elem: $(this).detach()};
        array.push(obj);
    });
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
    $(jq).appendTo('.publication-container');
});

$('#author-heading').click(function(event){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {author: $(this).find('.authors').text(), elem: $(this).detach()};
        array.push(obj);
    });
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
    $(jq).appendTo('.publication-container');
});

$('#title-heading').click(function(event){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {title: $(this).find('.titles').text(), elem: $(this).detach()};
        array.push(obj);
    });
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
    $(jq).appendTo('.publication-container');
});