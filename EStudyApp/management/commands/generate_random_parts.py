from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question
import random

class Command(BaseCommand):
    help = 'Generate random parts for a test'

    def add_arguments(self, parser):
        parser.add_argument('test_id', type=int, help='ID of the test to generate parts for')
        parser.add_argument('--parts', nargs='+', type=int, help='List of part numbers to generate (1-7)')

    def handle(self, *args, **kwargs):
        test_id = kwargs['test_id']
        part_numbers = kwargs.get('parts') or range(1, 8)  # Default to all parts if not specified

        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Test with ID {test_id} not found'))
            return

        parts_created = 0
        
        for part_number in part_numbers:
            try:
                # Get part description
                part_description = PartDescription.objects.get(part_name=f"Part {part_number}")
                
                # Create part
                part = Part.objects.create(
                    part_description=part_description,
                    test=test
                )

                # Create question sets based on part type
                if part_number in [1, 2]:  # Single question per set
                    self._create_single_question_sets(part, part_description.quantity)
                elif part_number in [3, 4]:  # Multiple questions per conversation/talk
                    self._create_conversation_sets(part, part_description.quantity)
                else:  # Reading parts
                    self._create_reading_sets(part, part_description.quantity)

                parts_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created Part {part_number}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating Part {part_number}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {parts_created} parts')
        )

    def _create_single_question_sets(self, part, total_questions):
        """Create question sets for Parts 1-2 (one question per set)"""
        for i in range(1, total_questions + 1):
            question_set = QuestionSet.objects.create(
                part=part,
                from_ques=i,
                to_ques=i,
                audio=f"audio_{part.part_description.part_name}_{i}.mp3"
            )
            
            # Create question
            Question.objects.create(
                question_set=question_set,
                part=part,
                question_number=i,
                question_text=f"Question {i}",
                answers={
                    "A": "Option A",
                    "B": "Option B",
                    "C": "Option C",
                    "D": "Option D"
                },
                correct_answer=random.choice(["A", "B", "C", "D"]),
                difficulty_level="BASIC"
            )

    def _create_conversation_sets(self, part, total_questions):
        """Create question sets for Parts 3-4 (multiple questions per conversation)"""
        questions_per_set = 3
        current_question = 1
        
        while current_question <= total_questions:
            set_number = (current_question - 1) // questions_per_set + 1
            
            question_set = QuestionSet.objects.create(
                part=part,
                from_ques=current_question,
                to_ques=min(current_question + questions_per_set - 1, total_questions),
                audio=f"conversation_{part.part_description.part_name}_{set_number}.mp3",
                page="Sample conversation text..."
            )
            
            # Create questions for this set
            for i in range(questions_per_set):
                if current_question <= total_questions:
                    Question.objects.create(
                        question_set=question_set,
                        part=part,
                        question_number=current_question,
                        question_text=f"Question {current_question}",
                        answers={
                            "A": "Option A",
                            "B": "Option B",
                            "C": "Option C",
                            "D": "Option D"
                        },
                        correct_answer=random.choice(["A", "B", "C", "D"]),
                        difficulty_level="BASIC"
                    )
                    current_question += 1

    def _create_reading_sets(self, part, total_questions):
        """Create question sets for Parts 5-7"""
        if part.part_description.part_name == "Part 5":
            # Single question per set for Part 5
            self._create_single_question_sets(part, total_questions)
        else:
            # Multiple questions per passage for Parts 6-7
            questions_per_set = 4 if part.part_description.part_name == "Part 6" else 5
            current_question = 1
            
            while current_question <= total_questions:
                set_number = (current_question - 1) // questions_per_set + 1
                
                question_set = QuestionSet.objects.create(
                    part=part,
                    from_ques=current_question,
                    to_ques=min(current_question + questions_per_set - 1, total_questions),
                    page=f"Sample reading passage for {part.part_description.part_name} set {set_number}..."
                )
                
                # Create questions for this set
                for i in range(questions_per_set):
                    if current_question <= total_questions:
                        Question.objects.create(
                            question_set=question_set,
                            part=part,
                            question_number=current_question,
                            question_text=f"Question {current_question}",
                            answers={
                                "A": "Option A",
                                "B": "Option B",
                                "C": "Option C",
                                "D": "Option D"
                            },
                            correct_answer=random.choice(["A", "B", "C", "D"]),
                            difficulty_level="BASIC"
                        )
                        current_question += 1 