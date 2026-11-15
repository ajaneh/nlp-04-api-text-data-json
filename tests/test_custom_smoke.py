"""Custom smoke tests for the custom_nlp EVTL pipeline."""

import json
import logging
from types import SimpleNamespace

import polars as pl
import pytest
import requests

from custom_nlp.config import API_URL, HTTP_REQUEST_HEADERS
from custom_nlp.stage01_extract import run_extract
from custom_nlp.stage02_validate import run_validate
from custom_nlp.stage03_transform import run_transform
from custom_nlp.stage04_load import run_load


def test_custom_json_stages_write_expected_csv(monkeypatch, tmp_path):
    """Run extraction through loading with a controlled TVMaze-like payload."""
    rows = [
        {
            "id": 415090,
            "name": "Unauthorized Magic",
            "season": 1,
            "number": 1,
            "summary": "<p>QUENTIN &amp; Margo visit FILLORY. Quentin returns.</p>",
            "rating": {"average": 7},
        },
        {
            "id": 522271,
            "name": "The Source of Magic",
            "season": 1,
            "number": 2,
            "summary": "<p>Julia visits Brakebills.</p>",
            "rating": {"average": 7.4},
        },
    ]
    payload = json.dumps(rows)

    def fake_get(url, *, headers, timeout):
        assert url == "https://api.tvmaze.com/shows/3083/episodes"
        assert headers["User-Agent"] == "api-request-magicians/1.0"
        assert headers["Accept"] == "application/json"
        assert timeout == 30
        return SimpleNamespace(
            text=payload,
            json=lambda: json.loads(payload),
            raise_for_status=lambda: None,
        )

    monkeypatch.setattr(requests, "get", fake_get)
    log = logging.getLogger(__name__)
    raw_path = tmp_path / "magicians_request_raw.json"
    csv_path = tmp_path / "magicians_request_processed.csv"

    extracted = run_extract(
        API_URL,
        HTTP_REQUEST_HEADERS,
        raw_path,
        log,
    )
    df = run_transform(run_validate(extracted, log), log)
    run_load(df, csv_path, log)

    assert json.loads(raw_path.read_text(encoding="utf-8")) == rows
    assert csv_path.stat().st_size > 0
    saved = pl.read_csv(csv_path)
    assert saved["id"].to_list() == [415090, 522271]
    assert set(saved.columns) == {
        "id",
        "season",
        "episode_number",
        "title",
        "summary",
        "rating",
        "season_episode",
        "fillory_mentions",
        "quentin_mentions",
        "margo_mentions",
    }
    assert saved["summary"].to_list() == [
        "QUENTIN & Margo visit FILLORY. Quentin returns.",
        "Julia visits Brakebills.",
    ]
    assert saved["season_episode"].to_list() == ["S1E1", "S1E2"]
    assert saved["fillory_mentions"].to_list() == [1, 0]
    assert saved["quentin_mentions"].to_list() == [2, 0]
    assert saved["margo_mentions"].to_list() == [1, 0]


def test_custom_validation_rejects_empty_records():
    """Reject empty data instead of creating an empty DataFrame."""
    with pytest.raises(ValueError, match="at least one record"):
        run_validate([], logging.getLogger(__name__))
