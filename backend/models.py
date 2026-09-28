from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
import enum
import datetime

class CameraStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"

class AlertSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"

class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    camera_type = Column(String)
    source_protocol = Column(String)
    stream_endpoint = Column(String)
    status = Column(Enum(CameraStatus), default=CameraStatus.ONLINE)
    last_heartbeat = Column(DateTime, default=datetime.datetime.utcnow)
    zone = Column(String)

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(String, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True)
    category = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(String, primary_key=True, index=True)
    camera_id = Column(String, ForeignKey("cameras.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    identifier = Column(String, index=True)
    confidence = Column(Float)
    vehicle_type = Column(String)
    bounding_box = Column(JSON)

    camera = relationship("Camera")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("detection_events.id"))
    camera_id = Column(String, ForeignKey("cameras.id"))
    identifier = Column(String)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.HIGH)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    camera = relationship("Camera")
    event = relationship("DetectionEvent")