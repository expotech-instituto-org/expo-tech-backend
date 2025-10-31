import os
import uuid
from typing import Optional
from urllib.parse import urlparse

from fastapi import UploadFile
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage


class GCSBucketManager:

    def __init__(self):
        try:
            emulator_host = os.getenv("STORAGE_EMULATOR_HOST")
            if emulator_host:
                self.storage_client = storage.Client(
                    credentials=AnonymousCredentials(),
                    client_options={"api_endpoint": emulator_host}
                )
            else:
                self.storage_client = storage.Client()

            self.gcp_bucket_name = os.getenv("GCP_BUCKET_NAME")
            if not self.gcp_bucket_name:
                raise ValueError("GCP_BUCKET_NAME environment variable is not set.")

            # Create bucket if using emulator and it doesn't exist
            if emulator_host:
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

    async def upload_image(
        self,
        image: UploadFile,
        image_to_replace: Optional[str]=None,
        folder: Optional[str]=None
    ) -> str:
        if not self.storage_client:
            raise RuntimeError("Storage service is not configured.")

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
        unique_filename = f"{folder + '/' if folder else ''}{uuid.uuid4()}-{image.filename}"
        blob = self.bucket.blob(unique_filename)

        await image.seek(0)
        blob.upload_from_file(image.file, content_type=image.content_type)
        blob.make_public()

        return blob.public_url

# For backward compatibility, you can instantiate a default manager and expose the function
_gcs_manager = GCSBucketManager()
upload_image = _gcs_manager.upload_image
