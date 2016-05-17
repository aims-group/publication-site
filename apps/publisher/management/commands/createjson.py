from django.core.management import BaseCommand
from publisher.models import Experiment, Frequency, Keyword, Model, Variable, Publication
from itertools import combinations
import json


class Command(BaseCommand):
    help = "Creates static json files "

    def handle(self, *args, **options):
        self.stdout.write("Creating network graph json file...")
        publications = Publication.objects.all()
        nodes = []
        links = []
        lookupdict = {}
        stats = {}
        max_size = 1
        for publication in publications:
            pair_list = []
            temp_count = []
            for experiment in publication.experiments.all():
                if not str(experiment) in lookupdict.keys():
                    size = Publication.experiments.through.objects.filter(experiment_id=experiment.id).count()
                    max_size = (size if size > max_size else max_size)
                    exp = {'size': size, 'score': 0, 'id': str(experiment), 'type': "circle", 'facet_type': 'experiment'}
                    nodes.append(exp)
                    lookupdict.update({str(experiment): len(nodes) - 1})
                pair_list.append(lookupdict[str(experiment)])
                temp_count.append(str(experiment))

            for frequency in publication.frequency.all():
                if not str(frequency) in lookupdict.keys():
                    size = Publication.frequency.through.objects.filter(frequency_id=frequency.id).count()
                    max_size = (size if size > max_size else max_size)
                    exp = {'size': size, 'score': 1, 'id': str(frequency), 'type': "circle", 'facet_type': 'frequency'}
                    nodes.append(exp)
                    lookupdict.update({str(frequency): len(nodes) - 1})
                pair_list.append(lookupdict[str(frequency)])
                temp_count.append(str(frequency))

            for keyword in publication.keywords.all():
                if not str(keyword) in lookupdict.keys():
                    size = Publication.keywords.through.objects.filter(keyword_id=keyword.id).count()
                    max_size = (size if size > max_size else max_size)
                    exp = {'size': size, 'score': 2, 'id': str(keyword), 'type': "circle", 'facet_type': 'keyword'}
                    nodes.append(exp)
                    lookupdict.update({str(keyword): len(nodes) - 1})
                pair_list.append(lookupdict[str(keyword)])
                temp_count.append(str(keyword))

            for model in publication.model.all():
                if not str(model) in lookupdict.keys():
                    size = Publication.model.through.objects.filter(model_id=model.id).count()
                    max_size = (size if size > max_size else max_size)
                    exp = {'size': size, 'score': 3, 'id': str(model), 'type': "circle", 'facet_type': 'model'}
                    nodes.append(exp)
                    lookupdict.update({str(model): len(nodes) - 1})
                pair_list.append(lookupdict[str(model)])
                temp_count.append(str(model))


            for variable in publication.variables.all():
                if not str(variable) in lookupdict.keys():
                    size = Publication.variables.through.objects.filter(variable_id=variable.id).count()
                    max_size = (size if size > max_size else max_size)
                    exp = {'size': size, 'score': 4, 'id': str(variable), 'type': "circle", 'facet_type': 'variable'}
                    nodes.append(exp)
                    lookupdict.update({str(variable): len(nodes) - 1})
                pair_list.append(lookupdict[str(variable)])
                temp_count.append(str(variable))

            for source in temp_count:
                for target in temp_count:
                    if not source == target:
                        if source not in stats.keys():
                            stats[source] = {}
                        if target not in stats[source]:
                            stats[source][target] = 0
                        stats[source][target] += 1


            links = links + [{"source": comb[0], "target": comb[1]} for comb in combinations(pair_list, 2)]

        data = {
            "max_size": max_size,
            "graph": [],
            "links": links,
            "nodes": nodes,
            "stats": stats,
            "directed": False,
            "multigraph": False
        }

        location = 'static/js/network-graph.json'
        with open(location, 'w') as outfile:
            json.dump(data, outfile)

        self.stdout.write("Finished creating network graph in: " + location)
