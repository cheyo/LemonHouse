from django.conf.urls import patterns, url

from house import views

urlpatterns = patterns('',
    url(r'^$', views.project_index, name='project_index'),
    url(r'^project/$', views.project_index, name='project_index'),
    url(r'^house/(\d+)/$', views.project_detail, name='project_detail'),
    url(r'^branch/(\d+)/$', views.branch_detail, name='branch_detail'),
    url(r'^company/(.+)/$', views.company_detail, name='company_detail'),
)
