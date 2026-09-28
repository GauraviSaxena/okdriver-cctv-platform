'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Fix Leaflet SSR Window Error
const MapComponent = dynamic(() => import('./components/MapComponent'), {
  ssr: false,
  loading: () => (
    <div className="h-[450px] bg-slate-900 rounded-lg flex items-center justify-center text-slate-400">
      Loading GIS Map Network...
    </div>
  ),
});

export default function Home() {
  const [vehicleNo, setVehicleNo] = useState('GJ01XX0001');
  const [routeHistory, setRouteHistory] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState('Connecting...');

  // Trace Route Handler
  const handleTraceRoute = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!vehicleNo) return;

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/trace/${vehicleNo}`);
      if (res.ok) {
        const data = await res.json();
        setRouteHistory(Array.isArray(data) ? data : data.trace || data.data || []);
      }
    } catch (err) {
      console.error("Trace Route Error:", err);
    }
  };

  useEffect(() => {
    // 1. Fetch Initial Camera List
    fetch('http://127.0.0.1:8000/api/v1/cameras')
      .then((res) => res.json())
      .then((data) => setCameras(data))
      .catch((err) => console.log('Camera fetch error:', err));

    // 2. WebSocket for Live Alerts with Auto-Reconnect
    let ws: WebSocket | null = null;
    let timer: NodeJS.Timeout;

    const connectWS = () => {
      ws = new WebSocket('ws://127.0.0.1:8000/ws');

      ws.onopen = () => {
        setWsStatus('Connected (Live)');
      };

      ws.onmessage = (event) => {
        try {
          const alertData = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
          setAlerts((prev) => [alertData, ...prev]);
        } catch (err) {
          console.error("WS Parse Error:", err);
        }
      };

      ws.onerror = () => {
        setWsStatus('Disconnected');
      };

      ws.onclose = () => {
        setWsStatus('Disconnected - Retrying...');
        timer = setTimeout(connectWS, 3000);
      };
    };

    connectWS();

    return () => {
      if (ws) ws.close();
      clearTimeout(timer);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white p-4 font-sans">
      {/* Top Navigation Bar */}
      <header className="flex justify-between items-center bg-slate-900 p-4 rounded-xl border border-slate-800 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-red-500 text-xl font-bold">((•))</span>
          <h1 className="text-xl font-bold tracking-wide">
            okDriver <span className="text-sky-400">CCTV Analytics Platform</span>
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${
            wsStatus.includes('Connected') && !wsStatus.includes('Retrying')
              ? 'bg-emerald-950 text-emerald-400 border-emerald-800' 
              : 'bg-red-950 text-red-400 border-red-800'
          }`}>
            WS Status: {wsStatus}
          </span>
          <button 
            onClick={() => window.location.reload()}
            className="bg-sky-600 hover:bg-sky-500 text-white text-xs px-3 py-1.5 rounded-lg font-medium transition cursor-pointer"
          >
            Refresh Cameras
          </button>
        </div>
      </header>

      {/* Main Dashboard Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        
        {/* Left 2/3 Column: Search & GIS Map */}
        <div className="lg:col-span-2 space-y-4">
          <form onSubmit={handleTraceRoute} className="flex gap-2">
            <input
              type="text"
              value={vehicleNo}
              onChange={(e) => setVehicleNo(e.target.value)}
              placeholder="Enter Vehicle Plate Number..."
              className="bg-slate-900 text-white p-3 px-4 rounded-xl border border-slate-800 w-full focus:outline-none focus:border-sky-500"
            />
            <button 
              type="submit"
              className="bg-sky-500 hover:bg-sky-600 text-white px-6 py-3 rounded-xl font-semibold whitespace-nowrap transition cursor-pointer"
            >
              Trace Route
            </button>
          </form>

          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <h2 className="text-md font-semibold mb-3 text-slate-300">
              Live GIS Camera Network & Movement
            </h2>
            <div className="rounded-lg overflow-hidden border border-slate-800">
              <MapComponent cameras={cameras} routeHistory={routeHistory} />
            </div>
          </div>
        </div>

        {/* Right 1/3 Column: Real-Time Critical Alerts Feed */}
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-800 flex flex-col h-[580px]">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-red-500">🛡️</span>
            <h2 className="text-md font-bold text-red-400">
              Real-time Critical Alerts ({alerts.length})
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {alerts.length === 0 ? (
              <div className="text-slate-500 text-sm text-center py-10">
                Listening for live camera triggers...
              </div>
            ) : (
              alerts.map((alert, idx) => {
                const plate = alert.identifier || alert.plate_number || alert.vehicle_no || alert.plate || 'GJ01XX0001';
                const cam = alert.camera_id || alert.location || alert.cam || 'C001';
                const conf = alert.confidence ? `(Conf: ${alert.confidence})` : '';

                return (
                  <div 
                    key={idx} 
                    className="bg-slate-950 p-3 rounded-lg border border-red-900/40 border-l-4 border-l-red-500"
                  >
                    <div className="flex justify-between items-start text-xs mb-1">
                      <span className="font-bold text-red-400 tracking-wider">
                        CRITICAL_WATCHLIST_MATCH
                      </span>
                      <span className="text-slate-500">Just Now</span>
                    </div>
                    <div className="text-sm font-semibold text-white">
                      Plate: {plate}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      Detected at: {cam} {conf}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>
    </div>
  );
}