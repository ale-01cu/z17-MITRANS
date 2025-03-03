from django.contrib import admin
from apps.comment.models import Comment


# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'created_at')
    search_fields = ('text', 'user__username')
    list_filter = ('created_at',)


admin.site.register(Comment, CommentAdmin)
