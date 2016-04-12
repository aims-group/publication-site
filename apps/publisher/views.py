from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from forms import PublicationForm
import pdb
import requests


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
    print r.json()
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
            url = initial['URL']
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
        pub_form = PublicationForm(initial={'doi': doi, 'isbn': isbn, 'title': title, 'url': url, 'page': page, 'publisher': publisher})
        return render(request, 'site/publication_details.html', {'pub_form': pub_form})
    elif r.status_code == 204 or 404 or 406:
        pub_form = PublicationForm()
        return render(request, 'site/publication_details.html', {'pub_form': pub_form, 'message': 'Unable to pre-fill form with the given DOI'})
    else:
        return HttpResponse(status=500)  # temporary
        # return (doi.strip('\n') + " -- Unknown status code returned (" + str(r.status_code) + ").\n")
