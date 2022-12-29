from .models import location
from datetime import datetime, timedelta

# delete old loaction
def my_scheduled_job():
  location.objects.filter(timestamp__lte=datetime.now()-timedelta(days=7)).delete()
