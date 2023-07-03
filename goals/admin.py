from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created", "updated", "is_deleted")
    search_fields = ("title", "user")


@admin.register(Goal)
class Goal(admin.ModelAdmin):
    list_display = ("id",
                    "title",
                    "created",
                    "updated",
                    "user",
                    "description",
                    "due_date",
                    "status",
                    "priority",
                    "category",)
    search_fields = ("title", "user")


@admin.register(GoalComment)
class GoalComment(admin.ModelAdmin):
    list_display = ("id", "user", "goal")
