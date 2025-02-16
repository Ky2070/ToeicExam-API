from django.db import models


# Create your models here.

class TOEICQuestion(models.Model):
    question_text = models.TextField(null=True, blank=True)  # Văn bản câu hỏi
    audio = models.FileField(upload_to='audio/', null=True, blank=True)  # File âm thanh
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # Ảnh minh họa
    predicted_part = models.CharField(max_length=10, null=True, blank=True)  # Kết quả phân loại (Part 1-7)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text if self.question_text else "Audio/Image Question"
