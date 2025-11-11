# Beyblade Combination Scraper

A Python script to scrape Beyblade X (BBX) winning combinations from the World Beyblade Organization forum and export them to CSV format.

## Features

- Extracts Beyblade combinations matching the pattern: `Name Number-Number Suffix`
  - Example: `PhoenixWing 1-60R`
  - Example: `WizardRod 1-60Hexa`
  - Example: `SharkScale 4-50Low Rush`
- Supports multi-word blade names and suffixes
- Can scrape multiple pages at once
- Exports to CSV with three columns: Part 1 (Name), Part 2 (Numbers), Part 3 (Suffix)
- Includes page number tracking
- Removes duplicate entries

## Requirements

- Python 3.6+
- Required packages:
  - `requests` - for fetching web pages
  - `beautifulsoup4` - for parsing HTML

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode (Recommended)

Run the script and follow the prompts:

```bash
python beyblade_scraper.py
```

You'll be asked for:
- Start page number (e.g., 1)
- End page number (e.g., 70)
- Output CSV filename (default: beyblade_combinations.csv)

### Example Session

```
Beyblade Combination Scraper
==================================================
Enter start page number (e.g., 1): 1
Enter end page number (e.g., 70): 10
Enter output CSV filename (default: beyblade_combinations.csv): my_combinations.csv

Scraping pages 1 to 10...
Scraping page 1...
  Found 45 combinations on page 1
Scraping page 2...
  Found 38 combinations on page 2
...

Saved 412 combinations to my_combinations.csv

Total combinations found: 412
```

## Output Format

The CSV file will contain four columns:

| Part 1 (Name) | Part 2 (Numbers) | Part 3 (Suffix) | Page |
|---------------|------------------|-----------------|------|
| PhoenixWing   | 1-60             | R               | 70   |
| WizardRod     | 1-60             | Hexa            | 70   |
| SharkScale    | 4-50             | Low Rush        | 70   |

## Test Script

A test script (`test_scraper.py`) is included to demonstrate the parsing logic without making web requests. Run it with:

```bash
python test_scraper.py
```

This will generate a sample CSV file (`test_combinations.csv`) from hardcoded sample data.

## Notes

- The script automatically removes duplicate combinations
- Multi-word names and suffixes are supported (e.g., "WhaleFlame Massive", "Low Rush")
- The page number is tracked for each combination
- The script handles connection errors gracefully

## Target Website

World Beyblade Organization - Winning Combinations
https://worldbeyblade.org/Thread-Winning-Combinations-at-WBO-Organized-Events-Beyblade-X-BBX

## License

Free to use for personal data analysis and research.
