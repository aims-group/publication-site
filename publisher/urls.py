from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.view, name='search'),
    re_path(r'^review', views.review, name='review'),
    path('advanced_search', views.advanced_search, name='advanced_search'),
    path('new', views.new, name='new'),
    re_path(r'^(?:edit/|process_dois/)?finddoi$', views.finddoi),
    re_path(r'^edit/(\d+)', views.edit, name='edit'),
    re_path(r'^view/(?P<project_name>[a-zA-Z0-9]*)/$', views.view, name='view'),
    re_path(r'^add_dois/', views.add_dois, name='add_dois'),
    re_path(r'^process_dois/', views.process_dois, name='process_dois'),
    re_path(r'^skip_doi/', views.skip_doi, name='skip_doi'),
    # url(r'^statistics/', views.statistics, name='statistics'),
    re_path(r'^(?:edit/|view/[a-zA-Z0-9]+/)?ajax/$', views.ajax),
    re_path(r'^(?:view/[a-zA-Z0-9]+/)?ajax/citation/(?P<pub_id>\d+)/$', views.ajax_citation),
    re_path(r'^(?:view/[a-zA-Z0-9]+/)?ajax/abstract/(?P<pub_id>\d+)/$', views.ajax_abstract),
    re_path(r'^(?:view/[a-zA-Z0-9]+/)?ajax/moreinfo/(?P<pub_id>\d+)/$', views.ajax_more_info),
    re_path(r'^(?:edit/)?ajax/data/prefetch_authors/$', views.ajax_prefetch_authors),
    re_path(r'^(?:edit/)?ajax/data/all_authors/$', views.ajax_all_authors),
]
