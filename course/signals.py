# signals.py
from Tools.demo.mcast import sender
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from course.models.course import Course
from course.models.rating import Rating
from course.models.lesson import Lesson, ReviewLesson
from course.models.blog import Blog, CommentBlog

@receiver([post_save, post_delete], sender=Course)
@receiver([post_save, post_delete], sender=Rating)
def clear_course_cache(sender, instance, **kwargs):
    cache.delete_pattern("course_list:*")
    cache.delete_pattern("course_rating:*")

@receiver([post_save, post_delete], sender=Lesson)
@receiver([post_save, post_delete], sender=Course)
@receiver([post_save, post_delete], sender=ReviewLesson)
def clear_lesson_cache(sender, instance, **kwargs):
    cache.delele_pattern("lesson_list:*")
    cache.delete_pattern("lesson_detail:*")
    cache.delete_pattern("lesson_review:*")

@receiver([post_save, post_delete], sender=Blog)
@receiver([post_save, post_delete], sender=CommentBlog)
def clear_blog_cache(sender, instance, **kwargs):
    cache.delete_pattern("blog_list:*")
    cache.delete_pattern("blog_detail:*")
    cache.detele_pattern("blog_panel:*")
    cache.delete_pattern("blog_panel_detail:*")
    cache.delete_pattern("blog_comment:*")