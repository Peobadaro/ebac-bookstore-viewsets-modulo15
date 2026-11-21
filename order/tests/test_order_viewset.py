from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from order.models import Order
from product.models import Product


class OrderViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="pedro", password="senha-teste-123")
        self.product_1 = Product.objects.create(title="Django", price=100)
        self.product_2 = Product.objects.create(title="Python", price=50)
        self.order = Order.objects.create(user=self.user)
        self.order.product.set([self.product_1])
        self.list_url = reverse("order-list", kwargs={"version": "v1"})
        self.detail_url = reverse("order-detail", kwargs={"version": "v1", "pk": self.order.id})

    def test_list_orders(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["product"][0]["title"], "Django")
        self.assertEqual(response.data[0]["total"], 100)

    def test_retrieve_order(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.id)

    def test_create_order(self):
        data = {"user": self.user.id, "products_id": [self.product_1.id, self.product_2.id]}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(response.data["total"], 150)

    def test_create_order_without_products(self):
        data = {"user": self.user.id, "products_id": []}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("products_id", response.data)

    def test_delete_order(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.exists())

    def test_retrieve_nonexistent_order(self):
        url = reverse("order-detail", kwargs={"version": "v1", "pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
