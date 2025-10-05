TicketFlow Dashboard - Backend 🚀

Welcome to the TicketFlow Dashboard backend! This project is a FastAPI-based backend for managing projects, tickets, notifications, and super-user features. It’s built to be simple, clean, and easy to connect with your frontend.

Think of this as the “engine room” of your project management app.



What This Project Does

TicketFlow backend lets you:

Authenticate users via email OTP

Create and manage projects

Create, update, and move tickets between columns

Send notifications for activity updates

Enable super-user mode for admins

Store all data in a SQL database

Basically, it’s a full-featured backend for a modern project management dashboard.

Tech Stack

Python 3.13+

FastAPI – The web framework

SQLAlchemy – Database ORM

SQLite – Simple file-based database

JWT (via python-jose) – For authentication

Email-validator & Python-dotenv – For OTP and config

Uvicorn – ASGI server

Getting Started
1. Clone the Repository
git clone https://github.com/gamerhub7/Ticket_Management.git
cd Ticket_Management/backend

2. Create a Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

Running the Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000


Visit http://localhost:8000 → Should return a simple health check:

{"status": "ok", "message": "TicketFlow API is running!"}


Visit http://localhost:8000/docs → Interactive API docs for testing all endpoints. 