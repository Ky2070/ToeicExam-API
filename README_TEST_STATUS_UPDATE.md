# Test Status Update System

This system automatically updates test publish status based on `publish_date` and `close_date`.

## How It Works

1. Tests will be automatically published when the current time passes the `publish_date`
2. Tests will be automatically unpublished when the current time passes the `close_date`

## Setup Instructions

### Using Cron (Recommended)

To run the status update command automatically every hour:

1. Edit your crontab:
   ```
   crontab -e
   ```

2. Add this line (adjust the path to your project):
   ```
   0 * * * * cd /path/to/ToeicExam-API && python manage.py update_test_status >> /path/to/logs/test_status.log 2>&1
   ```

This will run the command every hour at minute 0 and log the output to the specified log file.

### Manual Run

You can also run the command manually to update test statuses:

```
python manage.py update_test_status
```

## Using in Code

To update a test's status in your code, you can call the `update_publish_status` method on a Test instance:

```python
from EStudyApp.models import Test

# Get a specific test
test = Test.objects.get(id='your-test-id')

# Update its publish status based on current time
status_changed = test.update_publish_status()

if status_changed:
    print(f"Test {test.name} status was updated to: {'published' if test.publish else 'unpublished'}")
else:
    print(f"No status change for test {test.name}")
```

## Testing

To test the functionality, you can create tests with:
- `publish_date` set to a few minutes in the future
- `close_date` set to a few more minutes after that

Then run the command before, during, and after these times to verify the status changes correctly. 