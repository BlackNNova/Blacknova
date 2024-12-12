# Writers Management System

A Flask-based web application for managing writers and their assignments.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` with your configuration

4. Initialize the database:
```bash
python init_db.py
```

5. Run the application:
```bash
flask run
```

6. Access the application:
- Open http://localhost:5000 in your web browser
- Register an admin account at http://localhost:5000/auth/signup

## Features

- Admin Dashboard
- Writer Management
- Order Assignment
- Order Status Tracking
- File Management
- Invoice Generation

## Project Structure

```
writers_management_system/
├── app/
│   ├── models/         # Database models
│   ├── templates/      # HTML templates
│   ├── utils/          # Utility functions
│   └── views/          # Route handlers
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration
└── run.py            # Application entry point
```
