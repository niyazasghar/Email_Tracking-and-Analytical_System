import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import engine
from models import Base
from routers import (
    auth,
    Email_Tracking,
    Status_Management,
    Analytics_Dashboard,
    Automated_FollowUps,
    imap_sync,
    recruitment_dashboard, placement_dashboard
)
from routers.imap_sync import sync_emails

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Email Tracking & Analytics System")

# Mount static files for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates directory (we assume your login.html is in the templates folder)
templates = Jinja2Templates(directory="templates")

# Include our routers
app.include_router(auth.router)
app.include_router(Status_Management.router)
app.include_router(Analytics_Dashboard.router)
app.include_router(Automated_FollowUps.router)
app.include_router(Email_Tracking.router)
app.include_router(imap_sync.router)
app.include_router(recruitment_dashboard.router)
app.include_router(placement_dashboard.router)

# -------------------------------------------
# Frontend Routes
# -------------------------------------------

# Home route now loads login.html instead of index.html.
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login page route (optional redundancy if "/" always shows login)
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Student Dashboard (for normal students)
@app.get("/student-dashboard")
def student_dashboard(request: Request):
    return templates.TemplateResponse("recruitment_dashboard.html", {"request": request})

# Superuser Dashboard
@app.get("/superuser-dashboard")
def superuser_dashboard(request: Request):
    return templates.TemplateResponse("superuser_dashboard.html", {"request": request})

# Email Tracking page route
@app.get("/send-email")
def send_email(request: Request):
    return templates.TemplateResponse("email_tracking.html", {"request": request})

# Automatic Follow-up page route
@app.get("/followups")
def followups(request: Request):
    return templates.TemplateResponse("automatic_followup.html", {"request": request})

# Analytics page route
@app.get("/analytics")
def analytics(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

# Status Management page route
@app.get("/status-management")
def status_management(request: Request):
    return templates.TemplateResponse("status_management.html", {"request": request})

# Placed Student page route
@app.get("/placed-student")
def placed_student(request: Request):
    return templates.TemplateResponse("placed_student.html", {"request": request})

# Management Dashboard route (for adding company, event, placed student)
@app.get("/management-dashboard")
def management_dashboard(request: Request):
    return templates.TemplateResponse("management_dashboard.html", {"request": request})
@app.get("/superuser-dashboard")
def superuser_dashboard(request: Request):
    return templates.TemplateResponse("superuser_dashboard.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
