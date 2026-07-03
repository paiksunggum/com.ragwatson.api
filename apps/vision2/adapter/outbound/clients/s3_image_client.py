from __future__ import annotations

import asyncio
import logging
import os
import uuid

import boto3

from apps.vision2.app.ports.output.image_storage_port import ImageStoragePort

logger = logging.getLogger("apps")


class S3ImageClient(ImageStoragePort):
    def __init__(self) -> None:
        self._bucket = os.getenv("S3_BUCKET_NAME", "")
        self._region = os.getenv("AWS_REGION", "ap-northeast-2")
        self._client = boto3.client("s3", region_name=self._region)

    def _put_object(self, key: str, content: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
        )

    async def upload(self, filename: str, content: bytes, content_type: str) -> str:
        if not self._bucket:
            raise RuntimeError("S3_BUCKET_NAME이 설정되어 있지 않습니다.")

        key = f"vision2/{uuid.uuid4()}_{filename}"
        await asyncio.to_thread(self._put_object, key, content, content_type)
        url = f"https://{self._bucket}.s3.{self._region}.amazonaws.com/{key}"
        logger.info("[S3ImageClient] 업로드 완료 key=%s url=%s", key, url)
        return url
