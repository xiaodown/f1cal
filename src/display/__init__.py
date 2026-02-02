"""Display module for rendering F1 dashboard."""

from abc import ABC, abstractmethod
from typing import Any
from flask import Flask, render_template, jsonify
from datetime import datetime


class DisplayBase(ABC):
    """Base class for display implementations."""
    
    @abstractmethod
    def render(self, data_cache: Any) -> None:
        """Render the data to the display."""
        pass


class WebDisplay(DisplayBase):
    """Web-based display using Flask with cached data."""
    
    def __init__(self, port: int = 5000):
        """Initialize web display."""
        self.port = port
        self.app = Flask(__name__, 
                        template_folder='../../templates',
                        static_folder='../../static')
        self.data_cache = None
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        @self.app.route('/')
        def dashboard():
            dashboard_data = self.data_cache.get_data()
            # Add last_updated timestamp for the template
            dashboard_data['last_updated'] = datetime.now()
            return render_template('dashboard.html', **dashboard_data)
        
        @self.app.route('/api/data')
        def api_data():
            return jsonify(self.data_cache.get_data())
        
        @self.app.route('/api/dashboard-data')
        def api_dashboard_data():
            """API endpoint for refresh - formats data for JavaScript"""
            data = self.data_cache.get_data()
            
            # Format the data to match what the JavaScript expects
            return jsonify({
                'next_event': data.get('next_event'),
                'event_after_next': data.get('event_after_next'),
                'standings': data.get('standings'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify(self.data_cache.get_cache_status())
        
        @self.app.route('/api/refresh', methods=['POST'])
        def api_refresh():
            """Force a data refresh."""
            self.data_cache.force_update()
            return jsonify({'status': 'refresh_initiated'})
    
    def render(self, data_cache: Any) -> None:
        """Start the web server with the data cache."""
        self.data_cache = data_cache
        
        print(f"Starting web server on http://localhost:{self.port}")
        print("Available endpoints:")
        print(f"  - Dashboard: http://localhost:{self.port}/")
        print(f"  - API Data: http://localhost:{self.port}/api/data")
        print(f"  - AJAX Dashboard Data: http://localhost:{self.port}/api/dashboard-data")
        print(f"  - Cache Status: http://localhost:{self.port}/api/status")
        print(f"  - Force Refresh: POST to http://localhost:{self.port}/api/refresh")
        print("Press Ctrl+C to stop")
        
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            data_cache.stop()


class DesktopDisplay(DisplayBase):
    """Desktop application display."""
    
    def render(self, data_cache: Any) -> None:
        """Render data as a desktop application."""
        print("Desktop display not implemented yet. Use web mode.")
        
        # Get current data
        data = data_cache.get_data()
        cache_status = data_cache.get_cache_status()
        
        print("Cache Status:")
        print(f"  - Has cached data: {cache_status['has_cached_data']}")
        print(f"  - Last update: {cache_status['last_update']}")
        print(f"  - Cache age: {cache_status['cache_age_hours']} hours")
        print(f"  - Update in progress: {cache_status['update_in_progress']}")
        
        print("\nData to display:")
        
        if data.get('next_event'):
            event = data['next_event']
            print(f"\nNext Event: {event['name']}")
            print(f"Location: {event['location']}")
            print(f"Date: {event['date']} at {event['time']}")
            print(f"Type: {event['type']}")
        
        if data.get('standings') and data['standings']['drivers']:
            standings = data['standings']
            print(f"\nTop 3 Drivers:")
            for i, driver in enumerate(standings['drivers'][:3], 1):
                print(f"  {i}. {driver['name']} - {driver['points']} pts")
            
            print(f"\nTop 3 Constructors:")
            for i, constructor in enumerate(standings['constructors'][:3], 1):
                print(f"  {i}. {constructor['name']} - {constructor['points']} pts")
        else:
            print("\nNo standings data available (beginning of season)")
        
        if data.get('event_after_next'):
            event = data['event_after_next']
            print(f"\nUpcoming: {event['name']}")
            print(f"Location: {event['location']}")
            print(f"Date: {event['date']}")
        
        if 'fetch_duration_minutes' in data and data['fetch_duration_minutes']:
            print(f"\nLast data fetch took: {data['fetch_duration_minutes']} minutes")