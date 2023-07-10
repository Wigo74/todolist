from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from core.models import User
from goals.models import Goal
from goals.serializers import GoalSerializer
from tests.factories import BoardFactory, CategoryFactory, BoardParticipantFactory, GoalFactory


@pytest.mark.django_db
class TestGoalListView:
    """ Тесты Goal список представления """

    url: str = reverse('goal-list')

    def test_active_goal_list_participant(self, auth_client, user) -> None:
        """
        Тест, чтобы убедиться, что аутентифицированный пользователь
        может получить список активных целей, где пользователь является участником доски.
        """
        board = BoardFactory()
        category = CategoryFactory(board=board)
        active_goals = GoalFactory.create_batch(size=5, category=category)
        BoardParticipantFactory(board=board, user=user)

        expected_response: Dict = GoalSerializer(active_goals, many=True).data
        sorted_expected_response: list = sorted(
            expected_response, key=lambda x: x["priority"]
        )
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_deleted_goal_list_participant(self, auth_client, user) -> None:
        """
        Тест, чтобы проверить, что аутентифицированный пользователь не может
        получить список удаленных целей, где пользователь является участником доски
        """
        board = BoardFactory()
        category = CategoryFactory(board=board)
        deleted_goals = GoalFactory.create_batch(
            size=5, category=category, status=Goal.Status.archived
        )
        BoardParticipantFactory(board=board, user=user)

        unexpected_response: Dict = GoalSerializer(deleted_goals, many=True).data
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    # def test_goal_list_not_participant(self, auth_client, user: User) -> None:
    #     """
    #     Тест, чтобы проверить, что аутентифицированный пользователь
    #     не может получить список целей, где пользователь не является участником доски
    #     """
    #     board = BoardFactory()
    #     category = CategoryFactory(board=board)
    #     goals = GoalFactory.create_batch(size=5, category=category)
    #     BoardParticipantFactory(board=board, user=user)
    #
    #     unexpected_response: Dict = GoalSerializer(goals, many=True).data
    #     response = auth_client.get(self.url)
    #
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json() == unexpected_response, "Получены чужие цели"

    def test_goal_create_deny(self, client) -> None:
        """
        Проверка того, что не аутентифицированные пользователи
        не могут получить доступ к конечной точке API создания цели.
        """
        response: Response = client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN, "Отказ в доступе не предоставлен"
