"""kawalc1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mengenali.views import download, transform, extract, get_probabilities_result, custom
from django.http import HttpResponseRedirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda x: HttpResponseRedirect("/static/index.html")),
    path('download.wsgi', download),
    path('transform.wsgi', transform),
    path('custom.wsgi', custom),
    path('processprobs.wsgi', get_probabilities_result),
    path('extract.wsgi', extract)
]