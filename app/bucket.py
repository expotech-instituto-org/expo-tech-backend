import os
import uuid
from typing import Optional
from urllib.parse import urlparse

from fastapi import UploadFile
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from google.oauth2 import service_account


class GCSBucketManager:

    def __init__(self):
        try:
            emulator_host = os.getenv("GCP_STORAGE_EMULATOR_HOST")

            if not emulator_host:
                credentials_info = {
                    "type": os.getenv("TYPE"),
                    "project_id": os.getenv("PROJECT_ID"),
                    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
                    "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
                    "client_email": os.getenv("CLIENT_EMAIL"),
                    "client_id": os.getenv("CLIENT_ID"),
                    "auth_uri": os.getenv("AUTH_URI"),
                    "token_uri": os.getenv("TOKEN_URI"),
                    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
                    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
                    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
                }

                if not all(credentials_info.values()):
                    raise RuntimeError("Missing one or more required GCP service account environment variables.")

                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                client_options = None
            else:
                credentials = AnonymousCredentials()
                client_options = {"api_endpoint": emulator_host}

            self.storage_client = storage.Client(credentials=credentials, client_options=client_options)

            self.gcp_bucket_name = os.getenv("GCP_BUCKET_NAME")
            if not self.gcp_bucket_name:
                raise ValueError("GCP_BUCKET_NAME environment variable is not set.")

            self.bucket = self.storage_client.bucket(self.gcp_bucket_name)

            # Ping: try to list blobs to test connection
            _ = list(self.bucket.list_blobs(max_results=1))
            print("Google Cloud Storage client initialized and connection verified.")
        except Exception as e:
            print(f"Error initializing Google Cloud Storage client: {e}")
            self.storage_client = None
            self.bucket = None

    async def delete_image(self, image_url: str):
        if not self.storage_client or not self.bucket:
            print("Warning: GCS is not enabled or not properly configured. Skipping image deletion.")
            return

        try:
            parsed_url = urlparse(image_url)
            blob_name = os.path.basename(parsed_url.path)
            if blob_name:
                blob = self.bucket.blob(blob_name)
                if blob.exists():
                    blob.delete()
                    print(f"Deleted image '{blob_name}' from GCS.")
                else:
                    print(f"Blob '{blob_name}' does not exist in GCS.")
            else:
                print("Could not parse blob name from image URL.")
        except Exception as e:
            print(f"Error deleting image from GCS: {e}")

    async def upload_image(
        self,
        image: UploadFile,
        image_to_replace: Optional[str]=None,
        folder: Optional[str]=None
    ) -> Optional[str]:
        if not self.storage_client or not self.bucket:
            print("Warning: GCS is not enabled or not properly configured. Skipping image upload.")
            return None

        # --- Delete old image if it exists ---
        if image_to_replace:
            old_blob_name = ""
            try:
                parsed_url = urlparse(image_to_replace)
                old_blob_name = os.path.basename(parsed_url.path)
                if old_blob_name:
                    old_blob = self.bucket.blob(old_blob_name)
                    if old_blob.exists():
                        old_blob.delete()
            except Exception as e:
                print(f"Warning: Could not delete old GCS object '{old_blob_name}': {e}")

        # --- Upload new image ---
        folder = (folder or "").strip("/")
        unique_filename = f"{'public/' + folder + '/' if folder else ''}{uuid.uuid4()}-{image.filename}"
        blob = self.bucket.blob(unique_filename)

        await image.seek(0)
        blob.upload_from_file(image.file, content_type=image.content_type)

        return blob.public_url

    async def generate_signed_url(self, blob_name: str, expiration: int = 3600) -> str:
        if not self.storage_client or not self.bucket:
            print("Warning: GCS is not enabled or not properly configured. Skipping signed URL generation.")
            return ""
        try:
            blob = self.bucket.blob(blob_name)
            url = blob.generate_signed_url(expiration=expiration)
            return url
        except Exception as e:
            print(f"Error generating signed URL for blob '{blob_name}': {e}")
            return ""

# For backward compatibility, you can instantiate a default manager and expose the function
_gcs_manager = GCSBucketManager()
upload_image = _gcs_manager.upload_image
delete_image = _gcs_manager.delete_image
