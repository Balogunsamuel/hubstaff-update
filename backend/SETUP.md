# Hubstaff Clone Backend Setup Guide

## Environment Configuration

### 1. Basic Setup

Copy the `.env` file and configure the following variables:

```bash
# Database
SECRET_KEY="your-secret-key-here"
MONGO_URL="mongodb://localhost:27017"
DB_NAME="hubstaff_clone"

# Frontend URL (change for production)
FRONTEND_URL="http://localhost:3000"

# File Storage
STORAGE_TYPE="local"  # or "supabase"
UPLOAD_DIR="uploads"
MAX_FILE_SIZE="10485760"  # 10MB

# Admin Configuration
DEFAULT_ADMIN_EMAIL="admin@example.com"
DEFAULT_ADMIN_PASSWORD="admin123"

# Security
INVITATION_EXPIRE_DAYS="7"
ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

### 2. Email Configuration (Optional)

For sending invitation emails, configure SMTP settings:

```bash
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
SMTP_FROM_EMAIL="noreply@hubstaff-clone.com"
```

If not configured, invitations will be printed to console.

### 3. AWS S3 Configuration (Optional)

For cloud storage, configure Supabase Storage:

```bash
STORAGE_TYPE="supabase"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key"
SUPABASE_BUCKET="your-bucket-name"
```

## Database Setup

### Initial Setup

Run the database setup command to create the default admin user:

```bash
python -m management.admin setup-database
```

This will create:
- Default admin user with email from `DEFAULT_ADMIN_EMAIL`
- Password from `DEFAULT_ADMIN_PASSWORD` 

## Admin Management Commands

### Create Admin User

```bash
python -m management.admin create-admin \
    --email admin@example.com \
    --name "Admin User" \
    --password admin123 \
    --company "Your Company"
```

### Reset User Password

```bash
python -m management.admin reset-password \
    --email user@example.com \
    --password newpassword123
```

### List All Users

```bash
# List all users
python -m management.admin list-users

# Filter by role
python -m management.admin list-users --role admin
python -m management.admin list-users --role manager  
python -m management.admin list-users --role user
```

## File Storage

### Local Storage

Files are stored in the `uploads/` directory by default. The structure is:

```
uploads/
├── screenshots/
│   └── {user_id}/
│       └── {filename}
└── avatars/
    └── {user_id}/
        └── {filename}
```

Files are served at `/uploads/{path}` endpoint.

### Cloud Storage

For production, configure AWS S3 or other cloud storage providers.

## Running the Server

```bash
# Development
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Production  
uvicorn server:app --host 0.0.0.0 --port 8001
```

## API Documentation

Once running, API documentation is available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Security Notes

1. **Change default credentials** in production
2. **Use strong SECRET_KEY** for JWT tokens
3. **Configure HTTPS** for production deployments
4. **Set up proper CORS** origins instead of allowing all origins
5. **Use environment variables** for sensitive configuration
6. **Backup your database** regularly

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MongoDB is running
   - Check `MONGO_URL` in `.env`

2. **File Upload Errors**
   - Check `UPLOAD_DIR` permissions
   - Verify `MAX_FILE_SIZE` setting

3. **Email Not Sending**
   - Check SMTP configuration
   - Verify credentials and app passwords

4. **Admin User Issues**
   - Use admin management commands
   - Check database for existing users

### Logs

Check server logs for detailed error information:

```bash
tail -f server.log
```