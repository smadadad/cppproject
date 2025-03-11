import csv
from io import StringIO
from result_portal_lib.models import Result
from result_portal_lib.aws_utils import upload_to_s3
import logging

logger = logging.getLogger(__name__)

def upload_results_to_s3_and_dynamodb(file, bucket_name):
    """Upload result CSV to S3 and store in DynamoDB with validation and duplicate check."""
    try:
        if not file.name.endswith('.csv'):
            raise ValueError("File must be a CSV")

        file_key = f'uploads/results/{file.name}'
        upload_to_s3(file, bucket_name, file_key)

        file.seek(0)  # Reset pointer after upload
        csv_content = file.read().decode('utf-8')
        csv_file = StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)

        required_fields = {'student_id', 'subject', 'score', 'grade'}
        if not required_fields.issubset(csv_reader.fieldnames):
            raise ValueError("CSV must contain 'student_id', 'subject', 'score', 'grade'")

        results = []
        for row in csv_reader:
            score = int(row['score'])
            if not (0 <= score <= 100):
                raise ValueError(f"Score {score} for {row['student_id']} must be between 0 and 100")
            try:
                Result.get(row['student_id'], row['subject'])
                logger.warning(f"Skipping existing result: {row['student_id']}, {row['subject']}")
                continue
            except Result.DoesNotExist:
                results.append(Result(
                    student_id=row['student_id'],
                    subject=row['subject'],
                    score=score,
                    grade=row['grade']
                ))

        with Result.batch_write() as batch:
            for result in results:
                batch.save(result)

        logger.info(f"Uploaded {len(results)} new results to DynamoDB")
        return {'message': 'Results uploaded successfully'}
    except ValueError as ve:
        logger.error(f"Validation error uploading results: {ve}")
        raise
    except csv.Error as ce:
        logger.error(f"CSV parsing error uploading results: {ce}")
        raise
    except Exception as e:
        logger.error(f"Error uploading results: {e}")
        raise

def fetch_student_results(student_id):
    """Retrieve results for a specific student."""
    try:
        results = Result.query(student_id)
        serialized = [{'student_id': r.student_id, 'subject': r.subject, 'score': r.score, 'grade': r.grade} for r in results]
        logger.info(f"Retrieved {len(serialized)} results for {student_id}")
        return {'results': serialized}
    except Exception as e:
        logger.error(f"Error retrieving results for {student_id}: {e}")
        raise

def fetch_all_results():
    """Retrieve all results."""
    try:
        results = Result.scan()
        serialized = [{'student_id': r.student_id, 'subject': r.subject, 'score': r.score, 'grade': r.grade} for r in results]
        logger.info(f"Retrieved {len(serialized)} total results")
        return {'results': serialized}
    except Exception as e:
        logger.error(f"Error retrieving all results: {e}")
        raise
