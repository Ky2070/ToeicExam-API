import csv
from datetime import timezone, datetime

from django.contrib.admin import SimpleListFilter
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from EStudyApp.models import (PartDescription, Part,
                              QuestionSet, Question, PartQuestionSet,
                              Test, History, Tag, QuestionType, HistoryTraining)


# Định nghĩa lớp ModelAdmin để thêm phân trang

class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('name_display', 'count_display', 'description_display')  # Hiển thị các cột tùy chỉnh
    list_filter = ('description',)
    list_per_page = 10  # Hiển thị 10 bản ghi trên mỗi trang
    ordering = ('id',)

    def name_display(self, obj):
        # Tạo từ điển ánh xạ tên loại câu hỏi với màu sắc và biểu tượng
        question_type_mapping = {
            'Tranh tả người': {'color': '#3498db', 'icon': '👤'},
            'Tranh tả vật': {'color': '#f39c12', 'icon': '🖼️'},
            'Câu hỏi WHAT': {'color': '#e74c3c', 'icon': '🧐'},
            'Câu hỏi WHO': {'color': '#2ecc71', 'icon': '👥'},
            'Câu hỏi WHERE': {'color': '#9b59b6', 'icon': '📍'},
            'Câu hỏi WHEN': {'color': '#f1c40f', 'icon': '🕒'},
            'Câu hỏi HOW': {'color': '#e67e22', 'icon': '🔧'},
            'Câu hỏi WHY': {'color': '#1abc9c', 'icon': '🤔'},
            'Câu hỏi YES/NO': {'color': '#16a085', 'icon': '✅❌'},
            'Câu hỏi đuôi': {'color': '#f39c12', 'icon': '🔗'},
            'Câu hỏi lựa chọn': {'color': '#8e44ad', 'icon': '🔘'},
            'Câu yêu cầu, đề nghị': {'color': '#34495e', 'icon': '📋'},  # Gộp "Câu yêu cầu" và "Đề nghị"
            'Câu trần thuật': {'color': '#95a5a6', 'icon': '📄'},

            # Thêm các loại câu hỏi mới
            'Câu hỏi về danh tính người nói': {'color': '#9b59b6', 'icon': '🗣️'},
            'Câu hỏi về chi tiết cuộc hội thoại': {'color': '#f1c40f', 'icon': '💬'},

            # Các loại câu hỏi mới xuất hiện ở cả Part 3 và Part 4
            'Câu hỏi về chủ đề, mục đích': {
                'color': '#16a085',
                'icon': '🎯',
                'description': [
                    {'description': 'Part 3', 'count': 8},  # 4 câu cho Part 3
                    {'description': 'Part 4', 'count': 3}  # 3 câu cho Part 4
                ]
            },
            'Câu hỏi về hành động tương lai': {
                'color': '#e67e22',
                'icon': '⏳',
                'description': [
                    {'description': 'Part 3', 'count': 3},  # 3 câu cho Part 3
                    {'description': 'Part 4', 'count': 4}  # 4 câu cho Part 4
                ]
            },
            'Câu hỏi kết hợp bảng biểu': {
                'color': '#8e44ad',
                'icon': '📊',
                'description': [
                    {'description': 'Part 3', 'count': 3},  # 3 câu cho Part 3
                    {'description': 'Part 4', 'count': 3}  # 3 câu cho Part 4
                ]
            },
            'Câu hỏi về hàm ý câu nói': {
                'color': '#34495e',
                'icon': '💭',
                'description': [
                    {'description': 'Part 3', 'count': 2},  # 2 câu cho Part 3
                    {'description': 'Part 4', 'count': 3}  # 3 câu cho Part 4
                ]
            },

            # Các chủ đề mới
            'Chủ đề: Company - General Office Work': {'color': '#2c3e50', 'icon': '🏢'},
            'Chủ đề: Company - Personnel': {'color': '#f39c12', 'icon': '👔'},
            'Chủ đề: Company - Event, Project': {'color': '#e74c3c', 'icon': '📅'},
            'Chủ đề: Company - Facility': {'color': '#1abc9c', 'icon': '🏠'},
            'Chủ đề: Shopping, Service': {'color': '#8e44ad', 'icon': '🛍️'},
            'Chủ đề: Order, delivery': {'color': '#3498db', 'icon': '📦'},
            'Chủ đề: Transportation': {'color': '#9b59b6', 'icon': '🚗'},

            # Thêm câu hỏi về yêu cầu, gợi ý
            'Câu hỏi về yêu cầu, gợi ý': {
                'color': '#95a5a6',
                'icon': '📋',
                'description': [
                    {'description': 'Part 3', 'count': 5},  # 3 câu cho Part 3
                    {'description': 'Part 4', 'count': 3}  # 3 câu cho Part 4
                ]
            },

            # Các câu hỏi Part 4 mới
            'Câu hỏi về chi tiết': {'color': '#e74c3c', 'icon': '🔍'},  # Part 4: Câu hỏi về chi tiết
            'Câu hỏi về danh tính, địa điểm': {'color': '#8e44ad', 'icon': '📍'},
            'Dạng bài: Announcement - Thông báo': {'color': '#16a085', 'icon': '📢'},  # Part 4: Dạng bài Announcement
            'Dạng bài: Excerpt from a meeting - Trích dẫn từ buổi họp': {'color': '#f39c12', 'icon': '📄'},
            # Part 4: Dạng bài từ buổi họp
            'Dạng bài: News report, Broadcast - Bản tin': {'color': '#3498db', 'icon': '📻'},
            # Part 4: Bản tin, phát thanh
            'Dạng bài: Talk - Bài phát biểu, diễn văn': {'color': '#9b59b6', 'icon': '🎤'},  # Part 4: Bài phát biểu
            'Dạng bài: Telephone message - Tin nhắn thoại': {'color': '#e67e22', 'icon': '📞'}  # Part 4: Tin nhắn thoại
        }

        # Kiểm tra xem tên loại câu hỏi có trong từ điển không
        if obj.name in question_type_mapping:
            # Nếu có, lấy màu sắc và biểu tượng tương ứng
            color = question_type_mapping[obj.name]['color']
            icon = question_type_mapping[obj.name]['icon']
        else:
            # Nếu không có trong từ điển, dùng màu sắc và biểu tượng mặc định
            color = '#7f8c8d'
            icon = '❓'

        return format_html(
            '<span style="color: white; background-color: {}; padding: 8px 12px; border-radius: 10px; '
            'font-weight: bold; font-size: 14px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">'
            '{} {}</span>',
            color,
            icon,
            obj.name
        )

    name_display.short_description = "Tên loại câu hỏi"

    def count_display(self, obj):
        if obj.count is not None:
            # Màu nền xanh lá cây tươi và dấu tích ✅
            return format_html(
                '<span style="color: white; background-color: #2ecc71; padding: 5px 10px; border-radius: 5px; '
                'font-weight: bold;">'
                '✅ {}</span>',
                obj.count
            )
        # Trường hợp không xác định số lượng
        return format_html(
            '<span style="color: white; background-color: #95a5a6; padding: 5px 10px; border-radius: 5px; '
            'font-weight: bold;">'
            '❓ Không xác định</span>'
        )

    count_display.short_description = "Số lượng câu hỏi"

    def description_display(self, obj):
        if obj.description:
            return format_html(
                '<span style="color: white; background-color: #3498db; padding: 8px 12px; border-radius: 10px; '
                'font-weight: bold; font-size: 14px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">'
                '{} </span>',
                obj.description
            )
        return format_html(
            '<span style="color: white; background-color: #7f8c8d; padding: 8px 12px; border-radius: 10px; font-size: '
            '14px; font-weight: bold;">'
            'Không có mô tả</span>'
        )

    description_display.short_description = "Mô tả"


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_display')  # Hiển thị cột tùy chỉnh
    list_per_page = 5  # Hiển thị 5 bản ghi trên mỗi trang

    def description_display(self, obj):
        if obj.description:
            # Mô tả có sẵn
            return format_html(
                '<span style="color: white; background-color: #2ecc71; padding: 5px 10px; border-radius: 5px; '
                'font-weight: bold;">'
                '📄 {}</span>',
                obj.description
            )
        # Trường hợp không có mô tả
        return format_html(
            '<span style="color: white; background-color: #e74c3c; padding: 5px 10px; border-radius: 5px; '
            'font-weight: bold;">'
            '❌ Không có mô tả</span>'
        )

    description_display.short_description = "Mô tả"


class PublishStatusFilter(SimpleListFilter):
    title = 'Trạng thái'  # Tiêu đề hiển thị trong giao diện Admin
    parameter_name = 'publish'  # Tham số URL

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
    list_display = ('name', 'colored_publish_status', 'colored_types', 'get_tags')

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def colored_types(self, obj):
        # Gán màu sắc và biểu tượng dựa trên giá trị `types`
        type_styles = {
            'Practice': ('badge-info', 'laptop', 'Practice'),
            'Online': ('badge-success', 'globe', 'Online'),
            'All': ('badge-warning', 'book', 'All'),
        }
        default_style = ('badge-secondary', 'question-circle', 'Unknown')

        css_class, icon, label = type_styles.get(obj.types, default_style)
        return format_html(
            '<span class="badge {}" style="border-radius: 20px;'
            ' font-size: 0.8rem; text-transform: uppercase;'
            ' cursor: pointer;'
            ' transition: opacity 0.3s ease;'
            ' opacity: 1;"'
            ' onmouseover="this.style.opacity=0.8;" onmouseout="this.style.opacity=1;">'
            '<i class="fas fa-{}" style="margin-right: 0.1rem;"></i> {}</span>',
            css_class, icon, label
        )

    colored_types.short_description = 'Loại bài kiểm tra'

    class Media:
        css = {
            'all': ('css/admin.css',)  # Liên kết tới file CSS tùy chỉnh
        }
        js = ('js/custom_admin.js',)  # Liên kết tới tệp JavaScript tùy chỉnh của bạn

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
    list_filter = (PublishStatusFilter, 'tags', 'types')  # Updated to use tags instead of tag
    list_per_page = 6
    readonly_fields = ('id', 'test_date',)

    # Sắp xếp các bài kiểm tra đã xuất bản trước
    ordering = ('-publish', 'id')

    # Sử dụng fields thay vì fieldsets
    fields = ('name', 'description', 'types', 'test_date', 'duration', 'question_count', 'part_count', 'tags', 'publish')

    actions = ['mark_tests_published', 'mark_tests_unpublished', 'mark_tests_as_practice',
               'mark_tests_as_online', 'mark_tests_as_all', 'export_to_csv']

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

    def mark_tests_as_practice(self, request, queryset):
        updated_count = queryset.exclude(types='Practice').update(types='Practice')
        skipped_count = queryset.filter(types='Practice').count()

        messages = []
        if updated_count:
            messages.append(f"{updated_count} bài kiểm tra đã được đặt thành loại 'Practice'.")
        if skipped_count:
            messages.append(f"{skipped_count} bài kiểm tra đã ở loại 'Practice' và không cần cập nhật.")

        self.message_user(request, "".join(messages))

    mark_tests_as_practice.short_description = "Đặt loại Test là 'Practice'"

    def mark_tests_as_online(self, request, queryset):
        updated_count = queryset.exclude(types='Online').update(types='Online')
        skipped_count = queryset.filter(types='Online').count()

        messages = []
        if updated_count:
            messages.append(f"{updated_count} bài kiểm tra đã được đặt thành loại 'Online'.")
        if skipped_count:
            messages.append(f"{skipped_count} bài kiểm tra đã ở loại 'Online' và không cần cập nhật.")

        self.message_user(request, " ".join(messages))

    mark_tests_as_online.short_description = "Đặt loại Test là 'Online'"

    def mark_tests_as_all(self, request, queryset):
        updated_count = queryset.exclude(types='All').update(types='All')
        skipped_count = queryset.filter(types='All').count()

        messages = []
        if updated_count:
            messages.append(f"{updated_count} bài kiểm tra đã được đặt thành loại 'All'.")
        if skipped_count:
            messages.append(f"{skipped_count} bài kiểm tra đã ở loại 'All' và không cần cập nhật.")

        self.message_user(request, " ".join(messages))

    mark_tests_as_all.short_description = "Đặt loại Test là 'All'"

    # Action export dữ liệu ra file CSV
    def export_to_csv(self, request, queryset):
        # Tạo response HTTP với header cho file CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tests.csv"'

        writer = csv.writer(response)
        # Ghi tiêu đề cột
        writer.writerow(
            ['ID', 'Name', 'Type', 'Test Date', 'Duration', 'Question Count', 'Part Count', 'Publish', 'Tags'])
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
                ", ".join([tag.name for tag in obj.tags.all()])
            ])

        self.message_user(request, f"Xuất dữ liệu thành công: {queryset.count()} bài kiểm tra.")
        return response

    export_to_csv.short_description = "Xuất dữ liệu ra CSV"

    # class Media:
    #     js = ('js/sweetalert2.all.min.js', 'js/custom_admin.js')


class PartDescriptionAdmin(admin.ModelAdmin):
    # Các cột hiển thị trong danh sách
    list_display = (
        'part_name',
        'short_description',
        'skill_display',
        'quantity_display',
    )
    list_per_page = 7  # Số lượng bản ghi mỗi trang
    search_fields = ('part_name', 'skill')  # Tìm kiếm theo tên hoặc kỹ năng
    ordering = ('id',)  # Sắp xếp tăng dần theo ID

    # 1. Hiển thị mô tả ngắn gọn
    def short_description(self, obj):
        if obj.part_description:
            return f'{obj.part_description[:50]}...' if len(obj.part_description) > 50 else obj.part_description
        return "Không có mô tả"

    short_description.short_description = "Mô tả"

    # 2. Hiển thị kỹ năng với định dạng màu sắc
    def skill_display(self, obj):
        if obj.skill == 'READING':
            # Hiển thị với màu xanh dương và biểu tượng sách
            return format_html(
                '<span style="color: white; background-color: #3498db; padding: 5px 10px; border-radius: 5px; '
                'font-weight: bold;">'
                '📘 Reading</span>'
            )
        elif obj.skill == 'LISTENING':
            # Hiển thị với màu xanh lá cây và biểu tượng tai nghe
            return format_html(
                '<span style="color: white; background-color: #2ecc71; padding: 5px 10px; border-radius: 5px; '
                'font-weight: bold;">'
                '🎧 Listening</span>'
            )
        # Trường hợp không xác định
        return format_html(
            '<span style="color: white; background-color: #7f8c8d; padding: 5px 10px; border-radius: 5px; '
            'font-weight: bold;">'
            '❓ Không xác định</span>'
        )

    skill_display.short_description = "Kỹ năng"

    def quantity_display(self, obj):
        if obj.quantity:
            # Màu xanh lá cây tươi (#1dd1a1) với icon dấu tích xanh ✅
            return format_html(
                '<span style="color: white; '
                'background-color: #1dd1a1; padding: 5px 10px; border-radius: 5px; font-weight: bold;">'
                '✅ {}</span>',
                obj.quantity,
            )
        # Trường hợp không có số lượng
        return format_html(
            '<span style="color: white; '
            'background-color: #7f8c8d; padding: 5px 10px; border-radius: 5px; font-weight: bold;">'
            'Không xác định</span>'
        )

    quantity_display.short_description = "Số lượng câu hỏi"

    # 4. Tích hợp CSS & JS tùy chỉnh (nếu cần)
    class Media:
        css = {
            'all': ('css/custom_part_description_admin.css',),
        }
        js = ('js/custom_part_description_admin.js',)


class PartAdmin(admin.ModelAdmin):
    list_display = (
        'part_description',
        'test',
        'is_active',
    )
    list_per_page = 7
    search_fields = ('part_description__name', 'test__name')  # Cho phép tìm kiếm theo các trường liên quan
    ordering = ('id', 'part_description',)  # Sắp xếp tăng dần theo ID

    # Thêm hành động tùy chỉnh
    actions = ['soft_delete_selected']

    # 1. Hiển thị trạng thái hoạt động với biểu tượng
    def is_active(self, obj):
        if hasattr(obj, 'deleted_at') and obj.deleted_at:
            return format_html('<span style="color: red;" title="Không hoạt động">&#10060;</span>')
        return format_html('<span style="color: green;" title="Hoạt động">&#9989;</span>')

    is_active.short_description = "Trạng thái"

    # 2. Hành động xóa mềm
    def soft_delete_selected(self, request, queryset):
        # Ví dụ: thêm trường `deleted_at` nếu bạn đang dùng xóa mềm
        count = queryset.update(deleted_at=datetime.now())
        self.message_user(request, f"Đã xóa mềm {count} phần.")

    soft_delete_selected.short_description = "Xóa mềm các bản ghi đã chọn"

    # 3. Cải thiện giao diện với CSS và JS tùy chỉnh
    class Media:
        css = {
            'all': ('css/custom_part_admin.css',),
        }
        js = ('js/custom_part_admin.js',)


class QuestionSetAdmin(admin.ModelAdmin):
    # 1. Hiển thị thông tin trong danh sách
    list_display = ('test', 'part', 'has_audio', 'has_image', 'short_page')
    list_per_page = 10  # Số lượng bản ghi trên mỗi trang
    search_fields = ('test__name', 'part__name')  # Tìm kiếm theo test hoặc part
    ordering = ('id',)  # Sắp xếp bản ghi (id tăng dần)

    # 2. Hiển thị trạng thái audio
    def has_audio(self, obj):
        return bool(obj.audio)

    has_audio.boolean = True
    has_audio.short_description = 'Có Audio'

    # 3. Hiển thị trạng thái hình ảnh
    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = 'Có Hình ảnh'

    # 4. Cắt ngắn nội dung text trong trường `page` để hiển thị ngắn gọn
    def short_page(self, obj):
        return obj.page[:50] + '...' if obj.page else "Không có nội dung"

    short_page.short_description = 'Nội dung trang'

    # 5. Thêm CSS & JS tùy chỉnh
    class Media:
        css = {
            'all': ('css/custom_admin.css',),
        }
        js = ('js/custom_admin.js',)

    # 6. Cho phép chỉnh sửa trong chi tiết
    fields = ('test', 'part', 'audio', 'page', 'image')

    # 7. Thêm chức năng xuất dữ liệu ra file CSV
    actions = ['export_to_csv']

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="question_sets.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Test', 'Part', 'Audio', 'Page', 'Image'])

        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.test.name if obj.test else 'N/A',
                obj.part.name if obj.part else 'N/A',
                obj.audio if obj.audio else '',
                obj.page if obj.page else '',
                obj.image if obj.image else ''
            ])

        self.message_user(request, f"Đã xuất {queryset.count()} bộ câu hỏi ra CSV.")
        return response

    export_to_csv.short_description = "Xuất dữ liệu ra CSV"


class QuestionAdmin(admin.ModelAdmin):
    def difficulty_icon(self, obj):
        icons = {
            'BASIC': '✅',
            'MEDIUM': '🔶',
            'DIFFICULTY': '⚠️',
            'VERY_DIFFICULTY': '🔥'
        }
        return icons.get(obj.difficulty_level, '❓')

    difficulty_icon.short_description = "Mức độ"
    list_display = (
        'id',
        'test',
        'question_set',
        'short_question_type',  # Hiển thị loại câu hỏi
        'short_part',  # Hiển thị phần
        'question_number',
        'short_question_text',
        'difficulty_icon',  # Thay thế cột mức độ khó bằng icon
        'correct_answer',
        'is_deleted',
    )
    list_per_page = 10  # Số lượng bản ghi mỗi trang
    search_fields = ('question_text', 'test__name', 'question_set__name')  # Tìm kiếm
    ordering = ('id',)  # Sắp xếp giảm dần

    # Các trường chỉnh sửa
    fields = (
        'test',
        'question_set',
        'question_type',  # Thêm loại câu hỏi
        'part',  # Thêm phần
        'question_number',
        'question_text',
        'correct_answer',
        'answers',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('created_at', 'updated_at')  # Chỉ đọc thời gian tạo/cập nhật

    # 1. Hiển thị nội dung ngắn gọn của câu hỏi
    def short_question_text(self, obj):
        return obj.question_text[:50] + "..." if obj.question_text else "Không có nội dung"

    short_question_text.short_description = "Nội dung Câu hỏi"

    def short_question_type(self, obj):
        if obj.question_type:
            return format_html(
                '<span class="badge badge-primary">{}</span>',
                obj.question_type.name
            )
        return format_html('<span class="badge badge-secondary">Không có loại</span>')

    short_question_type.short_description = "Loại câu hỏi"

    def short_part(self, obj):
        if obj.part and obj.part.part_description:
            # Lấy giá trị part_name
            part_name = str(obj.part.part_description).strip()

            # Lấy tên Test từ Part và cắt ngắn tên Test nếu cần
            test_name = str(obj.part.test.name)
            # Tách tên Test thành các từ và chỉ lấy phần đầu (ví dụ: "new economy 2")
            test_name_parts = test_name.split()
            if len(test_name_parts) > 3:
                test_name = " ".join(test_name_parts[:2]) + " " + test_name_parts[-1]
            else:
                test_name = " ".join(test_name_parts)

            # print(f"DEBUG: part_name = '{part_name}', test_name = '{test_name}'")  # Debug để kiểm tra giá trị thực tế

            # Kiểm tra điều kiện Part 1 đến Part 4
            if any(f"Part {i}" in part_name for i in range(1, 5)):
                return format_html(
                    '<b style="color: #00F2C3;">{} - {}</b>',
                    part_name,
                    test_name
                )

            # Kiểm tra điều kiện Part 5 đến Part 7
            elif any(f"Part {i}" in part_name for i in range(5, 8)):
                return format_html(
                    '<b style="color: #E14ECA;">{} - {}</b>',
                    part_name,
                    test_name
                )

            # Trường hợp khác
            else:
                return format_html(
                    '<b style="color: black;">{} - {}</b>',
                    part_name,
                    test_name
                )

        # Nếu không có part hoặc part_description, trả về thông báo mặc định
        return "No part available"

    short_part.short_description = "Phần đề thi"

    # 2. Kiểm tra trạng thái xóa
    def is_deleted(self, obj):
        if obj.deleted_at:
            # Chỉ hiển thị biểu tượng "x" màu đỏ
            return format_html('<span style="color: red;" title="Đã xóa">&#10060;</span>')
        # Chỉ hiển thị biểu tượng "✓" màu xanh
        return format_html('<span style="color: green;" title="Hoạt động">&#9989;</span>')

    is_deleted.short_description = "Trạng thái"

    # 3. Hành động xóa mềm các bản ghi được chọn

    actions = ['soft_delete_selected', 'restore_selected', 'export_to_csv']

    def restore_selected(self, request, queryset):
        count = queryset.update(deleted_at=None)
        self.message_user(request, f"Đã phục hồi {count} câu hỏi.")

    restore_selected.short_description = "Phục hồi các bản ghi đã chọn"

    def soft_delete_selected(self, request, queryset):
        count = queryset.update(deleted_at=datetime.now())
        self.message_user(request, f"Đã xóa mềm {count} câu hỏi.")

    soft_delete_selected.short_description = "Xóa mềm các bản ghi đã chọn"

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="questions.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Test', 'Question Set', 'Number', 'Text', 'Difficulty', 'Deleted'])
        for obj in queryset:
            writer.writerow(
                [obj.id, obj.test, obj.question_set, obj.question_type.name if obj.question_type else '',
                 obj.part.part_description if obj.part else '', obj.question_number, obj.question_text,
                 obj.difficulty_level,
                 obj.deleted_at])
        return response

    export_to_csv.short_description = "Export to CSV"

    # 4. Thêm CSS & JS tùy chỉnh
    class Media:
        css = {
            'all': ('css/custom_admin.css',),
        }
        js = ('js/custom_admin.js',)


class PartQuestionSetAdmin(admin.ModelAdmin):
    list_per_page = 20


class HistoryAdmin(admin.ModelAdmin):
    # Số lượng bản ghi hiển thị trên mỗi trang
    list_per_page = 10

    # Tùy chỉnh các cột có thể nhấp để truy cập chi tiết
    list_display_links = ('user', 'test')

    # Thêm tính năng tìm kiếm theo user và test
    search_fields = ('user__username', 'test__name')

    # Thêm tính năng lọc theo các trường
    list_filter = ('user', 'test', 'created_at')

    # Tùy chỉnh hiển thị các trường chi tiết khi chỉnh sửa
    fields = ('user', 'test', 'score', 'start_time', 'end_time',
              'correct_answers', 'wrong_answers', 'unanswer_questions',
              'percentage_score', 'listening_score', 'reading_score',
              'complete', 'test_result', 'created_at')

    # Đảm bảo hiển thị completion_time đúng cách
    def completion_time(self, obj):
        return obj.completion_time  # Sử dụng phương thức completion_time trong model

    completion_time.admin_order_field = 'end_time'  # Sắp xếp theo end_time

    # Tùy chỉnh tiêu đề của cột
    completion_time.short_description = 'Completion Time (seconds)'

    # Tùy chỉnh màu sắc cho cột 'complete' dựa trên trạng thái
    def complete(self, obj):
        if obj.complete:
            return '<span style="color: green;">Complete</span>'
        return '<span style="color: red;">Not Complete</span>'

    complete.allow_tags = True  # Cho phép hiển thị HTML

    # Định dạng hiển thị các trường điểm số (score, percentage_score, listening_score, reading_score)
    def formatted_score(self, obj):
        if obj.score:
            return f"{obj.score:.0f}"
        return "N/A"

    def formatted_percentage(self, obj):
        if obj.percentage_score is not None:
            return f"{obj.percentage_score:.2f}%"  # Hiển thị 2 chữ số thập phân
        return "0%"  # Nếu không có giá trị, trả về 0%

    # Hiển thị các trường điểm số với định dạng
    formatted_score.short_description = 'Score'
    formatted_percentage.short_description = 'Percentage'

    list_display = (
        'user', 'test', 'formatted_score',
        'correct_answers', 'wrong_answers', 'unanswer_questions',
        'formatted_percentage', 'complete', 'completion_time', 'created_at'
    )

    # Tùy chỉnh các trường không cho phép chỉnh sửa (readonly)
    readonly_fields = ('user', 'test', 'score', 'start_time', 'end_time',
                       'correct_answers', 'wrong_answers', 'unanswer_questions',
                       'percentage_score', 'listening_score', 'reading_score',
                       'test_result')


class HistoryTrainingAdmin(admin.ModelAdmin):
    list_per_page = 10


# Đăng ký các mô hình với phân trang
admin.site.register(Tag, TagAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(PartDescription, PartDescriptionAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(QuestionSet, QuestionSetAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(PartQuestionSet, PartQuestionSetAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(QuestionType, QuestionTypeAdmin)
admin.site.register(HistoryTraining, HistoryTrainingAdmin)
