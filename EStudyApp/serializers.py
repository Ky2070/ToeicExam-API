from rest_framework import serializers
from .models import PartDescription, Test, Part, QuestionSet, Question, Course, Lesson


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id',
                  'question_number',
                  'question_text',
                  'correct_answer',
                  'difficulty_level',
                  'answers',
                  ]


class QuestionSetSerializer(serializers.ModelSerializer):
    question_question_set = QuestionSerializer(many=True, read_only=True)  # Liên kết đến các câu hỏi

    class Meta:
        model = QuestionSet
        fields = ['id', 'audio', 'page', 'image', 'question_question_set']


class PartDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartDescription
        # fields = ['part_description']
        fields = '__all__'


class PartSerializer(serializers.ModelSerializer):
    question_set_part = QuestionSetSerializer(many=True, read_only=True)  # Liên kết đến các QuestionSet trong Part
    question_part = QuestionSerializer(many=True, read_only=True)
    part_description= PartDescriptionSerializer(read_only=True)

    class Meta:
        model = Part
        fields = ['id', 'part_description', 'question_set_part', 'question_part']


class TestDetailSerializer(serializers.ModelSerializer):
    part_test = PartSerializer(many=True, read_only=True)  # Liên kết đến các Part trong Test

    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'test_date', 'duration', 'part_test']


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'test_date', 'duration']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'duration']


class LessonSerializer(serializers.ModelSerializer):
    lesson_course = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'quiz']
