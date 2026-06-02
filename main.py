#!/usr/bin/env python3
"""Instagram Followers/Following Tracker
Tracks followers and following counts with JSON storage
KWGT widget-friendly output format
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

# Configuration
DATA_DIR = Path.home() / ".instacounts"
DATA_FILE = DATA_DIR / "accounts.json"
CONFIG_FILE = DATA_DIR / "config.json"
WIDGET_FILE = DATA_DIR / "widget.json"

# Create data directory
DATA_DIR.mkdir(exist_ok=True)


def load_config():
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"accounts": []}


def save_config(config):
    """Save configuration to config.json"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_data():
    """Load tracking data from JSON"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"tracks": []}


def save_data(data):
    """Save tracking data to JSON"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def scrape_instagram_user(username):
    """
    Scrape Instagram user data using requests + BeautifulSoup
    Returns dict with followers, following, posts counts
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://www.instagram.com/{username}/"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract JSON data from HTML
        if 'window._sharedData' in response.text:
            start = response.text.find('window._sharedData = ') + len('window._sharedData = ')
            end = response.text.find('};', start) + 1
            json_str = response.text[start:end]
            data = json.loads(json_str)
            
            user_info = data['entry_data']['ProfilePage'][0]['graphql']['user']
            
            return {
                'username': user_info['username'],
                'followers': user_info['edge_followed_by']['count'],
                'following': user_info['edge_follow']['count'],
                'posts': user_info['edge_owner_to_timeline_media']['count'],
                'is_private': user_info['is_private'],
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error scraping {username}: {str(e)}", file=sys.stderr)
        return None


def track_account(username):
    """Track a single account and store data"""
    print(f"Tracking {username}...", end=" ")
    
    user_data = scrape_instagram_user(username)
    
    if not user_data:
        print("FAILED")
        return False
    
    data = load_data()
    
    # Add to tracks
    data['tracks'].append(user_data)
    
    # Keep only last 1000 entries per account to prevent file bloat
    account_tracks = [t for t in data['tracks'] if t.get('username') == username]
    if len(account_tracks) > 1000:
        data['tracks'] = [t for t in data['tracks'] if t.get('username') != username]
        data['tracks'].extend(account_tracks[-1000:])
    
    save_data(data)
    print("OK")
    
    return user_data


def update_widget_file():
    """Update widget.json with latest data - KWGT friendly format"""
    data = load_data()
    config = load_config()
    
    widget_data = {
        'updated': datetime.now().isoformat(),
        'accounts': []
    }
    
    # Group by account and get latest data
    accounts_dict = {}
    for track in data['tracks']:
        username = track.get('username')
        if username not in accounts_dict:
            accounts_dict[username] = track
        else:
            # Keep newer timestamp
            if track.get('timestamp') > accounts_dict[username].get('timestamp', ''):
                accounts_dict[username] = track
    
    for account in accounts_dict.values():
        username = account.get('username')
        
        # Calculate changes if there's historical data
        change_followers = 0
        change_following = 0
        
        account_history = [t for t in data['tracks'] if t.get('username') == username]
        if len(account_history) > 1:
            prev = account_history[-2]
            change_followers = account['followers'] - prev['followers']
            change_following = account['following'] - prev['following']
        
        widget_data['accounts'].append({
            'username': username,
            'followers': account['followers'],
            'following': account['following'],
            'posts': account['posts'],
            'change_followers': change_followers,
            'change_following': change_following,
            'is_private': account.get('is_private', False),
            'last_update': account.get('timestamp'),
            'formatted_followers': format_number(account['followers']),
            'formatted_following': format_number(account['following'])
        })
    
    with open(WIDGET_FILE, 'w') as f:
        json.dump(widget_data, f, indent=2)
    
    print(f"\nWidget file updated: {WIDGET_FILE}")


def format_number(num):
    """Format number with K, M suffixes for display"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def show_stats(username):
    """Show statistics for a specific account"""
    data = load_data()
    account_data = [t for t in data['tracks'] if t.get('username') == username]
    
    if not account_data:
        print(f"No data found for {username}")
        return
    
    print(f"\n=== Stats for @{username} ===")
    latest = account_data[-1]
    
    print(f"Current followers: {latest['followers']:,} ({format_number(latest['followers'])})")
    print(f"Current following: {latest['following']:,} ({format_number(latest['following'])})")
    print(f"Posts: {latest['posts']:,}")
    print(f"Private: {latest['is_private']}")
    print(f"Last updated: {latest['timestamp']}")
    
    if len(account_data) > 1:
        first = account_data[0]
        print(f"\nTotal followers change: {latest['followers'] - first['followers']:+,}")
        print(f"Total following change: {latest['following'] - first['following']:+,}")
        print(f"Tracked since: {first['timestamp']}")
    
    print()


def add_account(username):
    """Add account to tracking list"""
    config = load_config()
    
    if username in config['accounts']:
        print(f"{username} is already tracked")
        return
    
    # Verify account exists
    user_data = scrape_instagram_user(username)
    if not user_data:
        print(f"Could not find Instagram account: {username}")
        return
    
    config['accounts'].append(username)
    save_config(config)
    print(f"Added {username} to tracking")


def remove_account(username):
    """Remove account from tracking list"""
    config = load_config()
    
    if username not in config['accounts']:
        print(f"{username} is not in tracking list")
        return
    
    config['accounts'].remove(username)
    save_config(config)
    print(f"Removed {username} from tracking")


def list_accounts():
    """List all tracked accounts"""
    config = load_config()
    
    if not config['accounts']:
        print("No accounts being tracked")
        return
    
    print("\nTracked accounts:")
    for account in config['accounts']:
        print(f"  - {account}")
    print()


def track_all():
    """Track all configured accounts"""
    config = load_config()
    
    if not config['accounts']:
        print("No accounts configured. Use 'add <username>' first")
        return
    
    print(f"Tracking {len(config['accounts'])} accounts...")
    
    for account in config['accounts']:
        track_account(account)
        time.sleep(2)  # Rate limiting
    
    update_widget_file()


def main():
    if len(sys.argv) < 2:
        print("Instagram Followers Tracker")
        print("\nUsage:")
        print("  python main.py add <username>        - Add account to track")
        print("  python main.py remove <username>     - Remove account from tracking")
        print("  python main.py list                  - List all tracked accounts")
        print("  python main.py track <username>      - Track specific account once")
        print("  python main.py track-all             - Track all configured accounts")
        print("  python main.py stats <username>      - Show stats for account")
        print("  python main.py widget                - Update widget.json")
        print("\nExample:")
        print("  python main.py add cristiano")
        print("  python main.py track-all")
        print("  python main.py stats cristiano")
        return
    
    command = sys.argv[1].lower()
    
    if command == "add" and len(sys.argv) > 2:
        add_account(sys.argv[2])
    elif command == "remove" and len(sys.argv) > 2:
        remove_account(sys.argv[2])
    elif command == "list":
        list_accounts()
    elif command == "track" and len(sys.argv) > 2:
        user_data = track_account(sys.argv[2])
        if user_data:
            update_widget_file()
    elif command == "track-all":
        track_all()
    elif command == "stats" and len(sys.argv) > 2:
        show_stats(sys.argv[2])
    elif command == "widget":
        update_widget_file()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()