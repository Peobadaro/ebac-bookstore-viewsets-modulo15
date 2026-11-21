from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Category, Product


class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Tecnologia", slug="tecnologia")
        self.product = Product.objects.create(title="Aprendendo Django", price=120)
        self.product.category.set([self.category])
        self.list_url = reverse("product-list", kwargs={"version": "v1"})
        self.detail_url = reverse(
            "product-detail", kwargs={"version": "v1", "pk": self.product.id}
        )

    def test_list_products(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Aprendendo Django")
        self.assertEqual(response.data[0]["category"][0]["slug"], "tecnologia")

    def test_retrieve_product(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["price"], 120)

    def test_create_product(self):
        data = {"title": "Python Fluente", "price": 200, "categories_id": [self.category.id]}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(title="Python Fluente")
        self.assertEqual(product.price, 200)
        self.assertEqual(list(product.category.all()), [self.category])
        self.assertEqual(response.data["category"][0]["title"], "Tecnologia")

    def test_create_product_with_invalid_price(self):
        data = {"title": "Livro grátis", "price": 0}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_update_product(self):
        response = self.client.patch(self.detail_url, {"price": 150}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 150)

    def test_delete_product(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.exists())

    def test_retrieve_nonexistent_product(self):
        url = reverse("product-detail", kwargs={"version": "v1", "pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
