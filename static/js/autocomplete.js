
var authors = new Bloodhound({
datumTokenizer: Bloodhound.tokenizers.whitespace,
queryTokenizer: Bloodhound.tokenizers.whitespace,
prefetch: '../ajax/data/authors/'
});

$('.typeahead-a').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
},
{
    name: 'authors',
    source: authors
});

var institutions = new Bloodhound({
datumTokenizer: Bloodhound.tokenizers.whitespace,
queryTokenizer: Bloodhound.tokenizers.whitespace,
prefetch: '../ajax/data/institutions/'
});

$('.typeahead-i').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
},
{
    name: 'institutions',
    source: institutions
});
