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
            use_gcs = os.getenv("GCP_ACTIVE", "false").lower() == "true"
            if not use_gcs:
                print("GCS feature flag is disabled. GCS will not be initialized.")
                self.storage_client = None
                self.bucket = None
                return

            json_path = os.getenv("GCP_CREDENTIALS_JSON")
            emulator_host = os.getenv("GCP_STORAGE_EMULATOR_HOST")

            if json_path and os.path.isfile(json_path):
                credentials = service_account.Credentials.from_service_account_file(json_path)
                client_options = None
            elif emulator_host:
                credentials = AnonymousCredentials()
                client_options = {"api_endpoint": emulator_host}
            else:
                raise RuntimeError("Neither a valid GCP_CREDENTIALS_JSON file nor STORAGE_EMULATOR_HOST is set. One is required.")

            self.storage_client = storage.Client(credentials=credentials, client_options=client_options) if credentials or client_options else storage.Client()

            self.gcp_bucket_name = os.getenv("GCP_BUCKET_NAME")
            if not self.gcp_bucket_name:
                raise ValueError("GCP_BUCKET_NAME environment variable is not set.")

            # Create bucket if using emulator and it doesn't exist
            if json_path and os.path.isfile(json_path):
                try:
                    self.bucket = self.storage_client.get_bucket(self.gcp_bucket_name)
                except Exception:
                    self.bucket = self.storage_client.create_bucket(self.gcp_bucket_name)
            else:
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
