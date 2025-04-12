from django.core.management.base import BaseCommand
from django.utils import timezone
from EStudyApp.models import Test
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates test publish status based on publish_date and close_date'

    def handle(self, *args, **options):
        current_time = timezone.now()
        
        # Find tests that should be published (publish_date has passed but not close_date)
        tests_to_publish = Test.objects.filter(
            publish=False,
            publish_date__lte=current_time,
            close_date__gt=current_time
        )
        
        publish_count = 0
        for test in tests_to_publish:
            test.publish = True
            test.save()
            publish_count += 1
            logger.info(f"Published test: {test.name} (ID: {test.id})")
        
        # Find tests that should be unpublished (close_date has passed)
        tests_to_unpublish = Test.objects.filter(
            publish=True,
            close_date__lte=current_time
        )
        
        unpublish_count = 0
        for test in tests_to_unpublish:
            test.publish = False
            test.save()
            unpublish_count += 1
            logger.info(f"Unpublished test: {test.name} (ID: {test.id})")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {publish_count} tests to published and {unpublish_count} tests to unpublished'
            )
        ) 