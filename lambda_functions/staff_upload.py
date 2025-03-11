import json
import base64
from api.admin_functions import upload_staff_data
import io

def lambda_handler(event, context):
    try:
        # Parse event (assume API Gateway sends base64-encoded file)
        body = json.loads(event['body'])
        file_content = base64.b64decode(body['file'])
        bucket_name = body['bucket_name']
        
        # Convert to file-like object
        file = io.BytesIO(file_content)
        file.name = 'staff.csv'  # Set a name for validation
        
        # Call existing function
        upload_staff_data(file, bucket_name)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Staff uploaded successfully"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }