from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question
import random

# add question_set to question part 5


class Command(BaseCommand):
    help = 'Generate parts for a test by copying from existing data'

    def handle(self, *args, **kwargs):
        ids = [95,96,97,98,99]
        tests = Test.objects.filter(id__in=ids)
        for test in tests:
            test.delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted tests!'))
