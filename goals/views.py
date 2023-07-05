from django.db import transaction
from rest_framework import permissions
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from goals.permissions import BoardPermissions, GoalCategoryPermissions, CommentPermissions
from goals.serializers import (
    GoalCreateSerializer,
    GoalCategorySerializer,
    GoalSerializer,
    CommentSerializer,
    GoalCategoryCreateSerializer, BoardSerializer, BoarWithParticipantsSerializer, CommentWithUserSerializer,
)


# GoalCategory

class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.filter(board__participants__user=self.request.user). \
            exclude(is_deleted=True)


class GoalCategoryDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermissions]

    def get_queryset(self):
        return GoalCategory.objects.exclude(is_deleted=True)

    def perform_destroy(self, instance: GoalCategory) -> None:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted'])
            instance.goal_set.update(status=Goal.Status.archived)


# Goal

class GoalCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ["title", "created"]
    search_fields = ["title", "description"]
    ordering = ["title"]

    def get_queryset(self):
        return Goal.objects.filter(
            category__board__participants__user=self.request.user).exclude(status=Goal.Status.archived)


class GoalListDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.exclude(status=Goal.Status.archived)

    def perform_destroy(self, instance: Goal) -> None:
        instance.status = Goal.Status.archived
        instance.save(update_fields=['status'])


# Comment

class CommentCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer


class CommentListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentWithUserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(
            goal__category__board__participants__user=self.request.user)


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [CommentPermissions]
    serializer_class = CommentWithUserSerializer

    def get_queryset(self):
        return GoalComment.objects.select_related("user").filter(
            goal__category__board__participants__user=self.request.user)


# Board

class BoardDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [BoardPermissions]
    serializer_class = BoarWithParticipantsSerializer
    queryset = Board.objects.prefetch_related('participants__user').exclude(is_deleted=True)

    def perform_destroy(self, instance: Board) -> None:
        # При удалении доски помечаем ее как is_deleted,
        # «удаляем» категории, обновляем статус целей
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )


class BordListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ["title", ]

    def get_queryset(self):
        return Board.objects.filter(participants__user=self.request.user).exclude(is_deleted=True)


class BoardCreateView(CreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: BoardSerializer) -> None:
        board = serializer.save()
        BoardParticipant.objects.create(user=self.request.user, board=board, role=BoardParticipant.Role.owner)
