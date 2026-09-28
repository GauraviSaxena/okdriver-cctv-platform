import requests
import time
import random

API_URL = "http://127.0.0.1:8000/api/v1/trigger_alert"

CAMERAS = ["C001", "C002", "C003"]
ALERT_TYPES = ["Overspeeding", "No Helmet", "Triple Riding", "Red Light Violation"]

print("🚀 Alert Simulator Started... Sending alerts to Backend every 3 seconds.\n")

alert_id = 100

while True:
    alert_payload = {
        "id": f"ALT-{alert_id}",
        "camera_id": random.choice(CAMERAS),
        "vehicle_no": f"GJ01XX{random.randint(1000, 9999)}",
        "type": random.choice(ALERT_TYPES),
        "timestamp": time.strftime("%I:%M:%S %p"),
        "severity": random.choice(["HIGH", "MEDIUM", "CRITICAL"])
    }

    try:
        response = requests.post(API_URL, json=alert_payload)
        if response.status_code == 200:
            print(f"✅ Alert Sent: {alert_payload['id']} | Vehicle: {alert_payload['vehicle_no']} | Type: {alert_payload['type']}")
        else:
            print(f"⚠️ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: Is backend running? ({e})")

    alert_id += 1
    time.sleep(3)