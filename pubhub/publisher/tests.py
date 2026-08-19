from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="logout-test",
            password="test-password",
        )
        self.client.force_login(self.user)

    def test_logout_rejects_get(self):
        response = self.client.get(reverse("logout"), secure=True)

        self.assertEqual(response.status_code, 405)

    def test_logout_accepts_post_and_redirects_to_login(self):
        response = self.client.post(reverse("logout"), secure=True)

        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)
