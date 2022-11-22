from django.shortcuts import render
from django.views import generic
from scraping.models import Data


class HomePageView(generic.ListView):
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Data.objects.all()
