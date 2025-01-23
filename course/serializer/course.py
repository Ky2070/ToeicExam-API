from rest_framework import serializers
from course.models.course import Course
from django.db.models import Avg, Count
# course serializer


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'level', 'duration', 'info',
                  'target', 'cover', 'banner', 'updated_at', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    rating_distribution = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 
                  'duration', 'info', 'target', 'cover', 
                  'banner', 'updated_at', 'created_at', 'average_rating',
                  'total_ratings', 'rating_distribution']
        
    def get_average_rating(self, obj):
        average = obj.course_rating.filter(
            star__isnull=False).aggregate(Avg('star'))['star__avg']
        return round(average, 1) if average is not None else 0

    def get_total_ratings(self, obj):
        return obj.course_rating.filter(star__isnull=False).count()

    def get_rating_distribution(self, obj):
        distribution = obj.course_rating.filter(star__isnull=False).values('star').annotate(
            count=Count('star')
        ).order_by('star')

        # Initialize counts for all star values (1-5)
        result = {str(i): 0 for i in range(1, 6)}

        # Update with actual counts
        for item in distribution:
            result[str(item['star'])] = item['count']

        return result

