from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TOEICQuestion
from .deepseek_api import classify_toeic_question

@csrf_exempt
def classify_question(request):
    """
    API nhận câu hỏi từ người dùng, gửi đến DeepSeek để phân loại.
    """
    if request.method == "POST":
        question_text = request.POST.get("question", "")
        predicted_part = classify_toeic_question(question_text)

        question = TOEICQuestion.objects.create(
            question_text=question_text,
            predicted_part=predicted_part
        )

        return JsonResponse({"question": question_text, "predicted_part": predicted_part})

    return JsonResponse({"error": "Invalid request"}, status=400)
