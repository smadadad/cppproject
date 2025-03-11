import json
from result_portal_lib.complaint_manager import ComplaintManager

def lambda_handler(event, context):
    try:
        cm = ComplaintManager()
        complaints = cm.get_complaints()
        
        return {
            "statusCode": 200,
            "body": json.dumps(complaints)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }