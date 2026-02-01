"""Test standings at beginning of season vs mid-season."""

import fastf1
import pandas as pd
from datetime import datetime
from src.data import F1DataFetcher

# Enable cache
fastf1.Cache.enable_cache('cache')

# Test current year (2026) - should have no completed races if we're in February
print("=== Testing 2026 standings (current year) ===")
fetcher = F1DataFetcher()
standings_2026 = fetcher.get_current_standings()
print(f"2026 Drivers: {standings_2026['drivers']}")
print(f"2026 Constructors: {standings_2026['constructors']}")

# Test mid-season 2025 standings by temporarily modifying the year
print("\n=== Testing 2025 standings (should have full season data) ===")
fetcher.current_year = 2025
standings_2025 = fetcher.get_current_standings()
print(f"2025 Drivers: {standings_2025['drivers']}")
print(f"2025 Constructors: {standings_2025['constructors']}")

print(f"\n=== Analysis ===")
print(f"2026 (beginning of season): {len(standings_2026['drivers'])} drivers with points")
print(f"2025 (full season): {len(standings_2025['drivers'])} drivers with points")