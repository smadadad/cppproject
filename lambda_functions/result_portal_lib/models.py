from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, UTCDateTimeAttribute
from django.conf import settings
import os

DEFAULT_REGION = os.environ.get('AWS_REGION', 'us-east-1')

class User(Model):
    """
    User model for storing user data in DynamoDB. Password is stored hashed (via admin_functions.py/auth.py).
    Table is created programmatically via aws_utils.setup_aws_resources() if enabled.
    """
    class Meta:
        table_name = 'Users'  # Matches settings.DYNAMODB_TABLES
        region = DEFAULT_REGION
    
    username = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute()  # Stores hashed password (PBKDF2)
    user_type = UnicodeAttribute()  # e.g., 'STUDENT', 'STAFF', 'ADMIN'
    email = UnicodeAttribute(null=False)
    reset_token = UnicodeAttribute(null=True)  # For password reset
    
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def id(self):
        return self.username

class Result(Model):
    """
    Result model for storing student results in DynamoDB.
    Table is created programmatically via aws_utils.setup_aws_resources() if enabled.
    """
    class Meta:
        table_name = 'Results'  # Matches settings.DYNAMODB_TABLES
        region = DEFAULT_REGION
    
    student_id = UnicodeAttribute(hash_key=True)
    subject = UnicodeAttribute(range_key=True)
    score = NumberAttribute()
    grade = UnicodeAttribute()

class Complaint(Model):
    """
    Complaint model for storing student complaints in DynamoDB.
    Table is created programmatically via aws_utils.setup_aws_resources() if enabled.
    """
    class Meta:
        table_name = 'Complaints'  # Matches settings.DYNAMODB_TABLES
        region = DEFAULT_REGION
    
    id = UnicodeAttribute(hash_key=True)
    student = UnicodeAttribute(null=False)  # Ensure non-null
    subject = UnicodeAttribute(null=False)  # Ensure non-null
    content = UnicodeAttribute(null=False)  # Ensure non-null
    created_at = UTCDateTimeAttribute()
    resolved = BooleanAttribute(default=False)