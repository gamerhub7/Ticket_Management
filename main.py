from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from database import engine, get_db, Base
from models import User, Project, Ticket, OTPCode, Notification
from security import create_access_token, get_current_user, verify_access_token

from pydantic import BaseModel, EmailStr
import random

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TicketFlow API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ticketflow-dashboard-rgr7t1uf.sites.blink.new"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Super-user password (store in env in production)
SUPER_USER_PASSWORD = "admin123"

# ----------------- Pydantic Schemas -----------------
class UserCreate(BaseModel):
    email: EmailStr

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    code: str

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None

class SuperUserVerify(BaseModel):
    password: str

# ----------------- Helper Functions -----------------
def generate_otp():
    return str(random.randint(100000, 999999))

def create_notification(db: Session, message: str, ticket_id: int = None, project_id: int = None):
    notification = Notification(
        message=message,
        ticket_id=ticket_id,
        project_id=project_id
    )
    db.add(notification)
    db.commit()

# ----------------- Auth Endpoints -----------------
@app.post("/api/auth/send-otp")
def send_otp(request: OTPRequest, db: Session = Depends(get_db)):
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    otp = OTPCode(email=request.email, code=code, expires_at=expires_at)
    db.add(otp)
    db.commit()
    print(f"OTP for {request.email}: {code}")
    return {"message": "OTP sent successfully", "dev_code": code}

@app.post("/api/auth/verify-otp")
def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    otp = db.query(OTPCode).filter(
        OTPCode.email == request.email,
        OTPCode.code == request.code,
        OTPCode.used == False,
        OTPCode.expires_at > datetime.utcnow()
    ).first()
    if not otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    otp.used = True
    db.commit()
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(email=request.email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    token = create_access_token({"user_id": user.id, "email": user.email})
    
    return {
        "message": "Login successful",
        "user": {"id": user.id, "email": user.email},
        "token": token
    }

# ----------------- Project Endpoints -----------------
@app.get("/api/projects")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "created_by": p.created_by,
            "creator_email": p.creator.email if p.creator else None,
            "ticket_count": len(p.tickets)
        }
        for p in projects
    ]

@app.post("/api/projects")
def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_project = Project(
        title=project.title,
        description=project.description,
        created_by=current_user["user_id"]
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    create_notification(db, f"Project '{project.title}' created", project_id=new_project.id)
    
    return {"id": new_project.id, "title": new_project.title, "description": new_project.description}

# ----------------- Ticket Endpoints -----------------
@app.post("/api/projects/{project_id}/tickets")
def create_ticket(
    project_id: int,
    ticket: TicketCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    max_order = db.query(Ticket).filter(
        Ticket.project_id == project_id, Ticket.status == ticket.status
    ).count()
    
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        order=max_order,
        project_id=project_id,
        created_by=current_user["user_id"],
        updated_by=current_user["user_id"]
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    create_notification(db, f"Ticket '{ticket.title}' created in {project.title}", ticket_id=new_ticket.id, project_id=project_id)
    
    return {"id": new_ticket.id, "title": new_ticket.title, "status": new_ticket.status}

# ----------------- Health Check -----------------
@app.get("/")
def health_check():
    return {"status": "ok", "message": "TicketFlow API is running!"}
