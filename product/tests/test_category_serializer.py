from django.test import TestCase

from product.models import Category
from product.serializers import CategorySerializer


class CategorySerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "title": "Tecnologia",
            "slug": "tecnologia",
            "description": "Livros de tecnologia",
            "active": True,
        }

    def test_serializer_accepts_valid_data(self):
        serializer = CategorySerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_title(self):
        data = {**self.valid_data}
        data.pop("title")
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_serializer_requires_slug(self):
        data = {**self.valid_data}
        data.pop("slug")
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("slug", serializer.errors)

    def test_serializer_rejects_invalid_slug(self):
        serializer = CategorySerializer(data={**self.valid_data, "slug": "slug inválido!"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("slug", serializer.errors)

    def test_serializer_rejects_duplicated_slug(self):
        Category.objects.create(title="Outra", slug="tecnologia")
        serializer = CategorySerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("slug", serializer.errors)

    def test_serializer_rejects_title_too_long(self):
        serializer = CategorySerializer(data={**self.valid_data, "title": "a" * 101})
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_description_is_optional(self):
        data = {"title": "Romance", "slug": "romance"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_creates_category(self):
        serializer = CategorySerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(category.title, "Tecnologia")
        self.assertEqual(category.slug, "tecnologia")
        self.assertTrue(category.active)

    def test_serializer_returns_expected_fields(self):
        category = Category.objects.create(**self.valid_data)
        data = CategorySerializer(category).data
        self.assertEqual(set(data.keys()), {"id", "title", "slug", "description", "active"})
        self.assertEqual(data["title"], "Tecnologia")
