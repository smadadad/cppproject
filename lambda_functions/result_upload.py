import json
import base64
from api.result_management import upload_results_to_s3_and_dynamodb
import io

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        file_content = base64.b64decode(body['file'])
        bucket_name = body['bucket_name']
        
        # Extract username from JWT (via API Gateway authorizer)
        uploaded_by = event['requestContext']['authorizer']['jwt']['claims']['username']
        
        file = io.BytesIO(file_content)
        file.name = 'results.csv'
        
        result = upload_results_to_s3_and_dynamodb(file, bucket_name, uploaded_by)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }