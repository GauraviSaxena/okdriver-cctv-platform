from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from models import CameraStatus, AlertSeverity, AlertStatus

class CameraCreate(BaseModel):
    id: str
    name: str
    department: str
    latitude: float
    longitude: float
    camera_type: str
    source_protocol: str
    stream_endpoint: str
    zone: str

class CameraResponse(CameraCreate):
    status: CameraStatus
    last_heartbeat: datetime

    class Config:
        from_attributes = True

class EventIngest(BaseModel):
    camera_id: str
    identifier: str
    confidence: float
    vehicle_type: str
    bounding_box: Optional[Any] = None

class WatchlistCreate(BaseModel):
    id: str
    identifier: str
    category: str
    notes: Optional[str] = None