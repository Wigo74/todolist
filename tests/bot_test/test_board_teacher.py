from unittest.mock import patch
import pytest
from django.urls import reverse
from rest_framework import status
from bot.tg.client import TgClient


@pytest.mark.django_db
class TestTgUser:
    url: str = reverse('verify_bot')

    def test_invalid_verification_code(self, auth_client, tg_user, faker):
        payload = {'verification_code': faker.pystr()}

        with patch.object(TgClient, 'send_message') as send_message_mock:
            response = auth_client.patch(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        tg_user.refresh_from_db()
        assert tg_user.user is None
        send_message_mock.assert_not_called()

    def test_valid_verification_code(self, auth_client, tg_user, user):
        payload = {'verification_code': tg_user.verification_code}

        with patch.object(TgClient, 'send_message') as send_message_mock:
            response = auth_client.patch(self.url, payload)

        assert response.status_code == status.HTTP_200_OK
        tg_user.refresh_from_db()
        assert tg_user.user == user
        send_message_mock.assert_called_once_with(tg_user.chat_id, 'You have been successfully verified')
