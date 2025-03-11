import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resultportal.settings')
django.setup()

# python3 manage.py shell
from result_portal_lib.models import User
testuser = User.get('testuser')
testuser.email = 'animashaunadams@gmail.com'
testuser.save()
staffuser = User.get('staffuser')
staffuser.email = 'smadapythontest@example.com'
staffuser.save()