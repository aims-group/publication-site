from django.conf.urls import include, url
from django.contrib import admin
from publisher.forms import RegistrationViewUniqueEmail


urlpatterns = [
    url(r'^', include('publisher.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/register/$', RegistrationViewUniqueEmail.as_view()),
    url(r'^accounts/', include('registration.backends.simple.urls')),
]
