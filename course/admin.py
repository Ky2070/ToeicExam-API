from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django import forms
from course.models import Course, Lesson, ReviewLesson, Blog
from django.contrib.postgres.forms import SimpleArrayField

from course.models.blog import CommentBlog


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
            'fields': ('title', 'description', 'level', 'info', 'target', 'banner', 'cover')
        }),
        ('Time Information', {
            'fields': ('duration', 'created_at', 'updated_at')
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new course
            obj.user = request.user
        super().save_model(request, obj, form, change)


class LessonAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Lesson
        fields = '__all__'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ('title', 'course', 'created_at', 'updated_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Lesson Information', {
            'fields': ('course', 'title', 'video', 'content', 'quiz')
        }),
        ('Time Information', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        # You can customize save behavior here if needed
        super().save_model(request, obj, form, change)


class ReviewLessonAdminForm(forms.ModelForm):
    class Meta:
        model = ReviewLesson
        fields = '__all__'


@admin.register(ReviewLesson)
class ReviewLessonAdmin(admin.ModelAdmin):
    form = ReviewLessonAdminForm
    list_display = ('user', 'lesson', 'publish_date', 'created_at', 'updated_at')
    list_filter = ('publish_date', 'created_at')
    search_fields = ('content', 'lesson__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'publish_date')
    ordering = ('-publish_date',)

    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'lesson', 'content')
        }),
        ('Time Information', {
            'fields': ('publish_date', 'created_at', 'updated_at')
        }),
    )


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at', 'updated_at','deleted_at')
    list_filter = ('is_published', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Blog Information', {
            'fields': ('title', 'content', 'part_info', 'from_ques', 'to_ques', 'author', 'questions_set', 'is_published')
        }),
        ('Time Information', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CommentBlog)
class CommentBlogAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'publish_date', 'created_at', 'updated_at', 'deleted_at')
    list_filter = ('publish_date', 'created_at')
    search_fields = ('content', 'blog__title', 'user__username')
    readonly_fields = ('publish_date', 'created_at', 'updated_at')
    ordering = ('-publish_date',)

    fieldsets = (
        ('Comment Information', {
            'fields': ('user', 'blog', 'parent', 'content')
        }),
        ('Time Information', {
            'fields': ('publish_date', 'created_at', 'updated_at','deleted_at')
        }),
    )