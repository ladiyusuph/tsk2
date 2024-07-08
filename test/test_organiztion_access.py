from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import Organisation, CustomUser


class OrganisationAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            email="user1@example.com",
            password="password123",
            first_name="User",
            last_name="One",
        )
        self.user2 = CustomUser.objects.create_user(
            email="user2@example.com",
            password="password123",
            first_name="User",
            last_name="Two",
        )
        self.org1 = Organisation.objects.create(name="User One's Organisation")
        self.org1.users.add(self.user1)

    def test_user_cannot_access_other_users_organisation(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/organisations/{self.org1.pk}/")
        self.assertEqual(response.status_code, 404)
