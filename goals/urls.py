from django.urls import path
from goals import views


urlpatterns = [
    path("goal_category/create", views.GoalCategoryCreateView.as_view()),
    path("goal_category/list", views.GoalCategoryListView.as_view()),
    path("goal_category/<pk>", views.GoalCategoryDetailView.as_view()),

    path("goal/create", views.GoalCreateView.as_view()),
    path("goal/list", views.GoalListView.as_view()),
    path("goal/<pk>", views.GoalListDetailView.as_view()),

    path("goal_comment/create", views.CommentCreateView.as_view()),
    path("goal_comment/list", views.CommentListView.as_view()),
    path("goal_comment/<pk>", views.CommentDetailView.as_view()),

    path("board/create", views.BoardCreateView.as_view()),
    path("board/list", views.BordListView.as_view()),
    path("board/<pk>", views.BoardDetailView.as_view()),
]


