from django.contrib import admin
from apps.user.models import UserAccount, Entity, FacebookPage


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'is_staff',
        'is_superuser',
        'is_active',
        'last_login',
        'created_at'
    )
    list_display_links = (
        'id',
        'email',
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'created_at'
    )
    readonly_fields = ('created_at',)
    list_per_page = 25


class EntityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'created_at'
    )
    list_display_links = (
        'id',
        'name',
    )
    search_fields = (
        'name',
        'created_at'
    )
    readonly_fields = ('created_at',)
    list_per_page = 25


class FacebookPageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'entity',
        'facebook_access_token',
        'facebook_page_id',
        'facebook_page_name',
        'created_at'
    )
    list_display_links = (
        'id',
        'entity',
    )
    search_fields = (
        'entity',
        'created_at'
    )
    readonly_fields = ('created_at',)
    list_per_page = 25


admin.site.register(Entity, EntityAdmin)
admin.site.register(FacebookPage, FacebookPageAdmin)
admin.site.register(UserAccount, UserAdmin)
