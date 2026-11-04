# ITCare AI – IT Asset & Support Management System

**ITCare AI** is a web-based IT management application designed to help IT support teams manage company assets, track technical support tickets, monitor system activity, and access guided troubleshooting assistance.

This project was developed as a practical portfolio project to demonstrate skills in backend development, database management, API integration, and frontend development.

## Key Features

- **Asset Management:** Add, view, search, edit, and delete IT assets.
- **Ticket Management:** Create support tickets and track their status and priority.
- **Dashboard:** View key statistics about assets and support tickets.
- **Analytics:** Visualize ticket statuses and asset categories.
- **IT Assistant:** Access rule-based troubleshooting guidance for common IT problems, including network, printer, login, and computer performance issues.
- **Database:** Store application data using SQLite.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API |
| SQLite | Database |
| HTML | Frontend structure |
| CSS | User interface design |
| JavaScript | Frontend functionality |

## Project Structure

```text
ITCare-AI/
│
├── api.py
├── main.py
├── assets.json
├── requirements.txt
├── itcare.db
└── frontend/
    └── index.html
```

*Note: Adjust this structure to match the actual files and folders in the repository.*

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yusefAJ1/ITCare-AI.git
cd ITCare-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the backend

```bash
uvicorn api:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

## Project Purpose

The goal of ITCare AI is to provide a simple and practical solution for everyday IT support operations while demonstrating real-world software development skills.

## Developer

**Yousuf Mohammed Ahmed Aljatlawi**

Software Engineering Graduate | IT Support | Python & Backend Development

GitHub: [@yusefAJ1](https://github.com/yusefAJ1)

---

*Developed as a personal software engineering portfolio project.*