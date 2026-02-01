# F1 Dashboard

A Formula 1 information dashboard optimized for Raspberry Pi displays, built with Python and FastF1. Perfect for showing next race information and championship standings on a 3.5" touchscreen.

This is still a work-in-progress.  A significant portion of it is vibe-coded, and I'm still working on testing it on the actual raspberry pi.

I am planning on using [this 3d printed case](https://www.printables.com/model/14035-raspberry-pi-4-adafruit-35-tft-case-with-fan) to hold the rpi and the adafruit 3.5" display.

## 🏁 Features

### Race Information
- **Next Event Display**: Shows upcoming Sprint Qualifying, Sprint, Qualifying, or Race sessions
- **Sprint Weekend Support**: Properly detects and displays Sprint events alongside traditional races
- **Timezone Conversion**: Displays times in your local timezone
- **Event After Next**: Preview of the following race weekend

### Championship Standings
- **Live Standings**: Top 3 drivers and constructors with current points
- **Spoiler Protection**: Blur standings until manually revealed (perfect for watching races delayed!)
- **Smart Change Detection**: Auto-blurs when new race results come in
- **Touch-Friendly**: Tap anywhere on standings to reveal

### Technical Features
- **Background Polling**: Automatically updates data every 12 hours
- **Minimal Cache**: Optimized FastF1 integration (2MB vs 5GB+ typical usage)
- **Raspberry Pi Optimized**: Designed for 3.5" touchscreens (480x320)
- **Fullscreen Support**: Toggle fullscreen with button or touch
- **RESTful API**: JSON endpoints for data access
- **Graceful Shutdown**: Proper cleanup on termination

## 🖥️ Display

The dashboard is optimized for visibility from 6 feet away with:
- Large, readable Rajdhani font
- High contrast F1-themed color scheme
- Medal-style gradients for podium positions
- Static background (no distracting animations)
- Responsive design for different screen sizes

## ⚡ Quick Start

### Requirements
- Python 3.8+
- Internet connection for F1 data
- ~50MB storage for cache (probably less)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd f1cal
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   python main.py
   ```

4. **Access the dashboard**
   - Open http://localhost:5000 in your browser
   - Or access from another device on your network

### Raspberry Pi Setup

For optimal Raspberry Pi experience:

1. **Auto-start on boot** (add to `/etc/rc.local`):
   ```bash
   cd /path/to/f1cal && python main.py --mode web &
   ```

2. **Configure display** for 3.5" touchscreen:
   ```bash
   # Add to /boot/config.txt
   hdmi_group=2
   hdmi_mode=87
   hdmi_cvt=480 320 60 6 0 0 0
   ```

## 🔧 Configuration

Edit `config/settings.py` to customize:

```python
# Display settings
DISPLAY_MODE = "web"
WEB_PORT = 5000
REFRESH_INTERVAL = 300  # seconds (5 minutes)

# Cache settings
CACHE_ENABLED = True
CACHE_DIRECTORY = "cache"
POLL_INTERVAL_HOURS = 12

# Display preferences
SHOW_STANDINGS = True
SHOW_NEXT_EVENT = True
SHOW_EVENT_AFTER_NEXT = True
```

## 🎯 Command Line Options

```bash
python main.py [options]
```

**Available options:**
- `--mode {web,desktop}`: Display mode (default: web, desktop not implemented)
- `--port PORT`: Web server port (default: 5000)
- `--poll-hours HOURS`: Hours between data updates (default: 12)
- `--cache-file FILE`: Cache file location (default: dashboard_data.json)
- `--force-update`: Force immediate data update on startup

**Examples:**
```bash
# Run on different port
python main.py --port 8080

# Update data every 6 hours
python main.py --poll-hours 6

# Force fresh data on startup
python main.py --force-update
```

## 🌐 API Endpoints

The dashboard provides REST API endpoints:

- `GET /`: Main dashboard HTML
- `GET /api/data`: Current F1 data (JSON)
- `GET /api/status`: Cache status and health
- `POST /api/refresh`: Force data refresh

## 🎨 Spoiler Protection

The dashboard includes intelligent spoiler protection for championship standings:

1. **First Time**: Standings are blurred with "Tap to reveal" message
2. **Reveal**: Tap anywhere on the standings to show current points
3. **Persistence**: Stays revealed until standings actually change
4. **Auto-Blur**: When new race results come in, automatically blurs again

Perfect for fans who watch races delayed but still want to see upcoming event information!

## 🏗️ Project Structure

```
f1cal/
├── config/
│   └── settings.py          # Configuration settings
├── src/
│   ├── data/
│   │   └── __init__.py      # F1 data fetching (FastF1 integration)
│   ├── display/
│   │   └── __init__.py      # Web and desktop display handlers
│   └── cache.py             # Background polling and caching
├── static/
│   └── css/
│       └── style.css        # Dashboard styling
├── templates/
│   └── dashboard.html       # Main dashboard template
├── tests/                   # Test scripts and utilities
├── main.py                  # Application entry point
└── requirements.txt         # Python dependencies
```

## 🔍 Data Sources

- **Race Data**: Official Formula 1 timing data via [FastF1](https://theoehrly.github.io/Fast-F1/)
- **Schedule**: Current and next year race calendars
- **Standings**: Live championship points calculated from race results
- **Sessions**: All session types (Practice, Sprint Qualifying, Sprint, Qualifying, Race)

## 🐛 Troubleshooting

**Dashboard shows no data:**
- Check internet connection
- Run with `--force-update` to refresh data
- Check logs for API errors

**Standings not updating:**
- Data updates every 12 hours by default
- Use `--poll-hours 1` for more frequent updates
- POST to `/api/refresh` to force update

**Display issues on Pi:**
- Ensure display resolution is set correctly
- Try fullscreen mode with the ⛶ button
- Check `static/css/style.css` for responsive breakpoints

## 📱 Touch Screen Usage

Optimized for touch interaction:
- **Tap fullscreen button**: Toggle fullscreen mode
- **Tap standings area**: Reveal/hide spoiler-protected standings
- **Responsive design**: Works on various screen sizes

## 🏆 Perfect For

- **Raspberry Pi projects**: Optimized for 3.5" displays
- **Home dashboards**: Always-on F1 information
- **Race viewing**: Spoiler protection for delayed viewing
- **F1 fans**: Comprehensive race and championship data

## 📜 License

GNU General Public License v3.0
