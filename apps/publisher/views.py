from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from forms import PublicationForm, AuthorForm
import requests
from models import Experiment, Frequency, Keyword, Model, Variable, Project, Funding, Author, Publication, Book, Conference, Journal, Magazine, Poster, Presentation, Technical_Report, Other, Journal_Options


@login_required()
def index(request):
    return render(request, 'site/search.html')


@login_required()
def new(request):
    if request.method == 'GET':
        return render(request, 'site/new_publication.html')
    elif request.method == 'POST':
        print 'got a post'
        return HttpResponse('new page post')


def finddoi(request):
    doi = request.GET.get('doi')
    accept = 'application/vnd.citationstyles.csl+json; locale=en-US'
    headers = {'accept': accept}
    if doi[:5].lower() == 'doi: ':  # grabs first 5 characters lowercases, and compares
        try:
            url = "http://dx.doi.org/" + doi.split()[1]  # removes "doi:" and whitespace leaving only the doi
        except IndexError:
            return (doi.strip('\n') + " -- Invalid DOI.\n")
    elif doi.startswith('doi:10'):
        url = "http://dx.doi.org/" + doi[4:]  # remove 'doi:'
    elif doi.startswith("http://dx.doi.org/"):
        url = doi
    else:
        url = "http://dx.doi.org/" + doi

    r = requests.get(url, headers=headers)
    #print r.json()
    if r.status_code == 200:
        #TODO: Catch differences between agencies e.g. Crossref vs DataCite
        initial = r.json()
        if 'DOI' in initial.keys():
            doi = initial['DOI']
        else:
            doi = ''
        if 'ISBN' in initial.keys():
            isbn = initial['ISBN']
        else:
            isbn = ''
        if 'title' in initial.keys():
            title = initial['title']
        else:
            title = ''
        if 'URL' in initial.keys():
            url = requests.get(initial['URL']).url
        else:
            url = ''
        if 'page' in initial.keys():
            page = initial['page']
        else:
            page = ''
        if 'publisher' in initial.keys():
            publisher = initial['publisher']
        else:
            publisher = ''
        if 'author' in initial.keys():
            authors_list = []
            AuthorFormSet = formset_factory(AuthorForm, extra=0)
            for author in initial['author']:
                authors_list.append({'first_name': author['given'], 'last_name': author['family']})
            author_form = AuthorFormSet(initial=authors_list)
        else:
            authors_form = ''
        init = {'doi': doi, 'isbn': isbn, 'title': title, 'url': url, 'page': page, 'publisher': publisher}
        form = PublicationForm(initial=init)
        return render(request, 'site/publication_details.html', {'form': form, 'author_form': author_form})
    elif r.status_code == 204 or 404 or 406:
        form = PublicationForm()
        authors_list = []
        AuthorFormSet = formset_factory(AuthorForm, extra=0)
        author_form = AuthorFormSet(initial=authors_list)
        return render(request, 'site/publication_details.html', {'form': form, 'author_form': author_form, 'message': 'Unable to pre-fill form with the given DOI'})
    else:
        return HttpResponse(status=500)  # temporary
        # return (doi.strip('\n') + " -- Unknown status code returned (" + str(r.status_code) + ").\n")
