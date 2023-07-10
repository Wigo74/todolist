from typing import Dict, Union

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models import Goal, BoardParticipant
from tests.factories import BoardFactory, BoardParticipantFactory, CategoryFactory, CreateGoalRequest


@pytest.mark.django_db
class TestGoalCreateView:
    """ Тесты для Goal создать представление """
    url: str = reverse('create-goal')

    def test_goal_create_owner_moderator(self, auth_client, user, due_date) -> None:
        """
        Тест, чтобы проверить, может ли новая цель быть
        успешно создана, когда пользователь является владельцем
        или модератором доски.
        """
        board = BoardFactory()
        category = CategoryFactory(board=board)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response: Response = auth_client.post(self.url, data=create_data)
        created_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED, "Цель не создалась"
        assert created_goal, "Созданной цели не существует"

    def test_goal_create_deleted_category(self, auth_client, user, due_date) -> None:
        """
        Тест, чтобы проверить, нельзя ли создать новую цель в удаленной категории
        """
        board = BoardFactory()
        category = CategoryFactory(board=board, is_deleted=True)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response = auth_client.post(self.url, data=create_data)
        unexpected_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Отказ в доступе не предоставлен"
        # assert response.json() == {'category': ['Не разрешено в удаленной категории']}
        assert not unexpected_goal, "Цель создана"

    def test_goal_create_deny(self, client) -> None:
        """
        Проверка того, что не аутентифицированные пользователи
        не могут получить доступ к конечной точке API создания цели.
        """
        response: Response = client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN, "Отказ в доступе не предоставлен"

    def test_failed_to_create_board_if_not_participant(self, auth_client, goal_category, faker):
        """
        Проверка того, что читатель не может создать цель на доске (если он не владелец)
        """
        data = {'category': goal_category.id, 'data': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_failed_to_create_board_if_reader(self, auth_client, board_participant, goal_category, faker):
        """
        Проверка того, что участник(читатель) не может создать цель на доске
        """
        board_participant.role = BoardParticipant.Role.reader
        board_participant.save(update_fields=['role'])

        data = {'category': goal_category.id, 'data': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'You do not have permission to perform this action.'}

    @pytest.mark.parametrize(
        'role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_have_to_create_to_with_role_owner_or_writer(
            self, auth_client, board_participant, goal_category, faker, role
    ):
        """
        Проверка того, что 'owner', 'writer' могут создать цель на доске
        """
        board_participant.role = role
        board_participant.save(update_fields=['role'])

        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures('board_participant')
    def test_create_goal_on_deleted_category(self, auth_client, goal_category, board_participant):
        """
         Тест на удаленною категорию
        """
        goal_category.is_deleted = True
        goal_category.save(update_fields=['is_deleted'])
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
