"""Configuration defaults for reproducible local runs."""

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime settings kept explicit and serializable."""

    seed: int = 7
    image_width: int = Field(default=800, gt=0)
    image_height: int = Field(default=600, gt=0)
    matplotlib_backend: str = "Agg"
    output_dir: str = "data"
    max_model_spend_usd: float = Field(default=0.0, ge=0)
