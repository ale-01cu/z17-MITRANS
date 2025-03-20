from django.contrib import admin
from .models import Source

# Register your models here.
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'description', 'created_at')
    search_fields = ('name', 'url', 'description')

admin.site.register(Source, SourceAdmin)
