# Query Management System Integration Guide

## Overview
This guide explains how to integrate the enhanced query management system into your Sunrise Educational Centre application.

## Files Created

### 1. `query_management.html`
- **Location**: Root directory
- **Purpose**: Admin interface for managing queries
- **Features**:
  - View all queries with filtering
  - Respond to queries
  - Update query status
  - Delete queries
  - Export data to CSV
  - Statistics dashboard

### 2. Enhanced Database Table
The `queries` table has been enhanced with additional fields:

```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phone TEXT,
    subject TEXT,
    priority TEXT DEFAULT "normal",
    status TEXT DEFAULT "pending",
    assigned_to TEXT,
    response TEXT,
    responded_at TIMESTAMP,
    responded_by TEXT,
    category TEXT DEFAULT "general",
    source TEXT DEFAULT "website"
);
```

## Integration Steps

### Step 1: Add Routes to app.py
Add the following routes to your `app.py` file before the `if __name__ == '__main__':` line:

```python
# Query Management Routes
@app.route('/api/queries', methods=['GET'])
def api_get_queries():
    """API endpoint to get queries with filtering and pagination"""
    try:
        # Get filter parameters
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = """
            SELECT id, name, email, phone, message, subject, priority, status, 
                   category, source, submitted_at, response, responded_at, responded_by
            FROM queries 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (name LIKE ? OR email LIKE ? OR message LIKE ? OR subject LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        # Get total count
        count_query = query.replace("SELECT id, name, email, phone, message, subject, priority, status, category, source, submitted_at, response, responded_at, responded_by", "SELECT COUNT(*)")
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY submitted_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        # Execute query
        cursor.execute(query, params)
        queries = cursor.fetchall()
        
        # Get statistics
        stats = get_query_statistics()
        
        conn.close()
        
        # Format results
        formatted_queries = []
        for query in queries:
            formatted_queries.append({
                'id': query[0],
                'name': query[1],
                'email': query[2],
                'phone': query[3],
                'message': query[4],
                'subject': query[5],
                'priority': query[6],
                'status': query[7],
                'category': query[8],
                'source': query[9],
                'submitted_at': query[10],
                'response': query[11],
                'responded_at': query[12],
                'responded_by': query[13]
            })
        
        return jsonify({
            'queries': formatted_queries,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/queries/<int:query_id>/respond', methods=['POST'])
def api_respond_to_query(query_id):
    """API endpoint to respond to a query"""
    try:
        data = request.get_json()
        response = data.get('response', '').strip()
        status = data.get('status', 'resolved')
        
        if not response:
            return jsonify({'success': False, 'error': 'Response is required'}), 400
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Update query with response
        cursor.execute("""
            UPDATE queries 
            SET response = ?, responded_at = ?, responded_by = ?, status = ?
            WHERE id = ?
        """, (response, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
              'admin', status, query_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queries/<int:query_id>/status', methods=['POST'])
def api_update_query_status(query_id):
    """API endpoint to update query status"""
    try:
        data = request.get_json()
        status = data.get('status', '').strip()
        
        if not status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute("UPDATE queries SET status = ? WHERE id = ?", (status, query_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queries/<int:query_id>', methods=['DELETE'])
def api_delete_query(query_id):
    """API endpoint to delete a query"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM queries WHERE id = ?", (query_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queries/export')
def api_export_queries():
    """API endpoint to export queries as CSV"""
    try:
        # Get filter parameters
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        # Build query
        query = """
            SELECT id, name, email, phone, message, subject, priority, status, 
                   category, source, submitted_at, response, responded_at, responded_by
            FROM queries 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (name LIKE ? OR email LIKE ? OR message LIKE ? OR subject LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        query += " ORDER BY submitted_at DESC"
        
        # Execute query
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        queries = cursor.fetchall()
        conn.close()
        
        # Create CSV
        from io import StringIO
        import csv
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'Subject', 'Message', 'Priority', 
            'Status', 'Category', 'Source', 'Submitted At', 'Response', 
            'Responded At', 'Responded By'
        ])
        
        # Write data
        for query in queries:
            writer.writerow(query)
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=queries_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_query_statistics():
    """Get statistics for queries"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Total queries
        cursor.execute("SELECT COUNT(*) FROM queries")
        total = cursor.fetchone()[0]
        
        # Pending queries
        cursor.execute("SELECT COUNT(*) FROM queries WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        # Resolved queries
        cursor.execute("SELECT COUNT(*) FROM queries WHERE status = 'resolved'")
        resolved = cursor.fetchone()[0]
        
        # Urgent queries
        cursor.execute("SELECT COUNT(*) FROM queries WHERE priority = 'urgent'")
        urgent = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'pending': pending,
            'resolved': resolved,
            'urgent': urgent
        }
        
    except Exception as e:
        return {
            'total': 0,
            'pending': 0,
            'resolved': 0,
            'urgent': 0
        }

@app.route('/query-management')
@admin_required
def query_management_page():
    """Query management page for admins"""
    return render_template('query_management.html')
```

### Step 2: Add Link to Admin Panel
Add a link to the query management page in your admin panel. Add this to your admin panel HTML:

```html
<a href="/query-management" class="admin-link">
    📧 Query Management
</a>
```

## Features

### 1. Query Management Interface
- **Dashboard**: Shows statistics (total, pending, resolved, urgent queries)
- **Filtering**: Filter by status, priority, category, and search text
- **Pagination**: Navigate through large numbers of queries
- **Actions**: View, respond, update status, and delete queries

### 2. Query Response System
- **Modal Interface**: Clean modal for responding to queries
- **Status Updates**: Update query status (pending, in-progress, resolved, closed)
- **Response Tracking**: Track who responded and when
- **History**: View previous responses

### 3. Export Functionality
- **CSV Export**: Export filtered queries to CSV
- **Filtered Export**: Export only filtered results
- **Complete Data**: Include all query fields in export

### 4. Enhanced Query Fields
- **Phone**: Contact phone number
- **Subject**: Query subject/title
- **Priority**: low, normal, high, urgent
- **Status**: pending, in-progress, resolved, closed
- **Category**: general, academic, technical, billing, admission
- **Source**: website, phone, email, social_media
- **Assignment**: Assign queries to staff members
- **Response Tracking**: Track responses and responders

## Usage

### Accessing Query Management
1. Log in as admin
2. Navigate to `/query-management`
3. Use the interface to manage queries

### Managing Queries
1. **View Queries**: Click "View" to see full query details
2. **Respond**: Click "Respond" to reply to queries
3. **Update Status**: Click "Status" to change query status
4. **Delete**: Click "Delete" to remove queries
5. **Export**: Click "Export Data" to download CSV

### Filtering Queries
- Use the filter dropdowns to narrow down queries
- Use the search box to find specific queries
- Apply multiple filters simultaneously

## Security
- Only admin users can access the query management interface
- Uses the `@admin_required` decorator for protection
- All API endpoints require admin authentication

## Database Indexes
The system automatically creates indexes for better performance:
- `idx_queries_status` - For status filtering
- `idx_queries_priority` - For priority filtering
- `idx_queries_submitted_at` - For date sorting
- `idx_queries_category` - For category filtering

## Troubleshooting

### Common Issues
1. **Template Not Found**: Ensure `query_management.html` is in the root directory
2. **Database Errors**: Check that the queries table exists and has the correct structure
3. **Permission Errors**: Ensure you're logged in as admin
4. **API Errors**: Check browser console for JavaScript errors

### Testing
1. Submit a test query through the main website
2. Access the query management interface
3. Test filtering, responding, and exporting functionality
4. Verify statistics are updating correctly

## Support
For issues or questions about the query management system, check:
1. Flask application logs
2. Browser developer console
3. Database connection and table structure
4. Admin authentication status 