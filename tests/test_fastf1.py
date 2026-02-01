"""Quick test to see FastF1 data structure."""

import fastf1
import pandas as pd
from datetime import datetime, timezone

# Enable cache
fastf1.Cache.enable_cache('../cache')

# Get current year schedule
schedule = fastf1.get_event_schedule(2024)  # Let's try 2024 which has completed data
print("Schedule columns:", schedule.columns.tolist())

# Filter out testing and show only race events
race_events = schedule[schedule['EventFormat'] != 'testing'].copy()
print(f"\nTotal events: {len(schedule)}, Race events: {len(race_events)}")

print("\nFirst race event:")
if not race_events.empty:
    first_race = race_events.iloc[0]
    print(first_race)
    print(f"\nSession5DateUtc type: {type(first_race['Session5DateUtc'])}")
    print(f"Sample race date: {first_race['Session5DateUtc']}")

# Test with proper timezone handling
now = pd.Timestamp.now(tz='UTC')
print(f"\nNow timestamp: {now}")

try:
    # Convert datetime columns to proper timezone-aware timestamps
    for col in ['Session1DateUtc', 'Session2DateUtc', 'Session3DateUtc', 'Session4DateUtc', 'Session5DateUtc']:
        race_events[col] = pd.to_datetime(race_events[col], utc=True)
    
    # Filter for future events
    upcoming = race_events[race_events['Session5DateUtc'] > now]
    print(f"Upcoming race events: {len(upcoming)}")
    
    if not upcoming.empty:
        next_race = upcoming.iloc[0]
        print(f"Next race: {next_race['EventName']} on {next_race['Session5DateUtc']}")
    else:
        print("No upcoming races in 2024")
        
        # Let's also check 2025 and 2026
        for year in [2025, 2026]:
            try:
                future_schedule = fastf1.get_event_schedule(year)
                future_races = future_schedule[future_schedule['EventFormat'] != 'testing'].copy()
                if not future_races.empty:
                    # Convert datetime columns
                    for col in ['Session1DateUtc', 'Session2DateUtc', 'Session3DateUtc', 'Session4DateUtc', 'Session5DateUtc']:
                        future_races[col] = pd.to_datetime(future_races[col], utc=True)
                    
                    upcoming_future = future_races[future_races['Session5DateUtc'] > now]
                    print(f"Upcoming races in {year}: {len(upcoming_future)}")
                    if not upcoming_future.empty:
                        next_race = upcoming_future.iloc[0]
                        print(f"Next race in {year}: {next_race['EventName']} on {next_race['Session5DateUtc']}")
                        break
            except Exception as e:
                print(f"Error getting {year} schedule: {e}")
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()