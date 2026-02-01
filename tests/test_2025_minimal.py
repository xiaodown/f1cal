"""Test minimal data loading with 2025 season."""

import os
import fastf1
from src.data import F1DataFetcher

def get_directory_size(path):
    total = 0
    if not os.path.exists(path):
        return 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_directory_size(entry.path)
    return total

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

print("=== Testing with 2025 season (has completed races) ===")

minimal_cache_before = get_directory_size('cache/fastf1_minimal')
print(f"Minimal cache before: {format_size(minimal_cache_before)}")

# Test with 2025 season that has completed races
fetcher = F1DataFetcher()
fetcher.current_year = 2025  # Override to test 2025 season
standings = fetcher.get_current_standings()

minimal_cache_after = get_directory_size('cache/fastf1_minimal')
print(f"Minimal cache after: {format_size(minimal_cache_after)}")
print(f"Added: {format_size(minimal_cache_after - minimal_cache_before)}")

print(f"\nResults:")
print(f"Driver standings: {len(standings['drivers'])} drivers")
print(f"Constructor standings: {len(standings['constructors'])} constructors")

if standings['drivers']:
    print(f"\nTop 3 drivers (2025 season):")
    for i, driver in enumerate(standings['drivers'][:3], 1):
        print(f"  {i}. {driver['name']} - {driver['points']} pts")
        
if standings['constructors']:
    print(f"\nTop 3 constructors (2025 season):")
    for i, constructor in enumerate(standings['constructors'][:3], 1):
        print(f"  {i}. {constructor['name']} - {constructor['points']} pts")