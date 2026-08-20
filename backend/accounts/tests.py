from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.registration_pending_url = reverse('registration_pending')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_register_view_get(self):
        """register view rendering validation"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_creates_inactive_user_and_sends_email(self):
        """Valid registration creates inactive user and sends activation email"""
        response = self.client.post(self.register_url, self.user_data)
        
        # Should redirect to registration pending page
        self.assertRedirects(response, self.registration_pending_url)
        
        # User should be created in DB but is_active should be False
        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_active)
        self.assertEqual(user.email, 'testuser@example.com')
        
        # One email should be sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, 'Бүртгэлээ баталгаажуулна уу - Expense Tracker')
        self.assertIn('testuser@example.com', sent_email.to)
        
        # The email content should contain the activation link parts (uid and token)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.assertIn(uid, sent_email.body)

    def test_activate_user_with_valid_token(self):
        """User activates successfully with a valid token"""
        # Create an inactive user first
        user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='Password123!',
            is_active=False
        )
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        activate_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(activate_url)
        
        # Refresh user from database
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Should redirect to user dashboard
        self.assertRedirects(response, reverse('user_dashboard'))
        
        # User should be logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_activate_user_with_invalid_token(self):
        """Activation fails with an invalid token"""
        user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='Password123!',
            is_active=False
        )
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = 'invalid-token-123456'
        
        activate_url = reverse('activate', kwargs={'uidb64': uid, 'token': invalid_token})
        response = self.client.get(activate_url)
        
        # User should remain inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
        # Should render the activation failed page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/activation_failed.html')

    def test_activate_user_with_invalid_uid(self):
        """Activation fails with an invalid user ID"""
        user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='Password123!',
            is_active=False
        )
        
        # Use an invalid/non-existent base64 user ID
        invalid_uid = urlsafe_base64_encode(force_bytes(99999))
        token = default_token_generator.make_token(user)
        
        activate_url = reverse('activate', kwargs={'uidb64': invalid_uid, 'token': token})
        response = self.client.get(activate_url)
        
        # User should remain inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
        # Should render the activation failed page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/activation_failed.html')

    def test_common_expenses_loaded_on_dashboard(self):
        """Dashboard view correctly loads common expenses from database"""
        user = User.objects.create_user(
            username='dashboarduser',
            email='dash@example.com',
            password='Password123!',
            is_active=True
        )
        self.client.force_login(user)
        
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('common_expenses', response.context)
        
        # Verify that seeded common expenses (e.g. Talh) are in the queryset
        common_expenses = response.context['common_expenses']
        self.assertTrue(common_expenses.filter(name='Талх').exists())


class ProfileAndSpendingLimitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='Password123!',
            is_active=True
        )
        self.client.force_login(self.user)
        self.dashboard_url = reverse('user_dashboard')

    def test_profile_update(self):
        """Updating user profile values via POST works successfully"""
        post_data = {
            'update_profile': '',
            'prof-first_name': 'Дорж',
            'prof-last_name': 'Бат',
            'prof-phone_number': '99112233',
            'prof-currency': '$',
            'prof-daily_limit': '50000',
            'prof-monthly_savings_goal': '500000',
        }
        response = self.client.post(self.dashboard_url, post_data)
        self.assertRedirects(response, self.dashboard_url)

        # Verify updated in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Дорж')
        self.assertEqual(self.user.last_name, 'Бат')
        self.assertEqual(self.user.phone_number, '99112233')
        self.assertEqual(self.user.currency, '$')
        self.assertEqual(self.user.daily_limit, 50000)
        self.assertEqual(self.user.monthly_savings_goal, 500000)

    def test_daily_limit_exceeded_alert(self):
        """Alert is triggered when daily limit is set and daily expenses exceed it"""
        from expenses.models import Expense
        from category.models import Category
        import datetime

        # Set a daily limit of 20000
        self.user.daily_limit = 20000
        self.user.save()

        # Create category and add expense under limit
        cat = Category.objects.create(name='Food', user=self.user, is_income=False)
        Expense.objects.create(
            user=self.user,
            amount=15000,
            category=cat,
            date=datetime.date.today(),
            description='Lunch'
        )

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['daily_limit_exceeded'])

        # Add another expense that pushes total today over 20000
        Expense.objects.create(
            user=self.user,
            amount=10000,
            category=cat,
            date=datetime.date.today(),
            description='Coffee'
        )

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['daily_limit_exceeded'])
        self.assertContains(response, 'Өдрийн зардлын хязгаар хэтэрлээ')


class ExportAndCrudTests(TestCase):
    """Tests for CSV export, expense delete, and expense edit features."""

    def setUp(self):
        from expenses.models import Expense
        from category.models import Category
        import datetime

        self.user = User.objects.create_user(
            username='exportuser',
            email='export@example.com',
            password='Password123!',
            is_active=True,
            currency='₮'
        )
        self.client.force_login(self.user)

        self.cat = Category.objects.create(name='Transport', user=self.user, is_income=False)
        self.expense = Expense.objects.create(
            user=self.user,
            amount=5000,
            category=self.cat,
            date=datetime.date.today(),
            description='Такси'
        )

    def test_csv_export(self):
        """CSV export returns a downloadable CSV file with correct content."""
        response = self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        self.assertIn('attachment', response['Content-Disposition'])
        content = response.content.decode('utf-8-sig')
        self.assertIn('5000', content)

    def test_delete_expense(self):
        """Deleting an expense removes it from the database."""
        from expenses.models import Expense
        pk = self.expense.pk
        response = self.client.post(reverse('delete_expense', kwargs={'pk': pk}))
        self.assertRedirects(response, reverse('user_dashboard'))
        self.assertFalse(Expense.objects.filter(pk=pk).exists())

    def test_delete_expense_requires_post(self):
        """GET request to delete endpoint should return 405."""
        response = self.client.get(reverse('delete_expense', kwargs={'pk': self.expense.pk}))
        self.assertEqual(response.status_code, 405)

    def test_delete_other_users_expense_forbidden(self):
        """Users cannot delete expenses belonging to another user."""
        other_user = User.objects.create_user(
            username='otheruser', email='other@example.com',
            password='Password123!', is_active=True
        )
        from expenses.models import Expense
        import datetime
        other_expense = Expense.objects.create(
            user=other_user, amount=1000, date=datetime.date.today(), description='Other'
        )
        response = self.client.post(reverse('delete_expense', kwargs={'pk': other_expense.pk}))
        self.assertEqual(response.status_code, 404)

    def test_edit_expense_get_json(self):
        """GET request to edit endpoint returns expense data as JSON."""
        response = self.client.get(reverse('edit_expense', kwargs={'pk': self.expense.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['amount'], '5000.00')

    def test_edit_expense_post(self):
        """POST request to edit endpoint updates the expense."""
        import datetime
        post_data = {
            'edit-amount': '7500',
            'edit-category': self.cat.pk,
            'edit-description': 'Автобус',
            'edit-date': datetime.date.today().isoformat(),
        }
        response = self.client.post(
            reverse('edit_expense', kwargs={'pk': self.expense.pk}),
            post_data
        )
        self.assertRedirects(response, reverse('user_dashboard'))
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.amount, 7500)
        self.assertEqual(self.expense.description, 'Автобус')


class RecurringExpenseTests(TestCase):
    """Tests for recurring expense model fields and management command."""

    def setUp(self):
        from category.models import Category

        self.user = User.objects.create_user(
            username='recuruser', email='recur@example.com',
            password='Password123!', is_active=True
        )
        self.cat = Category.objects.create(name='Subscription', user=self.user, is_income=False)

    def test_create_recurring_expense_sets_next_date(self):
        """Creating a recurring expense via POST sets next_recurrence_date."""
        import datetime
        self.client.force_login(self.user)

        post_data = {
            'create_expense': '',
            'exp-amount': '10000',
            'exp-category': self.cat.pk,
            'exp-description': 'Netflix',
            'exp-date': datetime.date.today().isoformat(),
            'exp-is_recurring': 'on',
            'exp-recurring_interval': 'monthly',
        }
        response = self.client.post(reverse('user_dashboard'), post_data)
        self.assertRedirects(response, reverse('user_dashboard'))

        from expenses.models import Expense
        exp = Expense.objects.get(description='Netflix')
        self.assertTrue(exp.is_recurring)
        self.assertEqual(exp.recurring_interval, 'monthly')
        self.assertIsNotNone(exp.next_recurrence_date)

    def test_auto_recurring_management_command(self):
        """Management command creates new expense copies for due recurring expenses."""
        from expenses.models import Expense
        from django.core.management import call_command
        import datetime

        Expense.objects.create(
            user=self.user,
            amount=5000,
            category=self.cat,
            date=datetime.date.today() - datetime.timedelta(days=7),
            description='Weekly bus',
            is_recurring=True,
            recurring_interval='weekly',
            next_recurrence_date=datetime.date.today(),
        )

        self.assertEqual(Expense.objects.count(), 1)
        call_command('auto_recurring')
        self.assertEqual(Expense.objects.count(), 2)

        new_exp = Expense.objects.filter(description__startswith='[Автомат]').first()
        self.assertIsNotNone(new_exp)
        self.assertEqual(new_exp.amount, 5000)
        self.assertEqual(new_exp.date, datetime.date.today())
