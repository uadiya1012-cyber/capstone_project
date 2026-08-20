from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from category.models import Category

User = get_user_model()

class CategoryPrivacyTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='Password123!', is_active=True
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='Password123!', is_active=True
        )
        self.global_cat = Category.objects.create(name='Global Food', user=None, is_income=False)
        self.user1_cat = Category.objects.create(name='User1 Food', user=self.user1, is_income=False)

    def test_global_category_visible_to_all(self):
        """Global categories should be visible in the list view."""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('category:category_list'))
        self.assertContains(response, 'Global Food')

    def test_other_user_category_hidden(self):
        """A user should not see other users' private categories in the list."""
        self.client.force_login(self.user2)
        response = self.client.get(reverse('category:category_list'))
        self.assertNotContains(response, 'User1 Food')

    def test_edit_global_category_forbidden_for_user(self):
        """Regular users cannot edit global categories."""
        self.client.force_login(self.user1)
        url = reverse('category:edit', kwargs={'pk': self.global_cat.pk})
        response = self.client.post(url, {'name': 'New Global Name'})
        self.assertRedirects(response, reverse('category:category_list'))
        self.global_cat.refresh_from_db()
        self.assertEqual(self.global_cat.name, 'Global Food')

    def test_delete_global_category_forbidden_for_user(self):
        """Regular users cannot delete global categories."""
        self.client.force_login(self.user1)
        url = reverse('category:delete', kwargs={'pk': self.global_cat.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('category:category_list'))
        self.assertTrue(Category.objects.filter(pk=self.global_cat.pk).exists())

    def test_user_can_delete_own_category(self):
        """Users can delete their own private categories."""
        self.client.force_login(self.user1)
        url = reverse('category:delete', kwargs={'pk': self.user1_cat.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('category:category_list'))
        self.assertFalse(Category.objects.filter(pk=self.user1_cat.pk).exists())
