# Django User Panel Application

A modern, responsive Django web application with user authentication, profile management, and AI agent configuration.

## Features

- ✅ Email-based user authentication (registration & login)
- ✅ Responsive side navigation menu
- ✅ User profile management (name, profile picture, mobile number)
- ✅ Dashboard with statistics and quick actions
- ✅ AI agent configuration with Facebook Page ID and system prompt
- ✅ Auto-generated webhook URL with copy functionality
- ✅ Modern UI with Tailwind CSS
- ✅ SQLite3 database
- ✅ Mobile-responsive design

## Tech Stack

- **Backend**: Django 6.0.2
- **Database**: SQLite3
- **Frontend**: HTML, Tailwind CSS (CDN)
- **Image Handling**: Pillow

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Start Development Server

```bash
python manage.py runserver
```

### 5. Access the Application

- **Main URL**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/login/
- **Register**: http://127.0.0.1:8000/register/

## Usage

### Registration
1. Navigate to the registration page
2. Enter your email and password
3. Click "Create Account"
4. You'll be automatically logged in and redirected to the dashboard

### Profile Management
1. Click "Profile" in the sidebar
2. Upload a profile picture
3. Enter your name and mobile number
4. Click "Save Changes"

### AI Agent Configuration
1. Click "AI Agent" in the sidebar
2. Enter your Facebook Page ID
3. Enter your AI system prompt
4. Your webhook URL will be displayed: `https://ftn8nbd.onrender.com/webhook-test/{your-email-prefix}`
5. Click "Copy URL" to copy the webhook URL to clipboard

## Webhook URL Format

The webhook URL is automatically generated based on your email address:

- **Format**: `https://ftn8nbd.onrender.com/webhook-test/{email_prefix}`
- **Example**: For email `joysd2005@gmail.com`, the webhook URL will be:
  ```
  https://ftn8nbd.onrender.com/webhook-test/joysd2005
  ```

## Project Structure

```
userpanel/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── userpanel_project/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/
│       ├── base.html
│       └── accounts/
│           ├── register.html
│           ├── login.html
│           ├── dashboard.html
│           ├── profile.html
│           └── ai_agent.html
├── static/
└── media/
```

## Features in Detail

### Authentication System
- Custom user model with email as username
- Secure password hashing
- Login/logout functionality
- Protected views with login_required decorator

### Responsive Design
- Mobile-first approach
- Hamburger menu for mobile devices
- Responsive grid layouts
- Tailwind CSS for modern styling

### User Profile
- Profile picture upload with preview
- Personal information management
- One-to-one relationship with User model

### AI Agent Configuration
- Facebook Page ID storage
- AI system prompt customization
- Auto-generated webhook URL
- Copy to clipboard functionality

## Database Models

### CustomUser
- Email (unique, used for login)
- Password (hashed)

### UserProfile
- User (OneToOne)
- Name
- Profile Picture
- Mobile Number

### AIAgentConfig
- User (OneToOne)
- Facebook Page ID
- System Prompt

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files (for production)
```bash
python manage.py collectstatic
```

## License

This project is open source and available for use.

## Support

For issues or questions, please refer to the walkthrough documentation.
