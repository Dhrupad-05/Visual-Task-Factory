"""Deterministic image effects used by the renderer."""

import numpy as np


def apply_effects(
    rgba_bytes: bytes,
    *,
    width: int,
    height: int,
    noise: str = "none",
    seed: int = 0,
) -> bytes:
    """Apply seeded RGB noise to an RGBA byte buffer without changing its size."""

    expected = width * height * 4
    if len(rgba_bytes) != expected:
        raise ValueError(f"expected {expected} RGBA bytes, got {len(rgba_bytes)}")
    if noise not in {"none", "light", "heavy"}:
        raise ValueError(f"unsupported noise level: {noise}")
    if noise == "none":
        return rgba_bytes

    image = np.frombuffer(rgba_bytes, dtype=np.uint8).copy().reshape((height, width, 4))
    scale = 3 if noise == "light" else 10
    rng = np.random.default_rng(seed)
    delta = rng.integers(-scale, scale + 1, size=(height, width, 1), dtype=np.int16)
    image[:, :, :3] = np.clip(image[:, :, :3].astype(np.int16) + delta, 0, 255)
    return image.tobytes()
