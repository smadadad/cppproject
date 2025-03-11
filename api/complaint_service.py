import logging
from result_portal_lib.models import Complaint
from result_portal_lib.aws_utils import send_sns_notification
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class ComplaintManager:
    """Handles complaint-related operations with DynamoDB and SNS notifications."""
    def __init__(self, sns_client=None):
        self.sns_client = sns_client  # For testing, unused here

    def submit_complaint(self, subject, content):
        try:
            if not subject or not content:
                raise ValueError("Subject and content are required")
            if len(subject) > 100 or len(content) > 1000:
                raise ValueError("Subject or content exceeds length limits")

            complaint = Complaint(
                id=str(datetime.utcnow().timestamp()),
                student='placeholder',
                subject=subject,
                content=content,
                created_at=datetime.utcnow(),
                resolved=False
            )
            complaint.save()
            self.notify_teachers(complaint)
            logger.info(f"Submitted complaint: {complaint.id}")
            return complaint
        except ValueError as ve:
            logger.error(f"Validation error submitting complaint: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error submitting complaint: {e}")
            raise

    def resolve_complaint(self, complaint_id):
        try:
            complaint = Complaint.get(complaint_id)
            complaint.resolved = True
            complaint.save()
            logger.info(f"Resolved complaint: {complaint_id}")
            return complaint
        except Complaint.DoesNotExist:
            logger.error(f"Complaint not found: {complaint_id}")
            raise
        except Exception as e:
            logger.error(f"Error resolving complaint: {e}")
            raise

    def get_complaints(self):
        try:
            complaints = Complaint.scan()
            return {'complaints': [self._serialize_complaint(c) for c in complaints]}
        except Exception as e:
            logger.error(f"Error retrieving complaints: {e}")
            raise

    def notify_teachers(self, complaint):
        try:
            message = f"New complaint from {complaint.student} about {complaint.subject}"
            send_sns_notification(
                message=message,
                subject="New Student Complaint",
                topic_arn=settings.AWS_SNS_TOPIC_ARN
            )
            logger.info(f"Notified teachers via SNS for complaint: {complaint.id}")
        except Exception as e:
            logger.error(f"Error notifying teachers via SNS: {e}")
            raise

    def _serialize_complaint(self, complaint):
        return {
            'id': complaint.id,
            'student': complaint.student,
            'subject': complaint.subject,
            'content': complaint.content,
            'created_at': complaint.created_at.isoformat(),
            'resolved': complaint.resolved
        }