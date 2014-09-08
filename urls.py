from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.http import HttpResponseRedirect

admin.autodiscover()
from mengenali.views import download, transform, extract, get_probabilities_result

urlpatterns = patterns('',
                       url(r'^$', lambda x: HttpResponseRedirect("/static/index.html")),

                       # Examples:
                       url(r'^download.wsgi', download),
                       url(r'^transform.wsgi', transform),
                       url(r'^processprobs.wsgi', get_probabilities_result),
                       url(r'^extract.wsgi', extract),

                       url(r'^admin/', include(admin.site.urls)),
)
