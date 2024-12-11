from django.core.management.base import BaseCommand
from EStudyApp.models import QuestionType  # Thay 'your_app' bằng tên ứng dụng của bạn


class Command(BaseCommand):
    help = 'Add sample QuestionTypes for Part 5 with Grammar description'

    def handle(self, *args, **kwargs):
        # Các câu hỏi ngữ pháp cho Part 5
        question_types = [
            ('Cấu trúc so sánh', 2, 'Grammar'),
            ('Đại từ', 2, 'Grammar'),
            ('Danh động từ', 1, 'Grammar'),
            ('Danh từ', 6, 'Grammar'),
            ('Động từ nguyên mẫu có to', 1, 'Grammar'),
            ('Giới từ', 1, 'Grammar'),
            ('Liên từ', 5, 'Grammar'),
            ('Mệnh đề quan hệ', 1, 'Grammar'),
            ('Thì', 2, 'Grammar'),
            ('Tính từ', 5, 'Grammar'),
            ('Trạng từ', 6, 'Grammar'),
            ('Câu hỏi ngữ pháp', 9, 'Part 5'),
            ('Câu hỏi từ loại', 9, 'Part 5'),
            ('Câu hỏi từ vựng', 12, 'Part 5')
        ]

        # Thêm dữ liệu vào cơ sở dữ liệu
        for name, count, description in question_types:
            QuestionType.objects.create(
                name=name,
                count=count,
                description=description
            )

        self.stdout.write(self.style.SUCCESS('Successfully added sample QuestionTypes for Part 5 with Grammar '
                                             'description'))
