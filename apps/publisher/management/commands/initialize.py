from django.core.management import BaseCommand
from publisher.models import Activity, Experiment, Frequency, Keyword, Model, Realm, Variable, JournalOptions, Project
from scripts.activity import activity_data
from scripts.experiment import experiment_data
from scripts.frequency import frequency_data
from scripts.keyword import keyword_data
from scripts.model import model_data
from scripts.realm import realm_data
from scripts.variable import variable_data
from scripts.journals import journal_names


def get_project(project_name):
    project = Project.objects.filter(project=project_name)
    if project:
        return project[0]
    else:
        project = Project(project=project_name)
        project.save()
    return project


class Command(BaseCommand):
    help = "Loads the database with dataset information such as controlled vocabulary."

    def handle(self, *args, **options):
        # Activities
        print('loading activities')
        for project in activity_data:
            project_obj = get_project(project['project_name'])
            for acts in project['activities']:
                if not Activity.objects.filter(activity=acts).exists():
                    new_act = Activity(activity=acts)
                    new_act.save()
                if not project_obj.activities.filter(activity=acts).exists():
                    activity = Activity.objects.filter(activity=acts)
                    project_obj.activities.add(activity[0])
        print('activities done')

        # Experiments
        print('loading experiments')
        for project in experiment_data:
            project_obj = get_project(project['project_name'])
            for exps in project['experiments']:
                if not Experiment.objects.filter(experiment=exps).exists():
                    new_exp = Experiment(experiment=exps)
                    new_exp.save()
                if not project_obj.experiments.filter(experiment=exps).exists():
                    experiment = Experiment.objects.filter(experiment=exps)
                    project_obj.experiments.add(experiment[0])
        print('experiments done')

        # Frequencies
        print('loading frequencies')
        for project in frequency_data:
            project_obj = get_project(project['project_name'])
            for freq in project['frequencies']:
                if not Frequency.objects.filter(frequency=freq).exists():
                    new_freq = Frequency(frequency=freq)
                    new_freq.save()
                if not project_obj.frequencies.filter(frequency=freq).exists():
                    frequency = Frequency.objects.filter(frequency=freq)
                    project_obj.frequencies.add(frequency[0])
        print('frequencies done')

        # Keywords
        print('loading keywords')
        for project in keyword_data:
            project_obj = get_project(project['project_name'])
            for keyw in project['keywords']:
                if not Keyword.objects.filter(keyword=keyw).exists():
                    new_keyw = Keyword(keyword=keyw)
                    new_keyw.save()
                if not project_obj.keywords.filter(keyword=keyw).exists():
                    keyword = Keyword.objects.filter(keyword=keyw)
                    project_obj.keywords.add(keyword[0])
        print('keywords done')

        # Models
        print('loading models')
        for project in model_data:
            project_obj = get_project(project['project_name'])
            for mod in project['models']:
                if not Model.objects.filter(model=mod).exists():
                    new_mod = Model(model=mod)
                    new_mod.save()
                if not project_obj.models.filter(model=mod).exists():
                    model = Model.objects.filter(model=mod)
                    project_obj.models.add(model[0])
        print('models done')

        # Realms
        print('loading realms')
        for project in realm_data:
            project_obj = get_project(project['project_name'])
            for realm in project['realms']:
                if not Realm.objects.filter(realm=realm).exists():
                    new_realm = Realm(realm=realm)
                    new_realm.save()
                if not project_obj.realms.filter(realm=realm).exists():
                    realm = Realm.objects.filter(realm=realm)
                    project_obj.realms.add(realm[0])
        print('realms done')

        # Variables
        print('loading variables')
        for project in variable_data:
            project_obj = get_project(project['project_name'])
            for var in project['variables']:
                if not Variable.objects.filter(variable=var).exists():
                    new_var = Variable(variable=var)
                    new_var.save()
                if not project_obj.variables.filter(variable=var).exists():
                    variable = Variable.objects.filter(variable=var)
                    project_obj.variables.add(variable[0])
        print('variables done')

        # Journals
        print('loading journal names')
        for jour in journal_names:
            new_jour = JournalOptions(journal_name=jour)
            if not JournalOptions.objects.filter(journal_name=jour).exists():
                new_jour.save()
        print('journal names done')

        print('all done')
