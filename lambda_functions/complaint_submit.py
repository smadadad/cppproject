import json
from result_portal_lib.complaint_manager import ComplaintManager

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        subject = body['subject']
        content = body['content']
        student = body.get('student', 'anonymous')  # Default if not provided
        
        cm = ComplaintManager()
        complaint = cm.submit_complaint(subject, content)
        complaint.student = student  # Update placeholder
        complaint.save()
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Complaint submitted", "id": complaint.id})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }