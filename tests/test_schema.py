import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from arqii.schema import FitQuality, PorticoJSON

FIXTURES = Path(__file__).parent / "fixtures" / "json"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.mark.parametrize("fixture", sorted(p.name for p in FIXTURES.glob("*.json")))
def test_all_fixtures_validate(fixture: str) -> None:
    PorticoJSON.model_validate(_load(fixture))


def test_pillar_count_below_minimum_rejected() -> None:
    data = _load("essay_2pillars.json")
    data["pillars"] = data["pillars"][:1]
    with pytest.raises(ValidationError):
        PorticoJSON.model_validate(data)


def test_pillar_count_above_maximum_rejected() -> None:
    data = _load("survey_9pillars_stretched.json")
    data["pillars"] = data["pillars"] + [{"label": "Extra", "summary": "Tenth pillar."}]
    with pytest.raises(ValidationError):
        PorticoJSON.model_validate(data)


def test_unknown_fit_quality_rejected() -> None:
    data = _load("codebase_3pillars.json")
    data["fit_quality"] = "perfect"
    with pytest.raises(ValidationError):
        PorticoJSON.model_validate(data)


def test_missing_required_field_rejected() -> None:
    data = _load("codebase_3pillars.json")
    del data["mece_check"]
    with pytest.raises(ValidationError):
        PorticoJSON.model_validate(data)


def test_fit_quality_enum_values() -> None:
    assert {q.value for q in FitQuality} == {
        "good",
        "stretched",
        "forced",
        "not_applicable",
    }
