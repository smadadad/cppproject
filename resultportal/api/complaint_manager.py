import boto3
from django.conf import settings
from .models import Complaint, User

class ComplaintManager:
    def __init__(self):
        self.sns_client = boto3.client('sns', region_name=settings.AWS_REGION)

    def create_complaint(self, student, subject, content):
        complaint = Complaint.objects.create(
            student=student,
            subject=subject,
            content=content
        )
        self.notify_teachers(complaint)
        return complaint

    def resolve_complaint(self, complaint_id):
        complaint = Complaint.objects.get(id=complaint_id)
        complaint.resolved = True
        complaint.save()
        return complaint

    def notify_teachers(self, complaint):
        teachers = User.objects.filter(role='TEACHER')
        for teacher in teachers:
            self.send_sns_notification(teacher.email, complaint)

    def send_sns_notification(self, email, complaint):
        message = f"New complaint from {complaint.student.get_full_name()} about {complaint.subject}"
        self.sns_client.publish(
            TopicArn=settings.AWS_SNS_TOPIC_ARN,
            Message=message,
            Subject="New Student Complaint",
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email
                }
            }
        )