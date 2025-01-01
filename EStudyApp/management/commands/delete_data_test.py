from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question
import random

class Command(BaseCommand):
    help = 'Delete all parts, question sets, and questions for a test'

    def add_arguments(self, parser):
        parser.add_argument('test_id', type=int, help='ID of the test to generate parts for')
        parser.add_argument('--parts', nargs='+', type=int, help='List of part numbers to generate (1-7)')

    def handle(self, *args, **kwargs):
        test_id = kwargs['test_id']
        # part_numbers = kwargs.get('parts') or range(1, 8)  # Default to all parts if not specified

        try:
            test = Test.objects.get(id=test_id)
            # print(test)
        except Test.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Test with ID {test_id} not found'))
            return
        
        parts = Part.objects.filter(test=test)
        for part in parts:
            part.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted part {part.id}'))
            
        question_sets = QuestionSet.objects.filter(test=test)
        for question_set in question_sets:
            question_set.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted question set {question_set.id}'))

        questions = Question.objects.filter(test=test)
        for question in questions:
            question.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted question {question.id}'))
    
        self.stdout.write(self.style.SUCCESS(f'Deleted all parts, question sets, and questions for test {test_id}'))