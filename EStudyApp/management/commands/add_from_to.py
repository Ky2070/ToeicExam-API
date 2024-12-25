from django.core.management.base import BaseCommand
from EStudyApp.models import Question, QuestionSet


class Command(BaseCommand):
    help = 'add from_ques and to_ques to question_set'

    def handle(self, *args, **kwargs):
        question_sets = QuestionSet.objects.all()
        for question_set_obj in question_sets:
            questions = Question.objects.filter(question_set=question_set_obj)
            question_set_obj.from_ques = questions.first().question_number if questions.first() else None
            question_set_obj.to_ques = questions.last().question_number if questions.last() else None
            question_set_obj.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {question_set_obj.id} question_set'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {question_sets.count()} question_sets'
            )
        )
