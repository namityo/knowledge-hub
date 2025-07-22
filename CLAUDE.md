# CLAUDE.md

This file provides guidance to Claude Code when working with this Knowledge Base application.

## 📋 Project Overview

Flask-based knowledge sharing web application with Japanese interface, full offline capability, and comprehensive API support.

**Key Features:** Article management, Markdown editor, file attachments, tagging system, commenting, likes, user authentication, popular articles ranking, REST API

**Tech Stack:** Flask 2.3.3, SQLAlchemy, SQLite, Bootstrap 5.1.3 (local), Japanese UI

**Important Policies:**
- 🚫 **No CDN Dependencies** - All assets hosted locally for offline operation
- 🔒 **Security First** - Header-based authentication, audit logging, file validation
- 🎯 **User-Controlled Execution** - Server startup, debugging, and Python commands are user's responsibility

## 🚀 Development Commands

### Environment Setup
```bash
# Activate virtual environment (Windows) - USER RUNS THIS
.venv\Scripts\activate

# Install dependencies - USER RUNS THIS
pip install -r requirements.txt
```

### Server Startup (User Responsibility)
```bash
# Flask development server - USER RUNS THIS
python app.py
# Access at http://127.0.0.1:5000

# Production ASGI server (recommended) - USER RUNS THIS
uvicorn asgi:app --host 127.0.0.1 --port 5000 --reload

# Production deployment - USER RUNS THIS
uvicorn asgi:app --host 0.0.0.0 --port 5000 --workers 4
```

### Testing & Debugging (User Responsibility)
```bash
# Database operations, debugging, testing - ALL USER RESPONSIBILITY
# User runs Python commands and testing as needed
```

### UI/Layout Verification
- **Use Playwright MCP** for screen layout confirmation and visual testing
- Access via `mcp__playwright__browser_*` tools for automated browser testing
- Screenshot capture and layout validation through MCP browser automation

## ⚙️ Configuration (Environment Variables)

### Core Application
```bash
SYSTEM_TITLE="ナレッジベース"                    # App title
SECRET_KEY="your-secret-key"                    # Flask session key
```

### User Authentication
```bash
USER_ID_HEADER_NAME="X-User-ID"                 # Header for user ID
USER_ID_PATTERN="^[a-zA-Z0-9_-]{3,20}$"        # Validation regex
DEFAULT_USER_ID="anonymous"                     # Fallback user
```

### Database
```bash
DATABASE_URL="sqlite:///path/to/db"             # Full database URL (priority)
DATABASE_DIR="../data"                          # Database directory
DATABASE_FILENAME="knowledge.db"                # Database filename
```

### File Upload
```bash
MAX_FILE_SIZE_MB="16"                           # Max upload size
ALLOWED_FILE_EXTENSIONS="pdf,doc,txt,png,jpg"  # Allowed extensions

# Upload directory configuration (optional)
UPLOAD_DIR="../uploads"                         # Relative path to parent directory
UPLOAD_DIR="/var/files/knowledge"               # Absolute path
# Default: "uploads" directory in project root
```

### API Authentication
```bash
API_KEY="your-api-key"                          # API authentication key
API_KEY_HEADER_NAME="X-API-Key"                 # API key header name
```

### Features
```bash
POPULAR_ARTICLES_COUNT="5"                     # Popular articles display count
```

### Logging
```bash
AUDIT_LOG_DIR="../logs"                        # Log directory
AUDIT_LOG_FILENAME="audit.log"                 # Log filename
```

## 🏗️ Architecture

### File Structure
```
knowledge-hub/
├── app.py                 # Main Flask application
├── asgi.py               # ASGI server entry point
├── requirements.txt      # Python dependencies
├── CLAUDE.md            # This file - development guidance
├── app/
│   ├── __init__.py       # App factory
│   ├── models.py         # Database models
│   ├── routes.py         # Web routes
│   ├── api.py           # REST API endpoints
│   ├── utils.py         # Helper functions
│   ├── config.py        # Configuration
│   └── database.py      # Database initialization
├── templates/            # Jinja2 templates
│   ├── base.html        # Base layout
│   ├── index.html       # Article listing
│   ├── form_editor.html # Create/edit form
│   ├── view.html        # Article detail
│   ├── popular.html     # Popular articles
│   └── drafts.html      # Draft articles
├── static/              # Local assets (no CDN)
│   ├── css/            # Bootstrap, FontAwesome, custom CSS
│   ├── js/             # Bootstrap, Highlight.js, Marked.js
│   └── webfonts/       # FontAwesome fonts
├── migrations/          # Flask-Migrate database migrations
├── instance/           # SQLite database location (default)
├── uploads/            # File upload storage (default)
└── create_test_data.py  # Test data generation script
```

### Core Models
- **Knowledge**: Articles with tags, comments, likes, attachments
- **Comment**: User comments with likes
- **Tag**: Tagging system with usage tracking
- **ViewHistory**: Date-based view tracking
- **Attachment**: File upload management

## 🌐 API Endpoints

### Authentication
All endpoints (except `/health`) require API key in header when `API_KEY` is set.

### Main Endpoints
```
GET  /api/v1/articles/latest     # Latest articles with pagination
GET  /api/v1/articles/{id}       # Article details (includes comments by default)
GET  /api/v1/articles/popular    # Popular articles by views/likes/comments
GET  /api/v1/tags               # Tag list with usage counts
GET  /api/v1/health             # Health check (no auth)
```

### Response Format
```json
{
  "status": "success|error",
  "data": { ... },
  "message": "error description"
}
```

## 📝 Development Guidelines

### Code Style
- **No comments unless requested** - Keep code clean and self-documenting
- **Follow existing patterns** - Check neighboring files for conventions
- **Security first** - Never expose secrets, validate all inputs
- **Offline capable** - No external dependencies, local assets only

### Database Operations
- Use migrations for schema changes
- Tag usage counts auto-calculated via `handle_tags()`
- View tracking prevents duplicate daily views per user

### Key Functions
- `handle_tags(knowledge, tags_string, author)` - Unified tag processing
- `get_bulk_engagement_stats(articles, days=None)` - Efficient N+1 prevention
- `get_current_user_id()` - Header-based user identification

### Important Notes
- **Server startup is user responsibility** - Hot reload enabled automatically
- **Testing and debugging are user tasks** - Application provides tools
- **UI verification uses Playwright MCP** - Automated browser testing
- **No CDN usage** - All assets must be local
- **Japanese interface** - All UI text in Japanese
- **Header-based auth** - No user table, ID from HTTP headers

## 🔧 Common Tasks

### Adding New Features
1. Update models if needed (with migration)
2. Add routes in `routes.py`
3. Add API endpoints in `api.py` if required
4. Update templates with consistent styling
5. Test with user-run commands and Playwright MCP

### File Upload Directory Management
- **Default**: Files stored in `uploads/` directory at project root
- **Custom Location**: Set `UPLOAD_DIR` environment variable
- **Migration**: User manually moves existing files from `app/uploads/` to new location
- **Permissions**: Ensure write permissions for upload directory

### Tag Management
- Tags auto-created on article save
- Usage counts maintained automatically
- Only public articles count toward usage

### Popular Articles
- Based on last 30 days activity
- Tracks views, likes, comments separately
- Display count configurable via `POPULAR_ARTICLES_COUNT`
- Rankings available via web UI and API

This knowledge base is designed for complete offline operation with local asset hosting, Japanese interface, and comprehensive API access for external integration.