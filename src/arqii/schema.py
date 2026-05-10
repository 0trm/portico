from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field


class Layer(BaseModel):
    label: str
    summary: str


class BaseLayer(BaseModel):
    labels: Annotated[list[str], Field(min_length=1, max_length=4)]
    summary: str


class FitQuality(StrEnum):
    GOOD = "good"
    STRETCHED = "stretched"
    FORCED = "forced"
    NOT_APPLICABLE = "not_applicable"


class PorticoJSON(BaseModel):
    # Reasoning-first fields (mitigate format tax; LLM thinks before it labels).
    input_type: str
    type_rationale: str
    decomposition_strategy: str
    scratch_outline: list[str]
    mece_check: str

    # Output fields.
    theme: str
    title: str
    roof: Layer
    pillars: Annotated[list[Layer], Field(min_length=2, max_length=9)]
    base: BaseLayer

    # Abstention.
    fit_quality: FitQuality
    notes_on_fit: str
