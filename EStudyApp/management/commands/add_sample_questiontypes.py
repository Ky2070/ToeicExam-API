from django.core.management.base import BaseCommand
from EStudyApp.models import QuestionType  # Thay 'your_app' bằng tên ứng dụng của bạn


class Command(BaseCommand):
    help = 'Thêm dữ liệu mẫu cho QuestionType'

    def handle(self, *args, **kwargs):
        # # Thêm câu hỏi "Câu hỏi về chủ đề, mục đích"
        #
        # QuestionType.objects.create(name='Câu hỏi về chủ đề, mục đích', count=3, description='Part 4')
        # # Thêm câu hỏi "Câu hỏi về hành động tương lai"
        # QuestionType.objects.create(name='Câu hỏi về hành động tương lai', count=4, description='Part 4')
        # # Thêm câu hỏi "Câu hỏi kết hợp bảng biểu"
        # QuestionType.objects.create(name='Câu hỏi kết hợp bảng biểu', count=3, description='Part 4')
        # # Thêm câu hỏi "Câu hỏi về hàm ý câu nói"
        # QuestionType.objects.create(name='Câu hỏi về hàm ý câu nói', count=3, description='Part 4')

        # Thêm câu hỏi "Câu hỏi về chi tiết"
        QuestionType.objects.create(name='Câu hỏi về chi tiết', count=9, description='Part 4')

        # Thêm câu hỏi "Câu hỏi về danh tính, địa điểm"
        QuestionType.objects.create(name='Câu hỏi về danh tính, địa điểm', count=5, description='Part 4')

        # Thêm câu hỏi "Câu hỏi yêu cầu, gợi ý"
        QuestionType.objects.create(name='Câu hỏi yêu cầu, gợi ý', count=3, description='Part 4')

        # Thêm câu hỏi "Dạng bài: Announcement - Thông báo"
        QuestionType.objects.create(name='Dạng bài: Announcement - Thông báo', count=6, description='Part 4')

        # Thêm câu hỏi "Dạng bài: Excerpt from a meeting - Trích dẫn từ buổi họp"
        QuestionType.objects.create(name='Dạng bài: Excerpt from a meeting - Trích dẫn từ buổi họp', count=3,
                                    description='Part 4')

        # Thêm câu hỏi "Dạng bài: News report, Broadcast - Bản tin"
        QuestionType.objects.create(name='Dạng bài: News report, Broadcast - Bản tin', count=3, description='Part 4')

        # Thêm câu hỏi "Dạng bài: Talk - Bài phát biểu, diễn văn"
        QuestionType.objects.create(name='Dạng bài: Talk - Bài phát biểu, diễn văn', count=15, description='Part 4')

        # Thêm câu hỏi "Dạng bài: Telephone message - Tin nhắn thoại"
        QuestionType.objects.create(name='Dạng bài: Telephone message - Tin nhắn thoại', count=3, description='Part 4')

        self.stdout.write(self.style.SUCCESS('Successfully added sample question types!'))
