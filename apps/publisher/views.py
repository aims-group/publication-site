from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change
from django.forms import forms, formset_factory, modelformset_factory
from forms import PublicationForm, AuthorFormSet, BookForm, ConferenceForm, JournalForm, MagazineForm, PosterForm, AuthorForm
from forms import PresentationForm, TechnicalReportForm, OtherForm, AdvancedSearchForm
from forms import ExperimentForm, FrequencyForm, KeywordForm, ModelForm, VariableForm
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from scripts.journals import journal_names
from fuzzywuzzy import process
from models import *
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
    selected_projects = []

    return {'pub_form': pub_form, 'author_form': author_form, 'book_form': book_form, 'conference_form': conference_form,
            'journal_form': journal_form, 'magazine_form': magazine_form, 'poster_form': poster_form,
            'presentation_form': presentation_form, 'technical_form': technical_form,
            'other_form': other_form, 'exp_form': exp_form, 'freq_form': freq_form,
            'keyword_form': keyword_form, 'model_form': model_form, 'var_form': var_form,
            'selected_projects': selected_projects, 'all_projects': all_projects}


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


def search(request):
    publications_to_load = 100  # number of publications to load at a time
    pubs = {}
    data = collections.OrderedDict()
    pubs["type"] = request.GET.get("type", "all")
    pubs["option"] = request.GET.get("option", "")
    pubs["total"] = Publication.objects.all().count()
    pubs["hide_search"] = "display:none;"
    try:
        scroll_count = int(request.GET.get("scroll_count", "0"))
    except ValueError as e:
        print e
        scroll_count = 0

    if request.method == 'GET':
        if pubs["type"] in ["all", "CMIP", "ESGF", "experiment", "frequency", "keyword", "model", "project", "program",  "status", "type", "variable", "year"]:
            pubs["search"] = True
            page_filter = request.GET.get("type", "all")
            display = request.GET.get('display', '')  # expect display == 'citations' or nothing

            if page_filter == 'all':
                publications = Publication.objects.all().order_by("-publication_date")
                pubs["pages"] = get_all_options()

            elif page_filter == "CMIP":
                option = request.GET.get("option", "all")
                pubs["option"] = option
                total_cmip_pubs = 0
                #todo: verify that no other logic needs to be here for dealing with CMIP oddities
                #Todo: there is a lot of double filtering going on. these can be replaced by using "publication_set" generally
                all_cmips = Project.objects.filter(project__contains="CMIP")
                if option == "all":
                    publications = Publication.objects.filter(projects__project__contains="CMIP").order_by("-publication_date")
                else:
                    publications = Publication.objects.filter(projects=Project.objects.filter(project=option)).order_by("-publication_date")
                for cmip in all_cmips.order_by('-project'):
                    if cmip.publication_set.count() == 0:
                        continue
                    project_data = {}
                    project_data['type'] = 'CMIP'
                    project_data['options'] = str(cmip).upper() #name of cmip being filtered
                    project_data['count'] = cmip.publication_set.count()
                    total_cmip_pubs += project_data['count']
                    data[(str(cmip))] = project_data
                data['all'] = {'type': 'CMIP', 'options': 'all', 'count': total_cmip_pubs}
                pubs['pages'] = data
            elif page_filter == 'experiment':
                option = request.GET.get("option", "1pctCO2")
                pubs["option"] = option
                publications = Publication.objects.filter(experiments=Experiment.objects.filter(experiment=option)).order_by("-publication_date")
                for exp in Experiment.objects.all().order_by('experiment'):
                    if Publication.objects.filter(experiments=Experiment.objects.filter(experiment=exp)).count() == 0:
                        continue
                    exps = {}
                    exps['type'] = 'experiment'
                    exps['options'] = str(exp.experiment)
                    exps['count'] = Publication.objects.filter(experiments=Experiment.objects.filter(experiment=exp)).count()
                    data[str(exp.experiment)] = exps
                pubs["pages"] = data

            elif page_filter == 'frequency':
                option = request.GET.get("option", "3-hourly")
                pubs["option"] = option
                publications = Publication.objects.filter(frequency=Frequency.objects.filter(frequency=option)).order_by("-publication_date")
                for frq in Frequency.objects.all().order_by('frequency'):
                    if Publication.objects.filter(frequency=Frequency.objects.filter(frequency=frq)).count() == 0:
                        continue
                    frqs = {}
                    frqs['type'] = 'frequency'
                    frqs['options'] = str(frq.frequency)
                    frqs['count'] = Publication.objects.filter(frequency=Frequency.objects.filter(frequency=frq)).count()
                    data[str(frq.frequency)] = frqs
                pubs["pages"] = data

            elif page_filter == 'keyword':
                option = request.GET.get("option", "Abrupt change")
                pubs["option"] = option
                publications = Publication.objects.filter(keywords=Keyword.objects.filter(keyword=option)).order_by("-publication_date")
                for kyw in Keyword.objects.all().order_by('keyword'):
                    if Publication.objects.filter(keywords=Keyword.objects.filter(keyword=kyw)).count() == 0:
                        continue
                    kyws = {}
                    kyws['type'] = 'keyword'
                    kyws['options'] = str(kyw.keyword)
                    kyws['count'] = Publication.objects.filter(keywords=Keyword.objects.filter(keyword=kyw)).count()
                    data[str(kyw.keyword)] = kyws
                pubs["pages"] = data

            elif page_filter == 'model':
                option = request.GET.get("option", "ACCESS1.0")
                pubs["option"] = option
                publications = Publication.objects.filter(model=Model.objects.filter(model=option)).order_by("-publication_date")
                for mod in Model.objects.all().order_by('model'):
                    if Publication.objects.filter(model=Model.objects.filter(model=mod)).count() == 0:
                        continue
                    mods = {}
                    mods['type'] = 'model'
                    mods['options'] = str(mod.model)
                    mods['count'] = Publication.objects.filter(model=Model.objects.filter(model=mod)).count()
                    data[str(mod.model)] = mods
                pubs["pages"] = data

            elif page_filter == 'status':
                option = request.GET.get("option", "Published")
                pubs["option"] = option
                lookup = 0
                for k, v in PUBLICATION_STATUS_CHOICE:
                    if str(v) == str(option):
                        lookup = k
                        break
                publications = Publication.objects.filter(status=lookup).order_by("-publication_date")
                for stat in range(0, len(PUBLICATION_STATUS_CHOICE)):
                    if Publication.objects.filter(status=stat).count() == 0:
                        continue
                    stats = {}
                    stats['type'] = 'status'
                    stats['options'] = PUBLICATION_STATUS_CHOICE[stat][1]
                    stats['count'] = Publication.objects.filter(status=stat).count()
                    data[str(PUBLICATION_STATUS_CHOICE[stat][1])] = stats
                pubs["pages"] = data

            elif page_filter == 'type':
                option = request.GET.get("option", "Journal")
                pubs["option"] = option
                lookup = 2
                for k, v in PUBLICATION_TYPE_CHOICE:
                    if str(v) == option:
                        lookup = k
                        break
                publications = Publication.objects.filter(publication_type=lookup).order_by("-publication_date")
                for pt in range(0, len(PUBLICATION_TYPE_CHOICE) - 1):
                    if Publication.objects.filter(publication_type=pt).count() == 0:
                        continue
                    pubtype = {}
                    pubtype['type'] = 'type'
                    typename = str(PUBLICATION_TYPE_CHOICE[pt][1])
                    pubtype['options'] = typename
                    pubtype['count'] = Publication.objects.filter(publication_type=pt).count()
                    data[typename] = pubtype
                pubs["pages"] = data

            elif page_filter == 'variable':
                option = request.GET.get("option", "air pressure")
                pubs["option"] = request.GET.get("option", "air pressure")
                publications = Publication.objects.filter(variables=Variable.objects.filter(variable=option)).order_by("-publication_date")
                for var in Variable.objects.all().order_by('variable'):
                    if Publication.objects.filter(variables=Variable.objects.filter(variable=var)).count() == 0:
                        continue
                    vars = {}
                    vars['type'] = 'variable'
                    vars['options'] = str(var.variable)
                    vars['count'] = Publication.objects.filter(variables=Variable.objects.filter(variable=var)).count()
                    data[str(var.variable)] = vars
                pubs["pages"] = data

            elif page_filter == 'year':
                now = datetime.datetime.now()
                option = request.GET.get("option", str(now.year))
                pubs["option"] = option
                publications = Publication.objects.filter(publication_date__year=option).order_by("-publication_date")
                for pub_years in AvailableYears.objects.all().order_by('-year'):
                    years = {}
                    years['type'] = 'year'
                    years['options'] = str(pub_years.year)
                    years['count'] = Publication.objects.filter(publication_date__year=pub_years.year).count()
                    data[str(pub_years.year)] = years
                pubs["pages"] = data

            elif page_filter == 'project':
                option = request.GET.get("option", "CMIP5")
                pubs["option"] = option
                publications = Publication.objects.filter(projects=Project.objects.filter(project=option)).order_by("-publication_date")
                for project in Project.objects.all().order_by('project'):
                    if Publication.objects.filter(projects=Project.objects.filter(project=project)).count() == 0:
                        continue
                    project_data = {}
                    project_data['type'] = 'project'
                    project_data['options'] = str(project)
                    project_data['count'] = Publication.objects.filter(projects=Project.objects.filter(project=project)).count()
                    data[(str(project))] = project_data
                pubs['pages'] = data

            elif page_filter == 'program':
                option = request.GET.get("option", "all")
                pubs["option"] = option
                if option == "all":
                    publications = Publication.objects.exclude(projects__project__contains="CMIP").order_by("-publication_date")
                else:
                    publications = Publication.objects.filter(projects=Project.objects.filter(project=option)).order_by("-publication_date")
                for program in Project.objects.all().order_by('project'):
                    if Publication.objects.filter(projects=Project.objects.filter(project=program)).count() == 0 or "CMIP" in str(program):
                        continue
                    program_data = {}
                    program_data['type'] = 'program'
                    program_data['options'] = str(program)
                    program_data['count'] = Publication.objects.filter(projects=Project.objects.filter(project=program)).count()
                    data[(str(program))] = program_data
                data['all'] = {'type': 'program', 'options': 'all', 'count': Publication.objects.exclude(projects__project__contains="CMIP").order_by("-publication_date").count()}
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
                    pubs["scroll_link"] = "/search?type={}&scroll_count={}".format(page_filter, scroll_count + 1)
                else:
                    pubs["scroll_link"] = "/search?type={}&option={}&scroll_count={}".format(page_filter, option.replace(' ', '%20'), scroll_count + 1)
                pubs["publications"] = publications[prev_articles:new_articles]
                return render(request, 'snippets/load_publications.html', pubs)

            else:
                if page_filter == 'all':
                    pubs["scroll_link"] = "/search?type={}&scroll_count=1".format(page_filter)
                else:
                    pubs["scroll_link"] = "/search?type={}&option={}&scroll_count=1".format(page_filter, option.replace(' ', '%20'))
                pubs["publications"] = publications[:publications_to_load]
    return render(request, 'site/search.html', pubs)

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
    pubs["total"] = Publication.objects.all().count()
    pubs["hide_search"] = "display:none;"
    try:
        scroll_count = int(request.GET.get("scroll_count", "0"))
    except ValueError as e:
        print e
        scroll_count = 0

    pubs["search"] = True
    page_filter = request.GET.get("type", "all")
    display = request.GET.get('display', '')  # expect display == 'citations' or nothing
    if project_name == "all":
        publications = Publication.objects.all().order_by("-publication_date")
    else:
        try:
            publications = Project.objects.get(project__iexact=project_name).publication_set.order_by("-publication_date")    
        except Project.DoesNotExist as e:
            print e
            return HttpResponse(status=404)
    if page_filter == 'all':
        pubs["pages"] = get_all_options()

    elif page_filter == 'experiment':
        option = request.GET.get("option", "1pctCO2")
        pubs["option"] = option
        publications = Publication.objects.filter(experiments=Experiment.objects.filter(experiment=option)).order_by("-publication_date")
        for exp in Experiment.objects.all().order_by('experiment'):
            if Publication.objects.filter(experiments=Experiment.objects.filter(experiment=exp)).count() == 0:
                continue
            exps = {}
            exps['type'] = 'experiment'
            exps['options'] = str(exp.experiment)
            exps['count'] = Publication.objects.filter(experiments=Experiment.objects.filter(experiment=exp)).count()
            data[str(exp.experiment)] = exps
        pubs["pages"] = data

    elif page_filter == 'frequency':
        option = request.GET.get("option", "3-hourly")
        pubs["option"] = option
        publications = Publication.objects.filter(frequency=Frequency.objects.filter(frequency=option)).order_by("-publication_date")
        for frq in Frequency.objects.all().order_by('frequency'):
            if Publication.objects.filter(frequency=Frequency.objects.filter(frequency=frq)).count() == 0:
                continue
            frqs = {}
            frqs['type'] = 'frequency'
            frqs['options'] = str(frq.frequency)
            frqs['count'] = Publication.objects.filter(frequency=Frequency.objects.filter(frequency=frq)).count()
            data[str(frq.frequency)] = frqs
        pubs["pages"] = data

    elif page_filter == 'keyword':
        option = request.GET.get("option", "Abrupt change")
        pubs["option"] = option
        publications = Publication.objects.filter(keywords=Keyword.objects.filter(keyword=option)).order_by("-publication_date")
        for kyw in Keyword.objects.all().order_by('keyword'):
            if Publication.objects.filter(keywords=Keyword.objects.filter(keyword=kyw)).count() == 0:
                continue
            kyws = {}
            kyws['type'] = 'keyword'
            kyws['options'] = str(kyw.keyword)
            kyws['count'] = Publication.objects.filter(keywords=Keyword.objects.filter(keyword=kyw)).count()
            data[str(kyw.keyword)] = kyws
        pubs["pages"] = data

    elif page_filter == 'model':
        option = request.GET.get("option", "ACCESS1.0")
        pubs["option"] = option
        publications = Publication.objects.filter(model=Model.objects.filter(model=option)).order_by("-publication_date")
        for mod in Model.objects.all().order_by('model'):
            if Publication.objects.filter(model=Model.objects.filter(model=mod)).count() == 0:
                continue
            mods = {}
            mods['type'] = 'model'
            mods['options'] = str(mod.model)
            mods['count'] = Publication.objects.filter(model=Model.objects.filter(model=mod)).count()
            data[str(mod.model)] = mods
        pubs["pages"] = data

    elif page_filter == 'status':
        option = request.GET.get("option", "Published")
        pubs["option"] = option
        lookup = 0
        for k, v in PUBLICATION_STATUS_CHOICE:
            if str(v) == str(option):
                lookup = k
                break
        publications = Publication.objects.filter(status=lookup).order_by("-publication_date")
        for stat in range(0, len(PUBLICATION_STATUS_CHOICE)):
            if Publication.objects.filter(status=stat).count() == 0:
                continue
            stats = {}
            stats['type'] = 'status'
            stats['options'] = PUBLICATION_STATUS_CHOICE[stat][1]
            stats['count'] = Publication.objects.filter(status=stat).count()
            data[str(PUBLICATION_STATUS_CHOICE[stat][1])] = stats
        pubs["pages"] = data

    elif page_filter == 'type':
        option = request.GET.get("option", "Journal")
        pubs["option"] = option
        lookup = 2
        for k, v in PUBLICATION_TYPE_CHOICE:
            if str(v) == option:
                lookup = k
                break
        publications = Publication.objects.filter(publication_type=lookup).order_by("-publication_date")
        for pt in range(0, len(PUBLICATION_TYPE_CHOICE) - 1):
            if Publication.objects.filter(publication_type=pt).count() == 0:
                continue
            pubtype = {}
            pubtype['type'] = 'type'
            typename = str(PUBLICATION_TYPE_CHOICE[pt][1])
            pubtype['options'] = typename
            pubtype['count'] = Publication.objects.filter(publication_type=pt).count()
            data[typename] = pubtype
        pubs["pages"] = data

    elif page_filter == 'variable':
        option = request.GET.get("option", "air pressure")
        pubs["option"] = request.GET.get("option", "air pressure")
        publications = Publication.objects.filter(variables=Variable.objects.filter(variable=option)).order_by("-publication_date")
        for var in Variable.objects.all().order_by('variable'):
            if Publication.objects.filter(variables=Variable.objects.filter(variable=var)).count() == 0:
                continue
            vars = {}
            vars['type'] = 'variable'
            vars['options'] = str(var.variable)
            vars['count'] = Publication.objects.filter(variables=Variable.objects.filter(variable=var)).count()
            data[str(var.variable)] = vars
        pubs["pages"] = data

    elif page_filter == 'year':
        now = datetime.datetime.now()
        option = request.GET.get("option", str(now.year))
        pubs["option"] = option
        publications = Publication.objects.filter(publication_date__year=option).order_by("-publication_date")
        for pub_years in AvailableYears.objects.all().order_by('-year'):
            years = {}
            years['type'] = 'year'
            years['options'] = str(pub_years.year)
            years['count'] = Publication.objects.filter(publication_date__year=pub_years.year).count()
            data[str(pub_years.year)] = years
        pubs["pages"] = data

    elif page_filter == 'project':
        option = request.GET.get("option", "CMIP5")
        pubs["option"] = option
        publications = Publication.objects.filter(projects=Project.objects.filter(project=option)).order_by("-publication_date")
        for project in Project.objects.all().order_by('project'):
            if Publication.objects.filter(projects=Project.objects.filter(project=project)).count() == 0:
                continue
            project_data = {}
            project_data['type'] = 'project'
            project_data['options'] = str(project)
            project_data['count'] = Publication.objects.filter(projects=Project.objects.filter(project=project)).count()
            data[(str(project))] = project_data
        pubs['pages'] = data

    elif page_filter == 'program':
        option = request.GET.get("option", "all")
        pubs["option"] = option
        if option == "all":
            publications = Publication.objects.exclude(projects__project__contains="CMIP").order_by("-publication_date")
        else:
            publications = Publication.objects.filter(projects=Project.objects.filter(project=option)).order_by("-publication_date")
        for program in Project.objects.all().order_by('project'):
            if Publication.objects.filter(projects=Project.objects.filter(project=program)).count() == 0 or "CMIP" in str(program):
                continue
            program_data = {}
            program_data['type'] = 'program'
            program_data['options'] = str(program)
            program_data['count'] = Publication.objects.filter(projects=Project.objects.filter(project=program)).count()
            data[(str(program))] = program_data
        data['all'] = {'type': 'program', 'options': 'all', 'count': Publication.objects.exclude(projects__project__contains="CMIP").order_by("-publication_date").count()}
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
                pubs["scroll_link"] = "/search?type={}&scroll_count={}".format(page_filter, scroll_count + 1)
            else:
                pubs["scroll_link"] = "/search?type={}&option={}&scroll_count={}".format(page_filter, option.replace(' ', '%20'), scroll_count + 1)
            pubs["publications"] = publications[prev_articles:new_articles]
            return render(request, 'snippets/load_publications.html', pubs)

        else:
            if page_filter == 'all':
                pubs["scroll_link"] = "/search?type={}&scroll_count=1".format(page_filter)
            else:
                pubs["scroll_link"] = "/search?type={}&option={}&scroll_count=1".format(page_filter, option.replace(' ', '%20'))
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
            if 'doi' in form.cleaned_data.keys() and form.cleaned_data['doi']:
                pubs = pubs.filter(doi__icontains=form.cleaned_data['doi'])

            if 'title' in form.cleaned_data.keys() and form.cleaned_data['title']:
                pubs = pubs.filter(title__icontains=form.cleaned_data['title'])

            if 'author' in form.cleaned_data.keys() and form.cleaned_data['author']:
                pubs = pubs.filter(authors__name__icontains=form.cleaned_data['author'])

            if 'date_end' in form.cleaned_data.keys() and form.cleaned_data['date_start'] and form.cleaned_data['date_end']:
                pubs = pubs.filter(publication_date__range=[form.cleaned_data['date_start'], form.cleaned_data['date_end']])

            elif 'date_start' in form.cleaned_data.keys() and form.cleaned_data['date_start']:
                pubs = pubs.filter(publication_date__gte=form.cleaned_data['date_start'])

            elif 'date_end' in form.cleaned_data.keys() and form.cleaned_data['date_end']:
                pubs = pubs.filter(publication_date__lte=form.cleaned_data['date_end'])

            if 'program' in form.cleaned_data.keys() and form.cleaned_data['program']:
                for prog in form.cleaned_data['program']:
                    pubs = pubs.filter(projects=prog)

            if 'project' in form.cleaned_data.keys() and form.cleaned_data['project']:
                for proj in form.cleaned_data['project']:
                    pubs = pubs.filter(projects=proj)

            if 'experiment' in form.cleaned_data.keys() and form.cleaned_data['experiment']:
                for exp in form.cleaned_data['experiment']:
                    pubs = pubs.filter(experiments__experiment=exp)

            if 'frequency' in form.cleaned_data.keys() and form.cleaned_data['frequency']:
                for freq in form.cleaned_data['frequency']:
                    pubs = pubs.filter(frequency__frequency=freq)

            if 'keyword' in form.cleaned_data.keys() and form.cleaned_data['keyword']:
                for keyw in form.cleaned_data['keyword']:
                    pubs = pubs.filter(keywords__keyword=keyw)

            if 'model' in form.cleaned_data.keys() and form.cleaned_data['model']:
                for model in form.cleaned_data['model']:
                    pubs = pubs.filter(model__model=model)

            if 'variable' in form.cleaned_data.keys() and form.cleaned_data['variable']:
                for var in form.cleaned_data['variable']:
                    pubs = pubs.filter(variables=var)
            if 'ajax' in request.POST.keys() and request.POST['ajax'] == 'true':
                return JsonResponse({'count': pubs.count()})
            if 'display' in request.POST.keys() and request.POST['display'] in ['citations', 'bibtex']:
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
    entries = Publication.objects.filter(submitter=request.user.id)
    if not entries:
        message = 'You do not have any publications to display. <a href="/new">Submit one.</a>'
    return render(request, 'site/review.html', {'message': message, 'entries': entries, 'error': None})


@login_required()
def delete(request, pub_id):
    publication = Publication.objects.get(id=pub_id)
    userid = request.user.id
    if userid == publication.submitter.id:
        publication.delete()
        return redirect('review')
    else:
        entries = Publication.objects.filter(submitter=userid)
        error = 'Error: You must be the owner of a submission to edit it.'
        return render(request, 'site/review.html', {'message': None, 'entries': entries, 'error': error})


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
        for project in pub_instance.projects.all():
            meta_form.append({
                'name': str(project),
                'exp_form': ExperimentForm(initial={'experiment': [box.id for box in pub_instance.experiments.all()]}, queryset=project.experiments),
                'freq_form': FrequencyForm(initial={'frequency': [box.id for box in pub_instance.frequency.all()]}, queryset=project.frequencies),
                'keyword_form': KeywordForm(initial={'keyword': [box.id for box in pub_instance.keywords.all()]}, queryset=project.keywords),
                'model_form': ModelForm(initial={'model': [box.id for box in pub_instance.model.all()]}, queryset=project.models),
                'var_form': VariableForm(initial={'variable': [box.id for box in pub_instance.variables.all()]}, queryset=project.variables),
            })
        meta_type = pub_instance.projects.first()
        ens = request.POST.getlist('ensemble')
        ensemble_data = str([[index + 1, int('0' + str(ens[index]))] for index in range(len(ens)) if ens[index] is not u''])
        return render(request, 'site/edit.html',
                      {'pub_form': pub_form, 'author_form': author_form_set, 'media_form': media_form, 'pub_type': pub_type,
                       'ensemble_data': ensemble_data, 'meta_form': meta_form, 'meta_type': meta_type, "all_projects": all_projects,
                        "selected_projects": selected_projects
                       })

    else:
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
                print "Unknown publication type found"

            meta_form = []
            all_projects = [ str(proj) for proj in Project.objects.all().order_by('project') ]
            selected_projects = [str(proj) for proj in publication.projects.all()]
            for project in publication.projects.all():
                meta_form.append({
                    'name': str(project),
                    'exp_form': ExperimentForm(initial={'experiment': [box.id for box in publication.experiments.all()]},
                                               queryset=project.experiments),
                    'freq_form': FrequencyForm(initial={'frequency': [box.id for box in publication.frequency.all()]}, queryset=project.frequencies),
                    'keyword_form': KeywordForm(initial={'keyword': [box.id for box in publication.keywords.all()]}, queryset=project.keywords),
                    'model_form': ModelForm(initial={'model': [box.id for box in publication.model.all()]}, queryset=project.models),
                    'var_form': VariableForm(initial={'variable': [box.id for box in publication.variables.all()]}, queryset=project.variables),
                })
            meta_type = publication.projects.first()
            # Technically, publications can have more than one project. currently only one is ever used, so take the first
            ensemble_data = str([[value['model_id'], value['ensemble']] for value in
                                 PubModels.objects.filter(publication_id=publication.id).values('model_id', 'ensemble')])
            return render(request, 'site/edit.html',
                          {'pub_form': pub_form, 'author_form': author_form, 'media_form': media_form, 'pub_type': publication.publication_type,
                          'ensemble_data': ensemble_data, 'meta_form': meta_form, 'meta_type': meta_type, "all_projects": all_projects,
                          "selected_projects": selected_projects
                           })
        else:
            entries = Publication.objects.filter(submitter=userid)
            error = 'Error: You must be the owner of a submission to edit it.'
            return render(request, 'site/review.html', {'message': None, 'entries': entries, 'error': error})


@login_required()
def new(request):
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
        return render(request, 'site/new_publication.html', all_forms)

    elif request.method == 'POST':
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
            return HttpResponse(status=200)
        meta_form = []
        project_string = request.POST.get('meta_type', 'CMIP5')
        for project in Project.objects.all():
            if str(project) == project_string:
                meta_form.append({
                    'name': str(project),
                    'exp_form': ExperimentForm(request.POST, queryset=project.experiments),
                    'freq_form': FrequencyForm(request.POST, queryset=project.frequencies),
                    'keyword_form': KeywordForm(request.POST, queryset=project.keywords),
                    'model_form': ModelForm(request.POST, queryset=project.models),
                    'var_form': VariableForm(request.POST, queryset=project.variables),
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
        except:
            status = 500
    if not empty and status == 200:
        # TODO: Catch differences between agencies e.g. Crossref vs DataCite
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
            url = requests.get(initial['URL'], stream=True, verify=False).url  # use llnl cert instead of verify=False
            url = url.split(';')[0]
        else:
            url = ''
        if 'container-title' in initial.keys():
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
        if 'page' in initial.keys():
            try:
                startpage, endpage = str(initial['page']).split('-')
            except:
                startpage = endpage = initial['page']
        else:
            startpage = ''
            endpage = ''
        if 'volume' in initial.keys():
            volume = initial['volume']
        else:
            volume = ''
        if 'issue' in initial.keys():
            issue = initial['issue']
        else:
            issue = ''
        if 'publisher' in initial.keys():
            publisher = initial['publisher']
        else:
            publisher = ''
        try:
            if 'published-print' in initial.keys():
                datelength = len(initial['published-print']['date-parts'][0])
                if datelength == 1:
                    publication_date = '1/1/' + str(initial['published-print']['date-parts'][0][0])
                elif datelength == 2:
                    publication_date = str(initial['published-print']['date-parts'][0][1]) + '/1/' + str(
                        initial['published-print']['date-parts'][0][0])
                elif datelength == 3:
                    publication_date = str(initial['published-print']['date-parts'][0][1]) + '/' + str(
                        initial['published-print']['date-parts'][0][2]) + '/' + str(initial['published-print']['date-parts'][0][0])
            elif 'issued' in initial.keys() and 'date-parts' in initial['issued'].keys() and initial['issued']['date-parts'][0][0]:
                datelength = len(initial['issued']['date-parts'][0])
                publication_date = initial['issued']['date-parts'][0][0]
                if datelength == 1:
                    publication_date = '1/1/' + str(initial['issued']['date-parts'][0][0])
                elif datelength == 2:
                    publication_date = str(initial['issued']['date-parts'][0][1]) + '/1/' + str(initial['issued']['date-parts'][0][0])
                elif datelength == 3:
                    publication_date = str(initial['issued']['date-parts'][0][1]) + '/' + str(initial['issued']['date-parts'][0][2]) + '/' + str(
                        initial['issued']['date-parts'][0][0])
            elif 'created' in initial.keys():
                publication_date = str(initial['created']['date-parts'][0][1]) + '/' + str(initial['created']['date-parts'][0][2]) + '/' + str(
                    initial['created']['date-parts'][0][0])
            else:
                publication_date = ''
        except Exception as e:
            print(e)
            publication_date = ''
        authors_list = []
        if 'author' in initial.keys():

            if 'given' in initial['author'][0].keys():
                for author in initial['author']:
                    authors_list.append({'name': author['family'] + ', ' + author['given']})

            elif 'literal' in initial['author'][0].keys():
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
    return render(request, 'site/statistics.html')


def network_graph(request):
    return render(request, 'site/network-graph.html')


# ajax
def ajax(request):
    return HttpResponseRedirect("/search?type='all'")


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

    experiments = ",".join(["{experiments.experiment}".format(experiments=experiments) for experiments in pub.experiments.all()])
    model = ",".join(["{model.model}".format(model=model) for model in pub.model.all()])
    variables = ",".join(["{variables.variable}".format(variables=variables) for variables in pub.variables.all()])
    keywords = ",".join(["{keywords.keyword}".format(keywords=keywords) for keywords in pub.keywords.all()])
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

