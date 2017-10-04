from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.view, name='search'),
    url(r'^review', views.review, name='review'),
    url(r'^advanced_search$', views.advanced_search, name='advanced_search'),
    url(r'^new$', views.new, name='new'),
    url(r'^finddoi$', views.finddoi),
    url(r'^edit/(\d+)', views.edit, name='edit'),
    url(r'^view/(?P<project_name>[a-zA-Z0-9]*)/$', views.view, name='view'),
    url(r'^add_dois/', views.add_dois, name='add_dois'),
    url(r'^process_dois/', views.process_dois, name='process_dois'),
    # url(r'^statistics/', views.statistics, name='statistics'),
    url(r'^ajax/?$', views.ajax),
    url(r'^ajax/citation/(?P<pub_id>\d+)/$', views.ajax_citation),
    url(r'^ajax/abstract/(?P<pub_id>\d+)/$', views.ajax_abstract),
    url(r'^ajax/moreinfo/(?P<pub_id>\d+)/$', views.ajax_more_info),
    url(r'^ajax/data/prefetch_authors/$', views.ajax_prefetch_authors),
    url(r'^ajax/data/all_authors/$', views.ajax_all_authors),
]
