"""Test the new minimal data loading approach."""

import os
import fastf1
import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data import F1DataFetcher

# First, let's see the current cache size
def get_directory_size(path):
    """Get the size of a directory in bytes."""
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
    """Format bytes as human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

print("=== BEFORE: Current cache size ===")
old_cache_size = get_directory_size('../cache')
print(f"Old cache size: {format_size(old_cache_size)}")

print("\n=== Testing minimal data loading ===")

# Test with minimal data loading
fetcher = F1DataFetcher()
standings = fetcher.get_current_standings()

print(f"Driver standings: {len(standings['drivers'])} drivers")
print(f"Constructor standings: {len(standings['constructors'])} constructors")

print("\n=== AFTER: New cache size ===")
new_cache_size = get_directory_size('../cache')
minimal_cache_size = get_directory_size('../cache/fastf1_minimal')

print(f"Old cache size: {format_size(old_cache_size)}")
print(f"New total cache size: {format_size(new_cache_size)}")
print(f"Minimal cache size: {format_size(minimal_cache_size)}")
print(f"Difference: {format_size(new_cache_size - old_cache_size)}")

if standings['drivers']:
    print(f"\nTop 3 drivers:")
    for i, driver in enumerate(standings['drivers'][:3], 1):
        print(f"  {i}. {driver['name']} - {driver['points']} pts")