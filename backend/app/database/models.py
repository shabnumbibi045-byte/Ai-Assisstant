"""Database Models - SQLAlchemy models for all entities."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model with authentication support."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    preferences = Column(JSON, default=dict)
    
    # Relationships
    permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")


class UserPermission(Base):
    """User permissions model."""
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module = Column(String(50), nullable=False)  # banking, travel, etc.
    permission_type = Column(String(50), nullable=False)  # read, write, execute
    granted = Column(Boolean, default=False)
    granted_at = Column(DateTime)
    granted_by = Column(String(255))
    
    # Relationships
    user = relationship("User", back_populates="permissions")


class ResearchProject(Base):
    """Research project model."""
    __tablename__ = "research_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    project_id = Column(String(255), unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")  # active, completed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column(JSON)


class TravelBooking(Base):
    """Travel booking metadata."""
    __tablename__ = "travel_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    booking_id = Column(String(255), unique=True, index=True)
    booking_type = Column(String(50))  # flight, hotel, car
    origin = Column(String(255))
    destination = Column(String(255))
    departure_date = Column(DateTime)
    return_date = Column(DateTime)
    status = Column(String(50))  # confirmed, cancelled, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    booking_data = Column(JSON)


class BankingMetadata(Base):
    """Banking account metadata (NO SENSITIVE DATA)."""
    __tablename__ = "banking_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    account_id = Column(String(255), index=True)
    account_type = Column(String(50))  # checking, savings, credit
    account_nickname = Column(String(255))
    last_synced = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON)


class AuditLog(Base):
    """Audit log for sensitive operations."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id_fk = Column(Integer, ForeignKey("users.id"))
    user_id = Column(String(255), index=True, nullable=False)
    action = Column(String(100), nullable=False)
    module = Column(String(50))
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    status = Column(String(50))  # success, failure
    ip_address = Column(String(50))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    extra_data = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Document(Base):
    """Uploaded documents."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), index=True, nullable=False)
    document_id = Column(String(255), unique=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    chunks_count = Column(Integer)
    status = Column(String(50), default="processing")  # processing, indexed, failed
    extra_data = Column(JSON)
    
    # Relationships
    owner = relationship("User", back_populates="documents")
