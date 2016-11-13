# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader

def index(request):
    template = loader.get_template("../html/index.html")
    return HttpResponse(template.render())
