from django.core.management.base import BaseCommand
from EStudyApp.models import Question


class Command(BaseCommand):
    help = 'Uppercase all answer keys in Question model'

    def handle(self, *args, **kwargs):
        questions = Question.objects.all()
        updated_count = 0

        for question in questions:
            if question.answers:
                try:
                    # Convert answer keys to uppercase
                    new_answers = {
                        key.upper(): value
                        for key, value in question.answers.items()
                    }

                    # Update the question only if answers changed
                    if new_answers != question.answers:
                        question.answers = new_answers
                        question.correct_answer = question.correct_answer.upper() if question.correct_answer else None
                        question.save()
                        updated_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error processing question {question.id}: {str(e)}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} questions'
            )
        )
