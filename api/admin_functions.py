# ~/environment/resultportal/api/admin_functions.py
import csv
from result_portal_lib.models import User
from result_portal_lib.aws_utils import upload_to_s3, subscribe_to_sns, publish_sns_message
from django.conf import settings
from django.contrib.auth.hashers import make_password
import secrets
import logging

logger = logging.getLogger(__name__)

def upload_staff_data(file, bucket_name):
    """Upload staff CSV data to S3 and create STAFF users in DynamoDB with SNS notifications."""
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

        # Use FRONTEND_URL from settings
        FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'https://yourdomain.com')
        for user, temp_password in staff_users:
            subscribe_to_sns(user.email)  # Subscribe staff to SNS topic
            message = (
                f"Welcome! Your staff account is created.\n"
                f"Username: {user.username}\n"
                f"Temporary Password: {temp_password}\n"
                f"Change it after login at {FRONTEND_URL}/change-password"
            )
            publish_sns_message(
                'Your Staff Account',
                message,
                user.email
            )
        
        logger.info(f"Uploaded and notified {len(staff_users)} staff users via SNS")
    except ValueError as ve:
        logger.error(f"Validation error uploading staff data: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error uploading staff data: {e}")
        raise

def upload_student_data(file, bucket_name):
    """Upload student CSV data to S3 and create STUDENT users in DynamoDB with SNS notifications."""
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

        # Use FRONTEND_URL from settings
        FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'https://yourdomain.com')
        for user, temp_password in student_users:
            subscribe_to_sns(user.email)  # Subscribe student to SNS topic
            message = (
                f"Welcome! Your student account is created.\n"
                f"Username: {user.username}\n"
                f"Temporary Password: {temp_password}\n"
                f"Change it after login at {FRONTEND_URL}/change-password"
            )
            publish_sns_message(
                'Your Student Account',
                message,
                user.email
            )
        
        logger.info(f"Uploaded and notified {len(student_users)} student users via SNS")
    except ValueError as ve:
        logger.error(f"Validation error uploading student data: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error uploading student data: {e}")
        raise