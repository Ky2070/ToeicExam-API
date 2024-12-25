from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question

class Command(BaseCommand):
    help = 'Create standard parts with proper question set ranges'

    def add_arguments(self, parser):
        parser.add_argument('test_id', type=int, help='ID of the test to create parts for')

    def handle(self, *args, **kwargs):
        test_id = kwargs['test_id']

        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Test with ID {test_id} not found'))
            return

        # Standard structure for each part
        PART_STRUCTURE = {
            'Part 1': {
                'sets': [(1, 6)],  # One set with questions 1-6
            },
            'Part 2': {
                'sets': [(7, 31)],  # One set with questions 7-31
            },
            'Part 3': {
                'sets': [
                    (32, 34), (35, 37), (38, 40),
                    (41, 43), (44, 46), (47, 49),
                    (50, 52), (53, 55), (56, 58),
                    (59, 61), (62, 64), (65, 67),
                    (68, 70)
                ],  # 13 sets of 3 questions each
            },
            'Part 4': {
                'sets': [
                    (71, 73), (74, 76), (77, 79),
                    (80, 82), (83, 85), (86, 88),
                    (89, 91), (92, 94), (95, 97),
                    (98, 100)
                ],  # 10 sets of 3 questions each
            },
            'Part 5': {
                'sets': [(101, 130)],  # One set with questions 101-130
            },
            'Part 6': {
                'sets': [
                    (131, 134), (135, 138),
                    (139, 142), (143, 146)
                ],  # 4 sets of 4 questions each
            },
            'Part 7': {
                'sets': [
                    (147, 151), (152, 156), (157, 161),
                    (162, 166), (167, 171), (172, 176),
                    (177, 181), (182, 186), (187, 191),
                    (192, 196), (197, 200)
                ],  # Multiple sets of varying question counts
            }
        }

        parts_created = 0

        for part_number in range(1, 8):
            try:
                part_name = f'Part {part_number}'
                part_description = PartDescription.objects.get(part_name=part_name)
                
                # Create part
                part = Part.objects.create(
                    part_description=part_description,
                    test=test
                )

                # Create question sets for this part
                structure = PART_STRUCTURE[part_name]
                for from_ques, to_ques in structure['sets']:
                    QuestionSet.objects.create(
                        part=part,
                        from_ques=from_ques,
                        to_ques=to_ques,
                        audio=f"audio_{part_name}_{from_ques}_{to_ques}.mp3" if part_number <= 4 else None,
                        page=f"page_{part_name}_{from_ques}_{to_ques}.html" if part_number >= 5 else None
                    )

                parts_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created {part_name} with {len(structure["sets"])} question sets'
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating Part {part_number}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {parts_created} parts with standard structure')
        ) 