import boto3
from django.conf import settings
import logging
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

logger = logging.getLogger(__name__)
DEFAULT_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def get_s3_client():
    return boto3.client('s3', region_name=DEFAULT_REGION)

def get_sns_client():
    return boto3.client('sns', region_name=DEFAULT_REGION)

def get_ses_client():
    return boto3.client('ses', region_name=DEFAULT_REGION)

def get_dynamodb_resource():
    return boto3.resource('dynamodb', region_name=DEFAULT_REGION)

def upload_to_s3(file, bucket_name, file_key):
    try:
        s3_client = get_s3_client()
        s3_client.upload_fileobj(file, bucket_name, file_key)
        logger.info(f"Successfully uploaded file to S3: {file_key}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Credentials error when uploading to S3: {e}")
        raise
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        raise

def send_ses_email(subject, body, to_email, from_email):
    try:
        ses_client = get_ses_client()
        response = ses_client.send_email(
            Source=from_email,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        logger.info(f"Email sent to {to_email}: {response['MessageId']}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Credentials error when sending SES email: {e}")
        raise
    except ClientError as e:
        logger.error(f"SES error (possibly unverified sender or permissions): {e}")
        raise
    except Exception as e:
        logger.error(f"Error sending SES email to {to_email}: {e}")
        raise

def send_sns_notification(message, subject, topic_arn):
    try:
        sns_client = get_sns_client()
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        logger.info(f"Successfully sent SNS notification: {response['MessageId']}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Credentials error when sending SNS notification: {e}")
        raise
    except Exception as e:
        logger.error(f"Error sending SNS notification: {e}")
        raise

def setup_aws_resources():
    dynamodb = boto3.client('dynamodb', region_name=DEFAULT_REGION)
    s3 = boto3.client('s3', region_name=DEFAULT_REGION)
    sns = boto3.client('sns', region_name=DEFAULT_REGION)
    ses = boto3.client('ses', region_name=DEFAULT_REGION)

    # DynamoDB Tables
    table_definitions = {
        'Users': {
            'KeySchema': [{'AttributeName': 'username', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'username', 'AttributeType': 'S'}]
        },
        'Results': {
            'KeySchema': [
                {'AttributeName': 'student_id', 'KeyType': 'HASH'},
                {'AttributeName': 'subject', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'student_id', 'AttributeType': 'S'},
                {'AttributeName': 'subject', 'AttributeType': 'S'}
            ]
        },
        'Complaints': {
            'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}]
        }
    }

    for table_name, config in settings.DYNAMODB_TABLES.items():
        try:
            dynamodb.describe_table(TableName=table_name)
            logger.info(f"DynamoDB table {table_name} already exists")
        except dynamodb.exceptions.ResourceNotFoundException:
            try:
                table_def = table_definitions[table_name]
                dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=table_def['KeySchema'],
                    AttributeDefinitions=table_def['AttributeDefinitions'],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': config['read_capacity'],
                        'WriteCapacityUnits': config['write_capacity']
                    }
                )
                dynamodb.get_waiter('table_exists').wait(TableName=table_name)
                logger.info(f"Created DynamoDB table {table_name}")
            except Exception as e:
                logger.error(f"Error creating DynamoDB table {table_name}: {e}")
                raise

    # S3 Bucket
    try:
        s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        logger.info(f"S3 bucket {settings.S3_BUCKET_NAME} already exists")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            try:
                s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
                logger.info(f"Created S3 bucket {settings.S3_BUCKET_NAME}")
            except Exception as e:
                logger.error(f"Error creating S3 bucket: {e}")
                raise
        else:
            logger.error(f"Error checking S3 bucket: {e}")
            raise

    # SNS Topic (Programmatic Creation)
    try:
        topics = sns.list_topics()['Topics']
        topic_arn = next((t['TopicArn'] for t in topics if settings.SNS_TOPIC_NAME in t['TopicArn']), None)
        if topic_arn:
            logger.info(f"SNS topic {settings.SNS_TOPIC_NAME} already exists: {topic_arn}")
            settings.AWS_SNS_TOPIC_ARN = topic_arn
        else:
            response = sns.create_topic(Name=settings.SNS_TOPIC_NAME)
            settings.AWS_SNS_TOPIC_ARN = response['TopicArn']
            logger.info(f"Created SNS topic {settings.SNS_TOPIC_NAME}: {settings.AWS_SNS_TOPIC_ARN}")
    except Exception as e:
        logger.error(f"Error setting up SNS topic: {e}")
        raise

    # SES Email Identity (Programmatic Verification, with permission fallback)
    try:
        identities = ses.list_identities(IdentityType='EmailAddress')['Identities']
        if settings.SES_SENDER in identities:
            status = ses.get_identity_verification_attributes(Identities=[settings.SES_SENDER])['VerificationAttributes'][settings.SES_SENDER]
            if status['VerificationStatus'] == 'Success':
                logger.info(f"SES email {settings.SES_SENDER} is already verified")
            else:
                logger.warning(f"SES email {settings.SES_SENDER} exists but is not verified (Status: {status['VerificationStatus']})")
        else:
            ses.verify_email_identity(EmailAddress=settings.SES_SENDER)
            logger.info(f"Requested verification for SES email {settings.SES_SENDER} - check your inbox to confirm")
    except ClientError as e:
        if 'AccessDenied' in str(e):
            logger.warning(f"SES setup skipped: No permission to manage SES identities. Manually verify {settings.SES_SENDER} in AWS SES.")
        else:
            logger.error(f"Error setting up SES email identity: {e}")
            raise
    except Exception as e:
        logger.error(f"Error setting up SES email identity: {e}")
        raise