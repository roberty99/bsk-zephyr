BSK Zephyr — Home Assistant Integration

A fully local Home Assistant integration for the BSK Zephyr inline ventilation fan.
Controls power, speed, mode, humidity target, buzzer, and exposes all onboard sensors.

No cloud. No dependencies. Fast local polling.
BSK Zephy have enabled a Home Assistant friednly local Web UI via that Advnaced Configuraition option in the BSK Connect app. 

⸻

✨ Features

✅ Full Fan Control (Integrated into one entity)
	•	On / Off
	•	Speed control (0–100%)
	•	Automatically maps to device range (22–80)
	•	Automatically powers on before adjusting speed
	•	Modes integrated as preset modes:
	•	Cycle 🔄
	•	Intake ⬅️
	•	Exhaust ➡️

✅ Controls
	•	Humidity target (35–100%)
	•	Buzzer (on/off)

✅ Sensors
	•	Temperature (°C)
	•	Humidity (%)
	•	Set humidity level
	•	WiFi RSSI
	•	Filter timer (hours)
	•	Hygiene status
	•	Current operation mode

✔ Device status is parsed from the device’s local HTML interface

✔ Optimistic mode disabled — real state always used

✔ Polling interval: 5 seconds

✔ Device grouping via shared base entity class

⸻

📦 Installation (HACS)

Add this repo as a Custom Repository in HACS:
	1.	Go to HACS → Integrations → … → Custom repositories
	2.	Paste your GitHub URL
	3.	Category: Integration
	4.	Install “BSK Zephyr”
	5.	Restart Home Assistant

🛠 Manual installation

Copy the folder:
custom_components/bsk_zephyr/

into your Home Assistant:
config/custom_components/bsk_zephyr/

Restart Home Assistant

🔧 Setup
	1.	Go to Settings → Devices & services → Add Integration
	2.	Search for BSK Zephyr
	3.	Enter the IP address of the device
(e.g., 192.168.0.37)

You’re done!

📡 Device Endpoints Used

Requires only local HTTP access:
GET  /
POST /on
POST /off
POST /fan      (speed=x)
POST /cycle
POST /intake
POST /exhaust
POST /humid    (level=x)
POST /buzzer   (state=0/1)

📝 Known limitations
	•	Device offers no event push — uses polling
	•	Speed must be between 22–80 (device enforced)
	•	HTML parsing relies on stable output formatting

  🙌 Credits

This integration was custom-built for controlling the
BSK Zephyr 160mm ventilation system via its local WiFi API.

