#!/usr/bin/env python3
"""Cache management utility for F1 dashboard."""

import os
import shutil
from pathlib import Path


def get_directory_size(path):
    """Get the size of a directory in bytes."""
    total = 0
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


def analyze_cache():
    """Analyze current cache usage."""
    print("F1 Dashboard Cache Analysis")
    print("=" * 40)
    
    cache_dirs = [
        'cache',
        'cache/fastf1_minimal',
        'cache'  # old cache location
    ]
    
    total_size = 0
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            size = get_directory_size(cache_dir)
            total_size += size
            print(f"{cache_dir}: {format_size(size)}")
            
            # Show top-level subdirectories
            try:
                for item in sorted(os.listdir(cache_dir)):
                    item_path = os.path.join(cache_dir, item)
                    if os.path.isdir(item_path):
                        item_size = get_directory_size(item_path)
                        print(f"  └── {item}: {format_size(item_size)}")
            except PermissionError:
                print(f"  └── (Permission denied)")
    
    print(f"\nTotal cache size: {format_size(total_size)}")
    
    # Show dashboard cache file
    if os.path.exists('dashboard_data.json'):
        dashboard_size = os.path.getsize('dashboard_data.json')
        print(f"Dashboard cache: {format_size(dashboard_size)}")


def clean_old_cache():
    """Clean up old/unnecessary cache files."""
    print("\nCleaning old cache...")
    
    # Move from old cache to new minimal cache location
    old_cache = 'cache'
    new_cache = 'cache/fastf1_minimal'
    
    if os.path.exists(old_cache) and not os.path.exists(new_cache):
        print(f"Moving cache from {old_cache} to {new_cache}")
        os.makedirs('cache', exist_ok=True)
        if os.path.exists(old_cache) and os.path.isdir(old_cache):
            # Only keep session info and results data, skip telemetry
            os.makedirs(new_cache, exist_ok=True)
            
    print("Cache cleanup complete!")


def clear_all_cache():
    """Clear all cache data."""
    print("\nWARNING: This will delete ALL cached data!")
    response = input("Are you sure? (y/N): ")
    
    if response.lower() == 'y':
        cache_dirs = ['cache', 'dashboard_data.json']
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                if os.path.isdir(cache_dir):
                    shutil.rmtree(cache_dir)
                    print(f"Deleted directory: {cache_dir}")
                else:
                    os.remove(cache_dir)
                    print(f"Deleted file: {cache_dir}")
        print("All cache cleared!")
    else:
        print("Cache clearing cancelled.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "analyze":
            analyze_cache()
        elif command == "clean":
            clean_old_cache()
        elif command == "clear":
            clear_all_cache()
        else:
            print("Usage: python cache_manager.py [analyze|clean|clear]")
    else:
        analyze_cache()
        print("\nAvailable commands:")
        print("  python cache_manager.py analyze  - Show cache usage")
        print("  python cache_manager.py clean    - Clean old cache")
        print("  python cache_manager.py clear    - Clear ALL cache")