from django.test import TestCase

from product.models import Category, Product
from product.serializers import ProductSerializer


class ProductSerializerTest(TestCase):
    def setUp(self):
        self.category_1 = Category.objects.create(title="Tecnologia", slug="tecnologia")
        self.category_2 = Category.objects.create(title="Python", slug="python")
        self.valid_data = {
            "title": "Aprendendo Django",
            "description": "Livro sobre Django",
            "price": 120,
            "active": True,
            "categories_id": [self.category_1.id, self.category_2.id],
        }

    def test_serializer_accepts_valid_data(self):
        serializer = ProductSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_title(self):
        data = {**self.valid_data}
        data.pop("title")
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_serializer_rejects_zero_price(self):
        serializer = ProductSerializer(data={**self.valid_data, "price": 0})
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_serializer_rejects_negative_price(self):
        serializer = ProductSerializer(data={**self.valid_data, "price": -10})
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_serializer_rejects_text_price(self):
        serializer = ProductSerializer(data={**self.valid_data, "price": "caro"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_serializer_rejects_nonexistent_category(self):
        serializer = ProductSerializer(data={**self.valid_data, "categories_id": [9999]})
        self.assertFalse(serializer.is_valid())
        self.assertIn("categories_id", serializer.errors)

    def test_product_without_category_is_valid(self):
        data = {**self.valid_data}
        data.pop("categories_id")
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.category.count(), 0)

    def test_serializer_creates_product_with_categories(self):
        serializer = ProductSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(product.title, "Aprendendo Django")
        self.assertEqual(product.price, 120)
        self.assertEqual(
            set(product.category.values_list("id", flat=True)),
            {self.category_1.id, self.category_2.id},
        )

    def test_serializer_updates_product_categories(self):
        product = Product.objects.create(title="Livro", price=50)
        product.category.set([self.category_1])
        serializer = ProductSerializer(
            product, data={"price": 60, "categories_id": [self.category_2.id]}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.price, 60)
        self.assertEqual(list(product.category.all()), [self.category_2])

    def test_serializer_returns_expected_fields(self):
        product = Product.objects.create(title="Livro", price=50)
        data = ProductSerializer(product).data
        self.assertEqual(
            set(data.keys()), {"id", "title", "description", "price", "active", "category"}
        )
        self.assertNotIn("categories_id", data)

    def test_category_is_nested_in_product(self):
        product = Product.objects.create(title="Livro", price=50)
        product.category.set([self.category_1])
        data = ProductSerializer(product).data
        self.assertEqual(len(data["category"]), 1)
        self.assertEqual(data["category"][0]["title"], "Tecnologia")
        self.assertEqual(data["category"][0]["slug"], "tecnologia")
        self.assertEqual(
            set(data["category"][0].keys()), {"id", "title", "slug", "description", "active"}
        )
