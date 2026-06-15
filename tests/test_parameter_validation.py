from instrument_app.domain.parameter_validation import validate_for_ready
from instrument_app.domain.recipe_models import ProcessParameters


def test_validate_requires_solvent() -> None:
    p = ProcessParameters(solvent="")
    assert len(validate_for_ready(p)) >= 1


def test_validate_accepts_default_with_solvent() -> None:
    p = ProcessParameters(solvent="水")
    assert validate_for_ready(p) == []
