from publisher.models import Project

def nav_options(request):
    return {'nav_options': Project.objects.all().order_by("project")}
