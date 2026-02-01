"""Data fetching and processing module for F1 information."""

import fastf1
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import pandas as pd
from config.settings import CACHE_DIRECTORY


class F1DataFetcher:
    """Handles fetching and processing F1 data using fastf1."""
    
    def __init__(self):
        """Initialize the F1 data fetcher."""
        # Enable FastF1 cache for better performance
        fastf1.Cache.enable_cache(CACHE_DIRECTORY)
        
        self.current_year = datetime.now().year
        # Get system timezone
        self.local_tz = datetime.now().astimezone().tzinfo
    
    def get_next_event(self) -> Optional[Dict[str, Any]]:
        """Get information about the next F1 event."""
        try:
            # Get the schedule for current year
            schedule = fastf1.get_event_schedule(self.current_year)
            
            # Filter out testing events and keep only race events
            race_events = schedule[schedule['EventFormat'] != 'testing'].copy()
            
            if race_events.empty:
                return None
            
            # Convert all session datetime columns to timezone-aware timestamps
            session_cols = ['Session1DateUtc', 'Session2DateUtc', 'Session3DateUtc', 'Session4DateUtc', 'Session5DateUtc']
            for col in session_cols:
                race_events[col] = pd.to_datetime(race_events[col], utc=True)
            
            # Filter for events that have any upcoming sessions
            now = pd.Timestamp.now(tz='UTC')
            upcoming_events = race_events[
                (race_events['Session1DateUtc'] > now) | 
                (race_events['Session2DateUtc'] > now) | 
                (race_events['Session3DateUtc'] > now) | 
                (race_events['Session4DateUtc'] > now) | 
                (race_events['Session5DateUtc'] > now)
            ]
            
            if upcoming_events.empty:
                # Try next year if no events left this year
                try:
                    schedule = fastf1.get_event_schedule(self.current_year + 1)
                    race_events = schedule[schedule['EventFormat'] != 'testing'].copy()
                    
                    if not race_events.empty:
                        # Convert all session datetime columns
                        for col in session_cols:
                            race_events[col] = pd.to_datetime(race_events[col], utc=True)
                        
                        upcoming_events = race_events[
                            (race_events['Session1DateUtc'] > now) | 
                            (race_events['Session2DateUtc'] > now) | 
                            (race_events['Session3DateUtc'] > now) | 
                            (race_events['Session4DateUtc'] > now) | 
                            (race_events['Session5DateUtc'] > now)
                        ]
                except:
                    return None
            
            if upcoming_events.empty:
                return None
            
            # Find the event with the next meaningful session
            next_event_info = None
            earliest_session_time = None
            
            for _, event in upcoming_events.iterrows():
                session_info = self._get_next_session_info(event, now)
                if session_info and session_info['session_time_utc']:
                    if earliest_session_time is None or session_info['session_time_utc'] < earliest_session_time:
                        earliest_session_time = session_info['session_time_utc']
                        next_event_info = {
                            'name': event['EventName'],
                            'location': f"{event['Location']}, {event['Country']}",
                            'date': session_info['date'],
                            'time': session_info['time'],
                            'type': session_info['type'],
                            'round': event['RoundNumber']
                        }
            
            return next_event_info
            
        except Exception as e:
            print(f"Error fetching next event: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_next_session_info(self, event: pd.Series, now: pd.Timestamp) -> Optional[Dict[str, Any]]:
        """Determine the next meaningful session for an event (Sprint Qualifying, Sprint, Qualifying, or Race)."""
        
        # Define sessions we care about - check each session number and its corresponding date column
        sessions_to_check = [
            ('Session2', 'Session2DateUtc'),
            ('Session3', 'Session3DateUtc'), 
            ('Session4', 'Session4DateUtc'),
            ('Session5', 'Session5DateUtc')
        ]
        
        # Find all upcoming meaningful sessions for this event
        upcoming_sessions = []
        
        for session_name_col, session_date_col in sessions_to_check:
            session_name = event.get(session_name_col, '')
            
            # Check if this session is one we care about and hasn't happened yet
            if (session_name in ['Sprint Qualifying', 'Sprint', 'Qualifying', 'Race'] and 
                pd.notna(event[session_date_col]) and 
                event[session_date_col] > now):
                
                upcoming_sessions.append({
                    'name': session_name,
                    'time_utc': event[session_date_col]
                })
        
        # If no upcoming meaningful sessions, return None
        if not upcoming_sessions:
            return None
            
        # Sort by time and get the earliest one
        upcoming_sessions.sort(key=lambda x: x['time_utc'])
        next_session = upcoming_sessions[0]
        
        # Convert from UTC to local timezone
        session_time_local = next_session['time_utc'].tz_convert(self.local_tz)
        
        return {
            'date': session_time_local.strftime('%Y-%m-%d'),
            'time': session_time_local.strftime('%I:%M %p %Z'),
            'type': next_session['name'],
            'session_time_utc': next_session['time_utc']  # Include for sorting in parent method
        }
    
    def get_current_standings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get current driver and constructor standings."""
        try:
            # Only look at current year for standings
            schedule = fastf1.get_event_schedule(self.current_year)
            
            # Filter out testing events
            race_events = schedule[schedule['EventFormat'] != 'testing'].copy()
            
            if race_events.empty:
                return {'drivers': [], 'constructors': []}
            
            # Convert datetime columns (only qualifying and race)
            for col in ['Session4DateUtc', 'Session5DateUtc']:
                race_events[col] = pd.to_datetime(race_events[col], utc=True)
            
            now = pd.Timestamp.now(tz='UTC')
            
            # Get completed races (where race has finished)
            completed_races = race_events[race_events['Session5DateUtc'] < now]
            
            # If no completed races this year, everyone has zero points
            if completed_races.empty:
                print("  No completed races in current season yet")
                return {'drivers': [], 'constructors': []}
            
            print(f"  Found {len(completed_races)} completed races this season")
            
            # Initialize points dictionaries
            driver_points = {}
            constructor_points = {}
            
            # Load results from ALL completed races and sum points
            for _, race in completed_races.iterrows():
                try:
                    print(f"  Loading results from {race['EventName']}...")
                    session = fastf1.get_session(self.current_year, race['RoundNumber'], 'R')
                    
                    # Only load results data - NOT full telemetry (this saves hundreds of MB per race)
                    session.load(laps=False, telemetry=False, weather=False, messages=False)
                    
                    results = session.results
                    
                    if not results.empty:
                        # Add points for each driver
                        for _, result in results.iterrows():
                            driver_name = result['FullName']
                            team_name = result['TeamName']
                            race_points = result['Points'] if pd.notna(result['Points']) else 0
                            
                            # Sum driver points
                            if driver_name in driver_points:
                                driver_points[driver_name] += race_points
                            else:
                                driver_points[driver_name] = race_points
                            
                            # Sum constructor points
                            if team_name in constructor_points:
                                constructor_points[team_name] += race_points
                            else:
                                constructor_points[team_name] = race_points
                                
                except Exception as e:
                    print(f"    Error loading {race['EventName']}: {e}")
                    continue
            
            # Sort and create standings lists
            driver_standings = []
            constructor_standings = []
            
            # Sort drivers by points (descending)
            sorted_drivers = sorted(driver_points.items(), key=lambda x: x[1], reverse=True)
            for driver, points in sorted_drivers[:3]:
                driver_standings.append({
                    'name': driver,
                    'points': int(points)
                })
            
            # Sort constructors by points (descending)
            sorted_constructors = sorted(constructor_points.items(), key=lambda x: x[1], reverse=True)
            for constructor, points in sorted_constructors[:3]:
                constructor_standings.append({
                    'name': constructor,
                    'points': int(points)
                })
            
            return {
                'drivers': driver_standings,
                'constructors': constructor_standings
            }
            
        except Exception as e:
            print(f"Error fetching standings: {e}")
            import traceback
            traceback.print_exc()
            return {'drivers': [], 'constructors': []}
    
    def get_event_after_next(self) -> Optional[Dict[str, Any]]:
        """Get information about the event after next."""
        try:
            # Get the schedule for current year
            schedule = fastf1.get_event_schedule(self.current_year)
            
            # Filter out testing events
            race_events = schedule[schedule['EventFormat'] != 'testing'].copy()
            
            if not race_events.empty:
                # Convert all session datetime columns
                session_cols = ['Session1DateUtc', 'Session2DateUtc', 'Session3DateUtc', 'Session4DateUtc', 'Session5DateUtc']
                for col in session_cols:
                    race_events[col] = pd.to_datetime(race_events[col], utc=True)
            
            # Filter for events that have any upcoming sessions
            now = pd.Timestamp.now(tz='UTC')
            upcoming_events = race_events[
                (race_events['Session1DateUtc'] > now) | 
                (race_events['Session2DateUtc'] > now) | 
                (race_events['Session3DateUtc'] > now) | 
                (race_events['Session4DateUtc'] > now) | 
                (race_events['Session5DateUtc'] > now)
            ] if not race_events.empty else pd.DataFrame()
            
            if len(upcoming_events) < 2:
                # Try next year if not enough events left
                try:
                    next_year_schedule = fastf1.get_event_schedule(self.current_year + 1)
                    next_year_races = next_year_schedule[next_year_schedule['EventFormat'] != 'testing'].copy()
                    
                    if not next_year_races.empty:
                        # Convert all session datetime columns
                        for col in session_cols:
                            next_year_races[col] = pd.to_datetime(next_year_races[col], utc=True)
                        
                        next_year_upcoming = next_year_races[
                            (next_year_races['Session1DateUtc'] > now) | 
                            (next_year_races['Session2DateUtc'] > now) | 
                            (next_year_races['Session3DateUtc'] > now) | 
                            (next_year_races['Session4DateUtc'] > now) | 
                            (next_year_races['Session5DateUtc'] > now)
                        ]
                        upcoming_events = pd.concat([upcoming_events, next_year_upcoming])
                except:
                    pass
            
            if len(upcoming_events) < 2:
                return None
            
            # Get the second upcoming event
            event_after_next = upcoming_events.iloc[1]
            
            # Convert race date to local timezone for display
            race_time_local = event_after_next['Session5DateUtc'].tz_convert(self.local_tz)
            
            return {
                'name': event_after_next['EventName'],
                'location': f"{event_after_next['Location']}, {event_after_next['Country']}",
                'date': race_time_local.strftime('%Y-%m-%d'),
                'round': event_after_next['RoundNumber']
            }
            
        except Exception as e:
            print(f"Error fetching event after next: {e}")
            return None