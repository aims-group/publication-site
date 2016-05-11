from publisher.models import Experiment, Frequency, Keyword, Model, Variable, Publication
from itertools import combinations
import json
import pdb

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

def init_graph():
    publications = Publication.objects.all()
    nodes = []
    links = []
    lookupdict = {}

    for publication in publications:
        pair_list = []

        for experiment in publication.experiments.all():
            if not str(experiment) in lookupdict.keys():
                size = Publication.experiments.through.objects.filter(experiment_id=experiment.id).count()
                exp = {'size': size, 'score': 0, 'id': str(experiment), 'type': "circle", 'facet_type': 'experiment'}
                nodes.append(exp)
                lookupdict.update({str(experiment): len(nodes)-1})
            pair_list.append(lookupdict[str(experiment)])

        for frequency in publication.frequency.all():
            if not str(frequency) in lookupdict.keys():
                size = Publication.frequency.through.objects.filter(frequency_id=frequency.id).count()
                exp = {'size': size, 'score': 0, 'id': str(experiment), 'type': "circle", 'facet_type': 'frequency'}
                nodes.append(exp)
                lookupdict.update({str(frequency): len(nodes) - 1})
            pair_list.append(lookupdict[str(frequency)])

        for keyword in publication.keywords.all():
            if not str(keyword) in lookupdict.keys():
                size = Publication.keywords.through.objects.filter(keyword_id=keyword.id).count()
                exp = {'size': size, 'score': 0, 'id': str(experiment), 'type': "circle", 'facet_type': 'keyword'}
                nodes.append(exp)
                lookupdict.update({str(keyword): len(nodes) - 1})
            pair_list.append(lookupdict[str(keyword)])

        for model in publication.model.all():
            if not str(model) in lookupdict.keys():
                size = Publication.model.through.objects.filter(model_id=model.id).count()
                exp = {'size': size, 'score': 0, 'id': str(experiment), 'type': "circle", 'facet_type': 'model'}
                nodes.append(exp)
                lookupdict.update({str(model): len(nodes) - 1})
            pair_list.append(lookupdict[str(model)])

        for variable in publication.variables.all():
            if not str(variable) in lookupdict.keys():
                size = Publication.variables.through.objects.filter(variable_id=variable.id).count()
                exp = {'size': size, 'score': 0, 'id': str(experiment), 'type': "circle", 'facet_type': 'variable'}
                nodes.append(exp)
                lookupdict.update({str(variable): len(nodes) - 1})
            pair_list.append(lookupdict[str(variable)])

        links.append([{"source": comb[0], "target": comb[1]} for comb in combinations(pair_list, 2)])

    data = {
        "graph": [],
        "links": links,
        "nodes": nodes,
        "directed": False,
        "multigraph": False
    }

    with open('debugme.json', 'w') as outfile:
        json.dump(data, outfile)
