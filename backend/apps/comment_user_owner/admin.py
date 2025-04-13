from django.contrib import admin
from .models import UserOwner

# Register your models here.

class UserOwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'created_at')
    readonly_fields = ('created_at',)
    list_per_page = 25

admin.site.register(UserOwner, UserOwnerAdmin)