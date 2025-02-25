from django.core.management.base import BaseCommand

from EStudyApp.models import Part, Question, QuestionSet, Test

class Command(BaseCommand):
    help = 'Fix data question'

    def handle(self, *args, **kwargs):
        test_id = 30
        try:
            test = Test.objects.get(id=test_id)
            part = Part.objects.filter(test=test)
            question_set = QuestionSet.objects.filter(part__in=part)
            total_question = 0
            for qs in question_set:
                questions = Question.objects.filter(question_set=qs)
                for q in questions:
                    q.test = test
                    q.save()
                    print(f"Successfully updated question {q.id} with test {test.id}")
                total_question += questions.count()
            print(f"Successfully updated {total_question} questions")
        except Exception as e:
            print(f"Error: {e}")
