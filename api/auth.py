from django.contrib.auth.backends import BaseBackend
from result_portal_lib.models import User  # Your PynamoDB User model
from django.contrib.auth.hashers import check_password
import logging

logger = logging.getLogger(__name__)

class DynamoDBAuthBackend(BaseBackend): 
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user against DynamoDB using username and password.
        Returns the PynamoDB User object if credentials are valid.
        """
        logger.info(f"Starting authentication for username: {username}, password provided: {bool(password)}")
        if not username or not password:
            logger.warning("Username or password missing in authentication request")
            return None
        
        try:
            logger.debug(f"Attempting to fetch user from DynamoDB with username: {username}")
            pynamo_user = User.get(username)
            logger.info(f"User found: {username}, stored password hash: {pynamo_user.password}")
            
            if check_password(password, pynamo_user.password):
                logger.info(f"Password verification successful for {username}")
                logger.debug(f"User prepared: is_active={pynamo_user.is_active}, id={pynamo_user.id}, user_type={pynamo_user.user_type}")
                return pynamo_user
            else:
                logger.info(f"Password verification failed for {username}")
                return None
        except User.DoesNotExist:
            logger.info(f"User {username} not found in DynamoDB")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication for {username}: {str(e)}")
            return None

    def get_user(self, user_id):
        """
        Retrieve a user by ID (username) from DynamoDB for session support.
        """
        try:
            logger.debug(f"Fetching user by ID: {user_id}")
            user = User.get(user_id)
            logger.info(f"User retrieved: {user_id}")
            return user
        except User.DoesNotExist:
            logger.info(f"User {user_id} not found in DynamoDB")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            return None