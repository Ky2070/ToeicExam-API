from django.conf import settings
from django.core.cache import cache
from EStudyApp.models import Test


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