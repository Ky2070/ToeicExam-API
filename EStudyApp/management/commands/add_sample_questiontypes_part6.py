from django.core.management.base import BaseCommand
from EStudyApp.models import QuestionType  # Thay 'your_app' bằng tên ứng dụng của bạn


class Command(BaseCommand):
    help = 'Add sample QuestionTypes for Part 6 with Grammar description'

    def handle(self, *args, **kwargs):
        # Các câu hỏi ngữ pháp cho Part 6, mô tả đã bao gồm thông tin về phần
        question_types = [
            ('Danh từ', 2, 'Grammar - Part 6'),
            ('Giới từ', 1, 'Grammar - Part 6'),
            ('Liên từ', 1, 'Grammar - Part 6'),
            ('Phân từ và Cấu trúc phân từ', 1, 'Grammar - Part 6'),
            ('Thể', 1, 'Grammar - Part 6'),
            ('Thì', 3, 'Grammar - Part 6'),
            ('Tính từ', 3, 'Grammar - Part 6'),

            ('Câu hỏi điền câu vào đoạn văn', 4, 'Part 6'),
            ('Câu hỏi ngữ pháp', 5, 'Part 6'),
            ('Câu hỏi từ loại', 2, 'Part 6'),
            ('Câu hỏi từ vựng', 5, 'Part 6'),

            ('Hình thức: Thông báo/ văn bản hướng dẫn (Notice/ Announcement Information)', 12, 'Part 6'),
            ('Hình thức: Thư điện tử/ thư tay (Email/ Letter)', 4, 'Part 6')
        ]

        # Thêm dữ liệu vào cơ sở dữ liệu
        for name, count, description in question_types:
            QuestionType.objects.create(
                name=name,
                count=count,
                description=description  # Mô tả đã bao gồm thông tin về Part 6
            )

        self.stdout.write(self.style.SUCCESS('Successfully added sample QuestionTypes for Part 6 with Grammar '
                                             'description'))
