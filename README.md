# Beyblade X Winning Combinations Tracker

Automated scraper that tracks Beyblade X winning combinations from the WBO forum and generates interactive charts for 30-day, 90-day, and year-to-date statistics.

## Quick Start

```bash
pip install -r requirements.txt
python beyblade_scraper.py
```

The scraper automatically generates:
- `30days_charts.html` - Last 30 days statistics
- `90days_charts.html` - Last 90 days statistics
- `ytd_charts.html` - Year-to-date statistics
- `index.html` - Landing page with navigation

**First run**: Scrapes all year-to-date data
**Subsequent runs**: Only scrapes new pages (fast, incremental updates)

## How It Works

1. Scrapes YTD combinations from the forum (starting page 22)
2. Filters YTD data to generate 90-day and 30-day reports
3. Creates CSV files and interactive HTML charts
4. Caches progress in `page_cache.json` for incremental updates

**Rate limiting**: 5 second delay between requests to avoid spamming the server

## Translation

Create `InitialsName.txt` to translate abbreviated bits (optional):

```
Initials	Name
R	Rush
H	Hexa
LR	Low Rush
```

## Output Format

CSV columns: `Blades, Ratchets, Bits, Page`

Example: `PhoenixWing 1-60 Rush` → `PhoenixWing | 1-60 | Rush | 75`

## Troubleshooting

**Cache corrupted?** Delete `page_cache.json` and re-run
**Slow first run?** Normal - scraping all YTD pages
**Subsequent runs slow?** Should only scrape new pages

## Requirements

- Python 3.11+
- `requests==2.31.0`
- `beautifulsoup4==4.12.2`

## Data Source

[WBO Beyblade X Winning Combinations Thread](https://worldbeyblade.org/Thread-Winning-Combinations-at-WBO-Organized-Events-Beyblade-X-BBX)
