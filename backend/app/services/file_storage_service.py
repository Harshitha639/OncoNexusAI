"""
Local disk storage for uploaded medical report files.

Files are stored under `settings.UPLOAD_DIR/{patient_id}/{uuid}.{ext}` so
filenames never collide and one patient's files are physically grouped
together. This module is the only place that touches the filesystem for
report uploads — services should call it rather than using `open()` directly.
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.base import PayloadTooLargeException, UnsupportedMediaTypeException
from app.models.enums import ReportFileType

logger = get_logger(__name__)

_EXTENSION_TO_FILE_TYPE: dict[str, ReportFileType] = {
    ".pdf": ReportFileType.PDF,
    ".jpg": ReportFileType.JPG,
    ".jpeg": ReportFileType.JPEG,
    ".png": ReportFileType.PNG,
}


def _validate_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.ALLOWED_REPORT_EXTENSIONS:
        allowed = ", ".join(settings.ALLOWED_REPORT_EXTENSIONS)
        raise UnsupportedMediaTypeException(
            message=f"Unsupported file type '{suffix or 'unknown'}'. Allowed types: {allowed}."
        )
    return suffix


def resolve_file_type(filename: str) -> ReportFileType:
    suffix = _validate_extension(filename)
    return _EXTENSION_TO_FILE_TYPE[suffix]


class FileStorageService:
    """Persists uploaded report files to local disk with unique filenames."""

    def __init__(self) -> None:
        self._base_dir = Path(settings.UPLOAD_DIR)

    def _patient_dir(self, patient_id: uuid.UUID) -> Path:
        directory = self._base_dir / str(patient_id)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    async def save(self, patient_id: uuid.UUID, upload: UploadFile) -> tuple[str, str, int]:
        """Validate, then stream `upload` to disk.

        Returns `(stored_filename, absolute_file_path, size_bytes)`.
        """
        if not upload.filename:
            raise UnsupportedMediaTypeException(message="Uploaded file has no filename.")

        suffix = _validate_extension(upload.filename)
        stored_filename = f"{uuid.uuid4().hex}{suffix}"
        destination = self._patient_dir(patient_id) / stored_filename

        size_bytes = 0
        chunk_size = 1024 * 1024  # 1 MB
        try:
            with destination.open("wb") as out_file:
                while chunk := await upload.read(chunk_size):
                    size_bytes += len(chunk)
                    if size_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
                        out_file.close()
                        destination.unlink(missing_ok=True)
                        raise PayloadTooLargeException(
                            message=(
                                f"File exceeds the maximum upload size of "
                                f"{settings.MAX_UPLOAD_SIZE_MB} MB."
                            )
                        )
                    out_file.write(chunk)
        finally:
            await upload.close()

        if size_bytes == 0:
            destination.unlink(missing_ok=True)
            raise UnsupportedMediaTypeException(message="Uploaded file is empty.")

        logger.info("Stored report file %s (%d bytes) for patient %s", stored_filename, size_bytes, patient_id)
        return stored_filename, str(destination), size_bytes

    def resolve_path(self, patient_id: uuid.UUID, stored_filename: str) -> Path:
        return self._patient_dir(patient_id) / stored_filename

    def delete(self, file_path: str) -> None:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info("Deleted report file %s", file_path)
