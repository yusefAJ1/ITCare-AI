# ITCare AI

**ITCare AI** is a beginner-friendly IT support and asset management web application built with Python, FastAPI, HTML, CSS, and JavaScript.

## Features

- Manage IT assets: add, search, view, and delete assets.
- Create and manage IT support tickets.
- Update ticket statuses.
- Dashboard showing ticket statistics.
- Filter tickets by status and priority.
- Rule-based troubleshooting suggestions for common IT problems.
- REST API built with FastAPI.

## Technologies Used

- Python
- FastAPI
- Uvicorn
- HTML
- CSS
- JavaScript
- JSON

## How to Run

### 1. Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Start the API server

```powershell
python -m uvicorn api:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

### 3. Start the frontend

Open a second terminal in the project folder:

```powershell
python -m http.server 5500
```

Open the application:

http://127.0.0.1:5500

## Project Purpose

This project demonstrates practical skills in IT support workflows, asset management, REST API development, and frontend integration.

## Future Improvements

- Integrate a real AI model for troubleshooting.
- Add user authentication and role-based access.
- Use a database instead of JSON files.
- Add automated tests and deployment.

## Author

Software Engineering Graduate | Aspiring Software Developer and IT Support Professional
