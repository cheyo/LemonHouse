from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_house.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'house.views.project_index', name='site_index'),
    #url(r'^.+', include('house.urls')),
    url(r'^house/$', 'house.views.project_index', name='project_index'),
    url(r'^house/search/$', 'house.views.project_search', name='project_search'),
    url(r'^house/(\d+)/$', 'house.views.project_detail', name='project_detail'),
    url(r'^house/(\d+)/(.+)/$', 'house.views.building_detail', name='building_detail'),
    url(r'^branch/(\d+)/$', 'house.views.branch_detail', name='branch_detail'),
    url(r'^company/$', 'house.views.company_index', name='company_index'),
    url(r'^company/search/$', 'house.views.company_search', name='company_search'),
    url(r'^company/(.+)/$', 'house.views.company_detail', name='company_detail'),
    url(r'^datastat/trend/$', 'house.views.datastat_trend_live', name='datastat_trend'),
    url(r'^datastat/trend/live/$', 'house.views.datastat_trend_live', name='datastat_trend_live'),
    url(r'^datastat/trend/all/$', 'house.views.datastat_trend_all', name='datastat_trend_all'),
    url(r'^datastat/trend/xml/live_count.xml$', 'house.views.trend_xml_live_count', name='trend_xml_live_count'),
    url(r'^datastat/trend/xml/live_size.xml$', 'house.views.trend_xml_live_size', name='trend_xml_live_size'),
    url(r'^datastat/trend/xml/all_count.xml$', 'house.views.trend_xml_all_count', name='trend_xml_all_count'),
    url(r'^datastat/trend/xml/all_size.xml$', 'house.views.trend_xml_all_size', name='trend_xml_all_size'),
    url(r'^datastat/companystat$', 'house.views.datastat_companystat', name='datastat_companystat'),
)


