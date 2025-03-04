from django import forms
from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import QuestionSetBank, QuestionBank

class QuestionSetBankAdminForm(forms.ModelForm):
    class Meta:
        model = QuestionSetBank
        fields = '__all__'
        widgets = {
            'page': CKEditorWidget(),
        }

class AnswersWidget(forms.Widget):
    template_name = 'admin/question_bank/answers_widget.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value:
            if isinstance(value, str):
                import json
                value = json.loads(value)
            context['answers'] = value
        else:
            context['answers'] = {'A': None, 'B': None, 'C': None, 'D': None}
        return context

class QuestionBankForm(forms.ModelForm):
    answer_a = forms.CharField(label='A', required=False, empty_value=None)
    answer_b = forms.CharField(label='B', required=False, empty_value=None)
    answer_c = forms.CharField(label='C', required=False, empty_value=None)
    answer_d = forms.CharField(label='D', required=False, empty_value=None)

    class Meta:
        model = QuestionBank
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.answers:
            if isinstance(self.instance.answers, str):
                import json
                answers = json.loads(self.instance.answers)
            else:
                answers = self.instance.answers
            self.fields['answer_a'].initial = answers.get('A', None)
            self.fields['answer_b'].initial = answers.get('B', None)
            self.fields['answer_c'].initial = answers.get('C', None)
            self.fields['answer_d'].initial = answers.get('D', None)

    def clean(self):
        cleaned_data = super().clean()
        # Convert empty strings to None
        for field in ['answer_a', 'answer_b', 'answer_c', 'answer_d']:
            if cleaned_data.get(field) == '':
                cleaned_data[field] = None
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.answers = {
            'A': self.cleaned_data['answer_a'],
            'B': self.cleaned_data['answer_b'],
            'C': self.cleaned_data['answer_c'],
            'D': self.cleaned_data['answer_d']
        }
        # Remove None values from answers
        instance.answers = {k: v for k, v in instance.answers.items() if v is not None}
        if commit:
            instance.save()
        return instance

class QuestionBankInline(admin.TabularInline):
    model = QuestionBank
    form = QuestionBankForm
    extra = 0
    fields = ('question_number', 'question_text', 'answer_a', 'answer_b', 'answer_c', 'answer_d', 'correct_answer', 'difficulty_level')
    ordering = ('question_number',)

@admin.register(QuestionSetBank)
class QuestionSetBankAdmin(admin.ModelAdmin):
    form = QuestionSetBankAdminForm
    list_display = ('part_description', 'from_ques', 'to_ques', 'created_at', 'updated_at')
    list_filter = ("part_description", "created_at", "updated_at")
    search_fields = ("page", "audio", "image")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 20
    inlines = [QuestionBankInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('part_description', 'from_ques', 'to_ques')
        }),
        ('Content', {
            'fields': ('page', 'audio', 'image'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    class Media:
        css = {
            'all': ('ckeditor/ckeditor.css',)
        }
        js = ('ckeditor/ckeditor.js',)

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    form = QuestionBankForm
    list_display = ('id', 'question_number', 'question_text', 'part_description', 'difficulty_level', 'correct_answer', 'created_at')
    list_filter = ('part_description', 'difficulty_level', 'question_type', 'created_at')
    search_fields = ('question_text', 'question_number')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    ordering = ('question_number',)

    fieldsets = (
        ('Question Information', {
            'fields': ('question_set', 'question_type', 'part_description', 'question_number', 'question_text')
        }),
        ('Answer Details', {
            'fields': (('answer_a', 'answer_b', 'answer_c', 'answer_d'), 'correct_answer', 'difficulty_level')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
