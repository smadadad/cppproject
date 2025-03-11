import json
import base64
from api.admin_functions import upload_student_data
import io

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        file_content = base64.b64decode(body['file'])
        bucket_name = body['bucket_name']
        
        file = io.BytesIO(file_content)
        file.name = 'students.csv'
        
        upload_student_data(file, bucket_name)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Students uploaded successfully"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }