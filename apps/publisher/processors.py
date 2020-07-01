from publisher.models import Project, PendingDoi
from django.conf import settings

def site_url(request):
    if hasattr(settings, 'SITE_ROOT'):
        return { 'site_root': settings.SITE_ROOT }
    else:
        return { 'site_root': '/' }

def nav_options(request):
    return {'nav_options': Project.objects.all().order_by("project")}

def pending_dois(request):
    try:
        if request.user.is_anonymous:
            return {}
        pending_count = PendingDoi.objects.filter(user=request.user).count()
        if pending_count > 0:
            return {'dois_pending': True, "dois_pending_count": pending_count}
        return {}
    except Exception as e:
        print(e)
        return {}