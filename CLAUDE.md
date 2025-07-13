# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment (Windows)
activate.bat
# Or manually: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### Traditional Flask Development Server
```bash
# Start the Flask development server
python app.py
# Access at http://127.0.0.1:5000
```

#### Uvicorn ASGI Server (Recommended for Production)
```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start with uvicorn (production-ready ASGI server)
uvicorn asgi:app --host 127.0.0.1 --port 5000 --reload

# Or run the asgi.py file directly
python asgi.py

# Production deployment (without reload)
uvicorn asgi:app --host 0.0.0.0 --port 5000 --workers 4
```

**Important:** 
- Server startup is handled manually by the user
- Hot reload is enabled automatically with `use_reloader=True` setting (Flask) or `--reload` flag (Uvicorn)
- Files (.py, .html, .css) are automatically monitored for changes
- Server will restart automatically when files are modified
- **Testing and Development**: Running `python app.py` or `uvicorn asgi:app --reload` is the user's responsibility for testing new features
- **Production**: Uvicorn provides better performance and async support compared to Flask's built-in server

### User Authentication
The application uses HTTP header-based user identification without requiring a user table.

#### User ID Specification
- **Header Name**: Configurable via `USER_ID_HEADER_NAME` environment variable (default: `X-User-ID`)
- **Validation**: Regular expression pattern from environment variable
- **Default Pattern**: `^[a-zA-Z0-9_-]{3,20}$` (alphanumeric, underscore, hyphen, 3-20 chars)
- **Fallback**: Invalid user IDs are replaced with the configured default user ID

#### Environment Variables for User ID
```bash
# Set custom header name for user identification
export USER_ID_HEADER_NAME="X-User-ID"                 # Default header name
export USER_ID_HEADER_NAME="Authorization-User"        # Custom header name
export USER_ID_HEADER_NAME="User-Identity"             # Alternative header name

# Set custom user ID validation pattern
export USER_ID_PATTERN="^[a-zA-Z0-9]{4,16}$"

# Set default user ID (when header is not provided)
export DEFAULT_USER_ID="guest"

# Examples of valid patterns:
export USER_ID_PATTERN="^[a-zA-Z0-9_-]{3,20}$"        # Default pattern
export USER_ID_PATTERN="^emp[0-9]{4}$"                 # Employee ID format (emp1234)
export USER_ID_PATTERN="^[a-z]+\.[a-z]+@company\.com$" # Email format

# Examples of default user ID settings:
export DEFAULT_USER_ID="anonymous"                     # Default value
export DEFAULT_USER_ID="guest"                         # Guest user
export DEFAULT_USER_ID="visitor"                       # Visitor user
export DEFAULT_USER_ID="demo"                          # Demo user
```

#### Usage Example
```bash
# Valid request with default header
curl -H "X-User-ID: user123" -X POST http://127.0.0.1:5000/create

# Valid request with custom header (when USER_ID_HEADER_NAME="Authorization-User")
curl -H "Authorization-User: emp1234" -X POST http://127.0.0.1:5000/create

# Invalid user ID (will be treated as configured default user ID)
curl -H "X-User-ID: invalid@#$" -X POST http://127.0.0.1:5000/create
```

#### Audit Logging
- All database operations are logged with user identification
- Invalid user IDs trigger warning logs
- Log file location configurable via environment variables

##### Audit Log Environment Variables
```bash
# Custom audit log directory (relative to app root or absolute path)
export AUDIT_LOG_DIR="../logs"                         # Parent directory's logs folder
export AUDIT_LOG_DIR="/var/log/knowledge"              # Absolute path
export AUDIT_LOG_DIR="./logs"                          # Relative path from app root

# Custom audit log filename
export AUDIT_LOG_FILENAME="app_audit.log"              # Custom filename
export AUDIT_LOG_FILENAME="security.log"               # Alternative filename
```

##### Audit Log Location Examples
```bash
# Development: default location
# No environment variables set
# Result: knowledge_app/audit.log

# Production: parent directory logs folder
export AUDIT_LOG_DIR="../logs"
export AUDIT_LOG_FILENAME="knowledge_audit.log"
# Result: knowledge_app/../logs/knowledge_audit.log

# Production: absolute path
export AUDIT_LOG_DIR="/var/log/knowledge"
# Result: /var/log/knowledge/audit.log
```

### Database
- SQLite database auto-created on first run
- Database schema initialized automatically via `db.create_all()` in app startup
- Database location configurable via environment variables

#### Database Environment Variables
```bash
# Custom database directory (relative to app root or absolute path)
export DATABASE_DIR="../data"                           # Parent directory's data folder
export DATABASE_DIR="/var/lib/knowledge"                # Absolute path
export DATABASE_DIR="./storage"                         # Relative path from app root

# Custom database filename
export DATABASE_FILENAME="knowledge_prod.db"            # Custom filename
export DATABASE_FILENAME="app.sqlite"                   # Alternative filename

# Full database URL (overrides DATABASE_DIR and DATABASE_FILENAME)
export DATABASE_URL="sqlite:///C:/data/knowledge.db"    # Windows absolute path
export DATABASE_URL="sqlite:////var/lib/knowledge/app.db" # Linux absolute path
export DATABASE_URL="postgresql://user:pass@host/db"    # PostgreSQL example
```

#### Database Location Examples
```bash
# Development: default location
# No environment variables set
# Result: knowledge_app/instance/knowledge.db

# Production: parent directory data folder
export DATABASE_DIR="../data"
export DATABASE_FILENAME="knowledge_prod.db"
# Result: knowledge_app/../data/knowledge_prod.db

# Production: absolute path
export DATABASE_DIR="/opt/knowledge/data"
# Result: /opt/knowledge/data/knowledge.db

# Custom database URL (highest priority)
export DATABASE_URL="sqlite:///C:/ProgramData/Knowledge/app.db"
# Result: C:/ProgramData/Knowledge/app.db
```

## Architecture Overview

This is a Flask-based knowledge sharing web application with the following structure:

### Core Components
- **Flask Application** (`app.py`): Single-file Flask app with all routes and database models
- **Database Models**: Multiple models for complete knowledge management system:
  - `Knowledge`: Core articles with metadata
  - `Comment`: User comments with Markdown support
  - `Like`: Article like system with user restrictions
  - `CommentLike`: Comment like system
  - `Attachment`: File upload and management
- **Templates**: Jinja2 templates extending `base.html` for consistent layout
- **Static Assets**: Complete offline-capable local asset hosting (Bootstrap 5, Font Awesome, Highlight.js, Marked.js)

### Key Routes and Functionality
- `/` - Homepage with search, filtering, and pagination
- `/create` - Rich Markdown editor with file upload support (uses `form_editor.html`)
- `/view/<id>` - Article view with comments, likes, and attachments
- `/edit/<id>` - Advanced split-pane editor with live preview (uses `form_editor.html`)
- `/delete/<id>` - Delete article (with confirmation)
- `/comment/<knowledge_id>` - Add comments to articles
- `/comment/delete/<comment_id>` - Delete user's own comments
- `/like/<knowledge_id>` - Toggle article likes
- `/comment/like/<comment_id>` - Toggle comment likes
- `/download/<attachment_id>` - Download attached files
- `/delete_attachment/<attachment_id>` - Delete file attachments

### Frontend Architecture
- **Base Template** (`templates/base.html`): Bootstrap 5 layout with Japanese navigation
- **Responsive Design**: Card-based grid layout using Bootstrap classes
- **Custom Styling** (`static/css/style.css`): Hover effects, gradient buttons, modern aesthetics
- **JavaScript**: Bootstrap bundle for interactive components

### Database Schema
```python
# Many-to-many relationship table for tags
knowledge_tags = db.Table('knowledge_tags',
    db.Column('knowledge_id', db.Integer, db.ForeignKey('knowledge.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Knowledge(db.Model):
    id = Integer, primary_key
    title = String(200), required
    content = Text, required  
    author = String(100), required
    created_at = DateTime, auto-generated
    updated_at = DateTime, auto-updated
    # Relationships
    comments = relationship to Comment
    likes = relationship to Like
    attachments = relationship to Attachment
    tags = relationship to Tag (many-to-many via knowledge_tags)

class Comment(db.Model):
    id = Integer, primary_key
    content = Text, required
    author = String(100), required
    created_at = DateTime, auto-generated
    knowledge_id = ForeignKey to Knowledge
    comment_likes = relationship to CommentLike

class Like(db.Model):
    id = Integer, primary_key
    user_id = String(100), required
    knowledge_id = ForeignKey to Knowledge
    created_at = DateTime, auto-generated
    # Unique constraint: one like per user per article

class CommentLike(db.Model):
    id = Integer, primary_key
    user_id = String(100), required
    comment_id = ForeignKey to Comment
    created_at = DateTime, auto-generated
    # Unique constraint: one like per user per comment

class Attachment(db.Model):
    id = Integer, primary_key
    filename = String(255), original filename
    stored_filename = String(255), UUID-based storage name
    file_size = Integer, size in bytes
    mime_type = String(100), detected MIME type
    knowledge_id = ForeignKey to Knowledge
    uploaded_by = String(100), uploader user ID
    created_at = DateTime, auto-generated

class Tag(db.Model):
    id = Integer, primary_key
    name = String(50), unique, required
    color = String(7), default='#007bff'
    usage_count = Integer, default=0
    created_at = DateTime, auto-generated
    created_by = String(100), required
    # Relationship
    knowledge_items = backref to Knowledge (many-to-many)
```

### Technology Stack
- Flask 2.3.3 with SQLAlchemy ORM
- SQLite database (location configurable via environment variables)
- Bootstrap 5.1.3 for responsive UI (locally hosted)
- Jinja2 templating with custom filters
- Japanese language interface
- Markdown processing with Marked.js (locally hosted)
- Highlight.js 11.9.0 for syntax highlighting (locally hosted)
- Font Awesome 6.0.0 icons (locally hosted with webfonts)

## 🚫 CDN Policy

**IMPORTANT: This application does NOT use external CDNs for any assets.**

All CSS, JavaScript, and font files are stored locally in the `/static` directory to ensure:
- **Offline functionality**: Application works without internet connection
- **Security**: No external dependencies that could be compromised
- **Performance**: Faster loading with local assets
- **Privacy**: No tracking from external CDN providers
- **Reliability**: No external points of failure

### Local Asset Structure
```
static/
├── css/
│   ├── bootstrap.min.css     # Bootstrap 5.1.3 (local)
│   ├── fontawesome.min.css   # Font Awesome 6.0.0 (local)
│   ├── highlight-github.min.css  # Highlight.js theme (local)
│   └── style.css             # Custom application styles
├── js/
│   ├── bootstrap.bundle.min.js   # Bootstrap JS (local)
│   ├── highlight.min.js      # Syntax highlighting (local)
│   └── marked.min.js         # Markdown processing (local)
└── webfonts/
    ├── fa-regular-400.woff2  # Font Awesome regular fonts
    └── fa-solid-900.woff2    # Font Awesome solid fonts
```

### Development Guidelines
- **Never use CDN links** in templates (e.g., avoid `https://cdn.jsdelivr.net/`)
- **Always download and host locally** any external assets
- **Update local files manually** when upgrading libraries
- **Test offline functionality** regularly to ensure no CDN dependencies
- Complete offline operation capability

## Features and Functionality

### Search System
- **Header Search Bar**: Always accessible search form in navigation bar
- **Search Scope**: Searches article titles, content, and comments
- **Search Results**: Displays match count and highlights search terms
- **Query Parameters**: Maintains search state across pagination
- **Real-time**: Instant search results on form submission
- **Filter Integration**: Works with user post filtering

### Pagination System
- **Page Size**: 10 articles per page
- **Navigation**: Previous/Next buttons with page numbers
- **Search Integration**: Pagination works with search results
- **Info Display**: Shows "X of Y items" and current page information
- **URL Parameters**: Clean URLs with page and search parameters

### Markdown Support
- **Full Markdown**: Complete GitHub Flavored Markdown support
- **Syntax Highlighting**: Code blocks with language-specific highlighting
- **Line Breaks**: Single line breaks recognized as actual breaks
- **Rich Content**: Supports headers, lists, links, tables, quotes, code
- **Help System**: Built-in Markdown guide with examples accessible via modal

### Content Management
- **CRUD Operations**: Create, Read, Update, Delete articles
- **User Authorization**: Only authors can edit/delete their own articles
- **Rich Editing**: Split-pane editor with real-time Markdown preview
- **Responsive Editor**: Mobile-friendly tabbed interface for editing
- **Content Preview**: 5-line preview with smart truncation on listing page

### UI/UX Enhancements
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Modern Layout**: Clean card-based design with proper spacing
- **Visual Hierarchy**: Clear separation between metadata and content
- **Interactive Elements**: Hover effects, loading states, form validation
- **Accessibility**: Proper ARIA labels and keyboard navigation

### Advanced Editor Features
- **Live Preview**: Real-time Markdown rendering as you type
- **Split View**: Side-by-side editing and preview on desktop
- **Tabbed Interface**: Space-efficient mobile editing with tabs
- **Syntax Help**: Comprehensive Markdown guide with copy-paste examples
- **Auto-sync**: Editor content synchronized across desktop/mobile views
- **File Upload**: Multi-file attachment support with client-side validation
- **Error Handling**: Bootstrap Toast notifications for better UX

## Updated Routes and Functionality

### Core Routes
- `/` - Homepage with search, filtering, pagination, and article grid
  - **Query Parameters**: `?search=keyword&page=1&my_posts=1`
  - **Features**: Header search, user post filtering, pagination controls, responsive cards
- `/create` - Rich Markdown editor with file upload support (unified template)
- `/view/<id>` - Article display with comments, likes, and compact attachment list
- `/edit/<id>` - Advanced split-pane editor with live preview and file management (unified template)
- `/delete/<id>` - Delete confirmation with user authorization

### UI Components
- **Header**: Fixed navigation with search bar and create button
- **Footer**: Consistent across all pages with proper spacing
- **Cards**: Modern article cards with metadata and content preview
- **Pagination**: Bootstrap pagination with page info
- **Modals**: Help system for Markdown syntax reference

## Dependencies and Requirements

### Python Dependencies (requirements.txt)
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7
Markdown==3.5.1
Pygments==2.17.2
```

### Frontend Dependencies (CDN)
- Bootstrap 5.1.3 (CSS + JS)
- Font Awesome 6.0.0 (Icons)
- Highlight.js 11.9.0 (Code syntax highlighting)
- Marked.js (Client-side Markdown processing for editor preview)

### Markdown Extensions
- `fenced_code`: GitHub-style code blocks with language specification
- `tables`: Table support
- `codehilite`: Server-side syntax highlighting via Pygments
- `nl2br`: Single line break recognition

## Performance and Optimization

### Database Optimization
- **Pagination**: Efficient database queries with LIMIT/OFFSET
- **Indexing**: Automatic primary key indexing
- **Search**: Uses SQLAlchemy's `contains()` for text search

### Frontend Optimization
- **CDN Assets**: All CSS/JS served from CDN
- **Responsive Images**: Optimized loading and display
- **Minimal Custom CSS**: Leverages Bootstrap classes
- **Progressive Enhancement**: Works without JavaScript

## Browser Compatibility
- Modern browsers with ES6+ support
- Mobile-first responsive design
- Graceful degradation for older browsers
- Accessibility standards compliance

## New Features Added

### Comment System
- **Markdown Support**: Comments support full Markdown formatting with syntax highlighting
- **Nested Display**: Comments ordered by newest first
- **User Management**: Users can only delete their own comments
- **Comment Counts**: Display comment count on article listing page
- **Search Integration**: Comments are included in search results

### Like System
- **Article Likes**: Users can like articles (except their own)
- **Comment Likes**: Users can like comments (except their own)
- **Visual Feedback**: Heart icons with like counts
- **User Restrictions**: Self-liking prevention with audit logging
- **Toggle Functionality**: Click to like/unlike with flash messages

### User Post Filtering
- **Filter Options**: "すべて" (All) and "自分の投稿" (My Posts) buttons
- **Search Integration**: Filtering works with search queries
- **Visual Indicators**: Badge system showing active filters
- **URL Parameters**: Clean URLs with filter state preservation

### File Attachment System
- **Multi-file Upload**: Support for multiple file attachments per article
- **File Type Validation**: Whitelist of allowed file extensions
- **Size Limits**: Configurable file size limits via environment variables
- **Security**: UUID-based filename storage to prevent conflicts
- **Download Support**: Secure file download with original filenames
- **File Management**: Users can delete attachments they uploaded
- **Visual Indicators**: Paperclip icons showing attachment count
- **Compact Display**: Simplified list format in article view

### Environment Configuration
All application settings can be customized via environment variables for different deployment environments:

#### Core Application Settings
- **System Title**: `SYSTEM_TITLE` - Customizable application branding (default: 'ナレッジベース')
- **Secret Key**: `SECRET_KEY` - Flask session encryption key (default: development fallback)

#### User Authentication Settings
- **User ID Header**: `USER_ID_HEADER_NAME` - HTTP header name for user identification (default: 'X-User-ID')
- **User ID Pattern**: `USER_ID_PATTERN` - Regex pattern for user ID validation (default: '^[a-zA-Z0-9_-]{3,20}$')
- **Default User ID**: `DEFAULT_USER_ID` - Fallback user ID for invalid/missing headers (default: 'anonymous')

#### Database Configuration
- **Database Directory**: `DATABASE_DIR` - Custom database directory path (relative or absolute)
- **Database Filename**: `DATABASE_FILENAME` - Custom database filename (default: 'knowledge.db')  
- **Database URL**: `DATABASE_URL` - Complete database URL (overrides DIR and FILENAME settings)

#### File Upload Settings
- **File Size Limit**: `MAX_FILE_SIZE_MB` - Maximum upload file size in MB (default: 16)
- **Allowed Extensions**: `ALLOWED_FILE_EXTENSIONS` - Comma-separated allowed file extensions

#### Audit Logging Settings
- **Log Directory**: `AUDIT_LOG_DIR` - Custom audit log directory path (relative or absolute)
- **Log Filename**: `AUDIT_LOG_FILENAME` - Custom audit log filename (default: 'audit.log')

#### File Upload Configuration
```bash
# Set maximum file size (in MB)
export MAX_FILE_SIZE_MB="32"                           # Allow up to 32MB files

# Set allowed file extensions (comma-separated, case-insensitive)
export ALLOWED_FILE_EXTENSIONS="pdf,doc,docx,txt,png,jpg,jpeg"  # Office + images only
export ALLOWED_FILE_EXTENSIONS="txt,md,json,csv"               # Text files only
export ALLOWED_FILE_EXTENSIONS="png,jpg,jpeg,gif,svg,webp"     # Images only
export ALLOWED_FILE_EXTENSIONS="zip,rar,7z,tar,gz"             # Archives only

# Examples for different environments:
# Development: All file types (default)
# No ALLOWED_FILE_EXTENSIONS set - uses built-in defaults

# Production: Restricted file types
export ALLOWED_FILE_EXTENSIONS="pdf,doc,docx,xls,xlsx,ppt,pptx,txt,csv,png,jpg,jpeg"

# Security-focused: Minimal file types
export ALLOWED_FILE_EXTENSIONS="txt,pdf,png,jpg"
```

#### Default Allowed Extensions
When `ALLOWED_FILE_EXTENSIONS` is not set, the following extensions are allowed:
- **Documents**: txt, pdf, doc, docx, xls, xlsx, ppt, pptx, csv, json, xml, md
- **Images**: png, jpg, jpeg, gif, svg, webp
- **Archives**: zip, rar, 7z

### UI/UX Improvements
- **Toast Notifications**: Bootstrap Toast system replacing browser alerts
- **Error Handling**: Improved file upload error feedback
- **Responsive Design**: Mobile-optimized tabbed editor interface
- **Consistent Styling**: Unified spacing and visual hierarchy
- **Progressive Enhancement**: JavaScript-enhanced features with fallbacks

### Security Features
- **File Type Restrictions**: Whitelist-based file type validation
- **User Authorization**: Ownership-based edit/delete permissions
- **Audit Logging**: Comprehensive activity logging with user identification
- **Input Validation**: Server-side validation for all user inputs
- **CSRF Protection**: Flask's built-in CSRF protection for forms

### Technical Improvements
- **Database Relationships**: Proper foreign key relationships with cascade deletes
- **File Storage**: Organized upload directory with UUID-based naming
- **Error Recovery**: Form data preservation during validation errors
- **Performance**: Efficient database queries with proper indexing
- **Static File Management**: Complete offline capability with local asset hosting

#### Static Assets and Offline Support
The application has been configured for complete offline operation by replacing all CDN dependencies with local files:

##### Local Static Files
```
static/
├── css/
│   ├── bootstrap.min.css        # Bootstrap 5.1.3 CSS framework
│   ├── fontawesome.min.css      # Font Awesome 6.0.0 icons (paths updated for local fonts)
│   ├── highlight-github.min.css # Highlight.js GitHub theme for syntax highlighting
│   └── style.css               # Custom application styles
├── js/
│   ├── bootstrap.bundle.min.js  # Bootstrap 5.1.3 JavaScript (includes Popper.js)
│   ├── highlight.min.js         # Highlight.js 11.9.0 for code syntax highlighting
│   └── marked.min.js           # Marked.js for Markdown parsing in editor preview
└── webfonts/
    ├── fa-solid-900.woff2      # Font Awesome solid icons font
    └── fa-regular-400.woff2    # Font Awesome regular icons font
```

##### Benefits of Local Assets
- **Complete Offline Operation**: No external network dependencies
- **Enhanced Security**: Eliminates external CDN attack vectors
- **Improved Performance**: Local file serving with browser caching
- **Reliability**: No dependency on external service availability
- **Corporate Network Friendly**: Works in restricted network environments

##### Flask Static File Serving
- **Automatic Configuration**: Flask serves static files from `/static/` URL path
- **Template Integration**: Uses `url_for('static', filename='...')` for dynamic URL generation
- **Caching Support**: Browsers cache static assets with 304 Not Modified responses
- **Font Path Updates**: Font Awesome CSS updated to reference local webfont files

##### Migration from CDN
Successfully migrated all external dependencies:
- **Bootstrap 5.1.3**: From cdn.jsdelivr.net to local files
- **Font Awesome 6.0.0**: From cdnjs.cloudflare.com to local files with path corrections
- **Highlight.js 11.9.0**: From cdnjs.cloudflare.com to local files
- **Marked.js**: From cdn.jsdelivr.net to local files

All functionality verified working including syntax highlighting, Markdown preview, responsive design, and icon display.

### Code Refactoring and Optimization

#### Template Consolidation (2025-07-12)
- **Unified Form Editor**: Consolidated `create.html` and `edit.html` into single `form_editor.html`
- **Mode-based Rendering**: Uses `mode` parameter ('create'/'edit') for conditional display
- **Code Reduction**: Eliminated 200+ lines of duplicate template code
- **Shared Logic**: Created `handle_file_uploads()` function for common file processing
- **Maintenance Benefits**: Single template to maintain for both create and edit functionality

#### Template Structure (Current)
```
templates/
├── base.html           # Base layout with navigation
├── form_editor.html    # Unified create/edit form (NEW)
├── index.html          # Article listing page
└── view.html           # Article detail view
```

#### Shared Functions in app.py
- `handle_file_uploads(knowledge_id, author)`: Common file upload processing
- `handle_tags(knowledge, tags_string, author)`: Unified tag processing for create/edit
- `allowed_file(filename)`: File extension validation
- `get_current_user_id()`: User identification from headers
- `validate_user_id(user_id)`: User ID pattern validation

#### Refactoring Benefits
- **DRY Principle**: Eliminated code duplication between create and edit
- **Consistency**: Guaranteed identical UI/UX for both operations
- **Maintainability**: Single point of change for form improvements
- **Testing**: Reduced test surface area
- **Developer Experience**: Faster development of new form features

### Tag System Implementation (2025-07-12)

#### Database Schema for Tags
```python
# Many-to-many association table
knowledge_tags = db.Table('knowledge_tags',
    db.Column('knowledge_id', db.Integer, db.ForeignKey('knowledge.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Tag(db.Model):
    id = Integer, primary_key
    name = String(50), unique, required     # Tag name (unique)
    color = String(7), default='#007bff'   # Display color (HEX)
    usage_count = Integer, default=0       # Usage frequency
    created_at = DateTime, auto-generated
    created_by = String(100), required     # Creator user ID

# Updated Knowledge model with tag relationship
class Knowledge(db.Model):
    # ... existing fields ...
    tags = relationship('Tag', secondary=knowledge_tags, lazy='subquery', 
                       backref=backref('knowledge_items', lazy=True))
```

#### Tag Features Implementation

##### User Interface
- **Tag Input Field**: Comma-separated tag input in unified form editor
- **Visual Display**: Color-coded badges with Font Awesome icons
- **Popular Tags**: Top 10 most-used tags displayed prominently above filters
- **Clickable Tags**: Tags are clickable links for instant filtering
- **Responsive Design**: Mobile-friendly tag layout with proper wrapping

##### Tag Management System
- **Auto-creation**: New tags created automatically when first used
- **Usage Tracking**: Automatic increment of usage_count for popularity ranking
- **Color Assignment**: Default blue color (#007bff) with future customization support
- **Duplicate Prevention**: Database constraint ensures unique tag names
- **Length Validation**: Maximum 50 characters per tag with user feedback

##### Filtering and Navigation
- **Tag Filtering**: Filter articles by specific tags via URL parameter `?tag=tagname`
- **Combined Filters**: Tags work with existing search and user post filters
- **Filter State Display**: Active filters shown as colored badges
- **Filter Clear**: One-click filter removal functionality
- **Popular Tag Navigation**: Quick access to frequently used tags

#### Technical Implementation

##### Backend Functions
```python
def handle_tags(knowledge, tags_string, author):
    """Unified tag processing for create/edit operations"""
    # Parse comma-separated tag string
    # Create new tags or increment usage count
    # Associate tags with knowledge article
    # Handle edge cases (None values, duplicates)

def tags_to_string_filter(tags):
    """Template filter for displaying tags as comma-separated string"""
    # Used in edit forms to populate tag input field
```

##### Route Enhancements
- **Create Route**: Added tag processing with `handle_tags()` function
- **Edit Route**: Tag editing with existing tag preservation and updates
- **Index Route**: Enhanced with tag filtering and popular tags query
- **URL Parameters**: Clean tag filtering with proper encoding support

##### Template Updates
- **form_editor.html**: Added tag input field with validation hints
- **index.html**: Popular tags section above filters, clickable tag displays
- **view.html**: Tag badges in article headers with filtering links
- **Responsive Layout**: Optimized tag display for desktop and mobile

#### User Experience Improvements

##### Information Architecture
1. **Popular Tags** (Top of page) - Discovery and quick navigation
2. **Filter Controls** (Below tags) - Post type filtering (All/My Posts)
3. **Active Filters** (Status display) - Current filter state visibility
4. **Content Area** - Tagged articles with inline tag navigation

##### Visual Design
- **Color Coding**: Consistent tag colors for visual recognition
- **Usage Indicators**: Tag usage count in parentheses for popularity context
- **Active State**: Selected tags highlighted with dark background
- **Hover Effects**: Interactive feedback for clickable elements

##### Navigation Flow
1. Users browse popular tags for content discovery
2. Click tags to filter relevant articles
3. Combine with search or user filters as needed
4. Clear filters easily with dedicated button

#### Database Migration Considerations
- **Backward Compatibility**: Existing articles continue to work without tags
- **Progressive Enhancement**: Tag features enhance but don't break existing functionality
- **Data Integrity**: Proper foreign key constraints and cascade deletes
- **Performance**: Indexed relationships for efficient tag-based queries

#### Future Enhancement Opportunities
- **Tag Colors**: Custom color assignment per tag
- **Tag Categories**: Hierarchical or categorized tag organization
- **Tag Suggestions**: Auto-complete based on existing tags
- **Tag Analytics**: Usage statistics and trending tags
- **Tag Management**: Admin interface for tag maintenance

### Liked Posts Filter System (2025-07-12)

#### Comprehensive Like-based Filtering
Enhanced the post filtering system to include posts that users have interacted with through likes, providing a personalized content discovery experience.

#### Filter Types Implementation
```python
# Filter button group in index.html
<div class="btn-group" role="group">
    <a href="?">すべて</a>                    # All posts
    <a href="?my_posts=1">自分の投稿</a>       # User's own posts  
    <a href="?liked_posts=1">いいねした投稿</a> # Liked posts (NEW)
</div>
```

#### Advanced Like Detection Logic
```python
# Backend filtering logic in app.py (lines 337-346)
if liked_posts == '1':
    query = query.filter(
        db.or_(
            # Articles directly liked by user
            Knowledge.likes.any(Like.user_id == current_user_id),
            # Articles with comments liked by user
            Knowledge.comments.any(Comment.comment_likes.any(CommentLike.user_id == current_user_id))
        )
    )
```

#### Feature Benefits

##### Content Discovery
- **Personal History**: Users can easily find content they've engaged with
- **Comprehensive Coverage**: Includes both article likes and comment likes
- **Quick Access**: Single-click filtering from main navigation
- **Context Preservation**: Filter state maintained across navigation

##### User Experience
- **Visual Feedback**: Active filter highlighted with distinctive styling
- **Status Display**: Red badge showing "いいねした投稿" when filter is active
- **Count Indicator**: Shows exact number of liked posts
- **Seamless Integration**: Works with existing search and tag filters

##### Technical Implementation
- **Database Efficiency**: Optimized SQL queries with proper joins
- **URL Parameters**: Clean URLs with `?liked_posts=1` parameter
- **State Management**: Filter state preserved across pagination and navigation
- **Backward Compatibility**: Non-breaking addition to existing functionality

#### Filtering Logic Details

##### Multi-level Like Detection
1. **Direct Article Likes**: Posts where user clicked the article's like button
2. **Comment Interaction**: Posts where user liked any comment within the article
3. **Combined Results**: Unified view of all user engagement regardless of interaction type

##### Filter Combination Support
- **Search + Liked Posts**: `?search=keyword&liked_posts=1`
- **Tags + Liked Posts**: `?tag=python&liked_posts=1` 
- **My Posts + Search**: `?my_posts=1&search=keyword`
- **All Filters Combined**: Full parameter combination support

#### UI/UX Design Patterns

##### Filter Button Group
```html
<!-- Three-button filter group with consistent styling -->
<div class="btn-group" role="group">
    <a class="btn btn-sm btn-primary">すべて</a>
    <a class="btn btn-sm btn-outline-primary">自分の投稿</a>
    <a class="btn btn-sm btn-outline-primary">いいねした投稿</a>
</div>
```

##### Active State Indication
- **Button Styling**: Active filter uses `btn-primary` (filled blue)
- **Inactive Styling**: Non-active filters use `btn-outline-primary` (outline only)
- **Badge Display**: Colored badge below buttons shows current filter status
- **Count Display**: Shows filtered result count (e.g., "4件" for liked posts)

##### Responsive Behavior
- **Mobile Optimization**: Button group wraps appropriately on small screens
- **Touch Targets**: Adequate touch target size for mobile interaction
- **Icon Integration**: Font Awesome icons (heart, user, list) for visual clarity

#### Database Query Optimization

##### Efficient Relationship Queries
```python
# Optimized query structure
query = Knowledge.query.filter(
    db.or_(
        # Primary table join (efficient)
        Knowledge.likes.any(Like.user_id == current_user_id),
        # Nested relationship join (properly indexed)
        Knowledge.comments.any(Comment.comment_likes.any(CommentLike.user_id == current_user_id))
    )
)
```

##### Performance Considerations
- **Lazy Loading**: Uses `lazy='subquery'` for related data loading
- **Index Usage**: Leverages existing primary key and foreign key indexes
- **Query Caching**: SQLAlchemy query result caching for repeated requests
- **Pagination Support**: Works efficiently with existing pagination system

#### Testing and Validation

##### User Interaction Scenarios
1. **Like Article**: User likes article → appears in liked posts filter
2. **Like Comment**: User likes comment → parent article appears in filter
3. **Unlike Actions**: Removing likes properly removes from filter
4. **Multiple Interactions**: Both article and comment likes on same post work correctly

##### Filter State Testing
- **URL Parameter Persistence**: Filter state maintained across page navigation
- **Combined Filtering**: Multiple filters work together correctly
- **Filter Clearing**: Returning to "すべて" properly clears all filters
- **Search Integration**: Search works correctly with liked posts filter active

#### Integration with Existing Systems

##### Search System Compatibility
- **Combined Queries**: Search + liked posts filter work together
- **Result Highlighting**: Search results properly highlight within liked posts
- **Parameter Handling**: Clean URL parameter management

##### Tag System Integration  
- **Tag Links**: Popular tags maintain liked posts filter when clicked
- **Filter Combinations**: Tag filtering + liked posts work seamlessly
- **URL Generation**: Proper parameter concatenation in template links

##### Pagination System Support
- **Page Navigation**: Filter state preserved across page changes
- **Result Counting**: Accurate pagination information with filtered results
- **Performance**: Efficient pagination with complex filter queries

#### Security and Privacy

##### User Data Protection
- **User Isolation**: Only shows user's own liked content
- **Header Validation**: Proper X-User-ID header validation
- **Audit Logging**: Like actions logged for security monitoring
- **Privacy Compliance**: No exposure of other users' like behavior

#### Future Enhancement Opportunities
- **Liked Comments View**: Dedicated view for comments user has liked
- **Like History**: Chronological view of user's like activity
- **Like Categories**: Group liked content by tags or date ranges
- **Export Functionality**: Export liked posts list for personal use
- **Social Features**: Share liked post collections (with privacy controls)

## REST API for External Applications (2025-07-13)

### Overview
The application provides a comprehensive REST API for external applications to access knowledge base content. The API supports authentication, filtering, pagination, and returns data in JSON format with Japanese time (JST) conversion.

### API Authentication
All API endpoints (except health check) require authentication via API key in HTTP headers.

#### Environment Variables for API Authentication
```bash
# Set API key for authentication (required for API access)
export API_KEY="your-secret-api-key-here"

# Customize API key header name (optional)
export API_KEY_HEADER_NAME="X-API-Key"              # Default header name
export API_KEY_HEADER_NAME="Authorization"          # Alternative header name
export API_KEY_HEADER_NAME="X-Auth-Token"           # Custom header name
```

#### Authentication Behavior
- **API_KEY not set**: Authentication is disabled (development mode)
- **API_KEY set**: All API endpoints require valid API key in headers
- **Missing API key**: Returns 401 Unauthorized error
- **Invalid API key**: Returns 403 Forbidden error

### API Endpoints

#### Base URL Structure
All API endpoints use the prefix `/api/v1/` for versioning support.

#### Authentication Required Endpoints

##### 1. Latest Articles
```
GET /api/v1/articles/latest
```

**Query Parameters:**
- `limit` (integer, optional): Number of articles to return (default: 10, max: 100)
- `offset` (integer, optional): Number of articles to skip for pagination (default: 0)
- `author` (string, optional): Filter articles by specific author
- `tag` (string, optional): Filter articles by specific tag name

**Example Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     "http://127.0.0.1:5000/api/v1/articles/latest?limit=5&author=user123"
```

##### 2. Specific Article
```
GET /api/v1/articles/{id}
```

**Path Parameters:**
- `id` (integer, required): Article ID to retrieve

**Example Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     "http://127.0.0.1:5000/api/v1/articles/17"
```

##### 3. Popular Articles
```
GET /api/v1/articles/popular
```

**Query Parameters:**
- `limit` (integer, optional): Number of articles to return (default: 10, max: 100)

**Example Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     "http://127.0.0.1:5000/api/v1/articles/popular?limit=3"
```

##### 4. Tags List
```
GET /api/v1/tags
```

Returns all tags ordered by usage count (most popular first).

**Example Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     "http://127.0.0.1:5000/api/v1/tags"
```

#### Public Endpoints (No Authentication Required)

##### Health Check
```
GET /api/v1/health
```

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/v1/health"
```

### API Response Format

#### Success Response Structure
```json
{
  "status": "success",
  "data": {
    // Response data varies by endpoint
  }
}
```

#### Error Response Structure
```json
{
  "status": "error",
  "message": "Error description in Japanese"
}
```

#### Article Object Structure
```json
{
  "id": 17,
  "title": "記事タイトル",
  "content": "記事内容（Markdown形式）",
  "author": "作成者",
  "created_at": "2025-07-13 13:09:57",
  "updated_at": "2025-07-13 13:09:57",
  "like_count": 5,
  "comment_count": 3,
  "attachment_count": 2,
  "tags": [
    {
      "id": 1,
      "name": "Python",
      "color": "#3776ab"
    }
  ],
  "is_draft": false
}
```

#### Pagination Object Structure
```json
{
  "pagination": {
    "total": 50,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

### Authentication Examples

#### Successful Authentication
```bash
# Request with valid API key
curl -H "X-API-Key: hogehoge" \
     "http://127.0.0.1:5000/api/v1/articles/latest"

# Response: 200 OK with article data
```

#### Authentication Errors
```bash
# Request without API key
curl "http://127.0.0.1:5000/api/v1/articles/latest"

# Response: 401 Unauthorized
{
  "status": "error",
  "message": "APIキーが必要です。ヘッダー「X-API-Key」にAPIキーを指定してください。"
}

# Request with invalid API key
curl -H "X-API-Key: invalid-key" \
     "http://127.0.0.1:5000/api/v1/articles/latest"

# Response: 403 Forbidden
{
  "status": "error",
  "message": "APIキーが無効です。"
}
```

### API Features

#### Japanese Time Zone Support
- All datetime fields automatically converted to JST (Japan Standard Time)
- Format: `YYYY-MM-DD HH:MM:SS` (24-hour format)
- Database stores UTC, API returns JST

#### Content Filtering
- **Draft Exclusion**: Only published articles (is_draft=false) are returned
- **Author Filtering**: Filter articles by specific author
- **Tag Filtering**: Filter articles by tag name
- **Search Integration**: API filters work with existing search logic

#### Data Security
- **User Privacy**: No exposure of user passwords or sensitive data
- **Content Validation**: All content properly escaped and validated
- **Error Handling**: Comprehensive error handling with meaningful messages

#### Performance Optimization
- **Pagination Support**: Efficient database queries with LIMIT/OFFSET
- **Query Optimization**: Optimized SQL queries with proper joins
- **Response Caching**: Browser-compatible caching headers
- **Rate Limiting**: Configurable via API key management

### Integration Examples

#### JavaScript/Node.js
```javascript
const apiKey = 'your-api-key';
const baseUrl = 'http://127.0.0.1:5000/api/v1';

async function getLatestArticles(limit = 10) {
    const response = await fetch(`${baseUrl}/articles/latest?limit=${limit}`, {
        headers: {
            'X-API-Key': apiKey
        }
    });
    return await response.json();
}
```

#### Python
```python
import requests

api_key = 'your-api-key'
base_url = 'http://127.0.0.1:5000/api/v1'

def get_latest_articles(limit=10):
    response = requests.get(
        f'{base_url}/articles/latest',
        headers={'X-API-Key': api_key},
        params={'limit': limit}
    )
    return response.json()
```

#### cURL Scripts
```bash
#!/bin/bash
API_KEY="your-api-key"
BASE_URL="http://127.0.0.1:5000/api/v1"

# Get latest 5 articles
curl -H "X-API-Key: $API_KEY" "$BASE_URL/articles/latest?limit=5"

# Get articles by specific author
curl -H "X-API-Key: $API_KEY" "$BASE_URL/articles/latest?author=user123"

# Get popular articles
curl -H "X-API-Key: $API_KEY" "$BASE_URL/articles/popular"
```

### Deployment Considerations

#### Production Environment Variables
```bash
# Set strong API key for production
export API_KEY="$(openssl rand -base64 32)"

# Optional: Custom header name for security
export API_KEY_HEADER_NAME="X-Knowledge-Auth"

# Optional: System title for API responses
export SYSTEM_TITLE="Corporate Knowledge Base"
```

#### Security Best Practices
- **Strong API Keys**: Use cryptographically secure random keys
- **HTTPS Only**: Deploy with SSL/TLS in production
- **Rate Limiting**: Implement rate limiting per API key
- **Audit Logging**: Monitor API access via audit logs
- **Regular Rotation**: Rotate API keys periodically

#### Monitoring and Analytics
- **Access Logs**: Track API usage patterns
- **Error Monitoring**: Monitor 4xx and 5xx responses
- **Performance Metrics**: Track response times and query performance
- **Usage Analytics**: Analyze most accessed content via API

### API Development and Testing

#### Local Development
```bash
# Start development server with API key
export API_KEY="development-key-123"
python app.py

# Test API endpoints
curl -H "X-API-Key: development-key-123" "http://127.0.0.1:5000/api/v1/articles/latest"
```

#### Testing Script
A test script `test_with_api_key.py` is provided for API development:
```bash
python test_with_api_key.py
```

#### Future API Enhancements
- **Versioning**: Support for multiple API versions (/api/v2/)
- **Content Creation**: POST endpoints for creating articles via API
- **Webhook Support**: Event notifications for content changes
- **GraphQL**: Alternative query interface for complex data needs
- **Real-time Updates**: WebSocket support for live content updates