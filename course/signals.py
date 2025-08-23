# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from course.models.course import Course

@receiver([post_save, post_delete], sender=Course)
def clear_course_cache(sender, instance, **kwargs):
    # Xóa cache khi History thay đổi
    cache.delete_pattern("course_list:*")