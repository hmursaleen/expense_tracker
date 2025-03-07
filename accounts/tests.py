from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
#The APITestCase class provides a test client that supports JSON requests and simplifies testing of DRF endpoints.
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationLoginTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_user_data = {
            "username": "testuser",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }

    def test_registration_success(self):
        """
        Test that a user can register successfully with valid data.
        """
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Registration successfull.")
        # Verify that the user has been created in the database.
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")

    def test_registration_password_mismatch(self):
        """
        Test registration fails when password and confirmation do not match.
        """
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = "DifferentPass!"
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Expect an error regarding the password mismatch.
        self.assertIn('password', response.data)
        self.assertIn("didn't match", str(response.data['password']))

    def test_registration_missing_required_field(self):
        """
        Test registration fails when a required field (e.g., email) is missing.
        """
        invalid_data = self.valid_user_data.copy()
        invalid_data.pop('email')
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The response should indicate that the email field is required.
        self.assertIn('email', response.data)

    def test_login_success(self):
        """
        Test that a user can log in with correct credentials.
        """
        # First, register the user.
        self.client.post(self.register_url, self.valid_user_data, format='json')
        login_data = {
            "username": "testuser",
            "password": "StrongPass123!"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Login successful.")

    def test_login_invalid_credentials(self):
        """
        Test login fails when the wrong password is provided.
        """
        # Register the user.
        self.client.post(self.register_url, self.valid_user_data, format='json')
        invalid_login_data = {
            "username": "testuser",
            "password": "WrongPass!"
        }
        response = self.client.post(self.login_url, invalid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Expect an error message indicating invalid credentials.
        # Depending on your serializer, the error might be in 'non_field_errors' or a similar key.
        self.assertTrue(any("Wrong credentials." in str(error) for error in response.data.values()))

    def test_login_missing_fields(self):
        """
        Test that login fails if required fields (e.g., username) are missing.
        """
        incomplete_login_data = {
            "password": "StrongPass123!"
        }
        response = self.client.post(self.login_url, incomplete_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Expect the error to indicate that username is required.
        self.assertIn('username', response.data)
