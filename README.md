# 🌅 Sunrise Educational Centre

A comprehensive educational management system built with Flask, designed for managing classes, resources, live sessions, and student interactions for Classes 9-12.

## 🚀 Features

### 📚 Study Resources Management
- **Class-specific resources** - Students see only resources for their enrolled class
- **Category-based organization** - Resources organized by type (worksheets, sample papers, etc.)
- **Paid/Free content filtering** - Respects user's payment status
- **Admin resource upload** - Teachers and admins can upload and manage resources

### 🎓 Live Class System
- **Real-time live classes** - Video streaming and interaction
- **Class scheduling** - Schedule classes in advance
- **Student participation** - Interactive features during live sessions
- **Recording management** - Store and manage class recordings

### 👥 User Management
- **Role-based access** - Students, Teachers, Admins with different permissions
- **Class enrollment** - Students assigned to specific classes (9, 10, 11, 12)
- **Payment status tracking** - Paid/unpaid student differentiation
- **User profiles** - Manage student information and progress

### 💬 Forum System
- **Class-specific discussions** - Topic-based forum discussions
- **Media sharing** - Upload and share images, documents
- **Moderation tools** - Admin controls for content management
- **Real-time messaging** - Live chat during sessions

### 📋 Admission Management
- **Online application** - Students can apply for admission
- **Admin approval workflow** - Review and approve/reject applications
- **Automatic user creation** - Approved students get accounts automatically
- **Document management** - Handle admission documents and photos

### 🔔 Notification System
- **Targeted notifications** - Send to specific classes or payment tiers
- **Live class alerts** - Notify students when classes start
- **Resource updates** - Alert students about new materials
- **Admin announcements** - Important updates and news

## 🛠️ Technical Stack

- **Backend**: Python Flask with SQLite database
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Real-time**: Flask-SocketIO for live features
- **File handling**: Secure file uploads and management
- **Authentication**: Session-based with role management
- **Responsive design**: Mobile-friendly interface

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies
```bash
pip3 install --break-system-packages -r requirements.txt
```

### Run the Application
```bash
python3 app.py
```

The application will start on `http://localhost:10000`

### Useful Routes

- `/` homepage
- `/auth` login/registration
- `/online-class` live classes (requires login)
- `/notifications` user notifications (requires login)
- `/api/live-classes/status` JSON status for live classes (requires login)

## 🔧 Configuration

### Environment Variables
- `PORT` - Server port (default: 10000)
- Database is automatically created as `users.db`

### Default Admin Access
- Admin code: `sec@011` (required for admin registration)
- Create admin account through the registration form

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── auth_handler.py        # Authentication and database functions
├── time_config.py         # Timezone configuration
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── uploads/              # User uploaded files
└── bulk_upload/          # Bulk operations modules
```

## 🎯 Recent Fixes & Updates

### ✅ Study Resources Route Fix (Latest)
- **Issue**: Study resources route not working due to missing `pytz` dependency
- **Solution**: Installed all required dependencies and verified functionality
- **Result**: All routes now fully functional with proper authentication
- **Documentation**: See `STUDY_RESOURCES_FIX.md` for detailed information

### ✅ Index.html Cleanup
- Removed 808 duplicate lines from index.html
- Fixed rendering issues and improved page performance
- Cleaned up HTML structure

## 🚀 Deployment

### Local Development
```bash
python3 app.py
```

### Production (Heroku/Railway)
The project includes:
- `Procfile` for Heroku deployment
- `requirements.txt` for dependency management
- Environment variable configuration

## 📱 Access Points

- **Home**: `/` - Main landing page
- **Authentication**: `/auth` - Login/Registration
- **Study Resources**: `/study-resources` - Class materials (requires login)
- **Forum**: `/forum` - Discussion boards (requires login)
- **Live Classes**: `/online-class` - Live sessions (requires login)
- **Admin Panel**: `/admin` - Management interface (admin only)

## 🔐 User Roles

1. **Students** - Access class resources, join live sessions, participate in forums
2. **Teachers** - Upload resources, manage live classes, moderate forums
3. **Admins** - Full system management, user administration, analytics

## 📊 Database Tables

- `users` - User accounts and profiles
- `classes` - Available classes (9, 10, 11, 12, admin, teacher)
- `resources` - Educational materials and files
- `categories` - Resource categorization
- `live_classes` - Live session management
- `forum_messages` - Discussion threads
- `notifications` - System announcements
- `admissions` - Application management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For technical issues or questions about the Sunrise Educational Centre system, please create an issue in this repository.

---

**🌅 Sunrise Educational Centre** - Empowering students through technology and quality education.
