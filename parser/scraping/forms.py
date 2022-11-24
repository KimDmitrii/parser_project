from django import forms
from .models import Data


class CategoryForm(forms.Form):
    category_list = forms.ModelChoiceField(
        queryset=Data.objects.values('category').distinct()
    )

