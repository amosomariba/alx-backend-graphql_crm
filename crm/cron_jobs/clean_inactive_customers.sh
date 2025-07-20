#!/bin/bash

# Activate virtual environment if needed
# source /path/to/venv/bin/activate

# Set the Django project directory
cd /path/to/your/project/root  # e.g., /home/amos/DJANGO_PROJECTS/crm_project

# Run the cleanup command using Django shell
deleted_count=$(./manage.py shell << EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lt=one_year_ago).distinct()
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log the result with timestamp
echo "\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
