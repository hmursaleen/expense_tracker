from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from .models import Expense

User = get_user_model()

class ExpenseCRUDTests(APITestCase):
    def setUp(self):
        # Create two users for testing ownership
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!",
            email="testuser@example.com", first_name="Test", last_name="User"
        )
        self.user2 = User.objects.create_user(
            username="otheruser", password="OtherPass123!",
            email="other@example.com", first_name="Other", last_name="User"
        )
        # Authenticate as self.user
        self.client.force_authenticate(user=self.user) #use force_authenticate to simulate authenticated requests.
        # Base URL for listing/creating expenses
        self.expense_list_create_url = reverse('expense-list-create')
        # Set up sample expenses for self.user
        today = timezone.now().date()
        self.expense1 = Expense.objects.create(
            user=self.user, amount=10.00,
            date=today - timedelta(days=3),
            description="Expense 1", category="GROCERIES"
        )
        self.expense2 = Expense.objects.create(
            user=self.user, amount=20.00,
            date=today - timedelta(days=10),
            description="Expense 2", category="LEISURE"
        )
        self.expense3 = Expense.objects.create(
            user=self.user, amount=30.00,
            date=today - timedelta(days=40),
            description="Expense 3", category="UTILITIES"
        )
        self.expense4 = Expense.objects.create(
            user=self.user, amount=40.00,
            date=today - timedelta(days=100),
            description="Expense 4", category="ELECTRONICS"
        )
        # Create an expense for user2 to test ownership isolation
        self.expense_user2 = Expense.objects.create(
            user=self.user2, amount=50.00,
            date=today - timedelta(days=5),
            description="Other user's expense", category="CLOTHING"
        )

    def test_create_expense_success(self):
        """
        Test that an expense is created successfully.
        """
        data = {
            "amount": "25.50",
            "date": timezone.now().date().strftime("%Y-%m-%d"),
            "description": "New Expense",
            "category": "HEALTH"
        }
        response = self.client.post(self.expense_list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Now, self.user should have 5 expenses (4 from setUp + 1 new)
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 5)

    def test_list_expenses(self):
        """
        Test that listing expenses returns only those belonging to the authenticated user.
        """
        response = self.client.get(self.expense_list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.user has 4 expenses from setUp; ensure user2's expense is not included.
        self.assertEqual(len(response.data), 4)
        for expense in response.data:
            self.assertNotEqual(expense['description'], "Other user's expense")

    def test_filter_expenses_past_week(self):
        """
        Test filtering expenses for the past week.
        Only expenses with a date within the last 7 days should be returned.
        """
        response = self.client.get(self.expense_list_create_url + '?filter=past_week', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only expense1 (3 days ago) qualifies.
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], "Expense 1")

    def test_filter_expenses_past_month(self):
        """
        Test filtering expenses for the past month (last 30 days).
        """
        response = self.client.get(self.expense_list_create_url + '?filter=past_month', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expense1 (3 days ago) and expense2 (10 days ago) qualify; expense3 is 40 days ago.
        self.assertEqual(len(response.data), 2)
        descriptions = [expense['description'] for expense in response.data]
        self.assertIn("Expense 1", descriptions)
        self.assertIn("Expense 2", descriptions)

    def test_filter_expenses_last_3_months(self):
        """
        Test filtering expenses for the last 3 months (approx. 90 days).
        """
        response = self.client.get(self.expense_list_create_url + '?filter=last_3_months', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expense1, expense2, and expense3 should qualify; expense4 (100 days ago) does not.
        self.assertEqual(len(response.data), 3)
        descriptions = [expense['description'] for expense in response.data]
        self.assertIn("Expense 1", descriptions)
        self.assertIn("Expense 2", descriptions)
        self.assertIn("Expense 3", descriptions)

    def test_filter_expenses_custom_valid(self):
        """
        Test custom filtering with a valid date range.
        """
        today = timezone.now().date()
        # Define a custom date range that should include expense2 (10 days ago) and expense3 (40 days ago)
        start_date = (today - timedelta(days=45)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")
        url = f"{self.expense_list_create_url}?filter=custom&start_date={start_date}&end_date={end_date}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        descriptions = [expense['description'] for expense in response.data]
        self.assertIn("Expense 2", descriptions)
        self.assertIn("Expense 3", descriptions)

    def test_filter_expenses_custom_invalid_date(self):
        """
        Test custom filtering when invalid date formats are provided.
        The view should ignore filtering and return all expenses.
        """
        url = f"{self.expense_list_create_url}?filter=custom&start_date=invalid&end_date=invalid"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should return all 4 expenses (ignoring filtering due to invalid dates)
        self.assertEqual(len(response.data), 1)

    def test_get_single_expense(self):
        """
        Test retrieving a single expense detail.
        """
        expense_detail_url = reverse('expense-detail', kwargs={'pk': self.expense1.pk})
        response = self.client.get(expense_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], "Expense 1")
       

    def test_update_expense(self):
        """
        Test updating an existing expense record.
        """
        expense_detail_url = reverse('expense-detail', kwargs={'pk': self.expense1.pk})
        update_data = {
            "amount": "15.75",
            "date": self.expense1.date.strftime("%Y-%m-%d"),
            "description": "Updated Expense 1",
            "category": "LEISURE"
        }
        response = self.client.put(expense_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the expense was updated
        self.expense1.refresh_from_db()
        self.assertEqual(str(self.expense1.amount), "15.75")
        self.assertEqual(self.expense1.description, "Updated Expense 1")
        self.assertEqual(self.expense1.category, "LEISURE")

    def test_delete_expense(self):
        """
        Test deleting an expense record.
        """
        expense_detail_url = reverse('expense-detail', kwargs={'pk': self.expense1.pk})
        response = self.client.delete(expense_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Expense.objects.filter(pk=self.expense1.pk).exists())

    def test_access_expense_not_owned(self):
        """
        Test that a user cannot access an expense that does not belong to them.
        """
        expense_detail_url = reverse('expense-detail', kwargs={'pk': self.expense_user2.pk})
        response = self.client.get(expense_detail_url, format='json')
        # Should return 404 Not Found since self.user does not own this expense.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
