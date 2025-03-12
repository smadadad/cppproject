# ~/environment/resultportal/api/views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from result_portal_lib.complaint_manager import ComplaintManager  # Corrected import
from .admin_functions import upload_staff_data, upload_student_data
from .result_management import upload_results_to_s3_and_dynamodb, fetch_student_results, fetch_all_results
from result_portal_lib.models import Result, User, Complaint  # Added Complaint for potential direct use
from result_portal_lib.aws_utils import subscribe_to_sns, publish_sns_message
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import secrets
import logging
import json
import csv
from io import TextIOWrapper
from datetime import datetime

logger = logging.getLogger(__name__)
complaint_manager = ComplaintManager()
FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'https://yourdomain.com')  # Default if not set

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_results_view(request):
    """Upload student results CSV (teacher only) and notify students via SNS."""
    try:
        if request.user.user_type != 'STAFF':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_by = request.user.username
        upload_results_to_s3_and_dynamodb(csv_file, settings.S3_BUCKET_NAME, uploaded_by)
        
        # Parse CSV to notify students
        csv_file.seek(0)
        reader = csv.DictReader(TextIOWrapper(csv_file, 'utf-8'))
        for row in reader:
            student_email = row.get('email')  # Assumes CSV has 'email'
            if student_email:
                message = f"Your results are ready! Log in: {FRONTEND_URL}/login"
                publish_sns_message("Results Ready", message, student_email)
        
        return JsonResponse({'message': 'File uploaded and students notified successfully'})
    except Exception as e:
        logger.error(f"Error in upload_results_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_results_view(request):
    """Get results for the authenticated student."""
    try:
        student_id = request.user.username
        logger.info(f"Fetching results for student_id: {student_id}")
        results = Result.scan(filter_condition=Result.student_id == student_id)
        results_list = [
            {"student_id": r.student_id, "subject": r.subject, "score": r.score, "grade": r.grade}
            for r in results
        ]
        logger.info(f"Found {len(results_list)} results for {student_id}")
        return Response({"results": results_list})
    except Exception as e:
        logger.error(f"Error in get_student_results_view: {e}")
        return Response({"results": [], "error": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_results_view(request):
    """Get all results (staff only)."""
    try:
        if request.user.user_type != 'STAFF':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        results = fetch_all_results()
        return JsonResponse(results)
    except Exception as e:
        logger.error(f"Error in get_all_results_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_complaint_view(request):
    """Submit a student complaint with validation and teacher notification."""
    try:
        data = json.loads(request.body)
        complaint = complaint_manager.submit_complaint(data['subject'], data['content'])
        complaint.student = request.user.username  # Set student after validation
        complaint.save()
        return JsonResponse({'message': 'Complaint submitted successfully'})
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)
    except Exception as e:
        logger.error(f"Error in submit_complaint_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_complaints_view(request):
    """Get all complaints (staff only)."""
    try:
        if request.user.user_type != 'STAFF':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return JsonResponse(complaint_manager.get_complaints())
    except Exception as e:
        logger.error(f"Error in get_complaints_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_complaint_view(request, complaint_id):
    """Resolve a complaint (staff only)."""
    try:
        if request.user.user_type != 'STAFF':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        complaint_manager.resolve_complaint(complaint_id)
        return JsonResponse({'message': 'Complaint resolved successfully'})
    except Complaint.DoesNotExist:
        return JsonResponse({'error': 'Complaint not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in resolve_complaint_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_staff_view(request):
    """Upload staff data CSV (admin only)."""
    try:
        if request.user.user_type != 'ADMIN':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        upload_staff_data(csv_file, settings.S3_BUCKET_NAME)
        return JsonResponse({'message': 'Staff data uploaded successfully'})
    except Exception as e:
        logger.error(f"Error in upload_staff_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_students_view(request):
    """Upload student data CSV (admin only) and notify via SNS."""
    try:
        if request.user.user_type != 'ADMIN':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        upload_student_data(csv_file, settings.S3_BUCKET_NAME)
        
        # Parse CSV to notify students
        csv_file.seek(0)
        reader = csv.DictReader(TextIOWrapper(csv_file, 'utf-8'))
        for row in reader:
            email = row.get('email')
            if email:
                subscribe_to_sns(email)
                message = f"Welcome! Your account was created. Log in: {FRONTEND_URL}/login"
                publish_sns_message("Welcome to Result Portal", message, email)
        
        return JsonResponse({'message': 'Student data uploaded and users notified successfully'})
    except Exception as e:
        logger.error(f"Error in upload_students_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
def password_reset_request(request):
    """Request a password reset link via SNS."""
    username = request.data.get('username')
    try:
        user = User.get(username)
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.save()
        reset_url = f"{FRONTEND_URL}/reset?token={reset_token}"
        publish_sns_message(
            'Password Reset Request',
            f'Click to reset your password: {reset_url}',
            user.email
        )
        return Response({'message': 'Reset link sent to your email'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in password_reset_request: {e}")
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def password_reset_confirm(request):
    """Confirm password reset with token."""
    token = request.query_params.get('token')
    new_password = request.data.get('password')
    try:
        user = User.scan(filter_condition=User.reset_token == token).next()
        user.password = make_password(new_password)
        user.reset_token = None
        user.save()
        return Response({'message': 'Password reset successful'})
    except StopIteration:
        return Response({'error': 'Invalid or expired token'}, status=400)
    except Exception as e:
        logger.error(f"Error in password_reset_confirm: {e}")
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for authenticated user."""
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    try:
        pynamo_user = User.get(request.user.username)
        if check_password(current_password, pynamo_user.password):
            pynamo_user.password = make_password(new_password)
            pynamo_user.save()
            return Response({'message': 'Password changed successfully'})
        else:
            return Response({'error': 'Current password is incorrect'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in change_password: {e}")
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def register_user(request):
    """Self-registration for new users with SNS welcome."""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    user_type = request.data.get('user_type', 'STUDENT')
    try:
        User.get(username)
        return Response({'error': 'Username already exists'}, status=400)
    except User.DoesNotExist:
        pass
    
    try:
        user = User(
            username=username,
            email=email,
            password=make_password(password),
            user_type=user_type
        )
        user.save()
        subscribe_to_sns(email)
        message = f"Welcome! Your account is created. Log in: {FRONTEND_URL}/login"
        publish_sns_message('Welcome to Result Portal', message, email)
        return Response({'message': 'User registered successfully'})
    except Exception as e:
        logger.error(f"Error in register_user: {e}")
        return Response({'error': str(e)}, status=400)

def get_admin_results_view(request):
    """Get all results for admin."""
    try:
        results = fetch_all_results()
        return JsonResponse(results)
    except Exception as e:
        logger.error(f"Error in get_admin_results_view: {e}")
        return JsonResponse({'error': str(e)}, status=400)