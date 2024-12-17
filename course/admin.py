from django.contrib import admin

# Register your models here.
# import course models
from course.models.course import Course
from course.models.lesson import Lesson
from course.models.blog import Blog

# Register models
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'level', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(Blog)