from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from django.conf import settings
        if getattr(settings, 'PROGRAMMATIC_AWS_SETUP', False):
            try:
                from result_portal_lib.aws_utils import setup_aws_resources
                setup_aws_resources()
                logger.info("AWS resources setup completed successfully")
            except Exception as e:
                logger.error(f"Failed to setup AWS resources on startup: {e}")
        else:
            logger.info("PROGRAMMATIC_AWS_SETUP is False; skipping AWS resource setup")