from rest_framework import serializers

from Authentication.serializers import UserSerializer
from EStudyApp.models import History, PartDescription, Test, Part, QuestionSet, Question, Course, Lesson, Tag, \
    QuestionType, State


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'user', 'test', 'name', 'info', 'used']
        read_only_fields = ['id']  # Để tự động tạo ID

class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ['id', 'name']


class QuestionDetailSerializer(serializers.ModelSerializer):
    question_type = serializers.StringRelatedField()

    class Meta:
        model = Question
        fields = ['id',
                  'question_number',
                  'question_text',
                  'difficulty_level',
                  'answers',
                  'question_type',
                  ]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id',
                  'question_number',
                  'question_text',
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
        fields = ['id', 'part_name', 'skill', 'quantity', 'part_description']


class PartSerializer(serializers.ModelSerializer):
    question_set_part = QuestionSetSerializer(many=True, read_only=True)  # Liên kết đến các QuestionSet trong Part
    question_part = QuestionSerializer(many=True, read_only=True)
    part_description = PartDescriptionSerializer(read_only=True)

    class Meta:
        model = Part
        fields = ['id', 'part_description', 'question_set_part', 'question_part']


class TestDetailSerializer(serializers.ModelSerializer):
    part_test = PartSerializer(many=True, read_only=True)  # Liên kết đến các Part trong Test

    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'test_date', 'duration', 'part_test']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class TestSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'test_date', 'duration', 'question_count', 'part_count', 'tag']


class PartListSerializer(serializers.ModelSerializer):
    part_description = PartDescriptionSerializer(read_only=True)

    class Meta:
        model = Part
        # fields = ['part_description']
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'duration']


class LessonSerializer(serializers.ModelSerializer):
    lesson_course = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'quiz']


class TestSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'name']


class HistoryDetailSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    test = TestSubmitSerializer(read_only=True)

    class Meta:
        model = History
        fields = [
            'id', 'user', 'test', 'score', 'start_time', 'end_time',
            'correct_answers', 'wrong_answers', 'unanswer_questions',
            'percentage_score', 'listening_score', 'reading_score',
            'complete'
        ]


class HistorySerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    test = TestSubmitSerializer(read_only=True)

    class Meta:
        model = History
        fields = [
            'id', 'user', 'test', 'score', 'start_time', 'end_time',
            'listening_score', 'reading_score',
            'complete'
        ]
