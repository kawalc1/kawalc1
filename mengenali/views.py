# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from os import path
import registration
import extraction


from django.views.static import serve as static_serve
def index(request):
    #return render(request, 'index.html')
    return static_serve(request, 'index.html', '/home/sjappelodorus/verifikatorc1/static')


def handle_uploaded_file(f, filename):
    with open(path.join(settings.STATIC_DIR, 'upload/' + filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def extract(request):
    filename = request.GET.get("filename", "")
    output = extraction.extract(filename, settings.STATIC_DIR)
    return HttpResponse(output)

def transform(request):
    if request.method == 'POST':
        filename = request.POST.get("flowFilename", "")
        handle_uploaded_file(request.FILES['file'], filename)

        output = registration.processFile(None, 1, settings.STATIC_DIR, filename)
        #output = settings.STATIC_DIR + 'poop'
        return HttpResponse(output)
    else :
        return HttpResponseNotFound('<h1>Page not found</h1>')
