# 🚁 Drone Operations Coordinator AI Agent

An AI-powered **Drone Operations Coordinator** for managing pilots, drone fleet inventory, project assignments, and conflict resolution using a **conversational interface** with **Google Sheets 2-way sync**.

This project automates the high-context operational coordination work done manually using spreadsheets and messages.

---

## 📌 Problem Overview

Skylark Drones operates multiple drone projects simultaneously. Coordination requires:

- Pilot roster tracking (availability, leave, assignments)
- Drone inventory tracking (available, deployed, maintenance)
- Matching pilots and drones to projects based on requirements
- Detecting conflicts (double booking, certification mismatch, maintenance issues)
- Supporting urgent reassignment scenarios

This AI Agent reduces manual overhead and improves scheduling accuracy.

---

## 🎯 Key Features

### ✅ 1. Pilot Roster Management
- Query pilots by:
  - location
  - certification
  - skill level
  - availability status
- View current assignments
- Update pilot status (**syncs back to Google Sheets**)

---

### ✅ 2. Assignment Tracking
- Match best pilot for a project based on:
  - required skills
  - required certifications
  - availability
  - location
- Track active assignments
- Support reassignment logic

---

### ✅ 3. Drone Fleet Inventory Management
- Query drones by:
  - capability (thermal camera, payload support, night ops etc.)
  - availability
  - location
- Track drone deployment status
- Flag drones under maintenance
- Update drone status (**syncs back to Google Sheets**)

---

### ✅ 4. Conflict Detection Engine
The agent detects and warns about:

- Pilot double booking (overlapping project dates)
- Drone double booking (overlapping deployment dates)
- Certification mismatch (pilot missing required certification)
- Drone maintenance assignment issue
- Location mismatch (pilot & drone in different city)

---

### 🚨 Bonus Feature: Urgent Reassignment (Mandatory)
The agent supports urgent projects by:
- finding available replacements immediately
- suggesting reassignments with minimum disruption
- recommending fallback options if no resources are free

---

## 🏗️ Architecture Overview

**Frontend**
- Streamlit Chat UI (conversational interface)

**Backend**
- Python-based agent logic (FastAPI optional)

**Database**
- Google Sheets used as the single source of truth

**Integration**
- Google Sheets API (2-way sync)

---

## 📂 Project Structure

drone-ops-coordinator-agent/
│── app/
│ │── agent.py
│ │── sheets_client.py
│ │── assignment_engine.py
│ │── conflict_detector.py
│ │── main.py
│
│── ui/
│ │── streamlit_app.py
│
│── data/
│ │── sample_pilot_roster.csv
│ │── sample_drone_fleet.csv
│
│── decision_log.md
│── requirements.txt
│── README.md
│── .env.example
│── .gitignore


---

## 🧾 Google Sheets Format

### 📌 Pilot Roster Sheet (Example Columns)
| name | skill_level | certifications | drone_experience | location | current_assignment | status |
|------|------------|----------------|------------------|----------|-------------------|--------|
| Ravi | Intermediate | DGCA,NightOps | DJI M300 | Bangalore | Project A | Available |

---

### 📌 Drone Fleet Sheet (Example Columns)
| model | serial_number | capabilities | location | status | current_assignment |
|------|--------------|--------------|----------|--------|-------------------|
| DJI M300 | DJI-102 | Thermal,Payload | Pune | Maintenance | None |

---

## 🔄 Google Sheets 2-Way Sync

This project supports **read + write** sync.

### Reads:
- Pilot Roster sheet
- Drone Fleet sheet

### Writes:
- Pilot status updates
- Drone status updates
- Assignment updates (optional)

---

## 🛠️ Tech Stack

| Component | Technology |
|----------|------------|
| Language | Python |
| UI | Streamlit |
| Sheets Integration | gspread + Google Sheets API |
| Data Handling | Pandas |
| Agent Logic | Custom rules + optional LLM support |

---

## ⚙️ Installation & Setup (Local)

### 1️⃣ Clone Repo
```bash
git clone https://github.com/Sushant-Khot/drone-ops-coordinator-agent.git
cd drone-ops-coordinator-agent
2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Setup Environment Variables
Create .env file using .env.example

5️⃣ Run Streamlit UI
streamlit run ui/streamlit_app.py
assumptions

tradeoffs

urgent reassignment interpretation

improvements planned if more time available

📦 Deliverables Checklist
✅ Hosted Prototype 
✅ Decision Log 
✅ Source Code ZIP
✅ README with architecture + setup guide
✅ Google Sheets 2-way sync

🔮 Future Improvements
If more time is available:

Add authentication for coordinator login

Add calendar-based scheduling visualization

Add project sheet integration

Auto-prioritization based on project urgency

Add notifications (Slack / Email integration)

👨‍💻 Author
Sushant Kantu Khot

