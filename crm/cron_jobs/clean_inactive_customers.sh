#!/bin/bash

# Get the absolute directory path of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set project root assuming script is in crm/cron_jobs/
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to project directory
cd "$PROJECT_ROOT" || exit

# Optional: activate virtual environment if required
# source "$PROJECT_ROOT/venv/bin/activate"

# Run Django shell to clean inactive customers
deleted_count=$(./manage.py shell <<EOF
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

# Check if deletion was successful
if [ -n "\$deleted_count" ]; then
    echo "\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
else
    echo "\$(date '+%Y-%m-%d %H:%M:%S') - Cleanup failed or no customers deleted" >> /tmp/customer_cleanup_log.txt
fi
