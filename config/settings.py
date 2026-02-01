# F1 Dashboard Configuration

# Display settings
DISPLAY_MODE = "web"
WEB_PORT = 5000
REFRESH_INTERVAL = 300  # seconds (5 minutes)

# FastF1 cache settings
CACHE_DIRECTORY = "cache"
CACHE_FILE = "dashboard_data.json"

# Display preferences
SHOW_STANDINGS = True
SHOW_NEXT_EVENT = True
SHOW_EVENT_AFTER_NEXT = True

# Polling interval 
#  Update the cache this often
#  Value in hours, integer
POLL_INTERVAL_HOURS = 12