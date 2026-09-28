'use client';

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Leaflet Default Marker Icon Fix for Next.js
const customIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function MapComponent({ cameras = [], routeHistory = [] }: any) {
  const centerPosition: [number, number] = [23.0225, 72.5714]; // Ahmedabad Default

  const routePositions: [number, number][] = (routeHistory || [])
    .map((item: any) => {
      const lat = parseFloat(item.latitude || item.lat);
      const lng = parseFloat(item.longitude || item.lng || item.lon);
      return !isNaN(lat) && !isNaN(lng) ? ([lat, lng] as [number, number]) : null;
    })
    .filter((pos): pos is [number, number] => pos !== null);

  return (
    <div style={{ height: '450px', width: '100%', position: 'relative' }}>
      <MapContainer 
        center={centerPosition} 
        zoom={12} 
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%', zIndex: 1 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Render Camera Markers */}
        {(cameras || []).map((cam: any, idx: number) => {
          const lat = parseFloat(cam.latitude || cam.lat);
          const lng = parseFloat(cam.longitude || cam.lng);
          if (isNaN(lat) || isNaN(lng)) return null;

          return (
            <Marker key={cam.id || idx} position={[lat, lng]} icon={customIcon}>
              <Popup>
                <b>Camera ID:</b> {cam.id || cam.camera_id}<br />
                <b>Location:</b> {cam.location || cam.name || 'GIS Node'}
              </Popup>
            </Marker>
          );
        })}

        {/* Render Route Polyline */}
        {routePositions.length > 0 && (
          <>
            <Polyline positions={routePositions} color="#0284c7" weight={5} opacity={0.8} />
            {routePositions.map((pos, idx) => (
              <Marker key={`route-${idx}`} position={pos} icon={customIcon}>
                <Popup>Trace Waypoint #{idx + 1}</Popup>
              </Marker>
            ))}
          </>
        )}
      </MapContainer>
    </div>
  );
}