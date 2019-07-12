from django.conf.urls import include, url
from django.contrib import admin
from publisher.forms import RegistrationViewUniqueEmail
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/logout/$', logout_then_login),
    url(r'^accounts/register/$', RegistrationViewUniqueEmail.as_view(template_name="registration/registration_form.html")),
    url(r'^accounts/', include('django_registration.backends.one_step.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^', include('publisher.urls')),
]
