import aioboto3
from typing import Optional, BinaryIO
from configs.settings import settings


async def upload_file_to_s3(file: BinaryIO, path: str) -> Optional[str]:
    session = aioboto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )

    try:
        async with session.client("s3", endpoint_url=settings.AWS_ENDPOINT_URL) as s3:
            await s3.upload_fileobj(file, settings.AWS_BUCKET_NAME, path)
            return f"https://{settings.AWS_GLOBAL_NAME}.{settings.AWS_ENDPOINT_URL.split('//')[1]}/{path}"
    except Exception as e:
        return None
