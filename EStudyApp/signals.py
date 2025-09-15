# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from EStudyApp.models import History, Test, Part, Question

@receiver([post_save, post_delete], sender=History)
def clear_history_cache(sender, instance, **kwargs):
    # Xóa cache khi History thay đổi
    cache.delete_pattern("history_detail*")
    cache.delete_pattern("submit_test*")

@receiver([post_save, post_delete], sender=Test)
@receiver([post_save, post_delete], sender=Part)
@receiver([post_save, post_delete], sender=Question)
def clear_test_cache(sender, instance, **kwargs):
    # Xóa cache khi Test thay đổi
    cache.delete_pattern("submit_test*")
    cache.delete_pattern("test_detail:*")
    cache.delete_pattern("test_part_detail:*")
    cache.delete_pattern("test_list:*")
