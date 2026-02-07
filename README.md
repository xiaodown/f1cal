# F1 Dashboard

A Formula 1 information dashboard optimized for Raspberry Pi displays, built with Python and FastF1. Perfect for showing next race information and championship standings on the official 5" Raspberry Pi Touch Display 2.

This is still a work-in-progress.  A significant portion of it is vibe-coded, and I'm still working on testing it on the actual raspberry pi.o

I used [this 3d printed case](https://www.printables.com/model/1532368-raspberry-pi-5-touch-display-2-case-with-stand) to hold everything, and it worked perfectly and looks great.  

Built for the official [Raspberry Pi Touch Display 2](https://www.raspberrypi.com/products/touch-display-2/) which provides a crisp 5" touchscreen experience.

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
- **Raspberry Pi Optimized**: Designed for the 5" Raspberry Pi Touch Display 2 (800x480)
- **Fullscreen Support**: Toggle fullscreen with button or touch
- **RESTful API**: JSON endpoints for data access
- **Graceful Shutdown**: Proper cleanup on termination

## 🖥️ Display

The dashboard is optimized for the 5" Touch Display 2 with visibility from 6 feet away:
- Large, readable Rajdhani font
- High contrast F1-themed color scheme
- Medal-style gradients for podium positions
- Static background (no distracting animations)
- Responsive design (800x480 optimized, works on other sizes)

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

For optimal Raspberry Pi experience with the 5" Touch Display 2:

#### Auto-start System Setup

The repository includes files for complete auto-start functionality:

1. **Install the systemd service** for the Flask server:
   ```bash
   # Copy and customize the service file
   sudo cp f1-dashboard.service /etc/systemd/system/
   
   # Edit paths and username to match your setup
   sudo nano /etc/systemd/system/f1-dashboard.service
   
   # Enable and start the service
   sudo systemctl enable f1-dashboard.service
   sudo systemctl start f1-dashboard.service
   ```

2. **Setup auto-login** (optional but recommended):
   ```bash
   # Copy and customize the autologin configuration
   sudo cp 50-autologin.conf /etc/lightdm/conf.d/
   
   # Edit username to match your system
   sudo nano /etc/lightdm/conf.d/50-autologin.conf
   ```

3. **Configure browser auto-start**:
   ```bash
   # Copy desktop file to autostart directory
   mkdir -p ~/.config/autostart
   cp autostart/f1-dashboard.desktop ~/.config/autostart/
   # OR for Firefox:
   cp autostart/f1-dashboard-firefox.desktop ~/.config/autostart/
   ```

**Important**: Update hardcoded paths in these files:
- `f1-dashboard.service`: Update `/home/xiaodown/code/f1cal` paths
- `50-autologin.conf`: Change `xiaodown` to your username
- Desktop files work as-is (they use localhost)

#### Display Configuration

The 5" Touch Display 2 works out-of-the-box with modern Raspberry Pi OS. No additional configuration needed!

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
- The 5" Touch Display 2 should work out-of-the-box
- Try fullscreen mode with the ⛶ button
- Check `static/css/style.css` for responsive breakpoints

## 📱 Touch Screen Usage

Optimized for the 5" Touch Display 2:
- **Tap fullscreen button**: Toggle fullscreen mode
- **Tap standings area**: Reveal/hide spoiler-protected standings
- **Responsive design**: 800x480 optimized, works on various screen sizes

## 🏆 Perfect For

- **Raspberry Pi projects**: Optimized for the 5" Touch Display 2
- **Home dashboards**: Always-on F1 information
- **Race viewing**: Spoiler protection for delayed viewing
- **F1 fans**: Comprehensive race and championship data

## 📜 License

GNU General Public License v3.0
