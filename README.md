# 🔗 LinkForge - URL Shortener

**Live Demo:** [Check it out here!](YOUR_LIVE_LINK_HERE) 🚀

A Flask-based URL shortener with user-specific namespaces and dynamic link management. Create custom short URLs that you can update anytime without breaking existing shares.

## ✨ Key Features

### 🎯 **Personal URL Namespaces**
Each user gets their own URL space - no more conflicts!
- **Traditional shorteners:** `/abc123` (first come, first served)
- **LinkForge:** `/username/project` (everyone can have their own `/portfolio` link)
- **Benefits:** Branded URLs, no collisions, professional appearance

### 🔄 **Dynamic Links**
The main innovation - change where your links go without breaking them:
- Create: `/alice/resume` → points to `portfolio-v1.pdf`
- Later update: `/alice/resume` → now points to `portfolio-v2.pdf`
- **Same link, different destination** - bookmarks and shares never break
- Perfect for portfolios, marketing campaigns, and evolving content

### 📊 **Click Analytics**
Track your link performance with detailed insights:
- **Total clicks** per link
- **Click timestamps** and patterns
- **Referrer tracking** (where clicks came from)
- **Export to CSV** for detailed analysis
- Privacy-focused (no personal data stored)

### 🔒 **Security Features**
Built with security in mind:
- **Password protection** for sensitive links (6-15 characters)
- **Link expiration** (1-7 days, weeks, months, or custom dates)
- **Secure authentication** with password hashing
- **Input validation** and SQL injection prevention
- **Session management** with secure cookies

### 📱 **QR Code System**
Visual sharing made easy:
- **Auto-generated QR codes** for every link
- **Expandable preview** - click to view large version
- **Download as PNG** with proper naming
- **Bulk download** multiple QR codes as ZIP
- Optimized for scanning with high contrast

### ⚡ **Bulk Operations**
Manage multiple links efficiently:
- **Select multiple links** with checkboxes
- **Bulk delete** selected links
- **Bulk CSV export** of analytics data
- **Bulk QR download** as ZIP archive

## 🏗️ **How It's Built**

### **Backend Architecture**
- **Flask Application Factory** - Modular, testable design
- **Blueprint Organization** - Separate modules for auth, links, and pages
- **PostgreSQL Database** - Reliable, scalable data storage
- **Request-scoped connections** - Efficient resource management

### **Security Implementation**
- **Werkzeug password hashing** - PBKDF2-SHA256 encryption
- **Parameterized SQL queries** - Injection attack prevention
- **CORS protection** - Cross-origin request security
- **Security headers** - XSS, clickjacking, and content sniffing protection

### **Database Design**
- **Users table** - Account management
- **Links table** - URL storage with namespacing
- **Clicks table** - Analytics and tracking
- **Proper relationships** and indexing for performance

## 🛠️ Tech Stack

- **Backend:** Flask (Python 3.11+)
- **Database:** PostgreSQL 13+
- **Frontend:** HTML5, CSS3, Minimal JavaScript
- **Security:** Flask-CORS, Werkzeug
- **QR Codes:** qrcode library with PIL
- **Deployment:** Gunicorn, Heroku/Render ready

## 🚀 Quick Start

1. **Clone and setup**
   ```bash
   git clone https://github.com/Yonko-luffy/LinkForge.git
   cd LinkForge
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   # Create .env file (see .env.example)
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:pass@localhost:5432/linkforge
   FLASK_ENV=development
   ```

3. **Run the application**
   ```bash
   python app.py
   # Visit http://localhost:5000
   ```

## 📁 Project Structure

```
LinkForge/
├── app.py                 # Application entry point
├── linkforge/            # Main package
│   ├── __init__.py       # App factory with security headers
│   ├── config.py         # Environment configuration
│   ├── models.py         # Database operations
│   ├── db_utils.py       # Connection management
│   ├── blueprints/       # Modular route organization
│   │   ├── auth.py       # User authentication
│   │   ├── links.py      # URL shortening & management
│   │   └── main.py       # Landing pages
│   ├── templates/        # Jinja2 HTML templates
│   └── static/          # CSS, JS, and assets
├── requirements.txt      # Python dependencies
└── .env.example         # Environment template
```

## 🎨 **User Experience**

1. **Register/Login** - Get your personal namespace
2. **Create links** - `yourname/portfolio`, `yourname/resume`, etc.
3. **Set options** - Password protection, expiration dates
4. **Track performance** - See clicks, referrers, export data
5. **Update anytime** - Change destinations without breaking links
6. **Share easily** - Copy links, download QR codes, bulk export

## 🔧 **Deployment**

Ready for production with:
- Environment-based configuration
- Production database support
- WSGI server compatibility (Gunicorn)
- Security headers and CORS
- Error handling and logging

## 📞 Contact

Built by **[Your Name]** 

Found a bug or have suggestions? Reach out:
- 📧 **Email:** [your.email@example.com] - Direct line for issues and feedback
- 💼 **LinkedIn:** [Your LinkedIn Profile] - Professional inquiries and connections
- 🐙 **GitHub:** [Your GitHub Profile] - Code discussions and contributions

---

*Clean Flask architecture showcasing backend development skills with modern security practices.*
