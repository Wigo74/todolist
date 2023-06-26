from django.urls import path

from core import views

urlpatterns = [
    path("signup", views.SignupView.as_view(), name='signup'),
    path("login", views.LoginView.as_view(), name='login'),
    path("profile", views.ProfileView.as_view(), name='profile'),
    path("update_password", views.UpdatePasswordView.as_view(), name='update_password'),
]


# from django.urls import path
#
# from core.views import RegistrationView, LoginView, ProfileView, UpdatePasswordView
#
# urlpatterns = [
#     path('signup', RegistrationView.as_view(), name='signup'),
#     path('login', LoginView.as_view(), name='login'),
#     path('profile', ProfileView.as_view(), name='profile'),
#     path('update_password', UpdatePasswordView.as_view(), name='update_password'),
# ]