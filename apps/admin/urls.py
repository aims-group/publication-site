"""pcmdi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from publisher.forms import LoginForm
from django.views.generic.edit import CreateView
from publisher.forms import RegisterForm

urlpatterns = [
    url(r'^', include('publisher.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'site/login.html', 'authentication_form': LoginForm}),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}),
    url('^register/', CreateView.as_view(template_name='site/registration.html', form_class=RegisterForm, success_url='/')),
]
