# Module 4: The Magicians Episode Summary Mentions

Project 04
**Web Mining & Applied NLP | Alex Heyert 2026 November**

## Project question

This project adapts the example EVTL pipeline to TVmaze episode data for
[*The Magicians*](https://www.tvmaze.com/shows/3083/the-magicians). It asks:

> How often do the episode summaries mention Fillory, Quentin, and Margo, and how do those mention counts vary across episodes?

The original project example retrieves JSONPlaceholder posts. This custom
pipeline instead retrieves episode records from TVmaze and uses Polars to
prepare an episode-level dataset.

## Data source and JSON structure

The source is TVmaze's
[episode API for show 3083](https://api.tvmaze.com/shows/3083/episodes).
TVmaze identifies show 3083 as [*The Magicians*](https://www.tvmaze.com/shows/3083/the-magicians).
The saved response contains 65 episode records: 13 episodes in each of five
seasons. Each record is a JSON object with fields including `id` (integer),
`name` (string), `season` and `number` (integers), `summary` (HTML-formatted
string), and nested `rating`, `image`, and `_links` objects.

The pipeline selects these source values:

| Source field | Output field | Use |
| --- | --- | --- |
| `id` | `id` | Episode identifier |
| `season` | `season` | Season number |
| `number` | `episode_number` | Episode number within the season |
| `name` | `title` | Episode title |
| `summary` | `summary` | Text used for keyword counts |
| `rating.average` | `rating` | TVmaze's episode rating, when available |

The [saved raw JSON](https://github.com/ajaneh/nlp-04-api-text-data-json/blob/main/data/raw/magicians_request_raw.json)
preserves the API response.

## Validation and transformation

The Validate stage requires the response to be a non-empty list and every
record to be a dictionary. It does not currently enforce required record keys
or field types. The Transform stage expects `id`, `season`, `number`, `name`,
and `summary`; it also reads `rating.average` when available. A changed or
incomplete API response could therefore pass the current validation checks
and still fail during transformation.

The Transform stage creates one row per episode in a Polars DataFrame. It
removes HTML tags from each summary and trims surrounding whitespace, then
adds:

- `season_episode`, a readable label such as `S2E13`.
- `fillory_mentions`, `quentin_mentions`, and `margo_mentions`, the number of
  case-insensitive, whole-word matches for each name in that episode's
  cleaned summary.

The Load stage writes the table to
[`data/processed/magicians_request_processed.csv`](https://github.com/ajaneh/nlp-04-api-text-data-json/blob/main/data/processed/magicians_request_processed.csv).

## Results and visual

The processed CSV has 65 rows, one per episode. Across those summaries,
Fillory appears 8 times, Quentin 42 times, and Margo 26 times. Quentin appears
in 38 episode summaries and reaches 3 mentions in one episode; Fillory and
Margo each appear at most once in any one summary. Comparing the side by side chart shows that as the show progresses and Margo becomes an integral part of Fillory, her name almost seems to replace mentions of Fillory.

![Character mentions across The Magicians episodes](images/character_mentions_distribution.png)

## Interpretation and limitations

The saved results show that Quentin is the most frequently mentioned of these
three names in the episode summaries. Fillory occurs in 8 of 65 summaries,
including three mentions in each of Seasons 1 and 2, one in Season 3, none in
Season 4, and one in Season 5.

The dataset/the show is known for it's short pithy summaries. Episode ratings are saved in the final CSV for potential future analysis.

The selected fields are the “(episode) summary, season, number (of episode in season), id, name (episode title), and rating”.

- [Project repository](https://github.com/ajaneh/nlp-04-api-text-data-json)
- [Custom pipeline source](https://github.com/ajaneh/nlp-04-api-text-data-json/blob/main/src/custom_nlp/pipeline_api_json.py)
- [Custom stages](https://github.com/ajaneh/nlp-04-api-text-data-json/tree/main/src/custom_nlp)
- [Automated tests](https://github.com/ajaneh/nlp-04-api-text-data-json/tree/main/tests)
- [Project instructions](project-instructions.md)
- [Glossary](glossary.md)
- [Professional Python Guide](https://denisecase.github.io/pro-analytics-02/)
