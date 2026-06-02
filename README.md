# Instagram Followers Tracker

A lightweight Python script for tracking Instagram followers/following counts on Android (Termux) and desktop. Perfect for KWGT widget integration.

## Features

✨ **Core Features:**
- Web scraping (no API key required)
- JSON file storage for historical tracking
- KWGT widget-friendly output format
- Lightweight and Termux-optimized
- Change detection (compare with previous counts)
- Formatted numbers (K, M suffixes)

## Installation

### On Termux (Android)

```bash
pkg install python3 pip
pip install requests beautifulsoup4
git clone https://github.com/wqauloises/Instagramcounts.git
cd Instagramcounts
chmod +x main.py
```

### On Desktop (Linux/Mac/Windows)

```bash
python3 -m pip install -r requirements.txt
```

## Usage

### Add an account to track
```bash
python3 main.py add cristiano
python3 main.py add messi
```

### List tracked accounts
```bash
python3 main.py list
```

### Track all accounts
```bash
python3 main.py track-all
```

### Track single account
```bash
python3 main.py track cristiano
```

### Show statistics
```bash
python3 main.py stats cristiano
```

### Update widget file
```bash
python3 main.py widget
```

## Data Files

All data is stored in `~/.instacounts/` (your home directory):

- **`accounts.json`** - Full tracking history
- **`config.json`** - List of tracked accounts
- **`widget.json`** - Latest data in KWGT-friendly format

### widget.json Example

```json
{
  "updated": "2026-06-02T15:30:45.123456",
  "accounts": [
    {
      "username": "cristiano",
      "followers": 629000000,
      "following": 500,
      "posts": 3500,
      "change_followers": 150000,
      "change_following": 0,
      "is_private": false,
      "last_update": "2026-06-02T15:30:45.123456",
      "formatted_followers": "629.0M",
      "formatted_following": "500"
    }
  ]
}
```

## KWGT Widget Integration

Use the `widget.json` file in your KWGT widgets:

1. In KWGT, add a new widget
2. Set data source to read from: `~/.instacounts/widget.json`
3. Create custom layouts using the JSON fields

### Useful widget fields:
- `formatted_followers` - Display followers with K/M suffix
- `change_followers` - Shows +/- change since last check
- `accounts[].username` - Username
- `updated` - Last update timestamp

## Automation (Termux)

### Schedule with cron (Termux)

```bash
# Install termux-api
pkg install termux-api

# Edit crontab
crontab -e

# Add this line to track every hour:
0 * * * * cd ~/Instagramcounts && python3 main.py track-all
```

### Schedule with GitHub Actions

Create `.github/workflows/track.yml`:

```yaml
name: Track Instagram
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python3 main.py track-all
```

## Storage

- **Data retention:** Last 1000 entries per account (prevents file bloat)
- **File location:** `~/.instacounts/` (hidden directory)
- **Format:** Plain JSON (human-readable)

## Troubleshooting

### "Could not find Instagram account"
- Check if the username is correct
- Instagram might be rate-limiting, wait a bit and try again
- Make sure you have internet connection

### No data appearing in widget.json
- Run `python3 main.py track-all` first
- Check if `~/.instacounts/` directory exists
- Run `python3 main.py widget` to manually update

### Rate limiting issues
- The script includes 2-second delays between requests
- If still hitting limits, add longer delays in the code
- Consider spacing out tracking times

## Tips

- Track multiple accounts and compare growth
- Use KWGT to display your favorite accounts
- Schedule tracking hourly for detailed analytics
- Export data to analyze trends over time

## License

MIT - Use freely!

## Note

This tool uses web scraping. Instagram might change their page structure, which could break the scraper. If it stops working, please open an issue.