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
from mengenali.views import download, transform, extract_upload, get_probabilities_result, custom, align, extract_tps, \
    get_probabilities_result_parsable, extract_roi, download_original
from django.http import HttpResponseRedirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda x: HttpResponseRedirect("/static/index.html")),
    path('download/<int:kelurahan>/<int:tps>/<str:filename>', download),
    path('downloadOriginal/<int:kelurahan>/<int:tps>', download_original),
    path('roi/<int:kelurahan>/<int:tps>/<str:filename>', extract_roi),

    path('align/<int:kelurahan>/<int:tps>/<str:filename>', align),
    path('extract/<int:kelurahan>/<int:tps>/<str:filename>', extract_tps),
    path('transform.wsgi', transform),
    path('custom.wsgi', custom),
    path('processprobs', get_probabilities_result_parsable),
    path('processprobs.wsgi', get_probabilities_result),
    path('extract.wsgi', extract_upload)
]