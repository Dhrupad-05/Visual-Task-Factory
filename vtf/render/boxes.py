"""Pixel bounding-box metadata produced by the renderer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PixelBox:
    """Inclusive-exclusive pixel rectangle in top-left image coordinates."""

    x0: float
    y0: float
    x1: float
    y1: float

    def clipped(self, width: int, height: int) -> "PixelBox":
        """Return this box clipped to the image canvas."""

        return PixelBox(
            max(0.0, min(self.x0, width)),
            max(0.0, min(self.y0, height)),
            max(0.0, min(self.x1, width)),
            max(0.0, min(self.y1, height)),
        )
