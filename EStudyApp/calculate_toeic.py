from EStudyApp.toeic_score_mapping import toeic_score_mapping


def calculate_toeic_score(listening_correct, reading_correct):
    """Hàm tính điểm TOEIC dựa trên số câu đúng."""
    listening_score = toeic_score_mapping.get(listening_correct, (0, 0))[0]
    reading_score = toeic_score_mapping.get(reading_correct, (0, 0))[1]
    overall_score = listening_score + reading_score
    return listening_score, reading_score, overall_score

