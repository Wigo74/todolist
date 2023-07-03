from rest_framework import serializers
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(queryset=GoalCategory.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user",)
        fields = "__all__"


class GoalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCategorySerializer(serializers.ModelSerializer):
    """ Модель вывода объекта """
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")
