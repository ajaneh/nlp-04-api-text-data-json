"""stage03_transform.py.

Alex Heyert, November 2026.

Source: validated JSON array from TVmaze API
Sink: Polars DataFrame

Purpose

  Transform validated JSON data into a structured format.

Analytical Questions

- Q. Which fields are needed from the JSON data?
- A. The fields needed are the episode name, summary, and rating.
- Q.How can records be normalized into tabular form?
- A. Each episode can be normalized into a row with consistent columns using polars

- Q. What derived fields would support analysis?
- A. The name and summary lengths can be derived to support analysis. Rating is not a
  constructed feature, but it could be valuable alongside the rest of the data,


"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

import logging
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
        records.append(
            {
                "episode_id": record["id"],
                "name": record["name"],
                "summary": record["summary"],
                "rating": record.get("rating", {}).get(
                    "average"
                ),  # extract nested rating object as a number
            }
        )

    df: pl.DataFrame = pl.DataFrame(records)

    # Derived fields
    df = df.with_columns(
        [
            pl.col("name").str.len_chars().alias("name_length"),
            pl.col("summary").str.len_chars().alias("summary_length"),
        ]
    )

    LOG.info("Transformation complete.")
    LOG.info(f"DataFrame preview:\n{df.head()}")
    LOG.info("Sink: Polars DataFrame created")

    # Return the transformed DataFrame for use in the next stage.
    return df
