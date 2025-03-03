from django.contrib import admin
from apps.post.models import Post


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'created_at')
    search_fields = ('content', 'user__username')
    list_filter = ('created_at',)


admin.site.register(Post, PostAdmin)
