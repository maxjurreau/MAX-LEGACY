"""
Minimal R2 (S3-compatible) storage adapter.
Uses boto3 compatible client — Cloudflare R2 supports S3-compatible APIs.
When running in Cloudflare Workers with a native binding, replace this adapter with the native API.
"""

import os
import logging
from typing import List, Dict
try:
    import boto3
    from botocore.client import Config
except Exception:
    boto3 = None  # In Cloudflare Workers, boto3 isn't available; replace with binding.

logger = logging.getLogger("r2_adapter")
R2_ENDPOINT = os.getenv("R2_ENDPOINT", None)  # e.g., https://<account>.r2.cloudflarestorage.com
R2_REGION = os.getenv("R2_REGION", "auto")

class R2StorageAdapter:
    def __init__(self, bucket_name: str):
        self.bucket = bucket_name
        self.client = None
        if boto3 and R2_ENDPOINT:
            self.client = boto3.client(
                "s3",
                endpoint_url=R2_ENDPOINT,
                config=Config(signature_version="s3v4"),
                aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
                region_name=R2_REGION,
            )
        else:
            logger.warning("boto3 or R2_ENDPOINT not configured; using in-memory fallback")
            self._store = {}

    def put_object(self, key: str, data: bytes, content_type: str = "application/octet-stream"):
        if self.client:
            self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)
        else:
            self._store[key] = {"data": data, "content_type": content_type}
        logger.debug("put_object", extra={"key": key})

    def get_object(self, key: str) -> bytes:
        if self.client:
            resp = self.client.get_object(Bucket=self.bucket, Key=key)
            return resp["Body"].read()
        return self._store.get(key, {}).get("data")

    def list_objects(self, prefix: str = "") -> List[Dict]:
        if self.client:
            resp = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            items = []
            for o in resp.get("Contents", []):
                items.append({
                    "key": o["Key"],
                    "size": o["Size"],
                    "last_modified": int(o["LastModified"].timestamp())
                })
            return items
        return [{"key": k, "size": len(v["data"]), "last_modified": None} for k, v in self._store.items() if k.startswith(prefix)]

    def delete_object(self, key: str):
        if self.client:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        else:
            self._store.pop(key, None)
        logger.debug("delete_object", extra={"key": key})
