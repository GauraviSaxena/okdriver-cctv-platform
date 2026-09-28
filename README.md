# okDriver - Integrated CCTV Monitoring & Real-Time Analytics Platform

A scalable prototype for a centralized CCTV monitoring, video analytics, and real-time alert platform built for **okDriver Smart Dashcams** / Gujarat Police Hackathon challenge.

---

## 🏗️ System Architecture Diagram

```mermaid
graph TD
    %% Source Layer
    subgraph Video_Sources [1. Video Ingestion & Camera Sources]
        C1[Camera C001 - Sabarmati Hwy]
        C2[Camera C002 - Chanakyapuri Circle]
        C3[Camera C003 - Naranpura Post]
    end

    %% Processing & Analytics Layer
    subgraph Analytics_Layer [2. AI Video Analytics Engine]
        ANPR[ANPR / Plate Recognition Engine]
        Video_Sources -->|RTSP / Stream Data| ANPR
    end

    %% Backend & Processing Layer
    subgraph Backend_Services [3. FastAPI Core Backend]
        API[FastAPI REST APIs]
        WS_Server[WebSocket Gateway]
        Watchlist_Engine[Watchlist Correlation Engine]
        
        ANPR -->|JSON Detection Event| API
        API --> Watchlist_Engine
        Watchlist_Engine -->|Real-time Alert Push| WS_Server
    end

    %% Storage Layer
    subgraph Data_Storage [4. Database Layer]
        DB[(PostgreSQL / SQLite Storage)]
        API <--> DB
        Watchlist_Engine <--> DB
    end

    %% Operator Dashboard Layer
    subgraph Frontend_Dashboard [5. Unified Operator Dashboard - Next.js]
        Map[Leaflet GIS Interactive Map]
        Alert_Panel[Real-time Critical Alerts Panel]
        Trace[ANPR Vehicle Movement History]
        
        WS_Server -->|Live WS Push| Alert_Panel
        API -->|Fetch Cameras & Trace| Map
        API -->|Fetch Route Path| Trace
    end
