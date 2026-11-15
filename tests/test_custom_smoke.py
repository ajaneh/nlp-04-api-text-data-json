"""Custom smoke tests for the custom_nlp EVTL pipeline."""

import json
import logging
from types import SimpleNamespace

import polars as pl
import pytest
import requests

from custom_nlp.stage01_extract import run_extract
from custom_nlp.stage02_validate import run_validate
from custom_nlp.stage03_transform import run_transform
from custom_nlp.stage04_load import run_load


def test_custom_json_stages_write_expected_csv(monkeypatch, tmp_path):
    """Run extraction through loading with a controlled TVMaze-like payload."""
    rows = [
        {
            "id": 3269808,
            "name": "The Boy",
            "summary": "<p>Luke Ellis wakes up at The Institute.</p>",
            "rating": {"average": 7},
        },
        {
            "id": 3291173,
            "name": "Shots for Dots",
            "summary": "<p>Luke bonds with the other Front Half residents.</p>",
            "rating": {"average": 7.4},
        },
    ]
    payload = json.dumps(rows)

    def fake_get(url, *, headers, timeout):
        assert url == "https://api.tvmaze.com/shows/77778/episodes"
        assert headers["Accept"] == "application/json"
        assert timeout == 30
        return SimpleNamespace(
            text=payload,
            json=lambda: json.loads(payload),
            raise_for_status=lambda: None,
        )

    monkeypatch.setattr(requests, "get", fake_get)
    log = logging.getLogger(__name__)
    raw_path = tmp_path / "api_request_institute_raw.json"
    csv_path = tmp_path / "api_request_institute_processed.csv"

    extracted = run_extract(
        "https://api.tvmaze.com/shows/77778/episodes",
        {"User-Agent": "api-request-institute/2.0", "Accept": "application/json"},
        raw_path,
        log,
    )
    df = run_transform(run_validate(extracted, log), log)
    run_load(df, csv_path, log)

    assert json.loads(raw_path.read_text(encoding="utf-8")) == rows
    assert csv_path.stat().st_size > 0
    saved = pl.read_csv(csv_path)
    assert saved.height > 0
    assert set(saved.columns) == {
        "episode_id",
        "name",
        "summary",
        "rating",
        "name_length",
        "summary_length",
    }


def test_custom_validation_rejects_empty_records():
    """Reject empty data instead of creating an empty DataFrame."""
    with pytest.raises(ValueError, match="at least one record"):
        run_validate([], logging.getLogger(__name__))
