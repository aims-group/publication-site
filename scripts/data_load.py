from publisher.models import Experiment, Frequency, Keyword, Model, Variable, Journal_Options
from scripts.experiment import experiment_data
from scripts.frequency import frequency_data
from scripts.keyword import keyword_data
from scripts.model import model_data
from scripts.variable import variable_data
from scripts.journals import journal_names

def run_data_load():
    if Experiment.objects.all():
        print 'experiments already loaded'
    else:
        print 'loading experiments'
        for exps in experiment_data:
            new_exp = Experiment()
            new_exp.experiment = exps
            new_exp.save()
        print 'exp done'

    if Frequency.objects.all():
        print 'frequency already loaded'
    else:
        print 'loading frequency'
        for freq in frequency_data:
            new_freq = Frequency()
            new_freq.frequency = freq
            new_freq.save()
        print 'freq done'

    if Keyword.objects.all():
        print 'keyword already loaded'
    else:
        print 'loading keyword'
        for keyw in keyword_data:
            new_keyw = Keyword()
            new_keyw.keyword = keyw
            new_keyw.save()
        print 'key done'

    if Model.objects.all():
        print 'model already loaded'
    else:
        print 'loading model'
        for mod in model_data:
            new_mod = Model()
            new_mod.model = mod
            new_mod.save()
        print 'mod done'

    if Variable.objects.all():
        print 'variable already loaded'
    else:
        print 'loading variable'
        for var in variable_data:
            new_var = Variable()
            new_var.variable = var
            new_var.save()
        print 'var done'

    if Journal_Options.objects.all():
        print 'journal names already loaded'
    else:
        print 'loading journal names'
        for jour in journal_names:
            new_jour = Journal_Options()
            new_jour.journal = jour
            new_jour.save()
        print 'journal names done'

    print 'all done'