# Beyblade X Winning Combinations Tracker

Automated scraper for tracking Beyblade X winning combinations from the World Beyblade Organization forum. Generates time-based statistics (30 days, 90 days, year-to-date) with interactive charts.

## Features

- **Fully Automated**: No user input required - generates all reports in one run
- **Time-Based Analysis**: Automatically creates 30-day, 90-day, and year-to-date statistics
- **Interactive Charts**: HTML pages with Chart.js visualizations showing top 10 for each category
- **Smart Translation**: Converts abbreviated bits (e.g., "R" → "Rush", "LR" → "Low Rush")
- **Incremental Updates**: Only scrapes new pages, appends to existing data
- **Cache Validation**: CSV is source of truth - cache auto-syncs if corrupted
- **Zero-HTTP Filtering**: 90/30 day reports generated from YTD data without web requests

## Quick Start

```bash
# Setup
pip install -r requirements.txt

# Run scraper (fully automated)
python beyblade_scraper.py
```

The script automatically:
1. Determines the current last page on the forum
2. Scrapes year-to-date data (starting from page 22, only new complete pages)
3. Filters YTD data to generate 90-day and 30-day reports (no additional HTTP requests)
4. Generates CSV summaries and interactive HTML charts for all three periods

**Subsequent runs**: Uses cached data, only scrapes new pages that appeared since last run

## Output Files

Each run generates three sets of files:

### 30-Day Report
- `30days.csv` - Raw combinations data
- `30days_summary.csv` - Frequency counts per component
- `30days_combo_counts.csv` - Full combination frequencies
- `30days_charts.html` - Interactive charts ✨

### 90-Day Report
- `90days.csv`
- `90days_summary.csv`
- `90days_combo_counts.csv`
- `90days_charts.html` - Interactive charts ✨

### Year-to-Date Report
- `ytd.csv`
- `ytd_summary.csv`
- `ytd_combo_counts.csv`
- `ytd_charts.html` - Interactive charts ✨

### Landing Page
- `index.html` - Navigation page with links to all three chart pages

## Data Format

Combinations are extracted in the pattern: `Blades Ratchets Bits`

**Examples**:
- `PhoenixWing 1-60 Rush` → `PhoenixWing | 1-60 | Rush | 75`
- `WizardRod 1-60 H` → `WizardRod | 1-60 | Hexa | 75` (translated)
- `Shark Scale 4-50 Low Rush` → `SharkScale | 4-50 | LowRush | 76` (spaces removed)

**CSV Columns**: `Blades, Ratchets, Bits, Page`

The Page column tracks which forum page each combination was found on, enabling date-based filtering.

## Translation System

The scraper uses `InitialsName.txt` to translate abbreviated bits:

```
Initials	Name
R	Rush
H	Hexa
LR	Low Rush
GF	Gear Flat
```

Translation is case-insensitive and happens before space normalization.

## How It Works

### First Run
1. **Fetch last page**: Uses `page=last` to determine current forum state
2. **Scrape YTD**: Starts from hardcoded page 22, scrapes up to (last page - 1)
3. **Cache pages**: Stores page numbers and dates in `page_cache.json`
4. **Extract combinations**: Parses post bodies using regex pattern with page numbers
5. **Translate & normalize**: Converts abbreviations and removes spaces
6. **Save to CSV**: Appends combinations to `ytd.csv` with Page column
7. **Filter for 90/30 days**: Generates 90-day and 30-day CSVs by filtering YTD based on cached page dates
8. **Generate analysis**: Creates frequency counts and visualizations for all three periods

### Subsequent Runs
1. **Load cache**: Reads `page_cache.json` to see which pages were already scraped
2. **Validate against CSV**: Checks ytd.csv to ensure cache is accurate (CSV is source of truth)
3. **Scrape only new pages**: Only fetches pages that appeared since last run
4. **Append to YTD**: Adds new combinations to ytd.csv (preserves all historical data)
5. **Regenerate 90/30 days**: Filters updated YTD CSV (zero HTTP requests)
6. **Update charts**: Regenerates all HTML visualizations

### Key Optimizations
- **Incremental scraping**: Only new pages are fetched, skipped pages have no delay
- **Zero HTTP for 90/30 days**: Generated purely by filtering ytd.csv using cached page dates
- **Cache validation**: CSV is always the source of truth; cache auto-corrects if corrupted
- **Rate limiting**: 5 second delay between HTTP requests to avoid server spam
- **Complete pages only**: Current last page is never scraped (still receiving new posts)

## Requirements

- Python 3.11+
- Dependencies:
  - `requests==2.31.0` - HTTP requests
  - `beautifulsoup4==4.12.2` - HTML parsing

## Cache File

The scraper uses `page_cache.json` to track scraped pages and dates:

```json
{
  "22": "2024-01-15T10:30:00",
  "23": "2024-01-20T14:45:00",
  "_metadata_ytd_start_page": 22,
  "_metadata_ytd_scraped_pages": [22, 23, 24, ...]
}
```

- **Page dates**: Maps page number → latest post date on that page
- **Start page metadata**: Caches YTD start page for instant subsequent runs
- **Scraped pages**: Tracks which pages have been processed

**Recovery**: If cache becomes corrupted, delete `page_cache.json` and re-run. The scraper will validate against ytd.csv and rebuild the cache.

## Troubleshooting

### "No combinations found"
- Check that the forum URL is accessible
- Verify `InitialsName.txt` exists (though not required)

### Duplicate data in ytd.csv
- Delete `page_cache.json` to rebuild from CSV
- Scraper will auto-detect and sync on next run

### Slow scraping
- First run takes longer (scraping all YTD pages)
- Subsequent runs are fast (only new pages)
- 5 second delay between requests is intentional (rate limiting)

## Data Source

All data sourced from: [WBO Beyblade X Winning Combinations Thread](https://worldbeyblade.org/Thread-Winning-Combinations-at-WBO-Organized-Events-Beyblade-X-BBX)
