# Drone Operations Coordinator AI Agent

An AI agent that handles core responsibilities of a drone operations coordinator for Skylark Drones: roster management, assignment tracking, drone inventory, and conflict detection with 2-way Google Sheets sync.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Conversational UI (Streamlit)                  │
├─────────────────────────────────────────────────────────────────┤
│                     Agent / Orchestration Layer                   │
│  (intent handling, tool calls, conflict checks, reassignments)   │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   Roster     │  Assignment  │   Drone      │   Conflict          │
│   Manager    │  Tracker     │   Inventory  │   Detector          │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│              Google Sheets Integration (2-way sync)              │
├─────────────────────────────────────────────────────────────────┤
│         Pilot Roster Sheet    │    Drone Fleet Sheet             │
└─────────────────────────────────────────────────────────────────┘
```

- **Tech stack**: Python 3.10+, Streamlit (UI), gspread + Google Auth (Sheets), OpenAI-compatible API or local LLM for conversation.
- **Data**: Pilot Roster and Drone Fleet live in Google Sheets; agent reads on load/refresh and writes back status updates.
- **Features**: Query pilots/drones by skill/capability/location, update status (Available/On Leave/Unavailable, drone status), match pilots to projects, track assignments, detect double-booking/skill/location/maintenance conflicts, support urgent reassignments.

## Setup

1. **Clone and install**
   ```bash
   cd drone-ops-coordinator-agent
   pip install -r requirements.txt
   ```

2. **Google Sheets**
   - Create two sheets: "Pilot Roster" and "Drone Fleet" (or use sheet IDs in env).
   - Use the CSV templates in `data/` to define columns; upload or copy structure to Sheets.
   - Enable Google Sheets API, create a service account, download JSON key, save as `credentials.json` in project root (or set `GOOGLE_APPLICATION_CREDENTIALS`).

3. **Environment**
   ```bash
   cp .env.example .env
   # Edit .env: GOOGLE_SHEET_ID, OPENAI_API_KEY (or other LLM endpoint), etc.
   ```

4. **Run**
   ```bash
   streamlit run app.py
   ```

## Deliverables

- **Hosted prototype**: Deploy to Streamlit Cloud / Replit / Vercel (see `DEPLOY.md` if present).
- **Decision Log**: `docs/DECISION_LOG.md` (assumptions, trade-offs, urgent reassignments interpretation).
- **Source**: This repo; ZIP for submission.

## License

MIT (or as specified by Skylark Drones).
