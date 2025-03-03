from django.contrib import admin
from apps.classification.models import Classification


# Register your models here.
class ClasificacionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


admin.site.register(Classification, ClasificacionAdmin)
