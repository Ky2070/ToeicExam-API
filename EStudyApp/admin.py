from django.contrib import admin
from EStudyApp.models import (PartDescription, Part,
                              QuestionSet, Question, PartQuestionSet,
                              Test, Course, Lesson, History, Tag, QuestionType)


# Định nghĩa lớp ModelAdmin để thêm phân trang
class QuestionTypeAdmin(admin.ModelAdmin):
    list_per_page = 20  # Hiển thị 20 bản ghi trên mỗi trang


class TagAdmin(admin.ModelAdmin):
    list_per_page = 10  # Hiển thị 20 bản ghi trên mỗi trang


class TestAdmin(admin.ModelAdmin):
    list_per_page = 20  # Hiển thị 20 bản ghi trên mỗi trang


class PartDescriptionAdmin(admin.ModelAdmin):
    list_per_page = 20


class PartAdmin(admin.ModelAdmin):
    list_per_page = 20


class QuestionSetAdmin(admin.ModelAdmin):
    list_per_page = 20


class QuestionAdmin(admin.ModelAdmin):
    list_per_page = 20


class PartQuestionSetAdmin(admin.ModelAdmin):
    list_per_page = 20


class CourseAdmin(admin.ModelAdmin):
    list_per_page = 20


class LessonAdmin(admin.ModelAdmin):
    list_per_page = 20


class HistoryAdmin(admin.ModelAdmin):
    list_per_page = 20


# Đăng ký các mô hình với phân trang
admin.site.register(Tag, TagAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(PartDescription, PartDescriptionAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(QuestionSet, QuestionSetAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(PartQuestionSet, PartQuestionSetAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(QuestionType, QuestionTypeAdmin)
