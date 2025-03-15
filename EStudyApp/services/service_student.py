from ..models import History, HistoryTraining
from django.db.models import Avg


def get_suggestions(user_id):
    history = History.objects.filter(user_id=user_id, complete=True)
    training = HistoryTraining.objects.filter(user_id=user_id, complete=True)

    if not history.exists() and not training.exists():
        return {"message": "Không có dữ liệu để phân tích."}

    # Trung bình điểm Listening và Reading
    avg_listening = history.aggregate(Avg('listening_score'))['listening_score__avg'] or 0
    avg_reading = history.aggregate(Avg('reading_score'))['reading_score__avg'] or 0

    # Tổng hợp số câu sai theo part
    part_errors = {}
    for train in training:
        parts = train.part_list.split(",") if train.part_list else []
        for part in parts:
            part_errors[part] = part_errors.get(part, 0) + train.wrong_answers

    # Xác định part có lỗi cao nhất
    weak_part = max(part_errors, key=part_errors.get, default="Không xác định")

    suggestion = "Luyện thêm " + weak_part if weak_part != "Không xác định" else "Làm thêm bài tập tổng hợp"

    return {
        "avg_listening": avg_listening,
        "avg_reading": avg_reading,
        "weak_part": weak_part,
        "suggestion": suggestion
    }
