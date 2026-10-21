import uuid
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.db import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    severity = Column(String, index=True) # low, medium, high, critical
    alert_type = Column(String, index=True) # ddos, brute_force, anomaly, etc.
    source_ip = Column(String, index=True)
    dest_ip = Column(String)
    status = Column(String, default="new") # new, acknowledged, closed
    details = Column(JSON) # raw packet data or ML score
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)