"""stage03_transform.py.

Alex Heyert, November 2026.

Source: validated JSON array from TVmaze API
Sink: Polars DataFrame

Purpose

  Transform validated JSON data into a structured format.

Analytical Questions

- Q. Which fields are needed from the JSON data?
- A. The fields needed are (episode) summary, season, number (of episode in season), id, name (episode title), and rating.
- Q.How can records be normalized into tabular form?
- A. Each episode can be normalized into a row with consistent columns using polars

- Q. What derived fields would support analysis?
- A. Occurrences of the word "Fillory" in the summary can be counted to support analysis of importance throughout the series.


"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

from html import unescape
import logging
import re
from typing import Any

import polars as pl

# ============================================================
# Section 2. Define Run Transform Function
# ============================================================


def run_transform(
    json_data: list[dict[str, Any]],
    LOG: logging.Logger,
) -> pl.DataFrame:
    """Transform JSON into a structured DataFrame.

    Args:
        json_data (list[dict[str, Any]]): Validated JSON data.
        LOG (logging.Logger): The logger instance.

    Returns:
        pl.DataFrame: The transformed dataset.
    """
    LOG.info("========================")
    LOG.info("STAGE 03: TRANSFORM starting...")
    LOG.info("========================")

    records: list[dict[str, Any]] = []

    for record in json_data:
        # Pull summary to format it before adding it to the record.
        summary = record["summary"]
        records.append(
            {
                "id": record["id"],
                "season": record["season"],
                "episode_number": record["number"],
                "title": record["name"],
                "summary": unescape(re.sub(r"<[^>]+>", " ", summary)).strip(),
                "rating": record.get("rating", {}).get(
                    "average"
                ),  # extract nested rating object as a number
            }
        )

    df: pl.DataFrame = pl.DataFrame(records)

    # Derived fields
    df = df.with_columns(
        [
            # Add season and episode number as a single column. IE S2E16
            (
                pl.lit("S")
                + pl.col("season").cast(pl.String)
                + pl.lit("E")
                + pl.col("episode_number").cast(pl.String)
            ).alias("season_episode"),
            # Add number of mentions of the word "fillory" (case-insensitive)
            pl.col("summary")
            .str.count_matches(r"(?i)\bfillory\b")
            .alias("fillory_mentions"),
            # Add number of "Quentin" mentions (case-insensitive)
            pl.col("summary")
            .str.count_matches(r"(?i)\bquentin\b")
            .alias("quentin_mentions"),
            # Add number of "Margo" mentions (case-insensitive)
            pl.col("summary")
            .str.count_matches(r"(?i)\bmargo\b")
            .alias("margo_mentions"),
        ]
    )

    LOG.info("Transformation complete.")
    LOG.info(f"DataFrame preview:\n{df.head()}")
    LOG.info("Sink: Polars DataFrame created")

    # Return the transformed DataFrame for use in the next stage.
    return df
