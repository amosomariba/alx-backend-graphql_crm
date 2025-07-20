#!/bin/bash

# Get the absolute directory path of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Define current working directory (cwd)
cwd="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to project root
cd "$cwd" || exit

# Optional: activate virtual environment
# source "$cwd/venv/bin/activate"

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

# Log the result
if [ -n "\$deleted_count" ]; then
    echo "\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
else
    echo "\$(date '+%Y-%m-%d %H:%M:%S') - Cleanup failed or no customers deleted" >> /tmp/customer_cleanup_log.txt
fi
