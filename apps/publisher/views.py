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
    if r.status_code == 200:
        initial = r.json()
        if 'isbn' in initial.keys():
            isbn = initial['isbn']
        else:
            isbn = ''
        if 'title' in initial.keys():
            title = initial['title']
        else:
            title = ''
        if 'url' in initial.keys():
            url = initial['url']
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
        pub_form = PublicationForm(initial={'isbn': isbn, 'title': title, 'url': url, 'page': page, 'publisher': publisher})
        return render(request, 'site/publication_details.html', {'pub_form': pub_form})
    # elif r.status_code == 204:
    #     return (doi.strip('\n') + " -- The request was OK but there was no metadata available.available.\n")
    # elif r.status_code == 404:
    #     return (doi.strip('\n') + " -- The DOI requested doesn't exist.\n")
    # elif r.status_code == 406:
    #     return (doi.strip('\n') + " -- Can't serve any requested content type.\n")
    else:
        return HttpResponse(status=500)  # temporary
        # return (doi.strip('\n') + " -- Unknown status code returned (" + str(r.status_code) + ").\n")
