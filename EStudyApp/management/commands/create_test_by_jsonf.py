import json
import os

from django.core.management.base import BaseCommand
from EStudyApp.models import Test, Part, PartDescription, QuestionSet, Question


class Command(BaseCommand):
    help = 'Import test data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_filename', type=str, help='Test JSON filename (without path)')
        parser.add_argument('answer_filename', type=str, help='Answer JSON filename (without path)')

    def handle(self, *args, **kwargs):
        def handle(self, *args, **kwargs):
            base_dir = os.path.abspath(os.path.dirname(__file__))  # Lấy thư mục chứa file lệnh
            test_json_path = os.path.join(base_dir, "../../../scrapper/data-test", kwargs['json_filename'])
            answer_json_path = os.path.join(base_dir, "../../../scrapper/answers", kwargs['answer_filename'])

            # Kiểm tra xem file có tồn tại không
            if not os.path.exists(test_json_path):
                self.stdout.write(self.style.ERROR(f"Test JSON file not found: {test_json_path}"))
                return
            if not os.path.exists(answer_json_path):
                self.stdout.write(self.style.ERROR(f"Answer JSON file not found: {answer_json_path}"))
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
                part_name = part_data["Part"]  # Lưu tên Part (nếu cần dùng sau này)
                for q in part_data["Danh sách câu hỏi"]:
                    correct_answers[q["question_number"]] = q["correct_answer"]

            # Create the test entry
            test = Test.objects.create(
                name=data["title"],
                types="Online",
                publish=False
            )

            # Iterate through parts and questions
            for part_name, questions in data["questions_by_part"].items():
                part_desc, _ = PartDescription.objects.get(
                    part_name=part_name,
                    defaults={"part_description": ""}
                )
                part = Part.objects.create(test=test, part_description=part_desc)
                # Nhóm các câu hỏi có cùng image/audio/page vào một QuestionSet
                grouped_questions = {}
                for question_data in questions:
                    key = (
                        question_data.get("image", ""), question_data.get("audio", ""), question_data.get("page", ""))
                    if key not in grouped_questions:
                        grouped_questions[key] = []
                    grouped_questions[key].append(question_data)

                for (image, audio, page), question_list in grouped_questions.items():
                    # Tạo QuestionSet cho nhóm câu hỏi này
                    question_set = QuestionSet.objects.create(
                        test=test,
                        part=part,
                        image=image,
                        audio=audio,
                        page=page
                    )
                for question_data in questions:
                    question_set, _ = QuestionSet.objects.get(
                        test=test, part=part
                    )
                    # Get correct answer for the current question number
                    question_number = question_data["question_number"]
                    correct_answer = correct_answers.get(question_number, "")

                    Question.objects.create(
                        test=test,
                        question_set=question_set,
                        part=part,
                        question_number=question_number,
                        question_text=question_data.get("question_text", ""),
                        answers=question_data.get("answers", {}),
                        correct_answer=correct_answer,
                    )

            self.stdout.write(self.style.SUCCESS('Successfully imported test data with correct answers!'))
