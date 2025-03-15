from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpass123")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="testuser@example.com", password="testpass123")

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass123")
        self.assertEqual(superuser.username, "admin")
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.check_password("adminpass123"))
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_no_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username="", email="admin@example.com", password="adminpass123")


class UserModelTests(TestCase):
    def test_user_str(self):
        user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpass123")
        self.assertEqual(str(user), "testuser")
