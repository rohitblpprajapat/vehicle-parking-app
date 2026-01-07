# Vehicle Parking Management System

A comprehensive multi-user web application for managing parking lots, parking spots, and vehicle reservations. The system provides role-based access with separate interfaces for regular users and administrators.

## 🚀 Features

### User Features

- **User Registration & Authentication**: Secure user registration and login system
- **Browse Parking Lots**: View available parking lots with real-time availability
- **Spot Reservation**: Reserve parking spots with time-based booking
- **Reservation Management**: View, modify, and cancel reservations
- **Cost Calculation**: Automatic pricing based on hourly rates and duration
- **User Dashboard**: Personal dashboard with reservation history and analytics
- **Profile Management**: Update personal information and change passwords

### Admin Features

- **Admin Dashboard**: Comprehensive overview of the parking system
- **Parking Lot Management**: Create, edit, and delete parking lots
- **Spot Management**: Manage individual parking spots within lots
- **User Management**: View and manage user accounts
- **Reservation Oversight**: Monitor all reservations across the system
- **Analytics & Reports**: Revenue tracking, occupancy statistics, and performance metrics
- **Real-time Monitoring**: Live updates on parking availability and usage

### Technical Features

- **Redis Caching**: High-performance caching for improved response times
- **Real-time Updates**: Live data synchronization across the application
- **Responsive Design**: Mobile-friendly interface
- **Role-based Access Control**: Secure separation of user and admin functionalities
- **API-first Architecture**: RESTful API design for scalability

## 🛠️ Tech Stack

### Backend

- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **Flask-Security-Too**: Authentication and authorization
- **Flask-Mail**: Email services
- **Celery**: Background task queue
- **Redis**: Caching, session management, and message broker
- **SQLite**: Database (configurable to PostgreSQL/MySQL)

### Frontend

- **Vue.js 3**: Progressive JavaScript framework
- **Vue Router**: Client-side routing
- **Chart.js**: Data visualization for analytics
- **Vite**: Build tool and development server

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 16+**
- **Redis Server** (for caching)
- **Git**

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/vehicle-parking-app.git
cd vehicle-parking-app
```

### 2. Backend Setup

#### Create and activate a virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Python dependencies:

```bash
pip install -r requirements.txt
```

#### Set up environment variables:

Create a `.env` file in the root `vehicle-parking-app` directory (or inside `backend/`). You can copy the example below:

```bash
# Security
SECRET_KEY="your-secret-key"
SECURITY_PASSWORD_SALT="your-password-salt"

# Database
DATABASE_URL="sqlite:///app.db"

# Redis & Celery
REDIS_URL="redis://localhost:6379/0"
CELERY_BROKER_URL="redis://localhost:6379/1"
CELERY_RESULT_BACKEND="redis://localhost:6379/1"

# Email (Optional - for reports)
MAIL_USERNAME="your-email@gmail.com"
MAIL_PASSWORD="your-app-password"
```

#### Initialize the database:

```bash
python app.py
```

### 3. Frontend Setup

#### Navigate to frontend directory:

```bash
cd ../frontend
```

#### Install Node.js dependencies:

```bash
npm install
```

### 4. Redis Setup

#### Install and start Redis:

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS (with Homebrew):**

```bash
brew install redis
brew services start redis
```

**Windows:**
Download and install from the official Redis website or use WSL.

## 🐳 Docker Setup (Recommended)

Run the entire application stack (Frontend, Backend, Redis, Celery) with a single command:

```bash
docker-compose up --build
```
- Access Frontend: `http://localhost:5173`
- Access Backend: `http://localhost:5000`

If you prefer manual setup, follow the steps below.

## 🏃‍♂️ Manual Setup & Running

### 1. Start Redis (if not running as a service):

```bash
redis-server
```

### 2. Start the Backend:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend will run on `http://localhost:5000`

### 3. Start Celery Worker (Background Tasks):

Open a new terminal:

```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

### 4. Start the Frontend:

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:5173`

## 🔑 Default Login Credentials

The application creates default accounts on first run:

### Admin Account

- **Email**: admin@example.com
- **Password**: admin123

### Test User Account

- **Email**: user@example.com
- **Password**: user123

## 📁 Project Structure

```
vehicle-parking-app/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── models.py           # Database models
│   ├── api_routes.py       # API endpoints
│   ├── config.py           # Configuration settings
│   ├── redis_cache.py      # Caching utilities
│   ├── sec.py              # Security configuration
│   ├── initial_data.py     # Database initialization
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── views/          # Vue.js pages
│   │   ├── components/     # Reusable components
│   │   ├── router/         # Route configuration
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
└── README.md
```

## 🔧 Configuration

### Environment Variables

The application supports the following environment variables:

| Variable                 | Default                    | Description                |
| ------------------------ | -------------------------- | -------------------------- |
| `SECRET_KEY`             | Auto-generated             | Flask secret key           |
| `DATABASE_URL`           | `sqlite:///app.db`         | Database connection string |
| `REDIS_URL`              | `redis://localhost:6379/0` | Redis connection string    |
| `SECURITY_PASSWORD_SALT` | Auto-generated             | Password hashing salt      |
| `CELERY_BROKER_URL`      | `redis://localhost:6379/1` | Redis DB for Celery Broker |
| `CELERY_RESULT_BACKEND`  | `redis://localhost:6379/1` | Redis DB for Celery Results|
| `MAIL_USERNAME`          | None                       | SMTP Email Username        |
| `MAIL_PASSWORD`          | None                       | SMTP Email Password        |

### Database Configuration

By default, the application uses SQLite. For production, consider using PostgreSQL or MySQL:

```bash
export DATABASE_URL="postgresql://user:password@localhost/parking_db"
```

## 🧪 Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python app.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Building for Production

```bash
cd frontend
npm run build
```

## 📝 API Documentation

The application provides a RESTful API with the following main endpoints:

- `GET /api/v1/parking-lots` - List all parking lots
- `POST /api/v1/reservations` - Create a new reservation
- `GET /api/v1/reservations` - Get user reservations
- `GET /api/v1/admin/analytics` - Admin analytics (admin only)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**: Ensure Redis server is running
2. **Database Issues**: Delete `instance/app.db` and restart the backend
3. **Port Conflicts**: Check if ports 5000 (backend) and 5173 (frontend) are available
4. **CORS Issues**: Ensure the frontend is running on the expected port

### Getting Help

If you encounter any issues, please check the console logs for error messages and ensure all prerequisites are properly installed.
