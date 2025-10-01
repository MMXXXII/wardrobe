from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views import View
from wardrobe.models import Item
from django.views.generic import TemplateView 
from typing import Any
# Create your views here.

class ShowItemView(TemplateView):
    template_name = "wardrobe/show_wardrobe.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
            context = super().get_context_data(**kwargs)
            context['wardrobe'] = Item.objects.all()

            return context