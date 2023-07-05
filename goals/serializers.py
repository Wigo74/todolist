from rest_framework.request import Request
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from django.db import transaction
from core.models import User
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


# GoalCategory

class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, board: Board) -> Board:
        if board.is_deleted:
            raise serializers.ValidationError("board is deleted")
        if not BoardParticipant.objects.filter(
                board_id=board.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user).exists():
            raise PermissionDenied
        return board

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")


class GoalCategorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")


# Goal

class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise serializers.ValidationError("category not found")
        if not BoardParticipant.objects.filter(
                board_id=value.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user).exists():
            raise PermissionDenied
        return value


class GoalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted category")

        if value.user != self.context["request"].user:
            raise serializers.ValidationError("not owner of category")
        return value


# Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise serializers.ValidationError("Goal not found")
        if not BoardParticipant.objects.filter(
                board_id=value.category.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user).exists():
            raise PermissionDenied
        return value


class CommentWithUserSerializer(CommentSerializer):
    user = UserSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)


# Board

class BoardSerializer(serializers.ModelSerializer):
    """Сериализатор на создание доски и на лист"""

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        required=True, choices=BoardParticipant.editable_choices
    )
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    def validate_user(self, user: User) -> User:
        if self.context['request'].user == user:
            raise serializers.ValidationError('Failed to change your role')
        return user

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoarWithParticipantsSerializer(BoardSerializer):
    """Сериализатор на detailView"""
    participants = BoardParticipantSerializer(many=True)

    def update(self, instance: Board, validated_data: dict) -> Board:
        request: Request = self.context['request']
        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=request.user).delete()
            BoardParticipant.objects.bulk_create(
                [
                    BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                    for participant in validated_data.get('participants', [])
                ],
                ignore_conflicts=True,
            )
            if title := validated_data.get('title'):
                instance.title = title
            instance.save()
        return instance
