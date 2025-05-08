from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import hashlib
from s3 import upload_file_to_s3
import utils
from datetime import datetime

app = FastAPI(title="Media API")

origins = [
    "http://localhost:3000",  # Замени на адрес твоего фронтенда
]

# убрать нахуй после тестирования
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_media(request: Request, file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png"]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    user_id = await utils.get_self_id(request.cookies)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    filename = (
        str(
            hashlib.sha1(
                (
                    str(user_id) + str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
                ).encode("utf-8")
            ).hexdigest()
        )
        + "."
        + file.filename.split(".")[-1]
    )
    path = f"uploads/{filename}"

    try:
        url = await upload_file_to_s3(file.file, path)
        if not url:
            raise HTTPException(status_code=500, detail="Failed to upload file")
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
