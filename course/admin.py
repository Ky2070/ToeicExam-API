from django.contrib import admin
from course.models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'user', 'created_at', 'updated_at')
    list_filter = ('level', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'description', 'level')
        }),
        ('Time Information', {
            'fields': ('duration', 'created_at', 'updated_at')
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new course
            obj.user = request.user
        super().save_model(request, obj, form, change)