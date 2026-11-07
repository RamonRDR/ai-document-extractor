"""Small, explicit environment configuration; no secret logging."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    ai_model: str
    ai_timeout_seconds: float
    max_upload_bytes: int
    max_batch_files: int

    @classmethod
    def from_env(cls) -> "Settings":
        timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))
        max_upload = int(os.getenv("MAX_UPLOAD_BYTES", "5242880"))
        max_batch = int(os.getenv("MAX_BATCH_FILES", "5"))
        if not 1 <= timeout <= 120:
            raise ValueError("AI_TIMEOUT_SECONDS must be between 1 and 120")
        if not 1024 <= max_upload <= 20 * 1024 * 1024:
            raise ValueError("MAX_UPLOAD_BYTES must be between 1024 and 20971520")
        if not 1 <= max_batch <= 10:
            raise ValueError("MAX_BATCH_FILES must be between 1 and 10")
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            ai_model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            ai_timeout_seconds=timeout,
            max_upload_bytes=max_upload,
            max_batch_files=max_batch,
        )
