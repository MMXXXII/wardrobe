from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from wardrobe.models import Brand, Category, Item, Store, Purchase

# -------------------- Brand --------------------
class BrandViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.brand = Brand.objects.create(name="TestBrand", description="Desc")

    def test_get_list(self):
        response = self.client.get("/api/brands/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create(self):
        data = {"name": "NewBrand", "description": "NewDesc"}
        response = self.client.post("/api/brands/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Brand.objects.filter(name="NewBrand").exists())

    def test_update(self):
        data = {"name": "UpdatedBrand"}
        response = self.client.patch(f"/api/brands/{self.brand.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.brand.refresh_from_db()
        self.assertEqual(self.brand.name, "UpdatedBrand")

    def test_delete(self):
        response = self.client.delete(f"/api/brands/{self.brand.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Brand.objects.filter(id=self.brand.id).exists())


# -------------------- Category --------------------
class CategoryViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="TestCategory")

    def test_get_list(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create(self):
        data = {"name": "NewCategory"}
        response = self.client.post("/api/categories/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Category.objects.filter(name="NewCategory").exists())

    def test_update(self):
        data = {"name": "UpdatedCategory"}
        response = self.client.patch(f"/api/categories/{self.category.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "UpdatedCategory")

    def test_delete(self):
        response = self.client.delete(f"/api/categories/{self.category.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())


# -------------------- Item --------------------
class ItemViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.brand = Brand.objects.create(name="Brand1", description="Desc1")
        self.category = Category.objects.create(name="Cat1")
        self.item = Item.objects.create(name="Item1", color="Red", brand=self.brand, category=self.category)

    def test_get_list(self):
        response = self.client.get("/api/items/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create(self):
        data = {"name": "Item2", "color": "Blue", "brand": self.brand.id, "category": self.category.id}
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Item.objects.filter(name="Item2").exists())

    def test_update(self):
        data = {"name": "UpdatedItem"}
        response = self.client.patch(f"/api/items/{self.item.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "UpdatedItem")

    def test_delete(self):
        response = self.client.delete(f"/api/items/{self.item.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())


# -------------------- Store --------------------
class StoreViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(name="Store1", address="Address1")

    def test_get_list(self):
        response = self.client.get("/api/stores/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create(self):
        data = {"name": "Store2", "address": "Address2"}
        response = self.client.post("/api/stores/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Store.objects.filter(name="Store2").exists())

    def test_update(self):
        data = {"address": "NewAddress"}
        response = self.client.patch(f"/api/stores/{self.store.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.store.refresh_from_db()
        self.assertEqual(self.store.address, "NewAddress")

    def test_delete(self):
        response = self.client.delete(f"/api/stores/{self.store.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Store.objects.filter(id=self.store.id).exists())


# -------------------- Purchase --------------------
class PurchaseViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.brand = Brand.objects.create(name="BrandA", description="DescA")
        self.category = Category.objects.create(name="CatA")
        self.item = Item.objects.create(name="ItemA", color="Green", brand=self.brand, category=self.category)
        self.store = Store.objects.create(name="StoreA", address="AddressA")
        self.purchase = Purchase.objects.create(item=self.item, store=self.store, amount=5, date=timezone.now().date())

    def test_get_list(self):
        response = self.client.get("/api/purchases/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_create(self):
        data = {"item": self.item.id, "store": self.store.id, "amount": 10, "date": "2025-10-01"}
        response = self.client.post("/api/purchases/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Purchase.objects.filter(amount=10).exists())

    def test_update(self):
        data = {"amount": 20}
        response = self.client.patch(f"/api/purchases/{self.purchase.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.amount, 20)

    def test_delete(self):
        response = self.client.delete(f"/api/purchases/{self.purchase.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Purchase.objects.filter(id=self.purchase.id).exists())