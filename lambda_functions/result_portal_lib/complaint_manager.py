import boto3
from django.conf import settings
from result_portal_lib.models import Complaint, User  # PynamoDB models
from result_portal_lib.aws_utils import send_sns_notification  # Use aws_utils
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ComplaintManager:
    """
    ComplaintManager handles all complaint-related operations, including submission,
    resolution, retrieval, and teacher notifications via AWS SNS. Designed for use
    in a Django library with frontend API compatibility, using PynamoDB for DynamoDB.
    """

    def __init__(self, sns_client=None):
        """
        Initialize the ComplaintManager with an optional SNS client for dependency injection.

        Args:
            sns_client: Optional boto3 SNS client instance (defaults to settings-based client).
        """
        self.sns_client = sns_client or boto3.client('sns')

    def submit_complaint(self, subject, content):
        """
        Submit a new complaint and notify teachers via SNS topic. Student is set in views.

        Args:
            subject: The subject of the complaint (string).
            content: The content of the complaint (string).

        Returns:
            Complaint: The created complaint object.

        Raises:
            ValueError: If subject or content is empty.
            Exception: If complaint creation or notification fails.
        """
        try:
            # Validate inputs
            if not subject or not content:
                raise ValueError("Subject and content are required")
            if len(subject) > 100 or len(content) > 1000:  # Example limits
                raise ValueError("Subject or content exceeds length limits")

            # Create complaint with PynamoDB (student set in views.py)
            complaint = Complaint(
                id=str(datetime.utcnow().timestamp()),  # Unique ID for DynamoDB
                student='placeholder',  # Updated in views
                subject=subject,
                content=content,
                created_at=datetime.utcnow(),
                resolved=False
            )
            complaint.save()  # PynamoDB save method

            # Notify teachers using aws_utils
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
        """
        Resolve a specific complaint by marking it as resolved.

        Args:
            complaint_id: The ID of the complaint to resolve (string).

        Returns:
            Complaint: The resolved complaint object.

        Raises:
            Complaint.DoesNotExist: If the complaint is not found.
            Exception: If resolution fails.
        """
        try:
            # Retrieve and update with PynamoDB
            complaint = Complaint.get(complaint_id)  # PynamoDB get method
            complaint.resolved = True
            complaint.save()  # PynamoDB save method
            logger.info(f"Resolved complaint: {complaint_id}")
            return complaint
        except Complaint.DoesNotExist:
            logger.error(f"Complaint not found: {complaint_id}")
            raise
        except Exception as e:
            logger.error(f"Error resolving complaint: {e}")
            raise

    def get_complaints(self):
        """
        Retrieve all complaints for staff dashboard.

        Returns:
            dict: A dictionary with 'complaints' key containing a list of serialized complaints.

        Raises:
            Exception: If retrieval fails.
        """
        try:
            # Fetch all complaints with PynamoDB scan
            complaints = Complaint.scan()  # PynamoDB scan method
            return {'complaints': [self._serialize_complaint(c) for c in complaints]}
        except Exception as e:
            logger.error(f"Error retrieving complaints: {e}")
            raise

    def notify_teachers(self, complaint):
        """
        Notify teachers about a new complaint via SNS topic using aws_utils.

        Args:
            complaint: The complaint object to notify about.

        Raises:
            Exception: If SNS notification fails.
        """
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

    def serialize_complaint(self, complaint):
        """
        Serialize a complaint object into a dictionary for frontend compatibility.

        Args:
            complaint: The complaint object to serialize.

        Returns:
            dict: Serialized complaint data.
        """
        return {
            'id': complaint.id,
            'student': complaint.student,
            'subject': complaint.subject,
            'content': complaint.content,
            'created_at': complaint.created_at.isoformat(),  # ISO string for frontend
            'resolved': complaint.resolved
        }