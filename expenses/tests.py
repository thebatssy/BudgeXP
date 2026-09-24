from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Expense, Budget


class ExpenseTrackerAPITests(APITestCase):

    def setUp(self):
        # Base user credentials
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "StrongPass123!"

        # Create primary test user
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

        # Create a second user for data isolation tests
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password=self.password
        )

        # API Endpoints
        self.register_url = reverse('register')
        self.token_obtain_url = reverse('token_obtain_pair')
        self.expense_list_url = reverse('expense-list')
        self.budget_list_url = reverse('budget-list')
        self.summary_url = reverse('budget_summary')

        # Obtain JWT Access Token for primary user
        response = self.client.post(self.token_obtain_url, {
            'username': self.username,
            'password': self.password
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    # ==========================================
    # 1. AUTHENTICATION TESTS
    # ==========================================

    def test_user_registration_success(self):
        """Test registering a new user with valid credentials."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], 'newuser')

    def test_jwt_login_success(self):
        """Test logging in returns access and refresh JWT tokens."""
        response = self.client.post(self.token_obtain_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    # ==========================================
    # 2. EXPENSE CRUD & PAGINATION TESTS
    # ==========================================

    def test_create_expense_authenticated(self):
        """Test creating an expense for authenticated user."""
        data = {
            'amount': '150.75',
            'category': 'FOOD',
            'date': '2026-09-10',
            'note': 'Weekly grocieries'
        }
        response = self.client.post(self.expense_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.get().user, self.user)

    def test_unauthenticated_expense_access_denied(self):
        """Test unauthenticated users cannot access expense list."""
        self.client.credentials()  # Clear auth headers
        response = self.client.get(self.expense_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_access_others_expenses(self):
        """Test users only receive their own expenses in queries."""
        # Create expense for other user
        Expense.objects.create(
            user=self.other_user,
            amount=Decimal('50.00'),
            category='UTILITIES',
            date='2026-09-01'
        )
        response = self.client.get(self.expense_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_expense_list_pagination(self):
        """Test global pagination returns 10 expenses per page."""
        for i in range(12):
            Expense.objects.create(
                user=self.user,
                amount=Decimal('10.00'),
                category='FOOD',
                date='2026-09-01'
            )
        response = self.client.get(self.expense_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 12)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])

    # ==========================================
    # 3. BUDGET VALIDATION TESTS
    # ==========================================

    def test_budget_creation_valid(self):
        """Test budget creation with valid month, year, and limit."""
        data = {
            'monthly_limit': '500.00',
            'month': 9,
            'year': 2026
        }
        response = self.client.post(self.budget_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_budget_custom_serializer_validation_errors(self):
        """Test custom error messages for invalid month, year, and limit."""
        invalid_data = {
            'monthly_limit': '-100.00',
            'month': 15,
            'year': 1999
        }
        response = self.client.post(self.budget_list_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Monthly budget limit must be greater than 0.', str(response.data['monthly_limit']))
        self.assertIn('Month must be an integer between 1 and 12.', str(response.data['month']))
        self.assertIn('Year must be between 2000 and 2100.', str(response.data['year']))

    def test_budget_unpaginated_response(self):
        """Verify BudgetViewSet disables pagination to return a flat list."""
        Budget.objects.create(user=self.user, monthly_limit=Decimal('200.00'), month=9, year=2026)
        response = self.client.get(self.budget_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)  # Direct list, not paginated object

    # ==========================================
    # 4. BUDGET SUMMARY ANALYTICS TESTS
    # ==========================================

    def test_budget_summary_calculation(self):
        """Test budget summary totals expenses and calculates budget status accurately."""
        # Setup Budget limit $500 for Sept 2026
        Budget.objects.create(user=self.user, monthly_limit=Decimal('500.00'), month=9, year=2026)

        # Add 2 Expenses totaling $520.50
        Expense.objects.create(user=self.user, amount=Decimal('200.00'), category='FOOD', date='2026-09-05')
        Expense.objects.create(user=self.user, amount=Decimal('320.50'), category='UTILITIES', date='2026-09-12')

        response = self.client.get(f"{self.summary_url}?month=9&year=2026")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['monthly_limit'], 500.0)
        self.assertEqual(response.data['total_expenses'], 520.5)
        self.assertEqual(response.data['remaining_budget'], -20.5)
        self.assertTrue(response.data['is_over_budget'])