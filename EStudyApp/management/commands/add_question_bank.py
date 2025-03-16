from django.core.management.base import BaseCommand

from EStudyApp.models import Part, PartDescription, Question, QuestionSet, Test
from question_bank.models import QuestionBank, QuestionSetBank


class Command(BaseCommand):
    help = 'Fix data question'

    def handle(self, *args, **kwargs):
        test_id = 31
        try:
            test = Test.objects.get(id=test_id)
            part = Part.objects.filter(test=test)
            question_sets = QuestionSet.objects.filter(part__in=part)
            for qs in question_sets:
                # get part description first
                part_description = qs.part.part_description

                question_set_bank = QuestionSetBank.objects.create(
                    part_description=part_description,
                    audio=qs.audio,
                    page=qs.page,
                    image=qs.image,
                    from_ques=qs.from_ques,
                    to_ques=qs.to_ques
                )
                
                question_set_bank.save()
                self.stdout.write(f"Successfully created question set bank {question_set_bank.id}")
                
                questions = Question.objects.filter(question_set=qs)
                for q in questions:
                    question_bank = QuestionBank.objects.create(
                        question_set=question_set_bank,
                        question_type=q.question_type,
                        part_description=part_description,
                        question_number=q.question_number,
                        question_text=q.question_text,
                        correct_answer=q.correct_answer,
                        answers=q.answers,
                        difficulty_level=q.difficulty_level
                    )
                    question_bank.save()
                    self.stdout.write(f"Successfully created question bank {question_bank.id}")
                self.stdout.write(f"Successfully created question set bank {question_set_bank.id}")
            self.stdout.write(f"Successfully created {question_sets.count()} question set banks")
        except Exception as e:
            print(f"Error: {e}")
