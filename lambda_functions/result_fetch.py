import json
from api.result_management import fetch_student_results

def lambda_handler(event, context):
    try:
        student_id = event['pathParameters']['student_id']
        result = fetch_student_results(student_id)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }