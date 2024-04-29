from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from publisher.forms import RegistrationViewUniqueEmail
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('accounts/logout/', logout_then_login),
    path('accounts/register/', RegistrationViewUniqueEmail.as_view(template_name="django_registration/registration_form.html"), name='register'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('publisher.urls'))
]
