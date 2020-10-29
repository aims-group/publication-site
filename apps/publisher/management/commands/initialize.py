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
        if Activity.objects.all():
            print('activities already loaded')
        else:
            print('loading activities')
            for project in activity_data:
                project_obj = get_project(project['project_name'])
                for acts in project['activities']:
                    pre_existing_activity = Activity.objects.filter(activity=acts)
                    if pre_existing_activity:
                        project_obj.activities.add(pre_existing_activity[0])
                    else:
                        new_act = Activity(activity=acts)
                        new_act.save()
                        project_obj.activities.add(new_act)
            print('act done')

        if Experiment.objects.all():
            print('experiments already loaded')
        else:
            print('loading experiments')
            for project in experiment_data:
                project_obj = get_project(project['project_name'])
                for exps in project['experiments']:
                    pre_existing_experiment = Experiment.objects.filter(experiment=exps)
                    if pre_existing_experiment:
                        project_obj.experiments.add(pre_existing_experiment[0])
                    else:
                        new_exp = Experiment(experiment=exps)
                        new_exp.save()
                        project_obj.experiments.add(new_exp)
            print('exp done')

        if Frequency.objects.all():
            print('frequency already loaded')
        else:
            print('loading frequency')
            for project in frequency_data:
                project_obj = get_project(project['project_name'])
                for freq in project['frequencies']:
                    pre_existing_frequency = Frequency.objects.filter(frequency=freq)
                    if pre_existing_frequency:
                        project_obj.frequencies.add(pre_existing_frequency[0])
                    else:
                        new_freq = Frequency(frequency=freq)
                        new_freq.save()
                        project_obj.frequencies.add(new_freq)
            print('freq done')

        if Keyword.objects.all():
            print('keyword already loaded')
        else:
            print('loading keyword')
            for project in keyword_data:
                project_obj = get_project(project['project_name'])
                for keyw in project['keywords']:
                    pre_existing_keyword = Keyword.objects.filter(keyword=keyw)
                    if pre_existing_keyword:
                        project_obj.keywords.add(pre_existing_keyword[0])
                    else:
                        new_keyw = Keyword(keyword=keyw)
                        new_keyw.save()
                        project_obj.keywords.add(new_keyw)
            print('key done')

        if Model.objects.all():
            print('model already loaded')
        else:
            print('loading model')
            for project in model_data:
                project_obj = get_project(project['project_name'])
                for mod in project['models']:
                    pre_existing_model = Model.objects.filter(model=mod)
                    if pre_existing_model:
                        project_obj.models.add(pre_existing_model[0])
                    else:
                        new_mod = Model(model=mod)
                        new_mod.save()
                        project_obj.models.add(new_mod)
            print('mod done')

        if Realm.objects.all():
            print('realm already loaded')
        else:
            print('loading realm')
            for project in realm_data:
                project_obj = get_project(project['project_name'])
                for realm in project['realms']:
                    pre_existing_realm = Realm.objects.filter(realm=realm)
                    if pre_existing_realm:
                        project_obj.realms.add(pre_existing_realm[0])
                    else:
                        new_realm = Realm(realm=realm)
                        new_realm.save()
                        project_obj.realms.add(new_realm)
            print('realm done')

        if Variable.objects.all():
            print('variable already loaded')
        else:
            print('loading variable')
            for project in variable_data:
                project_obj = get_project(project['project_name'])
                for var in project['variables']:
                    pre_existing_variable = Variable.objects.filter(variable=var)
                    if pre_existing_variable:
                        project_obj.variables.add(pre_existing_variable[0])
                    else:
                        new_var = Variable(variable=var)
                        new_var.save()
                        project_obj.variables.add(new_var)
            print('var done')

        if JournalOptions.objects.all():
            print('journal names already loaded')
        else:
            print('loading journal names')
            for jour in journal_names:
                new_jour = JournalOptions(journal_name=jour)
                new_jour.save()
            print('journal names done')

        print('all done')
