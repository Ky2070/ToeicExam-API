from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question
import random

class Command(BaseCommand):
    help = 'Generate parts for a test by copying from existing data'

    def add_arguments(self, parser):
        parser.add_argument('target_test_id', type=int, help='ID of the test to generate parts for')
        parser.add_argument('--parts', nargs='+', type=int, help='List of part numbers to generate (1-7)')

    def handle(self, *args, **kwargs):
        target_test_id = kwargs['target_test_id']
        part_numbers = kwargs.get('parts') or range(1, 8)

        try:
            target_test = Test.objects.get(id=target_test_id)
        except Test.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Target test with ID {target_test_id} not found'))
            return

        parts_created = 0
        
        for part_number in part_numbers:
            try:
                # Get part description
                part_description = PartDescription.objects.get(part_name=f"Part {part_number}")
                
                # Get random existing part of the same type
                existing_parts = Part.objects.filter(
                    part_description=part_description
                ).exclude(test_id=target_test_id)
                
                if not existing_parts.exists():
                    self.stdout.write(
                        self.style.WARNING(f'No existing parts found for Part {part_number}')
                    )
                    continue
                
                # Select random source part
                source_part = random.choice(existing_parts)
                
                # Create new part
                new_part = Part.objects.create(
                    part_description=part_description,
                    test=target_test
                )

                # Copy question sets and questions
                self._copy_question_sets(source_part, new_part)

                parts_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully copied Part {part_number}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating Part {part_number}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {parts_created} parts')
        )

    def _copy_question_sets(self, source_part, target_part):
        """Copy all question sets and their questions from source to target part"""
        for source_question_set in QuestionSet.objects.filter(part=source_part):
            # Create new question set
            new_question_set = QuestionSet.objects.create(
                part=target_part,
                audio=source_question_set.audio,
                page=source_question_set.page,
                image=source_question_set.image,
                from_ques=source_question_set.from_ques,
                to_ques=source_question_set.to_ques
            )

            # Copy all questions in this set
            for source_question in Question.objects.filter(question_set=source_question_set):
                Question.objects.create(
                    question_set=new_question_set,
                    part=target_part,
                    question_type=source_question.question_type,
                    question_text=source_question.question_text,
                    difficulty_level=source_question.difficulty_level,
                    correct_answer=source_question.correct_answer,
                    question_number=source_question.question_number,
                    answers=source_question.answers
                ) 