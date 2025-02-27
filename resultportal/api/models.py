# models.py
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, UTCDateTimeAttribute

class User(Model):
    class Meta:
        table_name = 'Users'
        region = 'your-region'
    
    username = UnicodeAttribute(hash_key=True)
    password = UnicodeAttribute()
    user_type = UnicodeAttribute()

class Result(Model):
    class Meta:
        table_name = 'Results'
        region = 'your-region'
    
    student_id = UnicodeAttribute(hash_key=True)
    subject = UnicodeAttribute(range_key=True)
    score = NumberAttribute()
    grade = UnicodeAttribute()

class Complaint(Model):
    class Meta:
        table_name = 'Complaints'
        region = 'your-region'
    
    id = UnicodeAttribute(hash_key=True)
    student = UnicodeAttribute()
    subject = UnicodeAttribute()
    content = UnicodeAttribute()
    created_at = UTCDateTimeAttribute()
    resolved = BooleanAttribute(default=False)