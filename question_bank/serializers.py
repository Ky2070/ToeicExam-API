from rest_framework import serializers
from .models import QuestionBank
from EStudyApp.models import PartDescription, QuestionType
from .models import QuestionSetBank

class PartDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartDescription
        fields = ['id', 'part_name', 'part_description', 'part_number', 'skill', 'quantity']

class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ['id', 'name', 'count', 'description']

class QuestionSetBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionSetBank
        fields = ['id', 'audio', 'page', 'image', 'from_ques', 'to_ques', 'note']

class QuestionBankSerializer(serializers.ModelSerializer):
    part_description = PartDescriptionSerializer(read_only=True)
    question_type = QuestionTypeSerializer(read_only=True)
    question_set = QuestionSetBankSerializer(read_only=True)
    
    class Meta:
        model = QuestionBank
        fields = [
            'id',
            'question_set',
            'question_type',
            'part_description',
            'question_text',
            'difficulty_level',
            'correct_answer',
            'question_number',
            'answers',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class QuestionBankCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = [
            'question_number',
            'question_text',
            'correct_answer',
            'answers'
        ]

    def to_internal_value(self, data):
        # Convert correct_answer to uppercase before saving
        if 'correct_answer' in data:
            data['correct_answer'] = str(data['correct_answer']).upper()
        return super().to_internal_value(data)

class QuestionSetBankCreateSerializer(serializers.ModelSerializer):
    part_description_id = serializers.PrimaryKeyRelatedField(
        queryset=PartDescription.objects.all(),
        source='part_description'
    )
    questions = QuestionBankCreateSerializer(many=True)
    
    class Meta:
        model = QuestionSetBank
        fields = [
            'part_description_id',
            'audio',
            'page',
            'image',
            'from_ques',
            'to_ques',
            'note',
            'questions'
        ]
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        part_description = validated_data.get('part_description')
        
        question_set = QuestionSetBank.objects.create(**validated_data)
        
        for question_data in questions_data:
            QuestionBank.objects.create(
                question_set=question_set,
                part_description=part_description,
                **question_data
            )
        
        return question_set

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': instance.id,
            'partDescription': {
                'id': instance.part_description.id if instance.part_description else None,
                'partName': instance.part_description.part_name if instance.part_description else None,
                'partDescription': instance.part_description.part_description if instance.part_description else None,
                'partNumber': instance.part_description.part_number if instance.part_description else None,
                'skill': instance.part_description.skill if instance.part_description else None,
                'quantity': instance.part_description.quantity if instance.part_description else None
            } if instance.part_description else None,
            'audio': data.get('audio'),
            'page': data.get('page'),
            'image': data.get('image'),
            'fromQues': data.get('from_ques'),
            'toQues': data.get('to_ques'),
            'note': data.get('note'),
            'questions': data.get('questions', [])
        }

class QuestionSetBankDetailSerializer(serializers.ModelSerializer):
    questions = QuestionBankSerializer(many=True, read_only=True, source='question_bank_question_set_bank')
    part_description = PartDescriptionSerializer(read_only=True)
    
    class Meta:
        model = QuestionSetBank
        fields = [
            'id',
            'part_description',
            'audio',
            'page',
            'image',
            'from_ques',
            'to_ques',
            'note',
            'questions',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class QuestionSetBankUpdateSerializer(serializers.ModelSerializer):
    part_description = serializers.PrimaryKeyRelatedField(
        queryset=PartDescription.objects.all(),
        source='part_description',
        required=False,
        write_only=True
    )
    part_description = PartDescriptionSerializer(read_only=True)
    questions = QuestionBankSerializer(many=True, source='question_bank_question_set_bank')

    class Meta:
        model = QuestionSetBank
        fields = [
            'id',
            'part_description',
            'audio',
            'page',
            'image',
            'from_ques',
            'to_ques',
            'note',
            'questions'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Handle case where part_description might be None
        part_description_data = None
        if instance.part_description:
            part_description_data = {
                'id': instance.part_description.id,
                'part_name': instance.part_description.part_name,
                'part_description': instance.part_description.part_description,
                'part_number': instance.part_description.part_number,
                'skill': instance.part_description.skill,
                'quantity': instance.part_description.quantity
            }
        
        return {
            'id': instance.id,
            'part_description': part_description_data,
            'audio': data.get('audio'),
            'page': data.get('page'),
            'image': data.get('image'),
            'from_ques': data.get('from_ques'),
            'to_ques': data.get('to_ques'),
            'note': data.get('note'),
            'questions': data.get('questions', []),
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }

    def to_internal_value(self, data):
        # Convert camelCase to snake_case
        internal_data = {}
        field_mapping = {
            'from_ques': 'from_ques',
            'to_ques': 'to_ques'
        }
        
        for key, value in data.items():
            if key in field_mapping:
                internal_data[field_mapping[key]] = value
            elif key == 'part_description':
                internal_data['part_description'] = value
            else:
                internal_data[key] = value
                
        return super().to_internal_value(internal_data)

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('question_bank_question_set_bank', [])
        
        # Update question set fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Refresh instance to get updated part_description
        instance.refresh_from_db()

        # Update questions
        if questions_data:
            existing_questions = {q.id: q for q in instance.question_bank_question_set_bank.all()}
            
            for question_data in questions_data:
                question_id = question_data.get('id')
                
                # Remove nested data that shouldn't be saved directly
                question_data.pop('question_set', None)
                question_data.pop('part_description', None)
                question_data.pop('question_type', None)
                question_data.pop('created_at', None)
                question_data.pop('updated_at', None)
                question_data.pop('id', None)  # Remove id after we've stored it
                
                if question_id and question_id in existing_questions:
                    # Update existing question
                    question = existing_questions[question_id]
                    for attr, value in question_data.items():
                        setattr(question, attr, value)
                    question.part_description = instance.part_description
                    question.save()
                    # Remove from existing_questions dict to track which ones were updated
                    existing_questions.pop(question_id)
                else:
                    # Create new question only if it doesn't exist
                    QuestionBank.objects.create(
                        question_set=instance,
                        part_description=instance.part_description,
                        **question_data
                    )
            
            # Delete questions that weren't in the update data
            for question in existing_questions.values():
                question.delete()

        return instance

class QuestionSetBankListSerializer(serializers.ModelSerializer):
    questions = QuestionBankSerializer(many=True, read_only=True, source='question_bank_question_set_bank')
    partDescription = PartDescriptionSerializer(source='part_description', read_only=True)

    class Meta:
        model = QuestionSetBank
        fields = [
            'id',
            'partDescription',
            'audio',
            'page',
            'image',
            'from_ques',
            'to_ques',
            'note',
            'questions',
            'created_at',
            'updated_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Handle case where part_description might be None
        part_description_data = None
        if instance.part_description:
            part_description_data = {
                'id': instance.part_description.id,
                'part_name': instance.part_description.part_name,
                'part_description': instance.part_description.part_description,
                'part_number': instance.part_description.part_number,
                'skill': instance.part_description.skill,
                'quantity': instance.part_description.quantity
            }
        
        return {
            'id': instance.id,
            'part_description': part_description_data,
            'audio': data.get('audio'),
            'page': data.get('page'),
            'image': data.get('image'),
            'from_ques': data.get('from_ques'),
            'to_ques': data.get('to_ques'),
            'note': data.get('note'),
            'questions': data.get('questions', []),
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        } 