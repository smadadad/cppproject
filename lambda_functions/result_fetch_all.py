import json
from api.result_management import fetch_all_results

def lambda_handler(event, context):
    try:
        # Extract username from JWT (via API Gateway auth)
        uploaded_by = event['requestContext']['authorizer']['jwt']['claims']['username']
        result = fetch_all_results(uploaded_by= uploaded_by)
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }