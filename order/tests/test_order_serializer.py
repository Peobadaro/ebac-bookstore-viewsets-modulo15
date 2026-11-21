from django.contrib.auth.models import User
from django.test import TestCase

from order.models import Order
from order.serializers import OrderSerializer
from product.models import Category, Product


class OrderSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="pedro", password="senha-teste-123")
        category = Category.objects.create(title="Tecnologia", slug="tecnologia")
        self.product_1 = Product.objects.create(title="Django", price=100)
        self.product_2 = Product.objects.create(title="Python", price=50)
        self.product_1.category.set([category])
        self.valid_data = {
            "user": self.user.id,
            "products_id": [self.product_1.id, self.product_2.id],
        }

    def test_serializer_accepts_valid_data(self):
        serializer = OrderSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_user(self):
        data = {**self.valid_data}
        data.pop("user")
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)

    def test_serializer_requires_products(self):
        data = {**self.valid_data}
        data.pop("products_id")
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("products_id", serializer.errors)

    def test_serializer_rejects_empty_product_list(self):
        serializer = OrderSerializer(data={**self.valid_data, "products_id": []})
        self.assertFalse(serializer.is_valid())
        self.assertIn("products_id", serializer.errors)

    def test_serializer_rejects_nonexistent_user(self):
        serializer = OrderSerializer(data={**self.valid_data, "user": 9999})
        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)

    def test_serializer_rejects_nonexistent_product(self):
        serializer = OrderSerializer(data={**self.valid_data, "products_id": [9999]})
        self.assertFalse(serializer.is_valid())
        self.assertIn("products_id", serializer.errors)

    def test_serializer_creates_order(self):
        serializer = OrderSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.product.count(), 2)

    def test_serializer_returns_expected_fields_and_total(self):
        order = Order.objects.create(user=self.user)
        order.product.set([self.product_1, self.product_2])
        data = OrderSerializer(order).data
        self.assertEqual(set(data.keys()), {"id", "user", "product", "total"})
        self.assertEqual(data["user"], self.user.id)
        self.assertEqual(data["total"], 150)

    def test_products_and_categories_are_nested_in_order(self):
        order = Order.objects.create(user=self.user)
        order.product.set([self.product_1])
        data = OrderSerializer(order).data
        self.assertEqual(data["product"][0]["title"], "Django")
        self.assertEqual(data["product"][0]["category"][0]["slug"], "tecnologia")
