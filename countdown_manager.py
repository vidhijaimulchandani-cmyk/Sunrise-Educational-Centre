import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

DATABASE = 'users.db'

def init_countdown_table():
    """Initialize the countdown settings table"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS countdown_settings (
                id INTEGER PRIMARY KEY,
                launch_date TEXT NOT NULL,
                launch_message TEXT NOT NULL,
                background_type TEXT DEFAULT 'gradient',
                background_color TEXT DEFAULT '#667eea',
                background_gradient TEXT DEFAULT 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                logo_text TEXT DEFAULT 'S',
                logo_color TEXT DEFAULT '#ff6b6b',
                gate_animation_enabled BOOLEAN DEFAULT 1,
                gate_message TEXT DEFAULT '🚀 Welcome to Sunrise Educational Centre! 🚀',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default settings if table is empty
        c.execute('SELECT COUNT(*) FROM countdown_settings')
        if c.fetchone()[0] == 0:
            c.execute('''
                INSERT INTO countdown_settings (
                    launch_date, launch_message, background_type, background_color, 
                    background_gradient, logo_text, logo_color, gate_animation_enabled, 
                    gate_message, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                '2024-02-01T00:00:00',
                '🚀 Our website will be live soon! Get ready for an amazing learning experience.',
                'gradient',
                '#667eea',
                'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'S',
                '#ff6b6b',
                1,
                '🚀 Welcome to Sunrise Educational Centre! 🚀',
                1
            ))
        
        conn.commit()
    except Exception as e:
        print(f"Error initializing countdown table: {e}")
    finally:
        conn.close()

def get_countdown_settings() -> Optional[Dict[str, Any]]:
    """Get current countdown settings"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM countdown_settings WHERE is_active = 1 ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        if row:
            return {
                'id': row[0],
                'launch_date': row[1],
                'launch_message': row[2],
                'background_type': row[3],
                'background_color': row[4],
                'background_gradient': row[5],
                'logo_text': row[6],
                'logo_color': row[7],
                'gate_animation_enabled': bool(row[8]),
                'gate_message': row[9],
                'is_active': bool(row[10]),
                'created_at': row[11],
                'updated_at': row[12]
            }
        return None
    except Exception as e:
        print(f"Error getting countdown settings: {e}")
        return None
    finally:
        conn.close()

def update_countdown_settings(settings: Dict[str, Any]) -> bool:
    """Update countdown settings"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        # Deactivate current active settings
        c.execute('UPDATE countdown_settings SET is_active = 0')
        
        # Insert new settings
        c.execute('''
            INSERT INTO countdown_settings (
                launch_date, launch_message, background_type, background_color,
                background_gradient, logo_text, logo_color, gate_animation_enabled,
                gate_message, is_active, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            settings.get('launch_date'),
            settings.get('launch_message'),
            settings.get('background_type'),
            settings.get('background_color'),
            settings.get('background_gradient'),
            settings.get('logo_text'),
            settings.get('logo_color'),
            settings.get('gate_animation_enabled', True),
            settings.get('gate_message'),
            True,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating countdown settings: {e}")
        return False
    finally:
        conn.close()

def toggle_countdown_status() -> bool:
    """Toggle countdown page on/off"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        current_settings = get_countdown_settings()
        if current_settings:
            new_status = not current_settings['is_active']
            c.execute('UPDATE countdown_settings SET is_active = ? WHERE id = ?', (new_status, current_settings['id']))
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Error toggling countdown status: {e}")
        return False
    finally:
        conn.close()

def is_countdown_active() -> bool:
    """Check if countdown page is active"""
    settings = get_countdown_settings()
    if not settings:
        return False
    # Temporarily disable countdown to show home page
    return False  # settings['is_active']

def get_launch_date() -> Optional[str]:
    """Get the launch date"""
    settings = get_countdown_settings()
    return settings['launch_date'] if settings else None

def is_website_live() -> bool:
    """Check if website launch date has passed"""
    settings = get_countdown_settings()
    if not settings or not settings['is_active']:
        return True  # If no countdown, website is live
    
    try:
        launch_date = datetime.fromisoformat(settings['launch_date'].replace('Z', '+00:00'))
        return datetime.now() > launch_date
    except:
        return True  # If date parsing fails, assume live

# Initialize table when module is imported
init_countdown_table()