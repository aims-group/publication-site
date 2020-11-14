from django.core.management import BaseCommand
from publisher.models import Experiment, Frequency, Project
from scripts.updated_values import replaced_frequencies, removed_frequencies


class Command(BaseCommand):
    help = "Update the values of project facets with new ones."

    def handle(self, *args, **options):

        # Frequencies
        print('replacing publication frequencies')
        for project_name, frequencies in replaced_frequencies.items():
            project = Project.objects.filter(project=project_name)[0]
            publications = Project.objects.get(project__iexact=project_name).publication_set
            for old_freq, new_freq in frequencies.items():
                # Add new frequency if not already in the table
                if not Frequency.objects.filter(frequency=new_freq).exists():
                    new_frequency = Frequency(frequency=new_freq)
                    new_frequency.save()
                # Add new frequency if not already in the project
                if not project.frequencies.filter(frequency=new_freq).exists():
                    project.frequencies.add(Frequency.objects.filter(frequency=new_freq)[0])
                # Replace old frequency in publications with new one
                if Frequency.objects.filter(frequency=old_freq).exists():
                    old_frequency = Frequency.objects.filter(frequency=old_freq)
                    for pub in publications.filter(frequency=old_frequency[0]):
                        pub.frequency.add(Frequency.objects.filter(frequency=new_freq)[0])
                        pub.frequency.filter(frequency=old_freq).delete()
        print('deleting old frequencies')
        # Remove old frequencies from table
        for old_freq in removed_frequencies:
            if Frequency.objects.filter(frequency=old_freq).exists():
                Frequency.objects.filter(frequency=old_freq).delete()
        print('frequencies done')