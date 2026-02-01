"""Main application entry point."""

import sys
import argparse
import signal
from datetime import datetime
from src.cache import F1DataCache
from src.display import WebDisplay, DesktopDisplay


def signal_handler(signum, frame, data_cache):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}, shutting down...")
    data_cache.stop()
    sys.exit(0)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='F1 Dashboard with Background Polling')
    parser.add_argument('--mode', choices=['web', 'desktop'], default='web',
                       help='Display mode (web or desktop)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port for web mode (default: 5000)')
    parser.add_argument('--poll-hours', type=int, default=12,
                       help='Hours between data polls (default: 12)')
    parser.add_argument('--cache-file', default='dashboard_data.json',
                       help='Cache file location (default: dashboard_data.json)')
    parser.add_argument('--force-update', action='store_true',
                       help='Force immediate data update on startup')
    
    args = parser.parse_args()
    
    print("F1 Dashboard Starting...")
    print(f"Mode: {args.mode}")
    print(f"Polling interval: {args.poll_hours} hours")
    print(f"Cache file: {args.cache_file}")
    
    try:
        # Initialize data cache with background polling
        data_cache = F1DataCache(
            cache_file=args.cache_file, 
            poll_interval_hours=args.poll_hours
        )
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, data_cache))
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, data_cache))
        
        # Force update if requested
        if args.force_update:
            print("Forcing immediate data update...")
            data_cache.force_update()
        
        # Initialize display
        if args.mode == 'web':
            display = WebDisplay(port=args.port)
        else:
            display = DesktopDisplay()
        
        print("Initialization complete!")
        
        # Start display (this will block)
        display.render(data_cache)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()