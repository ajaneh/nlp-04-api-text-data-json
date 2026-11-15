"""stage05_visualize.py.

Alex Heyert, November 2026.

Source: saved CSV file from stage04_load.py
Sink: Visualizations (plots)

Purpose

  Visualize the transformed data to support analysis.

Analytical Questions

- How can we visualize the distribution of Fillory mentions across episodes?
- How can we visualize the relationship between season/episode and Fillory mentions?

"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

ROOT_PATH: Path = Path.cwd()


def visualize_fillory_mentions(processed_csv_path: Path, LOG: logging.Logger) -> None:
    """Visualize the distribution of Fillory mentions across episodes.

    Args:
        processed_csv_path (Path): Path to the processed CSV file.
        LOG (logging.Logger): The logger instance.
    """
    LOG.info("VISUALIZE FILLORY MENTIONS")
    LOG.info(f"Reading processed CSV from {processed_csv_path}")
    df = pl.read_csv(processed_csv_path)
    LOG.info(f"Loaded {len(df)} rows from processed CSV")

    # Use 3 aligned dot plots for easier comparison
    fig, axes = plt.subplots(3, 1, figsize=(10, 6), sharex=True)  # noqa: RUF059
    x = np.arange(len(df))
    for ax, column, color, label in (
        (axes[0], "fillory_mentions", "blue", "Fillory"),
        (axes[1], "quentin_mentions", "red", "Quentin"),
        (axes[2], "margo_mentions", "green", "Margo"),
    ):
        ax.plot(x, df[column], color=color, marker="o", label=label)
        ax.set_ylabel("Number of Mentions")
        ax.legend()
    axes[0].set_title("Character Mentions Across Episodes")
    axes[2].set_xlabel("Episode")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(df["season_episode"], rotation=70, ha="right")
    for ax in axes:
        # Make all Y axis the same, 0 to 3
        ax.set_ylim(0, 3)
    plt.savefig(ROOT_PATH / "data/processed/character_mentions_distribution.png")
    LOG.info(
        "Saved combined character mentions visualization to data/processed/character_mentions_distribution.png"
    )
    plt.show()
    LOG.info("CLOSE PLOTS TO END PROGRAM or PRESS CTRL+C")
