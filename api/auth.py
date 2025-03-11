from django.contrib.auth.backends import BaseBackend
from result_portal_lib.models import User as PynamoUser
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import logging

logger = logging.getLogger(__name__)
DjangoUser = get_user_model()

class DynamoDBAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info(f"Starting authentication for username: {username}, password provided: {bool(password)}")
        if not username or not password:
            logger.warning("Username or password missing in authentication request")
            return None
        
        try:
            logger.debug(f"Attempting to fetch user from DynamoDB with username: {username}")
            pynamo_user = PynamoUser.get(username)
            logger.info(f"User found: {username}, stored password hash: {pynamo_user.password}")
            
            if check_password(password, pynamo_user.password):
                logger.info(f"Password verification successful for {username}")
                django_user, created = DjangoUser.objects.get_or_create(username=username)
                django_user.is_active = True
                django_user.user_type = pynamo_user.user_type  # Set dynamically
                logger.debug(f"Django user prepared: is_active={django_user.is_active}, id={django_user.id}, user_type={django_user.user_type}")
                return django_user
            else:
                logger.info(f"Password verification failed for {username}")
                return None
        except PynamoUser.DoesNotExist:
            logger.info(f"User {username} not found in DynamoDB")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication for {username}: {str(e)}")
            return None

    def get_user(self, username):
        logger.info(f"Starting get_user for username: {username}")
        try:
            logger.debug(f"Fetching user from Django ORM with username: {username}")
            django_user = DjangoUser.objects.get(username=username)
            logger.info(f"User retrieved: {username}")
            django_user.is_active = True
            if not hasattr(django_user, 'user_type'):  # Fetch if not set
                pynamo_user = PynamoUser.get(username)
                django_user.user_type = pynamo_user.user_type
            logger.debug(f"Django user prepared: is_active={django_user.is_active}, id={django_user.id}, user_type={django_user.user_type}")
            return django_user
        except DjangoUser.DoesNotExist:
            logger.info(f"User {username} not found in Django ORM")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_user for {username}: {str(e)}")
            return None