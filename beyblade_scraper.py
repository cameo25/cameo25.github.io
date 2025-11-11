#!/usr/bin/env python3
"""
Beyblade Combination Scraper
Scans WBO forum pages for Beyblade combinations and exports to CSV
"""

import re
import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
import os
import time

# Create a persistent session
session = requests.Session()

def load_translations(file_path: str = None) -> Dict[str, str]:
    """
    Load translation mappings from a file.

    Args:
        file_path: Path to the translation file. If None, uses InitialsName.txt in the script directory.

    Returns:
        Dictionary mapping initials to full names
    """
    translations = {}

    # Default to InitialsName.txt in the same directory as the script
    if file_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "InitialsName.txt")

    if not os.path.exists(file_path):
        print(f"Warning: Translation file not found at {file_path}")
        return translations

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Skip header line
            next(f)

            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    initial = parts[0].strip()
                    name = parts[1].strip()
                    translations[initial] = name
    except Exception as e:
        print(f"Warning: Could not load translations: {e}")

    return translations

def translate_suffix(suffix: str, translations: Dict[str, str]) -> str:
    """
    Translate abbreviated suffix to full name.

    Args:
        suffix: The suffix to translate
        translations: Dictionary of translations

    Returns:
        Translated suffix or original if no translation found
    """
    # Try exact match first (case-sensitive)
    if suffix in translations:
        return translations[suffix]

    # Try case-insensitive match
    for key, value in translations.items():
        if key.lower() == suffix.lower():
            return value

    # No translation found, return original
    return suffix

def fetch_page(page_number) -> str:
    """
    Fetch a specific page from the WBO forum.

    Args:
        page_number: Page number to fetch, or "last" for the most recent page
    """
    url = f"https://worldbeyblade.org/Thread-Winning-Combinations-at-WBO-Organized-Events-Beyblade-X-BBX?page={page_number}"

    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://worldbeyblade.org/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin'
    }

    try:
        # Add a small delay before each request to appear more human-like
        time.sleep(2)
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page {page_number}: {e}")
        return ""

def get_last_page_number() -> Optional[int]:
    """
    Fetch the last page and determine its actual page number.

    Returns:
        The page number of the last page, or None if unable to determine
    """
    html = fetch_page("last")
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # Look for <li class="active multipage-current">
    active_page = soup.find('li', class_='active multipage-current')
    if active_page:
        # Find the <a> tag inside it
        link = active_page.find('a')
        if link:
            # Extract the text and get the page number (remove the "(current)" part)
            page_text = link.get_text().strip()
            # Remove the "(current)" text if present
            page_text = page_text.replace('(current)', '').strip()
            try:
                return int(page_text)
            except ValueError:
                pass

    # If we can't determine, return None
    return None

def parse_forum_date(date_str: str) -> Optional[datetime]:
    """Parse forum date string to datetime object."""
    try:
        # Remove extra characters and normalize
        date_str = date_str.replace('\xa0', ' ').strip()

        # Try parsing with different formats
        for fmt in ["%b. %d, %Y %I:%M %p", "%b %d, %Y %I:%M %p"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None
    except Exception:
        return None

def extract_dates_from_page(html_content: str) -> List[datetime]:
    """Extract all dates from posts on a page as datetime objects."""
    soup = BeautifulSoup(html_content, 'html.parser')
    dates = []

    # Look for post dates
    post_dates = soup.find_all('span', class_='post_date')

    for date_elem in post_dates:
        date_text = date_elem.get_text().strip()
        parsed_date = parse_forum_date(date_text)
        if parsed_date:
            dates.append(parsed_date)

    return dates

def find_page_for_date(target_date: datetime, start_page: int = 200, max_pages_to_check: int = 200) -> Optional[int]:
    """
    Search backwards from start_page to find the page containing posts from target_date.

    Args:
        target_date: The date to search for
        start_page: Page to start searching from (searches backwards)
        max_pages_to_check: Maximum number of pages to check

    Returns:
        Page number containing the target date, or None if not found
    """
    print(f"  Searching for page with posts from {target_date.strftime('%m-%d-%Y')}...")

    for page_num in range(start_page, start_page - max_pages_to_check, -1):
        html = fetch_page(page_num)

        if not html:
            continue

        dates = extract_dates_from_page(html)

        if not dates:
            continue

        # Sort dates to get earliest and latest
        dates.sort()
        earliest = dates[0]
        latest = dates[-1]

        # Check if target date falls within this page's date range
        if earliest <= target_date <= latest:
            print(f"  Found! Page {page_num} (date range: {earliest.strftime('%m-%d-%Y')} to {latest.strftime('%m-%d-%Y')})")
            return page_num

    print(f"  Could not find page for {target_date.strftime('%m-%d-%Y')}")
    return None

def extract_combinations(html_content: str, translations: Dict[str, str] = None) -> List[Tuple[str, str, str]]:
    """
    Extract Beyblade combinations from HTML content.
    Pattern: Blades Ratchets Bits
    Returns list of tuples: (blades, ratchets, bits)

    Args:
        html_content: The HTML content to parse
        translations: Optional dictionary for translating abbreviated bits
    """
    if translations is None:
        translations = {}

    soup = BeautifulSoup(html_content, 'html.parser')

    # Regex pattern to match combinations like "PhoenixWing 1-60R" or "WizardRod 1-60Hexa"
    # Use [ \t] instead of \s to avoid matching across newlines
    # Lookahead allows optional whitespace before newline, end-of-string, comma, or open-paren
    pattern = r'([A-Za-z]+(?:[ \t]+[A-Za-z]+)*)[ \t]+(\d+-\d+)([A-Za-z]+(?:[ \t]+[A-Za-z]+)*?)(?=\s*(?:\n|$|,|\())'

    combinations = []

    # Extract text only from post bodies to avoid navigation/header noise
    post_bodies = soup.find_all('div', class_='post_body')

    if not post_bodies:
        # Fallback to entire page if post bodies not found
        post_bodies = [soup]

    for post in post_bodies:
        text = post.get_text()

        # Find all combinations in this post
        matches = re.findall(pattern, text, re.MULTILINE)

        for match in matches:
            part1 = match[0].strip()
            part2 = match[1].strip()
            part3 = match[2].strip()

            # Translate abbreviated bits if translations are available
            if translations:
                part3 = translate_suffix(part3, translations)

            # Remove spaces from all parts for consistency
            part1 = part1.replace(' ', '')
            part2 = part2.replace(' ', '')
            part3 = part3.replace(' ', '')

            # Create tuple
            key = (part1, part2, part3)

            # Filter out invalid matches
            if part1 and part2 and part3:
                # Make sure none of the parts contain newlines
                if '\n' not in part1 and '\n' not in part2 and '\n' not in part3:
                    combinations.append(key)

    return combinations

def scrape_multiple_pages(start_page: int, end_page, translations: Dict[str, str] = None) -> List[Tuple[str, str, str]]:
    """
    Scrape multiple pages and return all combinations (including duplicates).
    Returns list of tuples: (blades, ratchets, bits)

    Args:
        start_page: First page number to scrape
        end_page: Last page number to scrape, or "last" for the most recent page
        translations: Optional dictionary for translating abbreviated bits
    """
    if translations is None:
        translations = {}

    # If end_page is "last", determine the actual page number
    actual_end_page = end_page
    if end_page == "last":
        actual_end_page = get_last_page_number()
        if actual_end_page is None:
            print("Could not determine last page number")
            return []
        print(f"Last page is: {actual_end_page}")

    all_combinations = []

    for page_num in range(start_page, actual_end_page + 1):
        print(f"Scraping page {page_num}...")
        html = fetch_page(page_num)

        if html:
            combinations = extract_combinations(html, translations)
            all_combinations.extend(combinations)
            print(f"  Found {len(combinations)} combinations on page {page_num}")
        else:
            print(f"  Skipping page {page_num} (no content)")

    return all_combinations

def save_to_csv(combinations: List[Tuple], output_file: str = "beyblade_combinations.csv"):
    """Save combinations to a CSV file with headers: Blades, Ratchets, Bits."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(['Blades', 'Ratchets', 'Bits'])

        # Write data
        writer.writerows(combinations)

    print(f"\nSaved {len(combinations)} combinations to {output_file}")

def generate_summary(input_file: str, output_file: str = "summary.csv"):
    """
    Generate a summary CSV with counts for Blades, Ratchets, and Bits.

    Args:
        input_file: Path to the original CSV file
        output_file: Path to save the summary CSV
    """
    from collections import Counter

    # Read the original CSV
    part1_list = []
    part2_list = []
    part3_list = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header

            for row in reader:
                if len(row) >= 3:
                    part1_list.append(row[0])
                    part2_list.append(row[1])
                    part3_list.append(row[2])
    except FileNotFoundError:
        print(f"Error: Could not find file {input_file}")
        return

    # Count occurrences for each part
    part1_counts = Counter(part1_list)
    part2_counts = Counter(part2_list)
    part3_counts = Counter(part3_list)

    # Write summary CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Blades Summary
        writer.writerow(['Blades', 'Count'])
        for name, count in sorted(part1_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([name, count])

        writer.writerow([])  # Blank row

        # Ratchets Summary
        writer.writerow(['Ratchets', 'Count'])
        for numbers, count in sorted(part2_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([numbers, count])

        writer.writerow([])  # Blank row

        # Bits Summary
        writer.writerow(['Bits', 'Count'])
        for suffix, count in sorted(part3_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([suffix, count])

    print(f"Summary saved to {output_file}")

def generate_combination_counts(input_file: str, output_file: str = "combination_counts.csv"):
    """
    Generate a CSV counting full combinations (Blades + Ratchets + Bits).

    Args:
        input_file: Path to the original CSV file
        output_file: Path to save the combination counts CSV
    """
    from collections import Counter

    # Read the original CSV
    combinations = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header

            for row in reader:
                if len(row) >= 3:
                    # Store combination as tuple (blades, ratchets, bits)
                    combinations.append((row[0], row[1], row[2]))
    except FileNotFoundError:
        print(f"Error: Could not find file {input_file}")
        return

    # Count occurrences of each full combination
    combo_counts = Counter(combinations)

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(['Blades', 'Ratchets', 'Bits', 'Count'])

        # Write combinations sorted by count (descending)
        for combo, count in sorted(combo_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([combo[0], combo[1], combo[2], count])

    print(f"Combination counts saved to {output_file}")

def generate_html_charts(summary_file: str, combo_counts_file: str, output_file: str = "charts.html", title: str = "Beyblade X Winning Combinations", timestamp: str = ""):
    """
    Generate an HTML page with bar charts for top 10 entries.

    Args:
        summary_file: Path to the summary CSV file
        combo_counts_file: Path to the combination counts CSV file
        output_file: Path to save the HTML file
        title: Title to display on the HTML page
        timestamp: Timestamp when the script was run
    """
    # Read summary CSV and extract top 10 for each section
    part1_data = []
    part2_data = []
    part3_data = []

    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            current_section = None

            for row in reader:
                if not row or len(row) < 2:
                    continue

                # Detect section headers
                if row[0] == 'Blades':
                    current_section = 'part1'
                    continue
                elif row[0] == 'Ratchets':
                    current_section = 'part2'
                    continue
                elif row[0] == 'Bits':
                    current_section = 'part3'
                    continue
                elif row[0] == 'Date Range':
                    break  # Stop at date range section

                # Add data to appropriate section (top 10 only)
                if current_section == 'part1' and len(part1_data) < 10:
                    try:
                        part1_data.append((row[0], int(row[1])))
                    except (ValueError, IndexError):
                        pass
                elif current_section == 'part2' and len(part2_data) < 10:
                    try:
                        part2_data.append((row[0], int(row[1])))
                    except (ValueError, IndexError):
                        pass
                elif current_section == 'part3' and len(part3_data) < 10:
                    try:
                        part3_data.append((row[0], int(row[1])))
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        print(f"Warning: Could not find summary file {summary_file}")
        return

    # Read combo counts CSV and get top 10
    combo_data = []
    try:
        with open(combo_counts_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header

            for i, row in enumerate(reader):
                if i >= 10:  # Only top 10
                    break
                if len(row) >= 4:
                    try:
                        label = f"{row[0]} {row[1]} {row[2]}"
                        count = int(row[3])
                        combo_data.append((label, count))
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        print(f"Warning: Could not find combo counts file {combo_counts_file}")
        return

    # Generate HTML with Chart.js
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}
        h2 {{
            color: #555;
            margin-top: 0;
        }}
    </style>
</head>
<body>
    <h1>{title} - Top 10 Statistics</h1>
    <div class="timestamp">Generated: {timestamp}</div>

    <div class="chart-container">
        <h2>Top 10 Most Used Full Combinations</h2>
        <div class="chart-wrapper">
            <canvas id="comboChart"></canvas>
        </div>
    </div>

    <div class="chart-container">
        <h2>Top 10 Most Used Blades</h2>
        <div class="chart-wrapper">
            <canvas id="part1Chart"></canvas>
        </div>
    </div>

    <div class="chart-container">
        <h2>Top 10 Most Used Ratchets</h2>
        <div class="chart-wrapper">
            <canvas id="part2Chart"></canvas>
        </div>
    </div>

    <div class="chart-container">
        <h2>Top 10 Most Used Bits</h2>
        <div class="chart-wrapper">
            <canvas id="part3Chart"></canvas>
        </div>
    </div>

    <script>
        const chartConfig = {{
            type: 'bar',
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }};

        // Blades Chart
        new Chart(document.getElementById('part1Chart'), {{
            ...chartConfig,
            data: {{
                labels: {[f'"{item[0]}"' for item in part1_data]},
                datasets: [{{
                    label: 'Count',
                    data: {[item[1] for item in part1_data]},
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }}
        }});

        // Ratchets Chart
        new Chart(document.getElementById('part2Chart'), {{
            ...chartConfig,
            data: {{
                labels: {[f'"{item[0]}"' for item in part2_data]},
                datasets: [{{
                    label: 'Count',
                    data: {[item[1] for item in part2_data]},
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }}]
            }}
        }});

        // Bits Chart
        new Chart(document.getElementById('part3Chart'), {{
            ...chartConfig,
            data: {{
                labels: {[f'"{item[0]}"' for item in part3_data]},
                datasets: [{{
                    label: 'Count',
                    data: {[item[1] for item in part3_data]},
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }}]
            }}
        }});

        // Full Combination Chart
        new Chart(document.getElementById('comboChart'), {{
            ...chartConfig,
            data: {{
                labels: {[f'"{item[0]}"' for item in combo_data]},
                datasets: [{{
                    label: 'Count',
                    data: {[item[1] for item in combo_data]},
                    backgroundColor: 'rgba(153, 102, 255, 0.5)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }}]
            }}
        }});
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML charts saved to {output_file}")

def scrape_time_period(days: int, title: str, output_prefix: str, translations: Dict[str, str], last_page_num: int, hardcoded_start_page: Optional[int] = None, search_start_page: Optional[int] = None) -> Optional[int]:
    """
    Scrape a specific time period and generate all output files.

    Args:
        days: Number of days back to scrape (e.g., 30, 90)
        title: Title for the HTML charts
        output_prefix: Prefix for output filenames (e.g., "30days", "90days")
        translations: Translation dictionary for bits
        last_page_num: The actual last page number (newest posts)
        hardcoded_start_page: If provided, use this start page instead of searching
        search_start_page: If provided, start searching from this page (optimization for longer periods)

    Returns:
        The start page used for scraping, or None if scraping failed
    """
    print(f"\n{'=' * 60}")
    print(f"Processing: {title}")
    print(f"{'=' * 60}")

    # Use hardcoded start page if provided, otherwise search for it
    if hardcoded_start_page is not None:
        start_page = hardcoded_start_page
        print(f"  Using hardcoded start page: {start_page}")
    else:
        # Calculate target date
        target_date = datetime.now() - timedelta(days=days)

        # Use search_start_page if provided, otherwise use last_page_num
        search_from = search_start_page if search_start_page is not None else last_page_num
        if search_start_page is not None:
            print(f"  Starting search from page {search_start_page} (optimization)")

        # Find the start page
        start_page = find_page_for_date(target_date, start_page=search_from, max_pages_to_check=200)

        if start_page is None:
            print(f"Could not find start page for {days} days ago. Skipping.")
            return None

    # Generate timestamp
    timestamp = datetime.now().strftime("%m-%d-%Y")

    # Scrape pages
    print(f"\nScraping pages {start_page} to {last_page_num}...")
    combinations = scrape_multiple_pages(start_page, last_page_num, translations)

    # Save to CSV
    if combinations:
        output_file = f"{output_prefix}.csv"
        save_to_csv(combinations, output_file)
        print(f"\nTotal combinations found: {len(combinations)}")

        # Generate summary
        summary_file = f"{output_prefix}_summary.csv"
        print("Generating summary...")
        generate_summary(output_file, summary_file)

        # Generate combination counts
        combo_counts_file = f"{output_prefix}_combo_counts.csv"
        print("Generating combination counts...")
        generate_combination_counts(output_file, combo_counts_file)

        # Generate HTML charts
        html_file = f"{output_prefix}_charts.html"
        print("Generating HTML charts...")
        generate_html_charts(summary_file, combo_counts_file, html_file, title, timestamp)
        print(f">> Completed: {html_file}")

        # Return the start page used
        return start_page
    else:
        print("\nNo combinations found.")
        return None

def initialize_session():
    """Initialize session by visiting the homepage to get cookies."""
    print("Initializing session...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    try:
        session.get('https://worldbeyblade.org/', headers=headers, timeout=30)
        print("Session initialized successfully")
        time.sleep(2)
    except Exception as e:
        print(f"Warning: Could not initialize session: {e}")

def main():
    """Main function."""
    print("Beyblade Combination Scraper")
    print("=" * 50)

    # Initialize session with homepage visit
    initialize_session()

    # Load translations for abbreviations
    print("\nLoading suffix translations...")
    translations = load_translations()
    if translations:
        print(f"Loaded {len(translations)} translations")
    else:
        print("No translations loaded (will use original suffixes)")

    # Get the current last page number
    print("\nDetermining the last page...")
    last_page_num = get_last_page_number()
    if last_page_num is None:
        print("ERROR: Could not determine the last page number. Exiting.")
        return

    print(f"Last page number: {last_page_num}")

    # Scrape 30 days
    start_page_30days = scrape_time_period(
        days=30,
        title="Last 30 Days",
        output_prefix="30days",
        translations=translations,
        last_page_num=last_page_num
    )

    # Scrape 90 days (use 30-day start page as optimization)
    scrape_time_period(
        days=90,
        title="Last 90 Days",
        output_prefix="90days",
        translations=translations,
        last_page_num=last_page_num,
        search_start_page=start_page_30days
    )

    # Scrape year to date
    days_since_jan1 = (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    scrape_time_period(
        days=days_since_jan1,
        title="Year to Date",
        output_prefix="ytd",
        translations=translations,
        last_page_num=last_page_num,
        hardcoded_start_page=22
    )

    print("\n" + "=" * 60)
    print("All scraping complete!")
    print("Generated files:")
    print("  - 30days_charts.html")
    print("  - 90days_charts.html")
    print("  - ytd_charts.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
