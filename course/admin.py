from django.contrib import admin
from django import forms
from course.models import Course
from django.contrib.postgres.forms import SimpleArrayField

class CourseAdminForm(forms.ModelForm):
    info = SimpleArrayField(
        forms.CharField(),
        delimiter=',',
        required=False,
        help_text='Enter items separated by commas'
    )
    target = SimpleArrayField(
        forms.CharField(),
        delimiter=',',
        required=False,
        help_text='Enter items separated by commas'
    )

    class Meta:
        model = Course
        fields = '__all__'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ('title', 'level', 'user', 'created_at', 'updated_at')
    list_filter = ('level', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'description', 'level', 'info', 'target', 'banner')
        }),
        ('Time Information', {
            'fields': ('duration', 'created_at', 'updated_at')
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new course
            obj.user = request.user
        super().save_model(request, obj, form, change)