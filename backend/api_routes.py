from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime

from database import get_db
import models, schemas

router = APIRouter(prefix="/api/v1", tags=["Analytics Platform"])

@router.post("/cameras", response_model=schemas.CameraResponse)
def create_camera(camera: schemas.CameraCreate, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.id == camera.id).first()
    if db_camera:
        raise HTTPException(status_code=400, detail="Camera ID already exists")
    
    new_camera = models.Camera(**camera.model_dump())
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera

@router.get("/cameras", response_model=List[schemas.CameraResponse])
def list_cameras(
    status: models.CameraStatus = None, 
    department: str = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Camera)
    if status:
        query = query.filter(models.Camera.status == status)
    if department:
        query = query.filter(models.Camera.department == department)
    return query.all()

@router.post("/watchlist")
def add_to_watchlist(entry: schemas.WatchlistCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Watchlist).filter(models.Watchlist.identifier == entry.identifier).first()
    if existing:
        raise HTTPException(status_code=400, detail="Identifier already in watchlist")
    
    watchlist_entry = models.Watchlist(**entry.model_dump())
    db.add(watchlist_entry)
    db.commit()
    db.refresh(watchlist_entry)
    return watchlist_entry

@router.post("/events/ingest")
async def ingest_ai_event(payload: schemas.EventIngest, db: Session = Depends(get_db)):
    from main import manager
    camera = db.query(models.Camera).filter(models.Camera.id == payload.camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Unknown Camera Source")

    event_id = f"EVT-{uuid.uuid4().hex[:8]}"
    detection_event = models.DetectionEvent(
        id=event_id,
        camera_id=payload.camera_id,
        identifier=payload.identifier,
        confidence=payload.confidence,
        vehicle_type=payload.vehicle_type,
        bounding_box=payload.bounding_box
    )
    db.add(detection_event)
    
    await manager.broadcast({
        "type": "NEW_DETECTION",
        "data": {
            "event_id": event_id,
            "camera_id": payload.camera_id,
            "identifier": payload.identifier,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    })

    watchlist_match = db.query(models.Watchlist).filter(
        models.Watchlist.identifier == payload.identifier
    ).first()

    alert_data = None
    if watchlist_match:
        alert_id = f"ALT-{uuid.uuid4().hex[:8]}"
        new_alert = models.Alert(
            id=alert_id,
            event_id=event_id,
            camera_id=payload.camera_id,
            identifier=payload.identifier,
            severity=models.AlertSeverity.CRITICAL,
            status=models.AlertStatus.NEW
        )
        db.add(new_alert)
        db.commit()

        alert_data = {
            "alert_id": alert_id,
            "identifier": payload.identifier,
            "category": watchlist_match.category,
            "camera_name": camera.name,
            "latitude": camera.latitude,
            "longitude": camera.longitude
        }

        await manager.broadcast({
            "type": "WATCHLIST_ALERT",
            "data": alert_data
        })
    else:
        db.commit()

    return {
        "status": "processed",
        "event_id": event_id,
        "watchlist_match": bool(watchlist_match),
        "alert": alert_data
    }

@router.get("/entities/trace")
def trace_entity_movement(identifier: str, db: Session = Depends(get_db)):
    events = db.query(models.DetectionEvent)\
               .filter(models.DetectionEvent.identifier == identifier)\
               .order_by(models.DetectionEvent.timestamp.asc())\
               .all()

    route = []
    for evt in events:
        cam = evt.camera
        route.append({
            "timestamp": evt.timestamp.isoformat(),
            "camera_id": cam.id,
            "camera_name": cam.name,
            "latitude": cam.latitude,
            "longitude": cam.longitude
        })

    return {
        "identifier": identifier,
        "total_detections": len(route),
        "route_history": route
    }