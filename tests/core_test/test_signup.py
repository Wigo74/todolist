import faker
import pytest
from django.urls import reverse
from rest_framework import status

from core.models import User
from tests.factories import SignUpRequest


@pytest.mark.django_db
class TestSignUpView:
    url = reverse('signup')

    def test_user_created(self, client):
        data = SignUpRequest.build()
        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get()
        assert response.json() == self._serialize_response(user)
        assert user.check_password(data['password'])

    @pytest.mark.parametrize(
        'password', ['123456', 'q1w2e3', '123456qwerty'], ids=['only numbers', 'too short', 'too common']
    )
    def test_password_too_weak(self, client, password):
        data = {
            'password': password,
            'password_repeat': password,
        }
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_passwords_missmatch(self, client, faker):
        data = SignUpRequest.build(password_repeat=faker.password())
        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': ['password and password_repeat is not equal']}

    @staticmethod
    def _serialize_response(user: User, **kwargs) -> dict:
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        data |= kwargs
        return data

    def test_user_already_exists(self, client, user):
        data = SignUpRequest.build(username=user.username)
        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'username': ['A user with that username already exists.']}
