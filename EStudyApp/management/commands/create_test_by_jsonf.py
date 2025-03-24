import json
import os

from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question


class Command(BaseCommand):
    help = 'Import test data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_filename', type=str,
                            help='Test JSON filename (without path)')
        parser.add_argument('answer_filename', type=str,
                            help='Answer JSON filename (without path)')
        parser.add_argument('test_id', type=int,
                            help='Test ID')

    def handle(self, *args, **kwargs):
        from_ques = 1
        base_dir = os.path.abspath(os.path.dirname(
            __file__))  # Lấy thư mục chứa file lệnh
        test_json_path = os.path.join(
            base_dir, "../../../scrapper/data-test", kwargs['json_filename'])
        answer_json_path = os.path.join(
            base_dir, "../../../scrapper/answers", kwargs['answer_filename'])
        test_id = kwargs['test_id']

        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(test_json_path):
            self.stdout.write(self.style.ERROR(
                f"Test JSON file not found: {test_json_path}"))
            return
        if not os.path.exists(answer_json_path):
            self.stdout.write(self.style.ERROR(
                f"Answer JSON file not found: {answer_json_path}"))
            return

            # Load test questions from JSON
        with open(test_json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            # Load correct answers from JSON
        with open(answer_json_path, 'r', encoding='utf-8') as file:
            answer_data = json.load(file)

        correct_answers = {}
        # Bỏ qua phần tử đầu tiên (là một chuỗi tiêu đề)
        for part_data in answer_data[1:]:
            # Lưu tên Part (nếu cần dùng sau này)
            part_name = part_data["Part"]
            for q in part_data["Danh sách câu hỏi"]:
                correct_answers[q["question_number"]] = q["correct_answer"]

        # Create the test entry
        # test = Test.objects.create(
        #     name=data["title"],
        #     types="Online",
        #     publish=True
        # )
        test = Test.objects.get(id=test_id)
        if test is None:
            self.stdout.write(self.style.ERROR(
                f"Test not found: {test_id}"))
            raise Exception(f"Test not found: {test_id}")

        # Iterate through parts and questions
        for part_name, questions in data["questions_by_part"].items():
            part_desc, _ = PartDescription.objects.get_or_create(
                part_name=part_name,
                defaults={"part_description": ""}
            )
            part = Part.objects.create(test=test, part_description=part_desc)
            self.stdout.write(self.style.SUCCESS(
                f"Part created: {part.part_description}"))
            # Nhóm các câu hỏi có cùng image/audio/page vào một QuestionSet
            grouped_questions = {}
            for question_data in questions:
                # Create a unique key string from the image, audio, and page values
                image = ','.join(question_data.get("image", [])) or ''
                audio = ','.join(question_data.get("audio", [])) or ''
                page = question_data.get("page", "")
                key = f"{image}_{audio}_{page}"

                if key not in grouped_questions:
                    grouped_questions[key] = {
                        'image': image,
                        'audio': audio,
                        'page': page,
                        'questions': []
                    }
                grouped_questions[key]['questions'].append(question_data)

            # Create QuestionSets and Questions
            for key, group_data in grouped_questions.items():
                # Tạo QuestionSet cho nhóm câu hỏi này
                if part.part_description.id == 1 or part.part_description.id == 2 or part.part_description.id == 5:

                    question_set = QuestionSet.objects.create(
                        test=test,
                        part=part,
                        from_ques=question_data["question_number"],
                        to_ques=question_data["question_number"],
                        image=group_data['image'],
                        audio=group_data['audio'],
                        page=group_data['page']
                    )

                    # Create questions for this QuestionSet
                    for question_data in group_data['questions']:
                        # Get correct answer for the current question number
                        question_number = int(question_data["question_number"])
                        correct_answer = correct_answers[question_data["question_number"]]
                        print(correct_answer)
                        question = Question.objects.create(
                            test=test,
                            question_set=question_set,
                            part=part,
                            question_number=question_number,
                            question_text=question_data.get(
                                "question_text", ""),
                            answers=question_data.get("answers", {}),
                            correct_answer=correct_answer,
                        )
                        
                        from_ques += 1

                        self.stdout.write(self.style.SUCCESS(
                            f"Question created: {question.question_number}"))

                if part.part_description.id == 3 or part.part_description.id == 4 or part.part_description.id == 6 or part.part_description.id == 7 or part.part_description.id == 8 or part.part_description.id == 9 or part.part_description.id == 10 or part.part_description.id == 11 or part.part_description.id == 12:
                    question_set = QuestionSet.objects.create(
                        test=test,
                        part=part,
                        from_ques=from_ques,
                        to_ques=from_ques + group_data['questions'][0]['question_set'],
                        image=group_data['image'],
                        audio=group_data['audio'],
                        page=group_data['page']
                    )

                    self.stdout.write(self.style.SUCCESS(
                        f"QuestionSet created: {question_set.id}"))

                    for questions_data in group_data['questions']:
                        from_ques = int(questions_data['questions'][0]['question_number'])
                        for question_data in questions_data['questions']:
                            correct_answer = correct_answers[question_data["question_number"]]
                            question = Question.objects.create(
                                test=test,
                                question_set=question_set,
                                part=part,
                                question_number=question_data["question_number"],
                                question_text=question_data.get(
                                    "question_text", ""),
                                answers=question_data.get("answers", {}),
                                correct_answer=correct_answer,
                            )
                            question_set.to_ques = question_data["question_number"]
                            from_ques += 1
                            question_set.save()
                            self.stdout.write(self.style.SUCCESS(
                                f"Question created: {question.question_number}"))

        self.stdout.write(self.style.SUCCESS(
            'Successfully imported test data with correct answers!'))
