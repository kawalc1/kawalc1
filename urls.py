from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.http import HttpResponseRedirect
admin.autodiscover()
from mengenali.views import transform

urlpatterns = patterns('',
    url(r'^$', lambda x: HttpResponseRedirect("/static/index.html")),

    # Examples:
    # url(r'^$', 'django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^transform.wsgi', transform),
    #url(r'^transform.wsgi', 'mengenali.views.transform', name='transform'),

    url(r'^admin/', include(admin.site.urls)),
)
