import hashlib
import logging
from django.conf import settings

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def _sanitize_key(file_key: str) -> str:
    """Return a truncated SHA256 hash of the key for safe logging."""
    return hashlib.sha256(file_key.encode()).hexdigest()[:12]


class KYCStorageService:
    """
    Service Layer for interacting with S3-compatible cloud storage.
    Enforces security protocols for sensitive KYC document retrieval.
    """

    @staticmethod
    def get_presigned_url(file_key: str, expiry: int = 900) -> str | None:
        """
        Generates a short-lived (Pre-signed) URL for private objects.
        
        Args:
            file_key (str): The full path/key of the file in the bucket.
            expiry (int): TTL in seconds (default 900s = 15m).
            
        Returns:
            str | None: Secure URL if successful, None otherwise.
        """
        if not file_key:
            return None

        try:
            # Initialize boto3 client with Django settings
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
                aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
                region_name=getattr(settings, "AWS_S3_REGION_NAME", "me-central-1"),
                endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
            )

            # Generate the URL for a 'get_object' operation
            bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
            if not bucket_name:
                logger.error("AWS_STORAGE_BUCKET_NAME not configured.")
                return None

            response = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": file_key,
                },
                ExpiresIn=expiry,
            )
            return response
        except ClientError:
            logger.exception(
                "Error generating pre-signed URL for file [%s]",
                _sanitize_key(file_key),
            )
            return None
        except Exception:
            logger.exception("Unexpected error in KYCStorageService")
            raise

