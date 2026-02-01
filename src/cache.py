"""Background data polling and caching system."""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from src.data import F1DataFetcher
from config.settings import CACHE_FILE,POLL_INTERVAL_HOURS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class F1DataCache:
    """Manages cached F1 data with background polling."""
    
    def __init__(self, cache_file: str = CACHE_FILE, poll_interval_hours: int = POLL_INTERVAL_HOURS):
        self.cache_file = cache_file
        self.poll_interval = timedelta(hours=poll_interval_hours)
        self.data_fetcher = F1DataFetcher()
        self.cached_data: Optional[Dict[str, Any]] = None
        self.last_update: Optional[datetime] = None
        self.update_in_progress = False
        self.stop_polling = False
        
        # Load existing cache
        self.load_cache()
        
        # Start background polling thread
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        logger.info(f"Started background polling every {poll_interval_hours} hours")
    
    def load_cache(self) -> None:
        """Load cached data from disk."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_content = json.load(f)
                    self.cached_data = cache_content.get('data')
                    last_update_str = cache_content.get('last_update')
                    if last_update_str:
                        self.last_update = datetime.fromisoformat(last_update_str)
                        logger.info(f"Loaded cached data from {last_update_str}")
                    
                    # Convert datetime strings back to datetime objects in the loaded data
                    if self.cached_data and 'last_updated' in self.cached_data:
                        if isinstance(self.cached_data['last_updated'], str):
                            self.cached_data['last_updated'] = datetime.fromisoformat(self.cached_data['last_updated'])
            else:
                logger.info("No existing cache found")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.cached_data = None
            self.last_update = None
    
    def save_cache(self, data: Dict[str, Any]) -> None:
        """Save data to cache file."""
        try:
            cache_content = {
                'data': data,
                'last_update': datetime.now().isoformat()
            }
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = f"{self.cache_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(cache_content, f, indent=2, default=str)
            
            os.rename(temp_file, self.cache_file)
            logger.info(f"Saved cache to {self.cache_file}")
            
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def fetch_fresh_data(self) -> Dict[str, Any]:
        """Fetch fresh data from F1 APIs."""
        logger.info("Fetching fresh F1 data...")
        
        try:
            # Add delays between API calls to be respectful
            logger.info("- Getting next event...")
            next_event = self.data_fetcher.get_next_event()
            
            # Small delay between calls
            time.sleep(2)
            
            logger.info("- Getting current standings...")
            standings = self.data_fetcher.get_current_standings()
            
            time.sleep(2)
            
            logger.info("- Getting event after next...")
            event_after_next = self.data_fetcher.get_event_after_next()
            
            data = {
                'next_event': next_event,
                'standings': standings,
                'event_after_next': event_after_next,
                'last_updated': datetime.now(),
                'fetch_duration_minutes': None  # Will be calculated by caller
            }
            
            logger.info("Fresh data fetched successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching fresh data: {e}")
            raise
    
    def update_data(self) -> None:
        """Update cached data with fresh fetch."""
        if self.update_in_progress:
            logger.info("Update already in progress, skipping...")
            return
        
        try:
            self.update_in_progress = True
            start_time = datetime.now()
            
            fresh_data = self.fetch_fresh_data()
            
            # Calculate fetch duration
            fetch_duration = datetime.now() - start_time
            fresh_data['fetch_duration_minutes'] = round(fetch_duration.total_seconds() / 60, 1)
            
            # Update cache
            self.cached_data = fresh_data
            self.last_update = datetime.now()
            
            # Save to disk
            self.save_cache(fresh_data)
            
            logger.info(f"Data update completed in {fresh_data['fetch_duration_minutes']} minutes")
            
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
        finally:
            self.update_in_progress = False
    
    def get_data(self) -> Dict[str, Any]:
        """Get cached data, fetching fresh if needed."""
        # If no cached data exists, fetch immediately
        if self.cached_data is None:
            logger.info("No cached data available, fetching immediately...")
            self.update_data()
        
        # If still no data after fetch attempt, return empty data
        if self.cached_data is None:
            logger.warning("Unable to fetch data, returning empty dataset")
            return {
                'next_event': None,
                'standings': {'drivers': [], 'constructors': []},
                'event_after_next': None,
                'last_updated': datetime.now(),
                'error': 'Unable to fetch F1 data'
            }
        
        # Make a copy and ensure datetime objects are properly handled
        data = self.cached_data.copy()
        
        # Convert string datetimes back to datetime objects for template
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        elif 'last_updated' not in data:
            data['last_updated'] = self.last_update or datetime.now()
        
        return data
    
    def should_update(self) -> bool:
        """Check if data should be updated based on age."""
        if self.last_update is None:
            return True
        
        age = datetime.now() - self.last_update
        return age >= self.poll_interval
    
    def _polling_loop(self) -> None:
        """Background polling loop."""
        logger.info("Background polling started")
        
        # Initial delay before first poll (let the server start up first)
        time.sleep(30)  # 30 seconds
        
        while not self.stop_polling:
            try:
                if self.should_update():
                    logger.info("Scheduled data update starting...")
                    self.update_data()
                
                # Sleep in small chunks so we can stop quickly if needed
                for _ in range(300):  # Check every 5 minutes if we should poll
                    if self.stop_polling:
                        break
                    time.sleep(60)  # 1 minute
                    
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
        
        logger.info("Background polling stopped")
    
    def stop(self) -> None:
        """Stop background polling."""
        logger.info("Stopping background polling...")
        self.stop_polling = True
        if self.polling_thread.is_alive():
            self.polling_thread.join(timeout=5)
    
    def force_update(self) -> None:
        """Force an immediate data update."""
        logger.info("Forcing immediate data update...")
        self.update_data()
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get information about cache status."""
        return {
            'has_cached_data': self.cached_data is not None,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'update_in_progress': self.update_in_progress,
            'should_update': self.should_update(),
            'cache_age_hours': round((datetime.now() - self.last_update).total_seconds() / 3600, 1) if self.last_update else None
        }