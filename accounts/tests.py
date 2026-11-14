from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass1234",
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="testsuperuser",
            email="testsuperuser@example.com",
            password="testpass1234",
        )
        self.assertEqual(admin_user.username, "testsuperuser")
        self.assertEqual(admin_user.email, "testsuperuser@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class SignupPageTests(TestCase):
    def test_url_exists_at_correct_location_signupview(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_view_name(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_form(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser",
                "email": "testuser@email.com",
                "password1": "testpass123",
                "password2": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].username, "testuser")
        self.assertEqual(get_user_model().objects.all()[0].email, "testuser@email.com")


class LoginTests(TestCase):
    def test_login_page(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_user_can_login(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )

        login_successful = self.client.login(
            username="testuser",
            password="testpass123",
        )
        self.assertTrue(login_successful)
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_login_with_wrong_password(self):
        User = get_user_model()
        User.objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )

        login_successful = self.client.login(
            username="testuser",
            password="wrongpassword",
        )
        self.assertFalse(login_successful)
        self.assertNotIn("_auth_user_id", self.client.session)


class LogoutTests(TestCase):
    def test_user_can_logout(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        self.client.force_login(user)

        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
