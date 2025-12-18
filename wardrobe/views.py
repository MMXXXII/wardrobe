from django.views.generic import TemplateView
from wardrobe.models import Category, Store, Product, Customer, Order

class ShowWardrobeView(TemplateView):
    template_name = "wardrobe/show_wardrobe.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["stores"] = Store.objects.all()
        context["products"] = Product.objects.all().select_related("category", "store")
        context["customers"] = Customer.objects.all().select_related("user", "store")
        context["orders"] = Order.objects.all().select_related("product", "customer", "user")
        return context