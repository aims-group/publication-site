from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.forms import forms, formset_factory, modelformset_factory
from .forms import PublicationForm, AuthorFormSet, BookForm, ConferenceForm, JournalForm, MagazineForm, PosterForm, AuthorForm
from .forms import PresentationForm, TechnicalReportForm, OtherForm, AdvancedSearchForm, DoiBatchForm
from .forms import ExperimentForm, FrequencyForm, KeywordForm, ModelForm, VariableForm
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.db import transaction
from itertools import chain
from scripts.journals import journal_names
from fuzzywuzzy import process
from .models import *
import requests
import datetime
import collections
import operator


# Helper functions
def save_publication(pub_form, request, author_form_set, pub_type, edit):

    publication = pub_form.save(commit=False)
    publication.submitter = request.user
    publication.publication_type = pub_type
    publication.save()
    # publication.projects.add(Project.objects.filter(project=request.POST.get('meta_type', ''))[0])
    
    #Remove any checkboxes that were unchecked in an edit
    publication.frequency.remove(*[f for f in publication.frequency.all() if str(f.id) not in request.POST.getlist("frequency")]) 
    publication.keywords.remove(*[k for k in publication.keywords.all() if str(k.id) not in request.POST.getlist("keyword")]) 
    publication.experiments.remove(*[e for e in publication.experiments.all() if str(e.id) not in request.POST.getlist("experiment")]) 
    publication.variables.remove(*[v for v in publication.variables.all() if str(v.id) not in request.POST.getlist("variable")]) 

    #Add any checkboxes that were checked
    publication.frequency.add(*[Frequency.objects.get(id=frequency_id) for frequency_id in request.POST.getlist("frequency")])
    publication.keywords.add(*[Keyword.objects.get(id=keywords_id) for keywords_id in request.POST.getlist("keyword")])
    publication.experiments.add(*[Experiment.objects.get(id=experiment_id) for experiment_id in request.POST.getlist("experiment")])
    publication.variables.add(*[Variable.objects.get(id=variable_id) for variable_id in request.POST.getlist("variable")])
    projects = request.POST.getlist('project')
    for proj in publication.projects.all(): #iterate over projects previously selected
        if proj.project in projects: #project is still selected
            projects.remove(proj.project) # so remove project from list since it is already in the db
        else: #Project has been deselected. remove from database
            publication.projects.remove(proj)
    for proj in projects: #iterate over remaining projects that were selected
        publication.projects.add(Project.objects.get(project=proj)) #these are all newly selected, so add them to db
    publication.save()  # might not be needed
    year = publication.get_year
    if not AvailableYears.objects.filter(year=year):
        avail = AvailableYears(year=year)
        avail.save()

    ensemble = request.POST.getlist('ensemble')
    models = request.POST.getlist('model')
    PubModels.objects.filter(publication=publication.id).exclude(model__in=models).delete()
    # Delete any experiments that were unchecked
    for model_id in models:
        model = Model.objects.get(id=model_id)
        pubmodel = PubModels.objects.filter(publication=publication.id, model=model_id)
        if pubmodel:
            pubmodel[0].ensemble = 1
            pubmodel[0].save()
        else:
            PubModels.objects.create(publication=publication, model=model, ensemble=1)
    if edit:
        author_form_set.save(commit=False)
    for authorform in author_form_set:
        form_is_filled = True
        if not authorform['name'].data:
            form_is_filled = False
        if form_is_filled:
            author = authorform.save()
            publication.authors.add(author.id)
    if edit:
        for obj in author_form_set.deleted_objects:
            obj.delete()
    return publication

# Helper function that will attempt to validate and save a publication.
# Returns a tuple of (boolean, dictionary)
# The boolean is true if the publication was submitted successfully and false if it was invalid
# The dictionary holds the forms that were checked. (Meta forms are not present)
def process_publication(request):
    pub_type = request.POST.get('pub_type', '')
    formset = formset_factory(AuthorForm, min_num=1, validate_min=True)
    author_form_set = formset(request.POST)
    all_forms = init_forms(author_form_set, request.POST)
    if pub_type == 'Book':
        pub_type = 0
        media_form = BookForm(request.POST, prefix='book')
    elif pub_type == 'Conference':
        pub_type = 1
        media_form = ConferenceForm(request.POST, prefix='conf')
    elif pub_type == 'Journal':
        pub_type = 2
        media_form = JournalForm(request.POST, prefix='journal')
    elif pub_type == 'Magazine':
        pub_type = 3
        media_form = MagazineForm(request.POST, prefix='mag')
    elif pub_type == 'Poster':
        pub_type = 4
        media_form = PosterForm(request.POST, prefix='poster')
    elif pub_type == 'Presentation':
        pub_type = 5
        media_form = PresentationForm(request.POST, prefix='pres')
    elif pub_type == 'Technical Report':
        pub_type = 6
        media_form = TechnicalReportForm(request.POST, prefix='tech')
    else:
        pub_type = 7
        media_form = OtherForm(request.POST, prefix='other')
    if media_form.is_valid() and all_forms['pub_form'].is_valid() and author_form_set.is_valid():
        publication = save_publication(all_forms['pub_form'], request, author_form_set, pub_type, False)
        media = media_form.save(commit=False)
        media.publication_id = publication
        media.save()
        return True, all_forms
    else:
        return False, all_forms

def init_forms(author_form, request=None, instance=None):
    # The author form is passed in seperately since it takes different arguments depending on the circumstances
    pub_form = PublicationForm(request, prefix='pub')
    book_form = BookForm(request, prefix='book')
    conference_form = ConferenceForm(request, prefix='conf')
    journal_form = JournalForm(request, prefix='journal')
    magazine_form = MagazineForm(request, prefix='mag')
    poster_form = PosterForm(request, prefix='poster')
    presentation_form = PresentationForm(request, prefix='pres')
    technical_form = TechnicalReportForm(request, prefix='tech')
    other_form = OtherForm(request, prefix='other')
    exp_form = ExperimentForm(request)
    freq_form = FrequencyForm(request)
    keyword_form = KeywordForm(request)
    model_form = ModelForm(request)
    var_form = VariableForm(request)
    all_projects = [str(proj) for proj in Project.objects.all().order_by('project')]

    return {'pub_form': pub_form, 'author_form': author_form, 'book_form': book_form, 'conference_form': conference_form,
            'journal_form': journal_form, 'magazine_form': magazine_form, 'poster_form': poster_form,
            'presentation_form': presentation_form, 'technical_form': technical_form,
            'other_form': other_form, 'exp_form': exp_form, 'freq_form': freq_form,
            'keyword_form': keyword_form, 'model_form': model_form, 'var_form': var_form, 'all_projects': all_projects}


def get_all_options():
    all_options = collections.OrderedDict()
    all_options['experiment'] = "Experiment"
    all_options['frequency'] = "Frequency"
    all_options['keyword'] = "Keyword"
    all_options['model'] = "Model"
    all_options['status'] = "Status"
    all_options['type'] = "Type"
    all_options['variable'] = "Variable"
    all_options['year'] = "Year"
    return all_options

def view(request, project_name="all"):
    if request.method != 'GET':
        return HttpResponse(status=405) # Method other than get not allowed
    projects = [str(x).lower() for x in Project.objects.all()]
    if project_name != "all" and not project_name.lower() in projects:
        return HttpResponse(status=404) #invalid project name
    publications_to_load = 100  # number of publications to load at a time
    pubs = {}
    data = collections.OrderedDict()
    pubs["category"] = project_name
    pubs["type"] = request.GET.get("type", "all")
    pubs["option"] = request.GET.get("option", "")
    pubs["hide_search"] = "display:none;"
    try:
        scroll_count = int(request.GET.get("scroll_count", "0"))
    except ValueError as e:
        print(e)
        scroll_count = 0

    pubs["search"] = True
    page_filter = request.GET.get("type", "all")
    display = request.GET.get('display', '')  # expect display == 'citations', 'bibtex' or nothing
    if project_name == "all":
        publications = Publication.objects.all().order_by("-publication_date")
        pubs["total"] = Publication.objects.all().count()
    else:
        try:
            publications = Project.objects.get(project__iexact=project_name).publication_set.order_by("-publication_date") 
            pubs["total"] = Project.objects.get(project__iexact=project_name).publication_set.count()  
        except Project.DoesNotExist as e:
            print(e)
            return HttpResponse(status=404)
    if page_filter == 'all':
        pubs["pages"] = get_all_options()

    elif page_filter == 'experiment':
        option = request.GET.get("option", "1pctCO2")
        pubs["option"] = option
        for exp in Experiment.objects.all().order_by('experiment'):
            if publications.filter(experiments=Experiment.objects.filter(experiment=exp)).count() == 0:
                continue
            exps = {}
            exps['type'] = 'experiment'
            exps['options'] = str(exp.experiment)
            exps['count'] = publications.filter(experiments=Experiment.objects.filter(experiment=exp)).count()
            data[str(exp.experiment)] = exps
        publications = publications.filter(experiments=Experiment.objects.filter(experiment=option)).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'frequency':
        option = request.GET.get("option", "3-hourly")
        pubs["option"] = option
        for frq in Frequency.objects.all().order_by('frequency'):
            if publications.filter(frequency=Frequency.objects.filter(frequency=frq)).count() == 0:
                continue
            frqs = {}
            frqs['type'] = 'frequency'
            frqs['options'] = str(frq.frequency)
            frqs['count'] = publications.filter(frequency=Frequency.objects.filter(frequency=frq)).count()
            data[str(frq.frequency)] = frqs
        publications = publications.filter(frequency=Frequency.objects.filter(frequency=option)).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'keyword':
        option = request.GET.get("option", "Abrupt change")
        pubs["option"] = option
        for kyw in Keyword.objects.all().order_by('keyword'):
            if publications.filter(keywords=Keyword.objects.filter(keyword=kyw)).count() == 0:
                continue
            kyws = {}
            kyws['type'] = 'keyword'
            kyws['options'] = str(kyw.keyword)
            kyws['count'] = publications.filter(keywords=Keyword.objects.filter(keyword=kyw)).count()
            data[str(kyw.keyword)] = kyws
        publications = publications.filter(keywords=Keyword.objects.filter(keyword=option)).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'model':
        option = request.GET.get("option", "ACCESS1.0")
        pubs["option"] = option
        for mod in Model.objects.all().order_by('model'):
            if publications.filter(model=Model.objects.filter(model=mod)).count() == 0:
                continue
            mods = {}
            mods['type'] = 'model'
            mods['options'] = str(mod.model)
            mods['count'] = publications.filter(model=Model.objects.filter(model=mod)).count()
            data[str(mod.model)] = mods
        publications = publications.filter(model=Model.objects.filter(model=option)).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'status':
        option = request.GET.get("option", "Published")
        pubs["option"] = option
        lookup = 0
        for k, v in PUBLICATION_STATUS_CHOICE:
            if str(v) == str(option):
                lookup = k
                break
        for stat in range(0, len(PUBLICATION_STATUS_CHOICE)):
            if publications.filter(status=stat).count() == 0:
                continue
            stats = {}
            stats['type'] = 'status'
            stats['options'] = PUBLICATION_STATUS_CHOICE[stat][1]
            stats['count'] = publications.filter(status=stat).count()
            data[str(PUBLICATION_STATUS_CHOICE[stat][1])] = stats
        publications = publications.filter(status=lookup).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'type':
        option = request.GET.get("option", "Journal")
        pubs["option"] = option
        lookup = 2
        for k, v in PUBLICATION_TYPE_CHOICE:
            if str(v) == option:
                lookup = k
                break
        for pt in range(0, len(PUBLICATION_TYPE_CHOICE) - 1):
            if publications.filter(publication_type=pt).count() == 0:
                continue
            pubtype = {}
            pubtype['type'] = 'type'
            typename = str(PUBLICATION_TYPE_CHOICE[pt][1])
            pubtype['options'] = typename
            pubtype['count'] = publications.filter(publication_type=pt).count()
            data[typename] = pubtype
        publications = publications.filter(publication_type=lookup).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'variable':
        option = request.GET.get("option", "air pressure")
        pubs["option"] = request.GET.get("option", "air pressure")
        for var in Variable.objects.all().order_by('variable'):
            if publications.filter(variables=Variable.objects.filter(variable=var)).count() == 0:
                continue
            vars = {}
            vars['type'] = 'variable'
            vars['options'] = str(var.variable)
            vars['count'] = publications.filter(variables=Variable.objects.filter(variable=var)).count()
            data[str(var.variable)] = vars
        publications = publications.filter(variables=Variable.objects.filter(variable=option)).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'year':
        now = datetime.datetime.now()
        option = request.GET.get("option", str(now.year))
        pubs["option"] = option
        for pub_years in AvailableYears.objects.all().order_by('-year'):
            years = {}
            years['type'] = 'year'
            years['options'] = str(pub_years.year)
            years['count'] = publications.filter(publication_date__year=pub_years.year).count()
            data[str(pub_years.year)] = years
        publications = publications.filter(publication_date__year=option).order_by("-publication_date")
        pubs["pages"] = data

    elif page_filter == 'project':
        option = request.GET.get("option", "CMIP5")
        pubs["option"] = option
        for project in Project.objects.all().order_by('project'):
            if publications.filter(projects=Project.objects.filter(project=project)).count() == 0:
                continue
            project_data = {}
            project_data['type'] = 'project'
            project_data['options'] = str(project)
            project_data['count'] = publications.filter(projects=Project.objects.filter(project=project)).count()
            data[(str(project))] = project_data
        publications = publications.filter(projects=Project.objects.filter(project=option)).order_by("-publication_date")
        pubs['pages'] = data

    elif page_filter == 'search':
        year = request.GET.get('year', '')
        author = request.GET.get('author', '')
        title = request.GET.get('title', '')
        try:
            year = int(year)
        except ValueError:
            year = ''

        if not year:
            publications = Publication.objects.all()
        else:
            publications = Publication.objects.filter(publication_date__year=year)

        if not author:
            pass
        else:
            publications = publications.filter(authors__name__icontains=author)

        if not title:
            pass
        else:
            publications = publications.filter(title__icontains=title)
        pubs['search_count'] = publications.count()
        pubs['publications'] = publications
        pubs['hide_search'] = False
        pubs["search_year"] = year
        pubs["search_author"] = author
        pubs["search_title"] = title
    if display in ['citations', "bibtex"]:
        publication_list = []
        for pub in publications:
            authors = [author.name for author in pub.authors.all().order_by('id')]
            pub_type = PUBLICATION_TYPE_CHOICE[pub.publication_type][1]
            if pub_type == 'Journal':
                if pub.doi in ['doi:', 'doi: ']:
                    pub.doi = ''
                if pub.doi and pub.doi.find('doi.org') != -1:
                    pub.doi = 'doi:' + pub.doi.split('doi.org/')[1]
                elif pub.doi and not pub.doi.startswith('doi:'):
                    pub.doi = 'doi:' + pub.doi
                journal = pub.journal_set.all()[0]
                obj = {'title': pub.title, 'url': pub.url, 'authors': authors,
                    'doi': pub.doi, 'journal_name': str(journal.journal_name), 'volume_number': journal.volume_number,
                    'start_page': journal.start_page, 'end_page': journal.end_page, 'type': pub_type,
                    'year': pub.publication_date.year, 'author_key': authors[0].split(',')[0]}
            elif pub_type == 'Book':
                book = pub.book_set.all()[0]
                obj = {'title': pub.title, 'url': pub.url, 'authors': authors,
                    'doi': pub.doi, 'book_name': str(book.book_name), 'chapter_title': book.chapter_title,
                    'start_page': book.start_page, 'end_page': book.end_page, 'type': pub_type,
                    'editor': book.editor, 'publisher': book.publisher, 'year': pub.publication_date.year, 'author_key': authors[0].split(',')[0]}
            elif pub_type == 'Technical Report':
                report = pub.technicalreport_set.all()[0]
                obj = {'title': pub.title, 'url': pub.url, 'authors': authors,
                        'doi': pub.doi, 'number': str(report.report_number), 'type': pub_type, 'editor': report.editor,
                        'issuer': report.issuer, 'year': pub.publication_date.year, 'author_key': authors[0].split(',')[0]}    
            else:
                obj = {'title': pub.title, 'year': pub.publication_date.year, 'url': pub.url, 'authors': authors,
                    'doi': pub.doi, 'type': pub_type, 'author_key': authors[0].split(',')[0]}
            publication_list.append(obj)
        data = {
            'publication_list': publication_list,
            'type': display
        }
        return render(request, 'site/print_citations.html', data)

    if page_filter != 'search':
        if scroll_count:
            prev_articles = publications_to_load*scroll_count
            new_articles = publications_to_load*(scroll_count+1)
            if page_filter == 'all':
                pubs["scroll_link"] = "?type={}&scroll_count={}".format(page_filter, scroll_count + 1)
            else:
                pubs["scroll_link"] = "?type={}&option={}&scroll_count={}".format(page_filter, option.replace(' ', '%20'), scroll_count + 1)
            pubs["publications"] = publications[prev_articles:new_articles]
            return render(request, 'snippets/load_publications.html', pubs)

        else:
            if page_filter == 'all':
                pubs["scroll_link"] = "?type={}&scroll_count=1".format(page_filter)
            else:
                pubs["scroll_link"] = "?type={}&option={}&scroll_count=1".format(page_filter, option.replace(' ', '%20'))
            pubs["publications"] = publications[:publications_to_load]
    return render(request, 'site/view.html', pubs)

def advanced_search(request):
    if request.method == 'GET':
        advanced_search_form = AdvancedSearchForm()
        return render(request, 'site/advanced_search.html', {'form': advanced_search_form})
    elif request.method == 'POST':
        form = AdvancedSearchForm(request.POST)
        if not form.is_valid():
            return render(request, 'site/advanced_search.html', {'form': form})
        else:
            pubs = Publication.objects.all()
            if 'doi' in list(form.cleaned_data.keys()) and form.cleaned_data['doi']:
                pubs = pubs.filter(doi__icontains=form.cleaned_data['doi'])

            if 'title' in list(form.cleaned_data.keys()) and form.cleaned_data['title']:
                pubs = pubs.filter(title__icontains=form.cleaned_data['title'])

            if 'author' in list(form.cleaned_data.keys()) and form.cleaned_data['author']:
                pubs = pubs.filter(authors__name__icontains=form.cleaned_data['author'])

            if 'date_end' in list(form.cleaned_data.keys()) and form.cleaned_data['date_start'] and form.cleaned_data['date_end']:
                pubs = pubs.filter(publication_date__range=[form.cleaned_data['date_start'], form.cleaned_data['date_end']])

            elif 'date_start' in list(form.cleaned_data.keys()) and form.cleaned_data['date_start']:
                pubs = pubs.filter(publication_date__gte=form.cleaned_data['date_start'])

            elif 'date_end' in list(form.cleaned_data.keys()) and form.cleaned_data['date_end']:
                pubs = pubs.filter(publication_date__lte=form.cleaned_data['date_end'])

            if 'project' in list(form.cleaned_data.keys()) and form.cleaned_data['project']:
                if request.POST.get("project_search_by_any", "off") == "on":
                    pubs = pubs.filter(projects__in=form.cleaned_data['project'])
                else:
                    for proj in form.cleaned_data['project']:
                        pubs = pubs.filter(projects=proj)

            meta_any_mode_pubs = Publication.objects.none() # Initialize variable so we can reference it without error
            meta_search_by_any = request.POST.get("meta_search_by_any", "off")
            if 'experiment' in list(form.cleaned_data.keys()) and form.cleaned_data['experiment']:
                if meta_search_by_any == "on":
                    meta_any_mode_pubs = meta_any_mode_pubs | pubs.filter(experiments__experiment__in=form.cleaned_data['experiment'])
                else:
                    for exp in form.cleaned_data['experiment']:
                        pubs = pubs.filter(experiments__experiment=exp)

            if 'frequency' in list(form.cleaned_data.keys()) and form.cleaned_data['frequency']:
                if meta_search_by_any == "on":
                    meta_any_mode_pubs = meta_any_mode_pubs | pubs.filter(frequency__frequency__in=form.cleaned_data['frequency'])
                else:
                    for freq in form.cleaned_data['frequency']:
                        pubs = pubs.filter(frequency__frequency=freq)

            if 'keyword' in list(form.cleaned_data.keys()) and form.cleaned_data['keyword']:
                if meta_search_by_any == "on":
                    meta_any_mode_pubs = meta_any_mode_pubs | pubs.filter(keywords__keyword__in=form.cleaned_data['keyword'])
                else:
                    for keyw in form.cleaned_data['keyword']:
                        pubs = pubs.filter(keywords__keyword=keyw)

            if 'model' in list(form.cleaned_data.keys()) and form.cleaned_data['model']:
                if meta_search_by_any == "on":
                    meta_any_mode_pubs = meta_any_mode_pubs | pubs.filter(model__model__in=form.cleaned_data['model'])
                else:
                    for model in form.cleaned_data['model']:
                        pubs = pubs.filter(model__model=model)

            if 'variable' in list(form.cleaned_data.keys()) and form.cleaned_data['variable']:
                if meta_search_by_any == "on":
                    meta_any_mode_pubs = meta_any_mode_pubs | pubs.filter(variables__variable__in=form.cleaned_data['variable'])
                else:
                    for var in form.cleaned_data['variable']:
                        pubs = pubs.filter(variables__variable=var)
            if meta_search_by_any == "on":
                pubs = meta_any_mode_pubs.distinct()
            pubs = pubs.distinct()
            if 'ajax' in list(request.POST.keys()) and request.POST['ajax'] == 'true':
                return JsonResponse({'count': pubs.count()})
            if 'display' in list(request.POST.keys()) and request.POST['display'] in ['citations', 'bibtex']:
                publication_list = []
                for pub in pubs.order_by("-publication_date"):
                    authors = [author.name for author in pub.authors.all().order_by('id')]
                    pub_type = PUBLICATION_TYPE_CHOICE[pub.publication_type][1]
                    if pub_type == 'Journal':
                        if pub.doi in ['doi:', 'doi: ']:
                            pub.doi = ''
                        if pub.doi and pub.doi.find('doi.org') != -1:
                            pub.doi = 'doi:' + pub.doi.split('doi.org/')[1]
                        elif pub.doi and not pub.doi.startswith('doi:'):
                            pub.doi = 'doi:' + pub.doi
                        journal = pub.journal_set.all()[0]
                        obj = {'title': pub.title, 'url': pub.url, 'authors': authors,
                            'doi': pub.doi, 'journal_name': str(journal.journal_name), 'volume_number': journal.volume_number,
                            'start_page': journal.start_page, 'end_page': journal.end_page, 'type': pub_type,
                            'year': pub.publication_date.year, 'author_key': authors[0].split(',')[0]}
                    elif pub_type == 'Book':
                        book = pub.book_set.all()[0]
                        obj = {'title': pub.title, 'url': pub.url, 'authors': authors,
                            'doi': pub.doi, 'book_name': str(book.book_name), 'chapter_title': book.chapter_title,
                            'start_page': book.start_page, 'end_page': book.end_page, 'type': pub_type,
                            'editor': book.editor, 'publisher': book.publisher, 'year': pub.publication_date.year, 'author_key': authors[0].split(',')[0]}
                    elif pub_type == 'Technical Report':
                        report = pub.technicalreport_set.all()[0]
                        obj = {'title': pub.title, 'url': pub.url, 'authors': authors,
                                'doi': pub.doi, 'number': str(report.report_number), 'type': pub_type, 'editor': report.editor,
                                'issuer': report.issuer, 'year': pub.publication_date.year, 'author_key': authors[0].split(',')[0]}    
                    else:
                        obj = {'title': pub.title, 'year': pub.publication_date.year, 'url': pub.url, 'authors': authors,
                            'doi': pub.doi, 'type': pub_type, 'author_key': authors[0].split(',')[0]}
                    publication_list.append(obj)
                return render(request, 'site/print_citations.html', {'publication_list': publication_list,
                                                                            'type': request.POST['display']})
            return render(request, 'site/advanced_search_results.html', {'publications': pubs.order_by("-publication_date"),
                                                                        'form': form})
    else:
        return HttpResponse(status=405)

@login_required()
def review(request):
    message = None
    pending_message = None
    error = None
    pending_error = None
    show_pending = True if request.GET.get('show_pending') == 'true' else False
    if request.method == "POST":
        userid = request.user.id
        delete_type = request.POST.get("delete-type", "")
        if delete_type == "all-doi":
            try:
                show_pending = True
                PendingDoi.objects.filter(user=request.user).delete()
            except Exception as e:
                print(e)
        else:
            try:
                delete_id = int(request.POST.get("delete-id", ""))
            except ValueError:
                if delete_type == "publication":
                    error = "Invalid id to delete."
                else:
                    pending_error = "Invalid id to delete."
                delete_type = "" # id was invalid. This will cause the view to render the page without deleting

        if delete_type == "publication":
            try:
                show_pending = False
                publication = Publication.objects.get(id=delete_id)
                if userid == publication.submitter.id:
                    try:
                        publication.delete()
                    except Exception as e:
                        error = "{}{}".format(
                            "Encountered an error while deleting. "
                            "If this error persists, please <a href='https://github.com/aims-group/publication-site/issues'>file an issue</a>."
                        )
                else:
                    error = 'Error: You must be the owner of a submission to edit it.'
                
            except Publication.DoesNotExist:
                pending_error = "Pending DOI does not exist and could not be deleted."


        elif delete_type == "doi":
            show_pending = True
            try:
                pending_doi = PendingDoi.objects.get(id=delete_id)
                if userid == pending_doi.user.id:
                    try:
                        pending_doi.delete()
                    except Exception as e:
                        pending_error = "{}{}".format(
                            "Encountered an error while deleting. "
                            "If this error persists, please <a href='https://github.com/aims-group/publication-site/issues'>file an issue</a>."
                        )
                else:
                    pending_error = 'Error: You must be the owner of a submission to edit it.'
            except PendingDoi.DoesNotExist:
                pending_error = "Pending DOI does not exist and could not be deleted."

    publications = Publication.objects.filter(submitter=request.user.id)
    pending_dois = PendingDoi.objects.filter(user=request.user).order_by("date_time")
    if not publications:
        message = 'You do not have any publications to display. <a href="/new">Submit one.</a>'
    if not pending_dois:
        pending_message = "You do not have any pending publications. If you have many publications to add, <a href='/add_dois'>click here</a>."
    return render(request, 'site/review.html', {'message': message, "pending_message": pending_message, 'publications': publications,
                                                'pending_dois': pending_dois, 'error': None, 'pending_error': pending_error, "show_pending": show_pending})
@login_required()
def skip_doi(request):
    try:
        pending_doi = PendingDoi.objects.filter(user=request.user).order_by('date_time').first()
        pending_doi.date_time = timezone.now()
        pending_doi.save()
    except Exception as e:
        print(e)
    return redirect('process_dois')

@login_required()
def edit(request, pubid):
    if request.method == 'POST':
        pub_instance = Publication.objects.get(id=pubid)
        if not request.user.id == pub_instance.submitter.id:
            entries = Publication.objects.filter(submitter=request.user.id)
            error = 'Error: You must be the owner of a submission to edit it.'
            return render(request, 'site/review.html', {'message': None, 'entries': entries, 'error': error})
        pub_form = PublicationForm(request.POST or None, pub_id=pubid, instance=pub_instance)
        author_form_set = AuthorFormSet(request.POST, queryset=pub_instance.authors.all())
        pub_type = int(request.POST.get('pub_type', ''))
        if pub_type == 0:  # book
            bookinstance = Book.objects.get(publication_id=pub_instance)
            media_form = BookForm(request.POST or None, instance=bookinstance)
        elif pub_type == 1:  # conference
            conferenceinstance = Conference.objects.get(publication_id=pub_instance)
            media_form = ConferenceForm(request.POST or None, instance=conferenceinstance)
        elif pub_type == 2:  # journal
            journalinstance = Journal.objects.get(publication_id=pub_instance)
            media_form = JournalForm(request.POST or None, instance=journalinstance)
        elif pub_type == 3:  # magazine
            magazineinstance = Magazine.objects.get(publication_id=pub_instance)
            media_form = MagazineForm(request.POST or None, instance=magazineinstance)
        elif pub_type == 4:  # poster
            posterinstance = Poster.objects.get(publication_id=pub_instance)
            media_form = PosterForm(request.POST or None, instance=posterinstance)
        elif pub_type == 5:  # presentation
            presentationinstance = Presentation.objects.get(publication_id=pub_instance)
            media_form = PresentationForm(request.POST or None, instance=presentationinstance)
        elif pub_type == 6:  # technical report
            techinstance = TechnicalReport.objects.get(publication_id=pub_instance)
            media_form = TechnicalReportForm(request.POST or None, instance=techinstance)
        elif pub_type == 7:  # other
            otherinstance = Other.objects.get(publication_id=pub_instance)
            media_form = OtherForm(request.POST or None, instance=otherinstance)
        if pub_type in range(8) and media_form.is_valid() and pub_form.is_valid() and author_form_set.is_valid():
            publication = save_publication(pub_form, request, author_form_set, pub_type, True)
            other = media_form.save(commit=False)
            other.publication_id = publication
            other.save()
            return redirect('review')

        meta_form = []
        all_projects = [str(proj) for proj in Project.objects.all().order_by('project')]
        selected_projects = [str(proj) for proj in request.POST.getlist("project", [])]
        for project in Project.objects.all().order_by('project'):
            if str(project) in selected_projects:
                meta_form.append({
                    'name': str(project),
                    'exp_form': ExperimentForm(initial={'experiment': [int(box) for box in request.POST.getlist("experiment") if box.isdigit()]}, queryset=project.experiments),
                    'freq_form': FrequencyForm(initial={'frequency': [int(box) for box in request.POST.getlist("frequency") if box.isdigit()]}, queryset=project.frequencies),
                    'keyword_form': KeywordForm(initial={'keyword': [int(box) for box in request.POST.getlist("keyword") if box.isdigit()]}, queryset=project.keywords),
                    'model_form': ModelForm(initial={'model': [int(box) for box in request.POST.getlist("model") if box.isdigit()]}, queryset=project.models),
                    'var_form': VariableForm(initial={'variable': [int(box) for box in request.POST.getlist("variable") if box.isdigit()]}, queryset=project.variables),
                })
            else:
                meta_form.append({
                    'name': str(project),
                    'exp_form': ExperimentForm(queryset=project.experiments),
                    'freq_form': FrequencyForm(queryset=project.frequencies),
                    'keyword_form': KeywordForm(queryset=project.keywords),
                    'model_form': ModelForm(queryset=project.models),
                    'var_form': VariableForm(queryset=project.variables),
                })
        meta_type = pub_instance.projects.first()
        ens = request.POST.getlist('ensemble')
        ensemble_data = str([[index + 1, int('0' + str(ens[index]))] for index in range(len(ens)) if ens[index] is not ''])
        return render(request, 'site/edit.html',
                      {'pub_form': pub_form, 'author_form': author_form_set, 'media_form': media_form, 'pub_type': pub_type,
                       'ensemble_data': ensemble_data, 'meta_form': meta_form, 'meta_type': meta_type, "all_projects": all_projects,
                        "selected_projects": selected_projects
                       })

    else: # Method == GET
        publication = Publication.objects.get(id=pubid)
        authors = publication.authors.all()
        userid = request.user.id
        if userid == publication.submitter.id:
            pub_form = PublicationForm(instance=publication)
            author_form = AuthorFormSet(queryset=authors)
            if publication.publication_type == 0:  # book
                media_form = BookForm(instance=Book.objects.get(publication_id=publication))
            elif publication.publication_type == 1:  # conference
                media_form = ConferenceForm(instance=Conference.objects.get(publication_id=publication))
            elif publication.publication_type == 2:  # journal
                media_form = JournalForm(instance=Journal.objects.get(publication_id=publication))
            elif publication.publication_type == 3:  # magazine
                media_form = MagazineForm(instance=Magazine.objects.get(publication_id=publication))
            elif publication.publication_type == 4:  # poster
                media_form = PosterForm(instance=Poster.objects.get(publication_id=publication))
            elif publication.publication_type == 5:  # presentation
                media_form = PresentationForm(instance=Presentation.objects.get(publication_id=publication))
            elif publication.publication_type == 6:  # technical report
                media_form = TechnicalReportForm(instance=TechnicalReport.objects.get(publication_id=publication))
            elif publication.publication_type == 7:  # other
                media_form = OtherForm(instance=Other.objects.get(publication_id=publication))
            else:
                print("Unknown publication type found")

            meta_form = []
            all_projects = [ str(proj) for proj in Project.objects.all().order_by('project') ]
            selected_projects = [str(proj) for proj in publication.projects.all()]
            for project in Project.objects.all().order_by('project'):
                if str(project) in selected_projects:
                    meta_form.append({
                        'name': str(project),
                        'exp_form': ExperimentForm(initial={'experiment': [box.id for box in publication.experiments.all()]},
                                                queryset=project.experiments),
                        'freq_form': FrequencyForm(initial={'frequency': [box.id for box in publication.frequency.all()]}, queryset=project.frequencies),
                        'keyword_form': KeywordForm(initial={'keyword': [box.id for box in publication.keywords.all()]}, queryset=project.keywords),
                        'model_form': ModelForm(initial={'model': [box.id for box in publication.model.all()]}, queryset=project.models),
                        'var_form': VariableForm(initial={'variable': [box.id for box in publication.variables.all()]}, queryset=project.variables),
                    })
                else:
                    meta_form.append({
                        'name': str(project),
                        'exp_form': ExperimentForm(queryset=project.experiments),
                        'freq_form': FrequencyForm(queryset=project.frequencies),
                        'keyword_form': KeywordForm(queryset=project.keywords),
                        'model_form': ModelForm(queryset=project.models),
                        'var_form': VariableForm(queryset=project.variables),
                    })
            meta_type = publication.projects.first()
            return render(request, 'site/edit.html',
                          {'pub_form': pub_form, 'author_form': author_form, 'media_form': media_form, 'pub_type': publication.publication_type,
                          'meta_form': meta_form, 'meta_type': meta_type, "all_projects": all_projects,
                          "selected_projects": selected_projects
                           })
        else:
            entries = Publication.objects.filter(submitter=userid)
            error = 'Error: You must be the owner of a submission to edit it.'
            return render(request, 'site/review.html', {'message': None, 'entries': entries, 'error': error})


@login_required()
def new(request, batch=False, batch_doi="", batch_doi_id=0): # Defaults to single submission. Option arguments passed from "process_dois"
    if request.method == 'GET':
        formset = formset_factory(AuthorForm, extra=0, min_num=1, validate_min=True)
        author_form = formset()
        all_forms = init_forms(author_form)
        meta_form = []
        for project in Project.objects.all():
            meta_form.append({
                'name': str(project),
                'exp_form': ExperimentForm(queryset=project.experiments),
                'freq_form': FrequencyForm(queryset=project.frequencies),
                'keyword_form': KeywordForm(queryset=project.keywords),
                'model_form': ModelForm(queryset=project.models),
                'var_form': VariableForm(queryset=project.variables),
            })
        meta_form.sort(key=lambda x: x['name'])
        all_forms.update({'meta_form': meta_form})
        if batch:
            all_forms.update({'batch': batch})
            all_forms.update({'batch_doi': batch_doi})
            all_forms.update({'batch_doi_id': batch_doi_id})
        return render(request, 'site/new_publication.html', all_forms)

    elif request.method == 'POST':
        submit_success, all_forms = process_publication(request)
        if submit_success: # if the publication was saved
            return HttpResponse(status=200)
        else: # the form was not valid re-rendder form with errors
            meta_form = []
            selected_projects = request.POST.getlist("project")
            for project in Project.objects.all():
                if str(project) in selected_projects:
                    meta_form.append({
                        'name': str(project),
                        'exp_form': ExperimentForm(initial={'experiment': [int(box) for box in request.POST.getlist("experiment") if box.isdigit()]}, queryset=project.experiments),
                        'freq_form': FrequencyForm(initial={'frequency': [int(box) for box in request.POST.getlist("frequency") if box.isdigit()]}, queryset=project.frequencies),
                        'keyword_form': KeywordForm(initial={'keyword': [int(box) for box in request.POST.getlist("keyword") if box.isdigit()]}, queryset=project.keywords),
                        'model_form': ModelForm(initial={'model': [int(box) for box in request.POST.getlist("model") if box.isdigit()]}, queryset=project.models),
                        'var_form': VariableForm(initial={'variable': [int(box) for box in request.POST.getlist("variable") if box.isdigit()]}, queryset=project.variables),
                    })
                else:
                    meta_form.append({
                        'name': str(project),
                        'exp_form': ExperimentForm(queryset=project.experiments),
                        'freq_form': FrequencyForm(queryset=project.frequencies),
                        'keyword_form': KeywordForm(queryset=project.keywords),
                        'model_form': ModelForm(queryset=project.models),
                        'var_form': VariableForm(queryset=project.variables),
                    })
            meta_form = sorted(meta_form, key=lambda proj: proj['name'])
            all_forms.update({'meta_form': meta_form})
            all_forms.update({'selected_projects': selected_projects})
            all_forms.update({'batch': batch})
            all_forms.update({'batch_doi': batch_doi})
            return render(request, 'site/publication_details.html', all_forms, status=400)


def finddoi(request):
    doi = request.GET.get('doi')
    if not doi or doi.isspace():
        empty = True
    else:
        empty = False
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
        try:
            r = requests.get(url, headers=headers)
            status = r.status_code
        except Exception:
            status = 500
    if not empty and status == 200:
        # TODO: Catch differences between agencies e.g. Crossref vs DataCite
        initial = r.json()
        if 'DOI' in list(initial.keys()):
            doi = initial['DOI']
        else:
            doi = ''
        if 'ISBN' in list(initial.keys()):
            isbn = initial['ISBN']
        else:
            isbn = ''
        if 'title' in list(initial.keys()):
            title = initial['title']
        else:
            title = ''
        if 'URL' in list(initial.keys()):
            try:
                url = requests.get(initial['URL'], stream=True).url
                url = url.split(';')[0]
            except requests.exceptions.ConnectionError:
                url = ''
        else:
            url = ''
        if 'container-title' in list(initial.keys()):
            container_title = initial['container-title']
            if container_title in journal_names:
                journal_index = journal_names.index(container_title)
                guessed_journal = False
            else:
                guess = process.extractOne(container_title, journal_names)
                if guess is None:
                    journal_index = 0
                else:
                    journal_name = guess[0]
                    journal_index = journal_names.index(journal_name)
                guessed_journal = True
        else:
            container_title = ''
            journal_index = 0
            guessed_journal = False
        if 'page' in list(initial.keys()):
            try:
                startpage, endpage = str(initial['page']).split('-')
            except:
                startpage = endpage = initial['page']
        else:
            startpage = ''
            endpage = ''
        if 'volume' in list(initial.keys()):
            volume = initial['volume']
        else:
            volume = ''
        if 'issue' in list(initial.keys()):
            issue = initial['issue']
        else:
            issue = ''
        if 'publisher' in list(initial.keys()):
            publisher = initial['publisher']
        else:
            publisher = ''
        try:
            if 'published-print' in list(initial.keys()):
                datelength = len(initial['published-print']['date-parts'][0])
                if datelength == 1:
                    publication_date = '1/1/' + str(initial['published-print']['date-parts'][0][0])
                elif datelength == 2:
                    publication_date = str(initial['published-print']['date-parts'][0][1]) + '/1/' + str(
                        initial['published-print']['date-parts'][0][0])
                elif datelength == 3:
                    publication_date = str(initial['published-print']['date-parts'][0][1]) + '/' + str(
                        initial['published-print']['date-parts'][0][2]) + '/' + str(initial['published-print']['date-parts'][0][0])
            elif 'issued' in list(initial.keys()) and 'date-parts' in list(initial['issued'].keys()) and initial['issued']['date-parts'][0][0]:
                datelength = len(initial['issued']['date-parts'][0])
                publication_date = initial['issued']['date-parts'][0][0]
                if datelength == 1:
                    publication_date = '1/1/' + str(initial['issued']['date-parts'][0][0])
                elif datelength == 2:
                    publication_date = str(initial['issued']['date-parts'][0][1]) + '/1/' + str(initial['issued']['date-parts'][0][0])
                elif datelength == 3:
                    publication_date = str(initial['issued']['date-parts'][0][1]) + '/' + str(initial['issued']['date-parts'][0][2]) + '/' + str(
                        initial['issued']['date-parts'][0][0])
            elif 'created' in list(initial.keys()):
                publication_date = str(initial['created']['date-parts'][0][1]) + '/' + str(initial['created']['date-parts'][0][2]) + '/' + str(
                    initial['created']['date-parts'][0][0])
            else:
                publication_date = ''
        except Exception as e:
            print(e)
            publication_date = ''
        authors_list = []
        if 'author' in list(initial.keys()):

            if 'given' in list(initial['author'][0].keys()):
                for author in initial['author']:
                    try:
                        name = ""
                        if 'family' in list(author.keys()):
                            name += author['family'] 
                        if 'given' in list(author.keys()):
                            name += ', ' + author['given']
                        authors_list.append({'name': name})
                    except Exception:
                        pass

            elif 'literal' in list(initial['author'][0].keys()):
                for author in initial['author']:
                    authors_list.append({'name': author['literal']})
            else:
                pass
        else:
            pass

        data = {'success': True, 'doi': doi, 'isbn': isbn, 'title': title, 'url': url, 'start_page': startpage, 'end_page': endpage, 'publisher': publisher,
                'publication_date': publication_date, 'volume_number': volume, 'issue': issue, 'authors_list': authors_list}
        data.update(dict.fromkeys(['book_name', 'conference_name', 'magazine_name'], container_title))
        data.update({'journal_index': journal_index, 'guessed_journal': guessed_journal})
        return JsonResponse(data)
    else:
        data = {'success': False, 'message': 'Unable to pre-fill form with the given DOI'}
        return JsonResponse(data)


def statistics(request):
    return render(request, 'site/statistics.html', {})

@login_required
def add_dois(request):
    if request.method == "GET":
        doi_batch_form = DoiBatchForm()
        return render(request, "site/add_dois.html", {'doi_batch_form': doi_batch_form})
    else: # method == POST
        doi_batch_form = DoiBatchForm(request.POST)
        if not doi_batch_form.is_valid():
            return render(request, "site/add_dois.html", {'doi_batch_form': doi_batch_form})
        # else: batch form is valid
        doi_list = [doi for doi in doi_batch_form.cleaned_data['dois'].splitlines() if not doi.isspace() and doi != ""]
        try:
            with transaction.atomic():
                for doi in doi_list:
                    PendingDoi(doi=doi, user=request.user).save()
            return render(request, "site/add_dois.html", {'doi_batch_form': doi_batch_form})
        except Exception as e:
            print(e)
            error = "{}{}".format(
                "Could not save list of DOIs. Double check that there is only 1 doi per line, and try again.",
                "If you continue to get this error, please <a href='https://github.com/aims-group/publication-site/issues'>submit an issue.</a>"
            )
            return render(request, "site/add_dois.html", {'doi_batch_form': doi_batch_form, 'error': error})

@login_required
def process_dois(request):
    if request.method == "GET":
        pending_dois = PendingDoi.objects.filter(user=request.user).order_by("date_time")
        if pending_dois:
            return new(request, True, pending_dois[0].doi, pending_dois[0].id)
        else:
            doi_batch_form = DoiBatchForm()
            info = "{}".format(
                "You do not have any DOIs to process. Add some with the form below."
            )
            return redirect("/add_dois/", request=request)
    else: # request.method == POST
        submit_success, all_forms = process_publication(request)
        if(submit_success):
            submitted_doi = all_forms['pub_form'].cleaned_data["doi"]
            try:
                doi_id = int(request.POST["batch_doi_id"])
            except:
                doi_id = 0
            pending_dois = PendingDoi.objects.filter(user=request.user, id=doi_id)
            if pending_dois.count > 0: # if the doi that was saved was a pending doi
                pending_dois[0].delete()  # remove it from the pool of pending entries
            if pending_dois: # if there are more dois pending for the user
                return JsonResponse({"batch_doi": pending_dois[0].doi}) # set up the form with the next one
            else:
                return HttpResponse(status=200)
        else: # form was not valid
            meta_form = []
            selected_projects = request.POST.getlist("project")
            for project in Project.objects.all():
                if str(project) in selected_projects:
                    meta_form.append({
                        'name': str(project),
                        'exp_form': ExperimentForm(initial={'experiment': [int(box) for box in request.POST.getlist("experiment") if box.isdigit()]}, queryset=project.experiments),
                        'freq_form': FrequencyForm(initial={'frequency': [int(box) for box in request.POST.getlist("frequency") if box.isdigit()]}, queryset=project.frequencies),
                        'keyword_form': KeywordForm(initial={'keyword': [int(box) for box in request.POST.getlist("keyword") if box.isdigit()]}, queryset=project.keywords),
                        'model_form': ModelForm(initial={'model': [int(box) for box in request.POST.getlist("model") if box.isdigit()]}, queryset=project.models),
                        'var_form': VariableForm(initial={'variable': [int(box) for box in request.POST.getlist("variable") if box.isdigit()]}, queryset=project.variables),
                    })
                else:
                    meta_form.append({
                        'name': str(project),
                        'exp_form': ExperimentForm(queryset=project.experiments),
                        'freq_form': FrequencyForm(queryset=project.frequencies),
                        'keyword_form': KeywordForm(queryset=project.keywords),
                        'model_form': ModelForm(queryset=project.models),
                        'var_form': VariableForm(queryset=project.variables),
                    })
            meta_form = sorted(meta_form, key=lambda proj: proj['name'])
            all_forms.update({'meta_form': meta_form})
            all_forms.update({'selected_projects': selected_projects})
            all_forms.update({'batch': True})
            all_forms.update({'batch_doi': ""})
            return render(request, 'site/publication_details.html', all_forms, status=400)

# ajax
def ajax(request):
    return HttpResponseRedirect("/?type='all'")


def ajax_citation(request, pub_id):
    pub = Publication.objects.get(id=pub_id)
    authors = [author.name for author in pub.authors.all().order_by('id')]
    pub_type = PUBLICATION_TYPE_CHOICE[pub.publication_type][1]
    if pub_type == 'Journal':
        journal = pub.journal_set.all()[0]
        json = {'title': pub.title, 'url': pub.url, 'authors': authors,
                'doi': pub.doi, 'journal_name': str(journal.journal_name), 'volume_number': journal.volume_number,
                "article_number":journal.article_number, 'start_page': journal.start_page, 'end_page': journal.end_page, 'type': pub_type,
                'year': pub.publication_date.year, 'month': pub.publication_date.month}
    elif pub_type == 'Book':
        book = pub.book_set.all()[0]
        json = {'title': pub.title, 'url': pub.url, 'authors': authors,
                'doi': pub.doi, 'book_name': str(book.book_name), 'chapter_title': book.chapter_title,
                'start_page': book.start_page, 'end_page': book.end_page, 'type': pub_type,
                'editor': book.editor, 'publisher': book.publisher, 'city_of_publication': book.city_of_publication, 'year': pub.publication_date.year}
    elif pub_type == 'Technical Report':
        report = pub.technicalreport_set.all()[0]
        json = {'title': pub.title, 'url': pub.url, 'authors': authors,
                'doi': pub.doi, 'number': str(report.report_number), 'type': pub_type, 'editor': report.editor,
                'issuer': report.issuer, 'year': pub.publication_date.year}
                
    else:
        json = {'title': pub.title, 'year': pub.publication_date.year, 'url': pub.url, 'authors': authors,
                'doi': pub.doi, 'type': pub_type}
    return JsonResponse(json)


def ajax_abstract(request, pub_id):
    pub = Publication.objects.get(id=pub_id)
    return JsonResponse({'abstract': pub.abstract})


def ajax_more_info(request, pub_id):
    pub = Publication.objects.get(id=pub_id)
    experiment_list = sorted(set([str(exp) for exp in pub.experiments.all()])) # remove duplicates by calling set()
    model_list = sorted(set([str(model) for model in pub.model.all()]))
    variable_list = sorted(set([str(variable) for variable in pub.variables.all()]))
    keyword_list = sorted(set([str(keyword) for keyword in pub.keywords.all()]))

    experiments = ",".join(experiment_list)
    model = ",".join(model_list)
    variables = ",".join(variable_list)
    keywords = ",".join(keyword_list)
    # frequency = ",".join(["{frequency.frequency}".format(frequency=frequency) for frequency in pub.frequency.all()])
    # tags = ",".join(["{tags.name}".format(tags=tags) for tags in pub.tags.all()])

    moreinfo = experiments + "|" + model + "|" + variables + "|" + keywords
    json = "{\"key\": \"" + moreinfo + "\"}"
    return HttpResponse(json)


def ajax_prefetch_authors(request):
    authors = Author.objects.all().values_list('name', 'institution').distinct()
    authors = [{'name': author[0], 'institution': author[1]} for author in authors]
    return JsonResponse(authors, safe=False)


def ajax_all_authors(request):
    authors = Author.objects.all().values_list('name', 'institution').distinct()
    authors = [{'name': author[0], 'institution': author[1]} for author in authors]
    return JsonResponse(authors, safe=False)
