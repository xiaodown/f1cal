#!/usr/bin/env python3
"""
Simple test to generate a dashboard with mock standings data.
"""

import os
from datetime import datetime

def create_test_dashboard():
    """Create a test dashboard with mock data to show the styling."""
    
    # Mock data for testing
    next_event = {
        'name': 'Saudi Arabian Grand Prix',
        'location': 'Jeddah, Saudi Arabia',
        'date': '2025-04-19',
        'time': '09:00 AM PST',
        'type': 'Qualifying'
    }
    
    standings = {
        'drivers': [
            {'name': 'Lando Norris', 'points': 76},
            {'name': 'Oscar Piastri', 'points': 67},
            {'name': 'Max Verstappen', 'points': 63}
        ],
        'constructors': [
            {'name': 'McLaren', 'points': 143},
            {'name': 'Mercedes', 'points': 86},
            {'name': 'Red Bull Racing', 'points': 65}
        ]
    }
    
    # Mock "event after next" data
    event_after_next = {
        'name': 'Miami Grand Prix',
        'location': 'Miami, USA',
        'date': '2025-05-04'
    }
    
    # Read the CSS file
    css_content = ""
    css_path = '../static/css/style.css'
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    
    # Generate driver standings HTML
    driver_standings_html = """
        <div class="driver-standings">
            <h3>Driver Standings</h3>"""
    for i, driver in enumerate(standings['drivers'], 1):
        driver_standings_html += f"""
            <div class="standing-item">
                <span class="position">{i}</span>
                <span class="name">{driver['name']}</span>
                <span class="points">{driver['points']}</span>
            </div>"""
    driver_standings_html += "\n        </div>"
    
    # Generate constructor standings HTML  
    constructor_standings_html = """
        <div class="constructor-standings">
            <h3>Constructor Standings</h3>"""
    for i, constructor in enumerate(standings['constructors'], 1):
        constructor_standings_html += f"""
            <div class="standing-item">
                <span class="position">{i}</span>
                <span class="name">{constructor['name']}</span>
                <span class="points">{constructor['points']}</span>
            </div>"""
    constructor_standings_html += "\n        </div>"
    
    # Generate the complete HTML
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>F1 Dashboard - Test with Standings</title>
    <style>""" + css_content + """</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Formula 1 Dashboard</h1>
            <div class="last-updated">
                Test with standings data - """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
            </div>
            <button id="fullscreen-btn" class="fullscreen-button" title="Toggle Fullscreen">⛶</button>
        </header>

        <main>
            <!-- Next Event Section -->
            <section class="next-event">
                <h2>Next Event</h2>
                <div class="event-card">
                    <h3>""" + next_event['name'] + """</h3>
                    <div class="event-details">
                        <div class="event-location">""" + next_event['location'] + """</div>
                        <div class="event-date">""" + next_event['date'] + """</div>
                        <div class="event-time">""" + next_event['time'] + """</div>
                        <div class="event-type">""" + next_event['type'] + """</div>
                    </div>
                </div>
            </section>

            <!-- Standings Section -->
            <section class="standings">
                <div class="standings-grid">
                    """ + driver_standings_html + """
                    """ + constructor_standings_html + """
                </div>
            </section>

            <!-- Event After Next -->
            <section class="event-after-next">
                <h2>Upcoming</h2>
                <div class="event-card small">
                    <h4>""" + event_after_next['name'] + """</h4>
                    <div class="event-details">
                        <span>""" + event_after_next['location'] + """</span>
                        <span>""" + event_after_next['date'] + """</span>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <script>
        // Fullscreen functionality
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        
        fullscreenBtn.addEventListener('click', function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log('Error attempting to enable fullscreen:', err);
                });
            } else {
                document.exitFullscreen();
            }
        });
        
        // Update button appearance based on fullscreen state
        document.addEventListener('fullscreenchange', function() {
            const btn = document.getElementById('fullscreen-btn');
            if (document.fullscreenElement) {
                btn.innerHTML = '⛉'; // Exit fullscreen icon
                btn.title = 'Exit Fullscreen';
            } else {
                btn.innerHTML = '⛶'; // Enter fullscreen icon
                btn.title = 'Toggle Fullscreen';
            }
        });
    </script>
</body>
</html>"""
    
    # Save to file
    test_file = '../test_dashboard_with_standings.html'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Test dashboard with standings created: {test_file}")
    print("This shows how the dashboard looks WITH championship standings data.")
    
    return test_file

if __name__ == "__main__":
    print("=== F1 Dashboard UI Test (With Standings) ===\n")
    test_file = create_test_dashboard()
    print(f"\nOpen {test_file} in your browser to see the dashboard with standings!")