import os
from typing import Any

from fastapi import APIRouter
from starlette.responses import StreamingResponse, FileResponse

from app.definitions import MEDIA_ROOT_DIR, ROOT_DIR

router = APIRouter()


def read_file(path, media_type="application/pdf", use_headers=True):
    f = open(path, "rb")

    # To view the file in the browser, use "inline" for the media_type
    headers = {"Content-Disposition": "inline; filename=privacy_en.pdf"}

    # Create a StreamingResponse object with the file-like object, media type and headers
    if use_headers:
        return StreamingResponse(f, media_type=media_type, headers=headers)
    else:
        return StreamingResponse(f, media_type=media_type)


@router.get("/privacy")
async def get_privacy() -> Any:
    return read_file(os.path.join(ROOT_DIR, "docs/privacy/privacy_en.pdf"))


@router.get("/eula")
async def get_privacy() -> Any:
    return read_file(os.path.join(ROOT_DIR, "docs/eula/eula_en.pdf"))


@router.get("/get_media/{filename}")
async def get_media(
        filename: str
) -> Any:
    filepath = os.path.join(MEDIA_ROOT_DIR, "practises", filename)
    return FileResponse(filepath, media_type="image/jpeg", filename=filename)
