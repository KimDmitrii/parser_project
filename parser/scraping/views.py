from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Data
from .forms import CategoryForm
# Create your views here.


def index(request):
    latest_data = Data.objects.values('category').distinct()
    context = {
        'latest_data': latest_data
    }
    return render(
        request,
        'scraping/index.html',
        context
    )


def listform(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
    else:
        form = CategoryForm()

    return render(
        request,
        'scraping/droplist.html',
        {'form': form}
    )

