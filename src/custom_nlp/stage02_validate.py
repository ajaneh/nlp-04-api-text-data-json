"""stage02_validate.py.

Alex Heyert, November 2026.

Source: raw JSON object
Sink: validated JSON object

Purpose

  Inspect JSON structure and validate that the data is usable.

Analytical Questions

- Q. What is the top-level structure of the JSON data?
- A. The top-level structure is a list of records.
- Q. What keys are present in each record?
- A. Each record contains the keys: id, url, name, summary, and image. #TODO use actual keys from the API response
- Q. What data types are associated with each field?
- A. The id field is an integer, while the url, name, summary, and image fields are strings. #TODO use actual data types from the API response
- Q. Does the data meet expectations for transformation?
- A. Yes, the data meets expectations for transformation.

"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

import logging
from typing import Any

# ============================================================
# Section 2. Define Run Validate Function
# ============================================================


def run_validate(
    json_data: Any,
    LOG: logging.Logger,
) -> list[dict]:
    """Inspect and validate JSON structure.

    Args:
        json_data (Any): The raw JSON data from the Extract stage.
        LOG (logging.Logger): The logger instance.

    Returns:
        list[dict]: The validated JSON data.
    """
    LOG.info("========================")
    LOG.info("STAGE 02: VALIDATE starting...")
    LOG.info("========================")

    # ============================================================
    # INSPECT JSON STRUCTURE
    # ============================================================

    LOG.info("JSON STRUCTURE INSPECTION:")

    # Log the type of the top-level JSON structure.
    # Use the built-in type() function to get the type
    # and built-in variable __name__ to log just the type name.
    LOG.info(f"Top-level type: {type(json_data).__name__}")

    if isinstance(json_data, list) and len(json_data) > 0:
        first_record = json_data[0]

        LOG.info(f"Keys in first record: {list(first_record.keys())}")

        LOG.info("Field types:")
        for key, value in first_record.items():
            LOG.info(f"{key}: {type(value).__name__}")

    # ============================================================
    # VALIDATE EXPECTATIONS
    # ============================================================

    if not isinstance(json_data, list):
        raise TypeError("Expected JSON data to be a list of records.")

    if len(json_data) == 0:
        raise ValueError("Expected at least one record.")

    if not all(isinstance(record, dict) for record in json_data):
        raise ValueError("Expected each record to be a dictionary.")

    LOG.info("Validation passed.")
    LOG.info("Sink: validated JSON object")

    # Return the validated JSON data for use in the next stage.
    return json_data
