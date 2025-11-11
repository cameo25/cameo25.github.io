# Beyblade X Winning Combinations Tracker

Automated scraper for tracking Beyblade X winning combinations from the World Beyblade Organization forum. Generates time-based statistics (30 days, 90 days, year-to-date) with interactive charts.

## Features

- **Fully Automated**: No user input required - generates all reports in one run
- **Time-Based Analysis**: Automatically creates 30-day, 90-day, and year-to-date statistics
- **Interactive Charts**: HTML pages with Chart.js visualizations showing top 10 for each category
- **Smart Translation**: Converts abbreviated bits (e.g., "R" → "Rush", "LR" → "Low Rush")

## Quick Start

```bash
# Setup
pip install -r requirements.txt

# Run scraper (fully automated)
python beyblade_scraper.py
```

The script automatically:
1. Determines the current last page on the forum
2. Finds appropriate date ranges for each time period
3. Generates CSV data and HTML charts for all three periods

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
- `PhoenixWing 1-60 Rush` → `PhoenixWing | 1-60 | Rush`
- `WizardRod 1-60 H` → `WizardRod | 1-60 | Hexa` (translated)
- `Shark Scale 4-50 Low Rush` → `SharkScale | 4-50 | LowRush` (spaces removed)

**CSV Columns**: `Blades, Ratchets, Bits`

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

1. **Fetch last page**: Uses `page=last` to determine current forum state
2. **Date-based search**: Searches backwards through pages to find date boundaries
3. **Extract combinations**: Parses post bodies using regex pattern
4. **Translate & normalize**: Converts abbreviations and removes spaces
5. **Generate analysis**: Creates frequency counts and visualizations

**Smart Optimization**: The 90-day scrape reuses the 30-day start page as a search hint, reducing HTTP requests.

## Requirements

- Python 3.11+
- Dependencies:
  - `requests==2.31.0` - HTTP requests
  - `beautifulsoup4==4.12.2` - HTML parsing

## Data Source

All data sourced from: [WBO Beyblade X Winning Combinations Thread](https://worldbeyblade.org/Thread-Winning-Combinations-at-WBO-Organized-Events-Beyblade-X-BBX)
