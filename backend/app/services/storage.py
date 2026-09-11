import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


class LocalFileStorage:
    def __init__(self, upload_dir: str, max_bytes: int):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes

    async def save_resume(self, upload: UploadFile) -> tuple[str, str, str]:
        original_name = Path(upload.filename or "resume").name
        suffix = Path(original_name).suffix.lower()
        content_type = upload.content_type or ""

        if suffix not in ALLOWED_EXTENSIONS or content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume must be a PDF, DOC, or DOCX file",
            )

        data = await upload.read(self.max_bytes + 1)
        if len(data) > self.max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Resume exceeds the maximum upload size",
            )

        storage_name = f"{uuid.uuid4()}{suffix}"
        path = self.upload_dir / storage_name
        path.write_bytes(data)

        return original_name, storage_name, content_type

    def path_for(self, storage_name: str) -> Path:
        path = (self.upload_dir / storage_name).resolve()
        root = self.upload_dir.resolve()

        if root not in path.parents:
            raise ValueError("Invalid storage path")

        return path

    def delete(self, storage_name: str) -> None:
        path = self.path_for(storage_name)
        if path.exists():
            path.unlink()
