"""Validated data contracts shared across the pipeline."""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AxisSpec(BaseModel):
    """Axis metadata needed to render and interpret a panel."""

    x_type: str
    y_type: Literal["linear", "log"]
    y_min: float
    y_max: float
    truncated: bool = False
    dual_axis: bool = False

    @model_validator(mode="after")
    def validate_range(self) -> "AxisSpec":
        if self.y_max <= self.y_min:
            raise ValueError("y_max must be greater than y_min")
        if self.y_type == "log" and self.y_min <= 0:
            raise ValueError("log axes require a positive y_min")
        return self


class SeriesSpec(BaseModel):
    """A named plotted series and its source values."""

    name: str = Field(min_length=1)
    color: str = Field(min_length=1)
    marker: str = "o"
    values: list[float] = Field(min_length=1)
    axis: Literal["left", "right"] = "left"


class PanelSpec(BaseModel):
    """One chart panel."""

    axes: AxisSpec
    series: list[SeriesSpec] = Field(min_length=1)
    x_labels: list[str] = Field(default_factory=list)
    legend_labels: list[str] = Field(default_factory=list)
    annotations: list[str] = Field(default_factory=list)


class StyleSpec(BaseModel):
    """Rendering style knobs stored in the scene spec."""

    font_size: int = Field(default=12, gt=0)
    palette: list[str] = Field(default_factory=list)
    grid: bool = True
    noise: str = "none"
    resolution: str = "high"
    clutter_level: str = "none"


class SceneSpec(BaseModel):
    """Single source of truth for one generated scene."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    seed: int
    chart_type: Literal["bar", "line", "scatter"]
    panels: list[PanelSpec] = Field(min_length=1)
    style: StyleSpec = Field(default_factory=StyleSpec)
    knobs: dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """A question, its spec-derived reference, and validation metadata."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    image_path: Path
    scene_id: str = Field(min_length=1)
    skill: str = Field(min_length=1)
    subskill: str = Field(min_length=1)
    question: str = Field(min_length=1)
    answer_type: Literal["numeric", "choice", "yes_no", "set", "text"]
    choices: list[str] | None = None
    reference_answer: Any
    tolerance: float | None = Field(default=None, ge=0)
    difficulty: dict[str, Any] = Field(default_factory=dict)
    validation: dict[str, Any] = Field(default_factory=dict)
    distractors: dict[str, Any] = Field(default_factory=dict)
    pair_id: str | None = None
    variant_of: str | None = None
    factor_changed: str | None = None
    severity_params: dict[str, Any] = Field(default_factory=dict)


class Prediction(BaseModel):
    """Raw model output associated with one task."""

    task_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    raw_text: str
    prompt_variant: str = "v1"
