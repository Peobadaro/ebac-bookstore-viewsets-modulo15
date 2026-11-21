from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Category


class CategoryViewSetTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            title="Tecnologia", slug="tecnologia", description="Livros de tecnologia"
        )
        self.list_url = reverse("category-list", kwargs={"version": "v1"})
        self.detail_url = reverse(
            "category-detail", kwargs={"version": "v1", "pk": self.category.id}
        )

    def test_list_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Tecnologia")

    def test_retrieve_category(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "tecnologia")

    def test_create_category(self):
        data = {"title": "Romance", "slug": "romance"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(slug="romance").exists())

    def test_create_category_with_invalid_data(self):
        response = self.client.post(self.list_url, {"title": "Sem slug"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("slug", response.data)

    def test_update_category(self):
        response = self.client.patch(self.detail_url, {"active": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertFalse(self.category.active)

    def test_delete_category(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.exists())

    def test_retrieve_nonexistent_category(self):
        url = reverse("category-detail", kwargs={"version": "v1", "pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
