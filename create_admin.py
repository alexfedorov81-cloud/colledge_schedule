import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'colledge_schedule.settings')
django.setup()

User = get_user_model()

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'your_password_123')
        print("Superuser created successfully!")
    else:
        print("Superuser already exists.")
except Exception as e:
    print(f"Error: {e}")
