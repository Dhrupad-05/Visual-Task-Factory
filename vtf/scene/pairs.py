"""Controlled one-factor scene variants."""

from copy import deepcopy
from dataclasses import dataclass

from vtf.schemas import SceneSpec


@dataclass(frozen=True)
class ScenePair:
    """Base and variant scenes plus pair-analysis metadata."""

    base: SceneSpec
    variant: SceneSpec
    pair_id: str
    variant_of: str
    factor_changed: str


def make_pair(scene: SceneSpec, *, factor: str, pair_id: str) -> ScenePair:
    """Create a variant that changes exactly one scene-spec field."""

    supported = {"axis_type", "baseline", "color_similarity", "dual_axis", "font_size"}
    if factor not in supported:
        raise ValueError(f"factor must be one of {sorted(supported)}")
    base = deepcopy(scene)
    variant = deepcopy(scene)
    panel = variant.panels[0]
    if factor == "axis_type":
        panel.axes.y_type = "log" if panel.axes.y_type == "linear" else "linear"
    elif factor == "baseline":
        panel.axes.y_min = max(1.0, panel.axes.y_min + 1.0)
    elif factor == "color_similarity":
        variant.style.palette = ["#777777"] * len(variant.style.palette)
    elif factor == "dual_axis":
        panel.axes.dual_axis = not panel.axes.dual_axis
    elif factor == "font_size":
        variant.style.font_size = variant.style.font_size + 2
    return ScenePair(
        base=base,
        variant=variant,
        pair_id=pair_id,
        variant_of=scene.id,
        factor_changed=factor,
    )
