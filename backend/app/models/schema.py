from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class HCP(Base):
    """
    Healthcare Professional (Doctor) Profile Table
    """
    __tablename__ = "hcp"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialty = Column(String(150), nullable=False, index=True)
    hospital = Column(String(255), nullable=False, index=True)
    contact_email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="hcp", cascade="all, delete-orphan")


class Interaction(Base):
    """
    Core HCP Interaction Log Table (populated by LangGraph AI)
    """
    __tablename__ = "interaction"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcp.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(100), default="Meeting")
    interaction_date = Column(Date, nullable=False, index=True)
    interaction_time = Column(String(20), default="12:00")
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(Text, nullable=True)
    samples_distributed = Column(Text, nullable=True)
    observed_sentiment = Column(String(50), default="Neutral")  # Positive, Neutral, Negative
    outcomes = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    status = Column(String(50), default="Draft", index=True)  # Draft, Confirmed, Saved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("HCP", back_populates="interactions")
    follow_ups = relationship("FollowUp", back_populates="interaction", cascade="all, delete-orphan")


class FollowUp(Base):
    """
    Follow-up Actions & Reminders Table
    """
    __tablename__ = "follow_up"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interaction.id", ondelete="CASCADE"), nullable=False, index=True)
    hcp_id = Column(Integer, ForeignKey("hcp.id", ondelete="CASCADE"), nullable=False, index=True)
    action_description = Column(Text, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), default="Pending")  # Pending, Completed, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interaction = relationship("Interaction", back_populates="follow_ups")
    hcp = relationship("HCP", back_populates="follow_ups")


class AuditLog(Base):
    """
    Immutable Audit Trail of all AI and Manual Modifications
    """
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(100), nullable=False)  # e.g., Interaction, HCP
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(100), nullable=False)  # e.g., AI_POPULATE, AI_EDIT, AI_SAVE
    changes = Column(Text, nullable=True)  # JSON representation of changes
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ChatHistory(Base):
    """
    Conversation Transcript between User and AI Assistant
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    sender = Column(String(50), nullable=False)  # user, ai, system
    message = Column(Text, nullable=False)
    tool_called = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
