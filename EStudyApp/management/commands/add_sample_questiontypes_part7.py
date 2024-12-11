from django.core.management.base import BaseCommand
from EStudyApp.models import QuestionType  # Thay 'your_app' bằng tên ứng dụng của bạn


class Command(BaseCommand):
    help = 'Add sample QuestionTypes for Part 7'

    def handle(self, *args, **kwargs):
        # Các câu hỏi và dạng bài cho Part 7, mô tả sử dụng 'Part 7'
        question_types = [
            ('Câu hỏi điền câu', 2, 'Part 7'),
            ('Câu hỏi suy luận', 25, 'Part 7'),
            ('Câu hỏi tìm chi tiết sai', 4, 'Part 7'),
            ('Câu hỏi tìm thông tin', 16, 'Part 7'),
            ('Câu hỏi tìm từ đồng nghĩa', 2, 'Part 7'),
            ('Câu hỏi về chủ đề, mục đích', 3, 'Part 7'),
            ('Câu hỏi về hàm ý câu nói', 2, 'Part 7'),

            ('Cấu trúc: một đoạn', 29, 'Part 7'),
            ('Cấu trúc: nhiều đoạn', 25, 'Part 7'),

            ('Dạng bài: Advertisement - Quảng cáo', 8, 'Part 7'),
            ('Dạng bài: Announcement/ Notice: Thông báo', 10, 'Part 7'),
            ('Dạng bài: Article/ Review: Bài báo/ Bài đánh giá', 11, 'Part 7'),
            ('Dạng bài: Email/ Letter: Thư điện tử/ Thư tay', 25, 'Part 7'),
            ('Dạng bài: Form - Đơn từ, biểu mẫu', 14, 'Part 7'),
            ('Dạng bài: Text message chain - Chuỗi tin nhắn', 6, 'Part 7')
        ]

        # Thêm dữ liệu vào cơ sở dữ liệu
        for name, count, description in question_types:
            QuestionType.objects.create(
                name=name,
                count=count,
                description=description  # Mô tả sẽ chỉ là 'Part 7'
            )

        self.stdout.write(self.style.SUCCESS('Successfully added sample QuestionTypes for Part 7'))
