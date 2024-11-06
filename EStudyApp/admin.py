from django.contrib import admin
from .models import PartDescription, Part, QuestionSet, Question, PartQuestionSet, Test


# Register your models here.
admin.site.register(Test)
admin.site.register(PartDescription)
admin.site.register(Part)
admin.site.register(QuestionSet)
admin.site.register(Question)
admin.site.register(PartQuestionSet)
