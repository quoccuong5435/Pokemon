"""Shared fixture `npa_data` (tests/conftest.py): the NPA 1.0 script and files built once per test session."""


def test_fixture_has_script(npa_data):
    assert "function PAX_Leg_QKey" in npa_data["script"]
    assert npa_data["opt_stats"]["form_models"] == 105


def test_fixture_script_uses_lf_line_breaks(npa_data):
    assert "\r" not in npa_data["script"]
