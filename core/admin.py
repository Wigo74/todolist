from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    readonly_fields = ('last_login', 'date_joined')

    search_fields = ('username', 'email', 'first_name', 'last_name',)
    filter_horizontal = ()
    list_filter = ('is_staff', 'is_active', 'is_superuser', )
    list_per_page = 10
    list_max_show_all = 100
