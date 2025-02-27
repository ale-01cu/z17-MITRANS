from django.contrib import admin
from apps.user.models import UserAccount


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'is_staff',
        'is_superuser',
        'is_active',
        'last_login',
        'create_at'
    )
    list_display_links = (
        'id',
        'email',
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'create_at'
    )
    readonly_fields = ('create_at',)
    list_per_page = 25


admin.site.register(UserAccount, UserAdmin)
