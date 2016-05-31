$( document ).ready(function() {
    year_sort_toggle = false;
    author_sort_toggle = false;
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
                authorstring += (', ' + author);
            });
            var citation = $('<span/>')
            .append($('<span/>').text(authorstring + ': ' + data.title + '. ' + data.date + '. '))
            .append($('<a/>').text(data.url).attr('href', data.url));
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
          data =  "<table class=\"table\">" +
                  "<th>Experiments</th><th>models</th><th>Variables</th><th>Keywords</th><tr>" +
                  "<td>" + metadata[0] + "</td>" +
                  "<td>" + metadata[1] + "</td>" +
                  "<td>" + metadata[2] + "</td>" +
                  "<td>" + metadata[3] + "</td>" +
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

$.fn.push = function(selector) {
    Array.prototype.push.apply(this, $.makeArray($(selector)));
    return this;
    //jquery .add does not preserve order so we make jquery use an array push
};

$('#year-published').click(function(event){
    //Note: chrome does not do a stable sort, whereas firefox and safari do.
    var array = []
    $('.publication').each(function(ind){
        var obj = {year: parseInt($(this).find('.date').text()), elem: $(this).detach()};
        array.push(obj);
    });
    if (!year_sort_toggle){
        array.sort(function(a, b){
            return a.year - b.year;
        });
        year_sort_toggle = !year_sort_toggle;
    }
    else {
        array.sort(function(a, b){
            return b.year - a.year;
        });
        year_sort_toggle = !year_sort_toggle;
    }
    jq = $();
    array.forEach(function(obj){
         jq = $(jq).push(obj.elem);
    });
    $(jq).appendTo('.publication-container');
});