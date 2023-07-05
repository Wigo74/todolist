from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class ParticipantsInline(admin.TabularInline):
    model = BoardParticipant
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(role=BoardParticipant.Role.owner)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "participants_count", "is_deleted")
    list_display_links = ["title"]
    list_filter = ["is_deleted"]
    search_fields = ["title"]
    inlines = [ParticipantsInline]

    def participants_count(self, obj: Board) -> int:
        return obj.participants.exclude(role=BoardParticipant.Role.owner).count()


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
