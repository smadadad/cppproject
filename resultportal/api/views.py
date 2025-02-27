# views.py
import json
import boto3
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User, Result, Complaint
from datetime import datetime

s3 = boto3.client('s3')
sns = boto3.client('sns')

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_results(request):
    if request.method == 'POST':
        csv_file = request.FILES['file']
        
        # Upload file to S3
        s3.upload_fileobj(csv_file, 'your-bucket-name', f'uploads/{csv_file.name}')
        
        return JsonResponse({'message': 'File uploaded successfully'})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_complaint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        complaint = Complaint(
            id=str(datetime.utcnow().timestamp()),
            student=request.user.username,
            subject=data['subject'],
            content=data['content'],
            created_at=datetime.utcnow(),
            resolved=False
        )
        complaint.save()
        
        # Send notification to teacher via SNS
        sns.publish(
            TopicArn='arn:aws:sns:region:account-id:TeacherNotifications',
            Message=f"New complaint submitted for {data['subject']}",
            Subject='New Complaint Notification'
        )
        
        return JsonResponse({'message': 'Complaint submitted successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_results(request):
    results = Result.query(request.user.username)
    return JsonResponse({'results': [dict(result) for result in results]})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_results(request):
    if request.user.user_type != 'STAFF':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    results = Result.scan()
    return JsonResponse({'results': [dict(result) for result in results]})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_complaints(request):
    if request.user.user_type != 'STAFF':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    complaints = Complaint.scan()
    return JsonResponse({'complaints': [dict(complaint) for complaint in complaints]})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_complaint(request, complaint_id):
    if request.method == 'POST':
        if request.user.user_type != 'STAFF':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        complaint = Complaint.get(complaint_id)
        complaint.resolved = True
        complaint.save()
        return JsonResponse({'message': 'Complaint resolved successfully'})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_staff(request):
    if request.method == 'POST':
        if request.user.user_type != 'ADMIN':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        csv_file = request.FILES['file']
        
        # Process and store staff data
        # This is a placeholder for the actual implementation
        
        return JsonResponse({'message': 'Staff data uploaded successfully'})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_students(request):
    if request.method == 'POST':
        if request.user.user_type != 'ADMIN':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        csv_file = request.FILES['file']
        
        # Process and store student data
        # This is a placeholder for the actual implementation
        
        return JsonResponse({'message': 'Student data uploaded successfully'})