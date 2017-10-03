from publisher.models import Project, PendingDoi

def nav_options(request):
    return {'nav_options': Project.objects.all().order_by("project")}

def pending_dois(request):
    try:
        if request.user.is_anonymous():
            return {}
        elif PendingDoi.objects.filter(user=request.user):
            return {'pending_dois_info': "You have DOIs pending submission. Click <a href='/process_dois'>here</a> to submit them."}
        return {}
    except Exception as e:
        print e
        return {}