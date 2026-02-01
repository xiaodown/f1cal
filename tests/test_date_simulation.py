#!/usr/bin/env python3
"""
Test script to simulate the F1 dashboard at a specific date.
This simulates being between race 4 and 5 of the 2025 season.
"""

import os
import sys
import shutil
from datetime import datetime, timezone
from unittest.mock import patch
import pandas as pd

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data import F1DataFetcher
from display import WebDisplay

def clear_cache():
    """Clear the existing cache to ensure fresh data."""
    cache_dir = '../cache'
    if os.path.exists(cache_dir):
        print(f"Clearing cache directory: {cache_dir}")
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)

def get_race_4_and_5_dates():
    """Get the dates for races 4 and 5 of 2025 to pick a date in between."""
    import fastf1
    
    # Temporarily enable cache
    fastf1.Cache.enable_cache('../cache')
    
    try:
        schedule = fastf1.get_event_schedule(2025)
        race_events = schedule[schedule['EventFormat'] != 'testing'].copy()
        
        if len(race_events) >= 5:
            race_4 = race_events.iloc[3]  # 4th race (0-indexed)
            race_5 = race_events.iloc[4]  # 5th race (0-indexed)
            
            print(f"Race 4: {race_4['EventName']} - Race Date: {race_4['Session5DateUtc']}")
            print(f"Race 5: {race_5['EventName']} - Race Date: {race_5['Session5DateUtc']}")
            
            # Convert to datetime objects
            race_4_date = pd.to_datetime(race_4['Session5DateUtc'])
            race_5_date = pd.to_datetime(race_5['Session5DateUtc'])
            
            # Pick a date in between (average of the two dates)
            midpoint = race_4_date + (race_5_date - race_4_date) / 2
            
            return midpoint, race_4, race_5
        else:
            raise ValueError("Not enough races in 2025 schedule")
            
    except Exception as e:
        print(f"Error getting race dates: {e}")
        return None, None, None

def test_dashboard_at_date(test_date):
    """Test the dashboard as if it were running at the specified date."""
    print(f"\n=== SIMULATING DASHBOARD AT: {test_date} ===\n")
    
    # Mock the current time to our test date
    with patch('src.data.datetime') as mock_datetime, \
         patch('src.data.pd.Timestamp.now') as mock_timestamp_now:
        
        # Configure the mocks
        mock_datetime.now.return_value = test_date.to_pydatetime()
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        mock_timestamp_now.return_value = pd.Timestamp(test_date, tz='UTC')
        
        # Create fetcher with mocked time
        fetcher = F1DataFetcher()
        # Override the current_year to 2025 for our test
        fetcher.current_year = 2025
        
        print("Fetching next event...")
        next_event = fetcher.get_next_event()
        
        print("Fetching current standings...")
        standings = fetcher.get_current_standings()
        
        print("\n=== RESULTS ===\n")
        
        if next_event:
            print("NEXT EVENT:")
            print(f"  Name: {next_event['name']}")
            print(f"  Location: {next_event['location']}")
            print(f"  Date: {next_event['date']}")
            print(f"  Time: {next_event['time']}")
            print(f"  Type: {next_event['type']}")
            print(f"  Round: {next_event['round']}")
        else:
            print("NEXT EVENT: None found")
        
        print("\nDRIVER STANDINGS:")
        if standings['drivers']:
            for i, driver in enumerate(standings['drivers'], 1):
                print(f"  {i}. {driver['name']}: {driver['points']} pts")
        else:
            print("  No driver standings available")
        
        print("\nCONSTRUCTOR STANDINGS:")
        if standings['constructors']:
            for i, constructor in enumerate(standings['constructors'], 1):
                print(f"  {i}. {constructor['name']}: {constructor['points']} pts")
        else:
            print("  No constructor standings available")
        
        return next_event, standings

def create_test_webpage(next_event, standings):
    """Create and save a test webpage with the results."""
    print("\n=== CREATING TEST WEBPAGE ===\n")
    
    # Read the CSS file
    css_content = ""
    css_path = 'static/css/style.css'
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    
    # Generate driver standings HTML
    driver_standings_html = ""
    if standings['drivers']:
        driver_standings_html = """
        <div class="driver-standings">
            <h3>Driver Standings</h3>"""
        for i, driver in enumerate(standings['drivers'], 1):
            driver_standings_html += f"""
            <div class="standing-item">
                <span class="position">{i}</span>
                <span class="name">{driver['name']}</span>
                <span class="points">{driver['points']}</span>
            </div>"""
        driver_standings_html += "\n        </div>"
    
    # Generate constructor standings HTML  
    constructor_standings_html = ""
    if standings['constructors']:
        constructor_standings_html = """
        <div class="constructor-standings">
            <h3>Constructor Standings</h3>"""
        for i, constructor in enumerate(standings['constructors'], 1):
            constructor_standings_html += f"""
            <div class="standing-item">
                <span class="position">{i}</span>
                <span class="name">{constructor['name']}</span>
                <span class="points">{constructor['points']}</span>
            </div>"""
        constructor_standings_html += "\n        </div>"
    
    # Generate the complete HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>F1 Dashboard - Test</title>
    <style>{css_content}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Formula 1 Dashboard</h1>
            <div class="last-updated">
                Test simulation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </header>

        <main>
            <!-- Next Event Section -->
            <section class="next-event">
                <h2>Next Event</h2>
                <div class="event-card">
                    <h3>{next_event['name'] if next_event else 'No upcoming event'}</h3>
                    {"<div class='event-details'>" if next_event else ""}
                        {"<div class='event-location'>" + next_event['location'] + "</div>" if next_event else ""}
                        {"<div class='event-date'>" + next_event['date'] + "</div>" if next_event else ""}
                        {"<div class='event-time'>" + next_event['time'] + "</div>" if next_event else ""}
                        {"<div class='event-type'>" + next_event['type'] + "</div>" if next_event else ""}
                    {"</div>" if next_event else ""}
                </div>
            </section>

            <!-- Standings Section -->
            <section class="standings">
                <div class="standings-grid">
                    {driver_standings_html}
                    {constructor_standings_html}
                </div>
            </section>
        </main>
    </div>
</body>
</html>"""
    
    # Save to file
    test_file = 'test_dashboard.html'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Test webpage saved as: {test_file}")
    print("You can open this file in your browser to see how it would look.")
    
    return test_file

def main():
    """Main test function."""
    print("=== F1 DASHBOARD DATE SIMULATION TEST ===\n")
    
    # Clear cache for fresh test
    clear_cache()
    
    print("Getting 2025 race schedule to find dates between race 4 and 5...")
    test_date, race_4, race_5 = get_race_4_and_5_dates()
    
    if test_date is None:
        print("Failed to get race dates. Exiting.")
        return
    
    print(f"\nTest date selected: {test_date}")
    print(f"This is after: {race_4['EventName']} ({race_4['Session5DateUtc']})")
    print(f"And before: {race_5['EventName']} ({race_5['Session5DateUtc']})")
    
    # Run the dashboard test
    next_event, standings = test_dashboard_at_date(test_date)
    
    # Create test webpage
    test_file = create_test_webpage(next_event, standings)
    
    print(f"\n=== TEST COMPLETE ===")
    print(f"Open {test_file} in your browser to see the simulated dashboard.")
    
    # Optionally start a simple web server to view the file
    response = input("\nWould you like to start a simple web server to view the page? (y/n): ")
    if response.lower().startswith('y'):
        import http.server
        import socketserver
        import webbrowser
        import threading
        
        port = 8000
        handler = http.server.SimpleHTTPRequestHandler
        
        def run_server():
            with socketserver.TCPServer(("", port), handler) as httpd:
                print(f"Serving at http://localhost:{port}/test_dashboard.html")
                httpd.serve_forever()
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Open browser
        webbrowser.open(f'http://localhost:{port}/test_dashboard.html')
        
        print("Press Enter to exit...")
        input()

if __name__ == "__main__":
    main()