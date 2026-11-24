"""Disk cache keyed by model, prompt, and image content."""

import hashlib
import json
from pathlib import Path


class DiskCache:
    """Small JSON disk cache that prevents duplicate model calls."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(model_name: str, prompt: str, image_path: Path) -> str:
        """Build a stable cache key from request identity and image bytes."""

        image_hash = hashlib.sha256(image_path.read_bytes()).hexdigest()
        payload = f"{model_name}\0{prompt}\0{image_hash}".encode()
        return hashlib.sha256(payload).hexdigest()

    def get(self, model_name: str, prompt: str, image_path: Path) -> str | None:
        """Return cached raw text or ``None`` on a cache miss."""

        path = self.root / f"{self.key(model_name, prompt, image_path)}.json"
        if not path.exists():
            return None
        record = json.loads(path.read_text(encoding="utf-8"))
        return str(record["raw_text"])

    def put(self, model_name: str, prompt: str, image_path: Path, raw_text: str) -> None:
        """Persist one raw response atomically enough for local runs."""

        path = self.root / f"{self.key(model_name, prompt, image_path)}.json"
        path.write_text(json.dumps({"raw_text": raw_text}), encoding="utf-8")
