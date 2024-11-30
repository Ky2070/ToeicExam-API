from django.conf import settings
from django.core.cache import cache
from EStudyApp.models import Test, QuestionSet, Question, PartQuestionSet


def get_cached_tests():
    cache_key = "all_tests"
    tests = cache.get(cache_key)
    if not tests:
        print("Cache miss! Fetching from database...")
        tests = list(Test.objects.all().order_by('id').values())
        cache.set(cache_key, tests, timeout=settings.CACHES['default'].get('TIMEOUT', 300))  # Lấy timeout từ settings
    else:
        print("Cache hit!")
    return tests


def get_cached_question_sets():
    cache_key = "all_question_sets"
    question_sets = cache.get(cache_key)
    if not question_sets:
        print("Cache miss! Fetching from database...")
        # Lấy danh sách QuestionSet từ cơ sở dữ liệu
        question_sets = list(QuestionSet.objects.all().order_by('id').values())
        # Lưu vào cache với thời gian timeout được cấu hình trong settings (5 phút)
        cache.set(cache_key, question_sets, timeout=settings.CACHES['default'].get('TIMEOUT', 300))
    else:
        print("Cache hit!")
    return question_sets


def get_cached_questions():
    cache_key = "all_questions"
    questions = cache.get(cache_key)
    if not questions:
        print("Cache miss! Fetching from database...")
        # Lấy danh sách Question từ cơ sở dữ liệu
        questions = list(Question.objects.all().order_by('id').values())
        # Lưu vào cache
        cache.set(cache_key, questions, timeout=settings.CACHES['default'].get('TIMEOUT', 3000))
    else:
        print("Cache hit!")
    return questions


def get_cached_part_question_sets():
    cache_key = "all_part_question_sets"
    part_question_sets = cache.get(cache_key)
    if not part_question_sets:
        print("Cache miss! Fetching from database...")
        # Lấy danh sách PartQuestionSet từ cơ sở dữ liệu
        part_question_sets = list(PartQuestionSet.objects.all().order_by('id').values())
        # Lưu vào cache
        cache.set(cache_key, part_question_sets, timeout=settings.CACHES['default'].get('TIMEOUT', 300))
    else:
        print("Cache hit!")
    return part_question_sets

# Sử dụng timeout tùy chỉnh
# def get_cached_tests():
#     cache_key = "all_tests"
#     tests = cache.get(cache_key)
#     if not tests:
#         print("Cache miss! Fetching from database...")
#         tests = list(Test.objects.all().order_by('id').values())
#         cache.set(cache_key, tests, timeout=60 * 15)  # Cache 15 phút
#     else:
#         print("Cache hit!")
#     return tests
