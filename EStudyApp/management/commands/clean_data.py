from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question
import random

# add question_set to question part 5


class Command(BaseCommand):
    help = 'Generate parts for a test by copying from existing data'

    def handle(self, *args, **kwargs):
        for i in range(101, 131):
            test = Test.objects.get(id=1)
            part = Part.objects.get(id=5)
            question = Question.objects.get(
                question_number=i, test=test, part=part)
            question_set = QuestionSet.objects.create(
                test=test,
                part=part,
                from_ques=question.question_number,
                to_ques=question.question_number,
                audio=None,
                page=None,
                image=None,
            )
            question.question_set = question_set
            question.save()

            self.stdout.write(self.style.SUCCESS(
                f'ADD question set with ID {question_set}'))
