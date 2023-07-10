from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.serializers import GoalCategorySerializer, BoardSerializer
from tests.factories import BoardFactory, CategoryFactory, BoardParticipantFactory


@pytest.mark.django_db
class TestCategoryListView:
    """Tests for GoalCategory list view"""

    url: str = reverse('category-list')

    def test_active_category_list_participant(self, auth_client, user) -> None:
        """
        Тест, чтобы убедиться, что аутентифицированный пользователь может
        получить список активных категорий, где пользователь является участником доски.
        """
        board = BoardFactory()
        active_categories = CategoryFactory.create_batch(size=5, board=board)
        BoardParticipantFactory(board=board, user=user)

        expected_response: Dict = GoalCategorySerializer(
            active_categories, many=True
        ).data
        sorted_expected_response: list = sorted(
            expected_response, key=lambda x: x["title"]
        )
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert response.json() == sorted_expected_response, "Списки категорий не совпадают"

    def test_deleted_category_list_participant(self, auth_client, user) -> None:
        """
        Тест, чтобы убедиться, что аутентифицированный пользователь не может
        получить список удаленных категорий, где пользователь является участником форума
        """
        board = BoardFactory()
        deleted_categories = CategoryFactory.create_batch(
            size=5, board=board, is_deleted=True
        )
        BoardParticipantFactory(board=board, user=user)

        unexpected_response: Dict = GoalCategorySerializer(
            deleted_categories, many=True
        ).data
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert not response.json() == unexpected_response, "Получены удаленные категории"

    def test_category_list_not_participant(self, auth_client) -> None:
        """
        Тест, чтобы убедиться, что аутентифицированный пользователь
        не может получить список категорий, где пользователь не является участником форума
        """
        board = BoardFactory()
        categories = CategoryFactory.create_batch(size=5, board=board)
        BoardParticipantFactory(board=board)

        unexpected_response: Dict = BoardSerializer(categories, many=True).data
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert not response.json() == unexpected_response, "Получены чужие категории"

    def test_category_create_deny(self, client) -> None:
        """
        Убедитесь, что пользователи, не прошедшие проверку подлинности,
        не могут получить доступ к конечной точке API создания категории.
        """
        response: Response = client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN, "Отказ в доступе не предоставлен"
