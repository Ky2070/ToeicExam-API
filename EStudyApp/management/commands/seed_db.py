from django.core.management.base import BaseCommand
from EStudyApp.models import Test, QuestionType, PartDescription, Part, QuestionSet, Question, PartQuestionSet
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed the database...'))

        partDescription1 = PartDescription.objects.create(
            part_name = 'Part 1',
            part_description = 'Part 1 của bài thi TOEIC Listening bao gồm 6 hình ảnh, mỗi hình ảnh đi kèm với 4 lựa chọn đáp án khác nhau. Nhiệm vụ của thí sinh là xem xét các hình ảnh, lắng nghe và chọn lựa mô tả chính xác nhất về mỗi hình ảnh.',
            skill = 'LISTENING',
            quantity = 6
        )
        partDescription1.save()

        partDescription2 = PartDescription.objects.create(
            part_name = 'Part 2',
            part_description = 'Part 2 của bài thi TOEIC Listening.',
            skill = 'LISTENING',
            quantity = 25
        )
        partDescription2.save()

        partDescription3 = PartDescription.objects.create(
            part_name = 'Part 3',
            part_description = 'Part 3 của bài thi TOEIC Listening',
            skill = 'LISTENING',
            quantity = 39
        )
        partDescription3.save()

        partDescription4 = PartDescription.objects.create(
            part_name = 'Part 4',
            part_description = 'Part 4 của bài thi TOEIC Listening',
            skill = 'LISTENING',
            quantity = 30
        )
        partDescription4.save()

        partDescription5 = PartDescription.objects.create(
            part_name = 'Part 5',
            part_description = 'Part 5 của bài thi TOEIC',
            skill = 'READING',
            quantity = 30
        )
        partDescription5.save()

        partDescription6 = PartDescription.objects.create(
            part_name = 'Part 6',
            part_description = 'Part 6 của bài thi TOEIC',
            skill = 'READING',
            quantity = 16
        )
        partDescription6.save()

        partDescription7 = PartDescription.objects.create(
            part_name = 'Part 7',
            part_description = 'Part 7 của bài thi TOEIC',
            skill = 'READING',
            quantity = 54
        )
        partDescription7.save()

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))












