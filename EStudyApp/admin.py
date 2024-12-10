import csv
from django.contrib.admin import SimpleListFilter
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from EStudyApp.models import (PartDescription, Part,
                              QuestionSet, Question, PartQuestionSet,
                              Test, Course, Lesson, History, Tag, QuestionType)


# Định nghĩa lớp ModelAdmin để thêm phân trang
class QuestionTypeAdmin(admin.ModelAdmin):
    list_per_page = 20  # Hiển thị 20 bản ghi trên mỗi trang


class TagAdmin(admin.ModelAdmin):
    list_per_page = 10  # Hiển thị 20 bản ghi trên mỗi trang

# Tạo bộ lọc tùy chỉnh khác nếu cần (ví dụ: "status")

# Tạo bộ lọc tùy chỉnh cho trường publish


class PublishStatusFilter(SimpleListFilter):
    title = 'Trạng thái'  # Tiêu đề hiển thị trong giao diện Admin
    parameter_name = 'publish'    # Tham số URL

    def lookups(self, request, model_admin):
        # Tùy chọn hiển thị trong bộ lọc
        return [
            ('published', 'Publish'),
            ('unpublished', 'Unpublish'),
        ]

    def queryset(self, request, queryset):
        # Logic lọc dựa trên giá trị được chọn
        if self.value() == 'published':
            return queryset.filter(publish=True)
        elif self.value() == 'unpublished':
            return queryset.filter(publish=False)
        return queryset


class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'colored_publish_status', 'tag')

    def colored_publish_status(self, obj):
        color = 'badge-success' if obj.publish else 'badge-danger'
        status = 'Publish' if obj.publish else 'Unpublish'

        # Thêm icon để giao diện trực quan hơn
        icon = 'check-circle' if obj.publish else 'times-circle'
        return format_html(
            '<span class="badge {}"><i class="fas fa-{}"></i> {}</span>',
            color, icon, status
        )

    colored_publish_status.short_description = 'Trạng thái'

    # Liên kết CSS tùy chỉnh với trang admin
    class Media:
        css = {
            'all': ('css/admin.css',)  # Liên kết tới file CSS tùy chỉnh
        }
        js = ('js/custom_admin.js',)  # Liên kết tới tệp JavaScript tùy chỉnh của bạn

    search_fields = ('name', 'description')
    list_filter = (PublishStatusFilter,)  # Thêm bộ lọc tùy chỉnh vào đây
    list_per_page = 6
    readonly_fields = ('id', 'test_date',)

    # Sắp xếp các bài kiểm tra đã xuất bản trước
    ordering = ('-publish', 'id')

    # Sử dụng fields thay vì fieldsets
    fields = ('name', 'description', 'type', 'test_date', 'duration', 'question_count', 'part_count', 'tag', 'publish')

    actions = ['mark_tests_published', 'mark_tests_unpublished', 'export_to_csv']

    def mark_tests_published(self, request, queryset):
        to_update = queryset.filter(publish=False)
        already_published = queryset.filter(publish=True)

        updated_count = to_update.update(publish=True)
        skipped_count = already_published.count()

        messages = []
        if updated_count:
            messages.append(f"{updated_count} bài kiểm tra đã được đánh dấu là 'Publish'.")
        if skipped_count:
            messages.append(f"{skipped_count} bài kiểm tra đã ở trạng thái 'Publish' và không cần cập nhật.")

        self.message_user(request, " ".join(messages))

    mark_tests_published.short_description = "Đánh dấu các bài kiểm tra là 'Publish'"

    def mark_tests_unpublished(self, request, queryset):
        to_update = queryset.filter(publish=True)
        already_unpublished = queryset.filter(publish=False)

        updated_count = to_update.update(publish=False)
        skipped_count = already_unpublished.count()

        messages = []
        if updated_count:
            messages.append(f"{updated_count} bài kiểm tra đã được đánh dấu là 'Unpublish'.")
        if skipped_count:
            messages.append(f"{skipped_count} bài kiểm tra đã ở trạng thái 'Unpublish' và không cần cập nhật.")

        self.message_user(request, " ".join(messages))

    mark_tests_unpublished.short_description = "Đánh dấu các bài kiểm tra là 'Unpublish'"

    # Action export dữ liệu ra file CSV
    def export_to_csv(self, request, queryset):
        # Tạo response HTTP với header cho file CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tests.csv"'

        writer = csv.writer(response)
        # Ghi tiêu đề cột
        writer.writerow(
            ['ID', 'Name', 'Type', 'Test Date', 'Duration', 'Question Count', 'Part Count', 'Publish', 'Tag'])
        # Ghi từng hàng dữ liệu
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.name,
                obj.type,
                obj.test_date,
                obj.duration,
                obj.question_count,
                obj.part_count,
                obj.publish,
                obj.tag.name if obj.tag else 'N/A'
            ])

        self.message_user(request, f"Xuất dữ liệu thành công: {queryset.count()} bài kiểm tra.")
        return response

    export_to_csv.short_description = "Xuất dữ liệu ra CSV"

    # class Media:
    #     js = ('js/sweetalert2.all.min.js', 'js/custom_admin.js')


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
