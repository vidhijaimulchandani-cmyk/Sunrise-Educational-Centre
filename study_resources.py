"""
Study Resources Management System for Sunrise Education Centre
Handles all study resource operations including upload, download, categorization, and access control
"""

import sqlite3
import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Union
from flask import session
try:
    from werkzeug.utils import secure_filename
    from werkzeug.datastructures import FileStorage
    WERKZEUG_AVAILABLE = True
except ImportError:
    import re
    def secure_filename(filename):
        """Fallback secure filename function"""
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        return filename
    WERKZEUG_AVAILABLE = False

# Database configuration
DATABASE = 'users.db'
UPLOAD_FOLDER = 'uploads'

def get_ist_timestamp():
    """Get current timestamp in IST format"""
    ist_time = datetime.now(timezone.utc).astimezone()
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

def ensure_resource_tables():
    """Ensure all resource-related tables exist with proper structure"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Main resources table
        c.execute('''CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            class_id INTEGER NOT NULL,
            filepath TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            paid_status TEXT DEFAULT 'unpaid',
            schedule_date TEXT,
            uploaded_by INTEGER,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            download_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            file_size INTEGER,
            file_type TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )''')
        
        # Check if columns exist and add them if they don't
        c.execute("PRAGMA table_info(resources)")
        existing_columns = [col[1] for col in c.fetchall()]
        
        columns_to_add = [
            ('paid_status', 'TEXT'),
            ('schedule_date', 'TEXT'),
            ('uploaded_by', 'INTEGER'),
            ('uploaded_at', 'TEXT'),
            ('download_count', 'INTEGER'),
            ('is_active', 'BOOLEAN'),
            ('file_size', 'INTEGER'),
            ('file_type', 'TEXT')
        ]
        
        for col_name, col_def in columns_to_add:
            if col_name not in existing_columns:
                c.execute(f'ALTER TABLE resources ADD COLUMN {col_name} {col_def}')
                print(f"✅ Added column {col_name} to resources table")
        
        # Set default values for existing rows
        c.execute('UPDATE resources SET paid_status = "unpaid" WHERE paid_status IS NULL')
        c.execute('UPDATE resources SET download_count = 0 WHERE download_count IS NULL')
        c.execute('UPDATE resources SET is_active = 1 WHERE is_active IS NULL')
        
        # Categories table
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            category_type TEXT DEFAULT 'general',
            target_class TEXT DEFAULT 'all',
            paid_status TEXT DEFAULT 'unpaid',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )''')
        
        # Resource downloads tracking
        c.execute('''CREATE TABLE IF NOT EXISTS resource_downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (resource_id) REFERENCES resources (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Resource ratings and reviews
        c.execute('''CREATE TABLE IF NOT EXISTS resource_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            review TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resource_id) REFERENCES resources (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(resource_id, user_id)
        )''')
        
        conn.commit()
        print("✅ Study resource tables ensured successfully")
        
    except Exception as e:
        print(f"❌ Error ensuring study resource tables: {e}")
    finally:
        conn.close()

def save_resource(filename: str, class_id: int, filepath: str, title: str, 
                 description: str = None, category: str = None, 
                 paid_status: str = 'unpaid', schedule_date: str = None,
                 uploaded_by: int = None, file_size: int = None, 
                 file_type: str = None) -> int:
    """
    Save a new resource to the database
    
    Args:
        filename: Name of the file
        class_id: ID of the class this resource belongs to
        filepath: Path to the file on disk
        title: Title of the resource
        description: Description of the resource
        category: Category of the resource
        paid_status: Whether this is for paid users only
        schedule_date: Date when resource should be available
        uploaded_by: ID of user who uploaded the resource
        file_size: Size of the file in bytes
        file_type: Type of the file (pdf, doc, etc.)
    
    Returns:
        Resource ID
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO resources 
            (filename, class_id, filepath, title, description, category, 
             paid_status, schedule_date, uploaded_by, file_size, file_type, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (filename, class_id, filepath, title, description, category,
              paid_status, schedule_date, uploaded_by, file_size, file_type, get_ist_timestamp()))
        
        resource_id = c.lastrowid
        conn.commit()
        print(f"✅ Saved resource: {title} (ID: {resource_id})")
        return resource_id
        
    except Exception as e:
        print(f"❌ Error saving resource: {e}")
        return None
    finally:
        conn.close()

def get_all_resources() -> List[Tuple]:
    """
    Get all resources from the database
    
    Returns:
        List of resource tuples
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT r.id, r.filename, r.class_id, r.filepath, r.title, r.description, 
                   r.category, r.paid_status, r.schedule_date, r.uploaded_by, 
                   r.uploaded_at, r.download_count, r.is_active, r.file_size, r.file_type,
                   c.name as class_name, u.username as uploaded_by_name
            FROM resources r
            LEFT JOIN classes c ON r.class_id = c.id
            LEFT JOIN users u ON r.uploaded_by = u.id
            WHERE r.is_active = 1
            ORDER BY r.uploaded_at DESC
        ''')
        resources = c.fetchall()
        return resources
        
    except Exception as e:
        print(f"❌ Error getting all resources: {e}")
        return []
    finally:
        conn.close()

def get_resources_for_class_id(class_id: int, paid_status: str = None) -> List[Tuple]:
    """
    Get resources for a specific class
    
    Args:
        class_id: ID of the class
        paid_status: Filter by paid status ('paid', 'unpaid', None for all)
    
    Returns:
        List of resource tuples
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        if paid_status:
            c.execute('''
                SELECT r.id, r.filename, r.class_id, r.filepath, r.title, r.description, 
                       r.category, r.paid_status, r.schedule_date, r.uploaded_by, 
                       r.uploaded_at, r.download_count, r.is_active, r.file_size, r.file_type,
                       c.name as class_name, u.username as uploaded_by_name
                FROM resources r
                LEFT JOIN classes c ON r.class_id = c.id
                LEFT JOIN users u ON r.uploaded_by = u.id
                WHERE r.class_id = ? AND r.paid_status = ? AND r.is_active = 1
                ORDER BY r.uploaded_at DESC
            ''', (class_id, paid_status))
        else:
            c.execute('''
                SELECT r.id, r.filename, r.class_id, r.filepath, r.title, r.description, 
                       r.category, r.paid_status, r.schedule_date, r.uploaded_by, 
                       r.uploaded_at, r.download_count, r.is_active, r.file_size, r.file_type,
                       c.name as class_name, u.username as uploaded_by_name
                FROM resources r
                LEFT JOIN classes c ON r.class_id = c.id
                LEFT JOIN users u ON r.uploaded_by = u.id
                WHERE r.class_id = ? AND r.is_active = 1
                ORDER BY r.uploaded_at DESC
            ''', (class_id,))
        
        resources = c.fetchall()
        return resources
        
    except Exception as e:
        print(f"❌ Error getting resources for class {class_id}: {e}")
        return []
    finally:
        conn.close()

def get_resource_by_id(resource_id: int) -> Optional[Tuple]:
    """
    Get a specific resource by ID
    
    Args:
        resource_id: ID of the resource
    
    Returns:
        Resource tuple or None
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT r.id, r.filename, r.class_id, r.filepath, r.title, r.description, 
                   r.category, r.paid_status, r.schedule_date, r.uploaded_by, 
                   r.uploaded_at, r.download_count, r.is_active, r.file_size, r.file_type,
                   c.name as class_name, u.username as uploaded_by_name
            FROM resources r
            LEFT JOIN classes c ON r.class_id = c.id
            LEFT JOIN users u ON r.uploaded_by = u.id
            WHERE r.id = ? AND r.is_active = 1
        ''', (resource_id,))
        
        resource = c.fetchone()
        return resource
        
    except Exception as e:
        print(f"❌ Error getting resource {resource_id}: {e}")
        return None
    finally:
        conn.close()

def get_resource_by_filename(filename: str) -> Optional[Tuple]:
    """
    Get a specific resource by filename
    
    Args:
        filename: Name of the file
    
    Returns:
        Resource tuple or None
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT r.id, r.filename, r.class_id, r.filepath, r.title, r.description, 
                   r.category, r.paid_status, r.schedule_date, r.uploaded_by, 
                   r.uploaded_at, r.download_count, r.is_active, r.file_size, r.file_type,
                   c.name as class_name, u.username as uploaded_by_name
            FROM resources r
            LEFT JOIN classes c ON r.class_id = c.id
            LEFT JOIN users u ON r.uploaded_by = u.id
            WHERE r.filename = ? AND r.is_active = 1
        ''', (filename,))
        
        resource = c.fetchone()
        return resource
        
    except Exception as e:
        print(f"❌ Error getting resource by filename {filename}: {e}")
        return None
    finally:
        conn.close()

def update_resource(resource_id: int, title: str = None, description: str = None, 
                   category: str = None, paid_status: str = None, 
                   schedule_date: str = None) -> bool:
    """
    Update a resource's information
    
    Args:
        resource_id: ID of the resource to update
        title: New title
        description: New description
        category: New category
        paid_status: New paid status
        schedule_date: New schedule date
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Build dynamic update query
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if paid_status is not None:
            updates.append("paid_status = ?")
            params.append(paid_status)
        if schedule_date is not None:
            updates.append("schedule_date = ?")
            params.append(schedule_date)
        
        if not updates:
            return False
        
        params.append(resource_id)
        query = f"UPDATE resources SET {', '.join(updates)} WHERE id = ?"
        
        c.execute(query, params)
        conn.commit()
        
        print(f"✅ Updated resource {resource_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating resource {resource_id}: {e}")
        return False
    finally:
        conn.close()

def delete_resource(filename: str) -> bool:
    """
    Delete a resource from the database
    
    Args:
        filename: Name of the file to delete
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Get filepath before deleting
        c.execute('SELECT filepath FROM resources WHERE filename = ?', (filename,))
        result = c.fetchone()
        
        if result:
            filepath = result[0]
            
            # Delete from database
            c.execute('DELETE FROM resources WHERE filename = ?', (filename,))
            conn.commit()
            
            # Delete physical file
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✅ Deleted file: {filepath}")
            
            print(f"✅ Deleted resource: {filename}")
            return True
        else:
            print(f"❌ Resource not found: {filename}")
            return False
        
    except Exception as e:
        print(f"❌ Error deleting resource {filename}: {e}")
        return False
    finally:
        conn.close()

def get_categories_for_class(class_id: int) -> List[Tuple]:
    """
    Get all categories that are available for a specific class
    
    Args:
        class_id: ID of the class
    
    Returns:
        List of category tuples
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Get categories that are either for all classes or specifically for this class
        c.execute('''
            SELECT id, name, description, category_type, target_class, paid_status 
            FROM categories 
            WHERE is_active = 1 
            AND (target_class = 'all' OR target_class = ?)
            ORDER BY name
        ''', (str(class_id),))
        
        categories = c.fetchall()
        return categories
        
    except Exception as e:
        print(f"❌ Error getting categories for class {class_id}: {e}")
        return []
    finally:
        conn.close()

def get_all_categories() -> List[Tuple]:
    """
    Get all categories
    
    Returns:
        List of all category tuples
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT id, name, description, category_type, target_class, paid_status, created_at
            FROM categories 
            WHERE is_active = 1
            ORDER BY name
        ''')
        
        categories = c.fetchall()
        return categories
        
    except Exception as e:
        print(f"❌ Error getting all categories: {e}")
        return []
    finally:
        conn.close()

def add_category(name: str, description: str = None, category_type: str = 'general',
                target_class: str = 'all', paid_status: str = 'unpaid', 
                created_by: int = None) -> int:
    """
    Add a new category
    
    Args:
        name: Name of the category
        description: Description of the category
        category_type: Type of category
        target_class: Target class for this category
        paid_status: Paid status for this category
        created_by: ID of user who created the category
    
    Returns:
        Category ID
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO categories 
            (name, description, category_type, target_class, paid_status, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, category_type, target_class, paid_status, created_by, get_ist_timestamp()))
        
        category_id = c.lastrowid
        conn.commit()
        print(f"✅ Added category: {name} (ID: {category_id})")
        return category_id
        
    except Exception as e:
        print(f"❌ Error adding category: {e}")
        return None
    finally:
        conn.close()

def update_category(category_id: int, name: str = None, description: str = None,
                   category_type: str = None, target_class: str = None,
                   paid_status: str = None) -> bool:
    """
    Update a category
    
    Args:
        category_id: ID of the category to update
        name: New name
        description: New description
        category_type: New category type
        target_class: New target class
        paid_status: New paid status
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Build dynamic update query
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if category_type is not None:
            updates.append("category_type = ?")
            params.append(category_type)
        if target_class is not None:
            updates.append("target_class = ?")
            params.append(target_class)
        if paid_status is not None:
            updates.append("paid_status = ?")
            params.append(paid_status)
        
        if not updates:
            return False
        
        params.append(category_id)
        query = f"UPDATE categories SET {', '.join(updates)} WHERE id = ?"
        
        c.execute(query, params)
        conn.commit()
        
        print(f"✅ Updated category {category_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating category {category_id}: {e}")
        return False
    finally:
        conn.close()

def delete_category(category_id: int) -> bool:
    """
    Delete a category (soft delete by setting is_active = 0)
    
    Args:
        category_id: ID of the category to delete
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('UPDATE categories SET is_active = 0 WHERE id = ?', (category_id,))
        conn.commit()
        
        print(f"✅ Deleted category {category_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting category {category_id}: {e}")
        return False
    finally:
        conn.close()

def track_resource_download(resource_id: int, user_id: int, ip_address: str = None,
                           user_agent: str = None) -> bool:
    """
    Track a resource download
    
    Args:
        resource_id: ID of the resource
        user_id: ID of the user downloading
        ip_address: IP address of the user
        user_agent: User agent string
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Add download record
        c.execute('''
            INSERT INTO resource_downloads 
            (resource_id, user_id, ip_address, user_agent, downloaded_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (resource_id, user_id, ip_address, user_agent, get_ist_timestamp()))
        
        # Update download count
        c.execute('''
            UPDATE resources 
            SET download_count = download_count + 1 
            WHERE id = ?
        ''', (resource_id,))
        
        conn.commit()
        print(f"✅ Tracked download for resource {resource_id} by user {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error tracking download: {e}")
        return False
    finally:
        conn.close()

def get_resource_downloads(resource_id: int) -> List[Tuple]:
    """
    Get download history for a resource
    
    Args:
        resource_id: ID of the resource
    
    Returns:
        List of download records
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT rd.id, rd.user_id, rd.downloaded_at, rd.ip_address, rd.user_agent,
                   u.username, u.email_address
            FROM resource_downloads rd
            LEFT JOIN users u ON rd.user_id = u.id
            WHERE rd.resource_id = ?
            ORDER BY rd.downloaded_at DESC
        ''', (resource_id,))
        
        downloads = c.fetchall()
        return downloads
        
    except Exception as e:
        print(f"❌ Error getting downloads for resource {resource_id}: {e}")
        return []
    finally:
        conn.close()

def add_resource_rating(resource_id: int, user_id: int, rating: int, 
                       review: str = None) -> bool:
    """
    Add or update a rating for a resource
    
    Args:
        resource_id: ID of the resource
        user_id: ID of the user rating
        rating: Rating (1-5)
        review: Optional review text
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT OR REPLACE INTO resource_ratings 
            (resource_id, user_id, rating, review, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (resource_id, user_id, rating, review, get_ist_timestamp()))
        
        conn.commit()
        print(f"✅ Added rating for resource {resource_id} by user {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding rating: {e}")
        return False
    finally:
        conn.close()

def get_resource_ratings(resource_id: int) -> List[Tuple]:
    """
    Get all ratings for a resource
    
    Args:
        resource_id: ID of the resource
    
    Returns:
        List of rating tuples
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT rr.id, rr.user_id, rr.rating, rr.review, rr.created_at,
                   u.username, u.email_address
            FROM resource_ratings rr
            LEFT JOIN users u ON rr.user_id = u.id
            WHERE rr.resource_id = ?
            ORDER BY rr.created_at DESC
        ''', (resource_id,))
        
        ratings = c.fetchall()
        return ratings
        
    except Exception as e:
        print(f"❌ Error getting ratings for resource {resource_id}: {e}")
        return []
    finally:
        conn.close()

def get_average_rating(resource_id: int) -> float:
    """
    Get average rating for a resource
    
    Args:
        resource_id: ID of the resource
    
    Returns:
        Average rating (0.0 if no ratings)
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
            FROM resource_ratings 
            WHERE resource_id = ?
        ''', (resource_id,))
        
        result = c.fetchone()
        avg_rating = result[0] if result and result[0] else 0.0
        return round(avg_rating, 1)
        
    except Exception as e:
        print(f"❌ Error getting average rating for resource {resource_id}: {e}")
        return 0.0
    finally:
        conn.close()

def search_resources(query: str, class_id: int = None, category: str = None,
                    paid_status: str = None) -> List[Tuple]:
    """
    Search resources by query
    
    Args:
        query: Search query
        class_id: Filter by class ID
        category: Filter by category
        paid_status: Filter by paid status
    
    Returns:
        List of matching resources
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Build search query
        search_conditions = ["r.is_active = 1"]
        params = []
        
        if query:
            search_conditions.append("(r.title LIKE ? OR r.description LIKE ? OR r.category LIKE ?)")
            search_param = f"%{query}%"
            params.extend([search_param, search_param, search_param])
        
        if class_id:
            search_conditions.append("r.class_id = ?")
            params.append(class_id)
        
        if category:
            search_conditions.append("r.category = ?")
            params.append(category)
        
        if paid_status:
            search_conditions.append("r.paid_status = ?")
            params.append(paid_status)
        
        where_clause = " AND ".join(search_conditions)
        
        c.execute(f'''
            SELECT r.id, r.filename, r.class_id, r.filepath, r.title, r.description, 
                   r.category, r.paid_status, r.schedule_date, r.uploaded_by, 
                   r.uploaded_at, r.download_count, r.is_active, r.file_size, r.file_type,
                   c.name as class_name, u.username as uploaded_by_name
            FROM resources r
            LEFT JOIN classes c ON r.class_id = c.id
            LEFT JOIN users u ON r.uploaded_by = u.id
            WHERE {where_clause}
            ORDER BY r.uploaded_at DESC
        ''', params)
        
        resources = c.fetchall()
        return resources
        
    except Exception as e:
        print(f"❌ Error searching resources: {e}")
        return []
    finally:
        conn.close()

def get_resource_statistics() -> Dict:
    """
    Get resource statistics
    
    Returns:
        Dictionary with resource statistics
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Total resources
        c.execute('SELECT COUNT(*) FROM resources WHERE is_active = 1')
        total_resources = c.fetchone()[0]
        
        # Resources by class
        c.execute('''
            SELECT c.name, COUNT(r.id) as count
            FROM resources r
            LEFT JOIN classes c ON r.class_id = c.id
            WHERE r.is_active = 1
            GROUP BY r.class_id, c.name
            ORDER BY count DESC
        ''')
        resources_by_class = c.fetchall()
        
        # Resources by category
        c.execute('''
            SELECT category, COUNT(*) as count
            FROM resources
            WHERE is_active = 1
            GROUP BY category
            ORDER BY count DESC
        ''')
        resources_by_category = c.fetchall()
        
        # Total downloads
        c.execute('SELECT SUM(download_count) FROM resources WHERE is_active = 1')
        total_downloads = c.fetchone()[0] or 0
        
        # Recent uploads (last 30 days)
        c.execute('''
            SELECT COUNT(*) FROM resources 
            WHERE is_active = 1 
            AND uploaded_at >= datetime('now', '-30 days')
        ''')
        recent_uploads = c.fetchone()[0]
        
        return {
            'total_resources': total_resources,
            'resources_by_class': resources_by_class,
            'resources_by_category': resources_by_category,
            'total_downloads': total_downloads,
            'recent_uploads': recent_uploads
        }
        
    except Exception as e:
        print(f"❌ Error getting resource statistics: {e}")
        return {}
    finally:
        conn.close()

def allowed_file(filename: str) -> bool:
    """
    Check if file type is allowed
    
    Args:
        filename: Name of the file
    
    Returns:
        True if allowed, False otherwise
    """
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes
    
    Args:
        filepath: Path to the file
    
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

def get_file_type(filename: str) -> str:
    """
    Get file type from filename
    
    Args:
        filename: Name of the file
    
    Returns:
        File type (extension)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return 'unknown'

def user_has_access_to_resource(filename: str, user_role: str, user_paid_status: str = None) -> bool:
    """
    Check if user has access to a resource
    
    Args:
        filename: Name of the resource file
        user_role: Role of the user
        user_paid_status: Paid status of the user
    
    Returns:
        True if user has access, False otherwise
    """
    # Admin and teachers have access to all resources
    if user_role in ['admin', 'teacher']:
        return True
    
    # Get resource details
    resource = get_resource_by_filename(filename)
    if not resource:
        return False
    
    # Check if resource is active
    if not resource[12]:  # is_active field
        return False
    
    # Check paid status
    resource_paid_status = resource[7]  # paid_status field
    if resource_paid_status == 'paid' and user_paid_status != 'paid':
        return False
    
    return True

def resolve_uploaded_file_path(filename: str) -> Optional[str]:
    """Resolve an uploaded file path by searching common folders"""
    # Direct path in uploads
    direct_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(direct_path):
        return direct_path
    # Search in nested subfolders under uploads
    for root, _dirs, files in os.walk(UPLOAD_FOLDER):
        if filename in files:
            return os.path.join(root, filename)
    return None

def can_preview_pdf(filename: str) -> Tuple[bool, str]:
    """Lightweight guard to check preview preconditions; returns (ok, message)."""
    if not session.get('role'):
        return False, 'You must be logged in to view resources.'
    if not filename.lower().endswith('.pdf'):
        return False, 'Invalid file type. Only PDF files can be previewed.'
    if not resolve_uploaded_file_path(filename):
        return False, 'File not found.'
    # Access check uses current session info
    role = session.get('role')
    paid = session.get('paid_status')
    if not user_has_access_to_resource(filename, role, paid):
        return False, 'You do not have access to this resource.'
    return True, ''

# Initialize tables when module is imported
ensure_resource_tables()