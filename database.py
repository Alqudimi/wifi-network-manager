from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    """Initialize database tables"""
    db.create_all()
    print("Database tables created successfully")

def reset_db():
    """Reset database - WARNING: This will delete all data"""
    db.drop_all()
    db.create_all()
    print("Database reset completed")
