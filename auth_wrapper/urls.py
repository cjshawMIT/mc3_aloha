from django.conf.urls import patterns, include, url
from django.views import generic
from django.http import HttpResponseRedirect


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', lambda x: HttpResponseRedirect('/vcb/')),
    # url(r'^video_search/', include('video_search.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('aloha.urls', namespace='aloha')),
    # url(r'^vcb/', include('vcb.urls', namespace="vcb")),
)
