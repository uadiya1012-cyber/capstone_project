from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from category.models import Category
from expenses.models import Expense
from budget.models import Budget

class ExpenseTrackerAPITests(APITestCase):

    def setUp(self):
        # Create user A
        self.user_a = CustomUser.objects.create_user(
            username='user_a',
            email='usera@example.com',
            password='Password123!',
            currency='₮'
        )
        # Create user B
        self.user_b = CustomUser.objects.create_user(
            username='user_b',
            email='userb@example.com',
            password='Password123!',
            currency='₮'
        )

        # Create global and user custom categories
        self.global_category = Category.objects.create(name='Global Food', user=None, is_income=False)
        self.category_a = Category.objects.create(name='User A Private', user=self.user_a, is_income=False)
        self.category_b = Category.objects.create(name='User B Private', user=self.user_b, is_income=False)

    def test_user_registration(self):
        url = reverse('api-register')
        data = {
            'username': 'new_user',
            'email': 'newuser@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'new_user')

    def test_user_login(self):
        url = reverse('api-login')
        data = {
            'username': 'user_a',
            'password': 'Password123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'user_a')

    def test_category_list_isolation(self):
        # Authenticate User A
        self.client.force_authenticate(user=self.user_a)
        url = reverse('category-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see global category and User A category, but NOT User B category
        names = [cat['name'] for cat in response.data]
        self.assertIn('Global Food', names)
        self.assertIn('User A Private', names)
        self.assertNotIn('User B Private', names)

    def test_expense_crud_isolation(self):
        # Create an expense for User B
        expense_b = Expense.objects.create(
            user=self.user_b,
            amount=500.00,
            category=self.category_b,
            date='2026-06-29'
        )

        # Authenticate User A
        self.client.force_authenticate(user=self.user_a)
        
        # Test GET expenses (should NOT see User B's expense)
        url = reverse('expense-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # Test POST expense (success with global category)
        data = {
            'amount': '1500.00',
            'category': self.global_category.id,
            'date': '2026-06-29',
            'description': 'Lunch'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '1500.00')

        # Test POST expense with User B's category (should fail validation)
        data_invalid = {
            'amount': '1000.00',
            'category': self.category_b.id,
            'date': '2026-06-29'
        }
        response = self.client.post(url, data_invalid, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_stats(self):
        # Create some test expenses for User A
        Expense.objects.create(
            user=self.user_a,
            amount=100.00,
            category=self.category_a,
            date='2026-06-29'
        )
        
        self.client.force_authenticate(user=self.user_a)
        url = reverse('api-dashboard')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tx_count', response.data)
        self.assertEqual(response.data['total_tx_count'], 1)
