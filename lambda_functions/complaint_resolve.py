import json
from result_portal_lib.complaint_manager import ComplaintManager

def lambda_handler(event, context):
    try:
        complaint_id = event['pathParameters']['complaint_id']
        cm = ComplaintManager()
        complaint = cm.resolve_complaint(complaint_id)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Complaint resolved", "id": complaint.id})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }