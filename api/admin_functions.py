import csv
from result_portal_lib.models import User
from result_portal_lib.aws_utils import upload_to_s3, send_ses_email
from django.conf import settings  # Add this import
from django.contrib.auth.hashers import make_password
import secrets
import logging

logger = logging.getLogger(__name__)

def upload_staff_data(file, bucket_name):
    """Upload staff CSV data to S3 and create STAFF users in DynamoDB with SES emails."""
    try:
        if not file.name.endswith('.csv'):
            raise ValueError("File must be a CSV")

        file_key = f'uploads/staff/{file.name}'
        upload_to_s3(file, bucket_name, file_key)

        file.seek(0)
        csv_reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        required_fields = {'username', 'email'}
        if not required_fields.issubset(csv_reader.fieldnames):
            raise ValueError("CSV must contain 'username' and 'email' columns")

        staff_users = []
        for row in csv_reader:
            username = row['username']
            if User.exists(username):
                logger.warning(f"Skipping existing user: {username}")
                continue
            temp_password = secrets.token_urlsafe(12)
            user = User(
                username=username,
                password=make_password(temp_password),
                user_type='STAFF',
                email=row['email']
            )
            staff_users.append((user, temp_password))

        with User.batch_write() as batch:
            for user, _ in staff_users:
                batch.save(user)

        for user, temp_password in staff_users:
            send_ses_email(
                'Your Staff Account',
                f'Username: {user.username}\nTemporary Password: {temp_password}\nChange it after login at /api/change_password/',
                user.email,
                from_email=settings.SES_SENDER  # Explicitly pass from_email
            )
        
        logger.info(f"Uploaded and emailed {len(staff_users)} staff users")
    except ValueError as ve:
        logger.error(f"Validation error uploading staff data: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error uploading staff data: {e}")
        raise

def upload_student_data(file, bucket_name):
    """Upload student CSV data to S3 and create STUDENT users in DynamoDB with SES emails."""
    try:
        if not file.name.endswith('.csv'):
            raise ValueError("File must be a CSV")

        file_key = f'uploads/students/{file.name}'
        upload_to_s3(file, bucket_name, file_key)

        file.seek(0)
        csv_reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        required_fields = {'username', 'email'}
        if not required_fields.issubset(csv_reader.fieldnames):
            raise ValueError("CSV must contain 'username' and 'email' columns")

        student_users = []
        for row in csv_reader:
            username = row['username']
            if User.exists(username):
                logger.warning(f"Skipping existing user: {username}")
                continue
            temp_password = secrets.token_urlsafe(12)
            user = User(
                username=username,
                password=make_password(temp_password),
                user_type='STUDENT',
                email=row['email']
            )
            student_users.append((user, temp_password))

        with User.batch_write() as batch:
            for user, _ in student_users:
                batch.save(user)

        for user, temp_password in student_users:
            send_ses_email(
                'Your Student Account',
                f'Username: {user.username}\nTemporary Password: {temp_password}\nChange it after login at /api/change_password/',
                user.email,
                from_email=settings.SES_SENDER  # Explicitly pass from_email
            )
        
        logger.info(f"Uploaded and emailed {len(student_users)} student users")
    except ValueError as ve:
        logger.error(f"Validation error uploading student data: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error uploading student data: {e}")
        raise