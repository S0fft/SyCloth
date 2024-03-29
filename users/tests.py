from datetime import timedelta
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from users.models import EmailVerification, User


class UserRegistrationViewTestCase(TestCase):

    def setUp(self) -> None:
        self.data: dict[str, str] = {
            'first_name': 'name', 'last_name': 'surname',
            'username': 'uname', 'email': 'email123.test@gmail.com',
            'password1': '654321qQ', 'password2': '654321qQ'
        }
        self.path: str = reverse('users:registration')

    def test_user_registration_get(self) -> None:
        response: str = self.client.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(response.context_data['title'], 'SyCloth - Registration')
        self.assertTemplateUsed(response, 'users/registration.html')

    # allauth.socialaccount.models.SocialApp.DoesNotExist
    def test_user_registration_post_success(self) -> None:
        username: str = self.data['username']
        self.assertFalse(User.objects.filter(username=username).exists())
        response: str = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=username).exists())

        email_verification = EmailVerification.objects.filter(user__username=username)
        self.assertTrue(email_verification.exists())
        self.assertEqual(
            email_verification.first().expiration.date(),
            (now() + timedelta(hours=48)).date()
        )

    def test_user_registration_post_error(self) -> None:
        User.objects.create(username=self.data['username'])
        response: str = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'A user with that username already exists.', html=True)
