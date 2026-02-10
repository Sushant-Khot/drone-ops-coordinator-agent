"""
Minimal runner for the Google Apps Script-backed Sheets client.

Run from the project root:
  python -m app.main

Note:
- `GOOGLE_SCRIPT_URL` must be set (for example in `.env`) to your deployed
  Google Apps Script Web App URL.
- The Apps Script is expected to serve:
    GET  ?sheet=Pilots   -> JSON rows
    GET  ?sheet=Drones   -> JSON rows
    POST JSON payloads for status updates (see SheetsClient methods)
"""

import os

from dotenv import load_dotenv

from app.sheets_client import SheetsClient


load_dotenv()

SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL", "").strip()


def main() -> None:
    if not SCRIPT_URL:
        raise RuntimeError(
            "Missing GOOGLE_SCRIPT_URL. Set it in .env (or environment) like:\n"
            "GOOGLE_SCRIPT_URL=https://script.google.com/macros/s/AKfycb.../exec"
        )

    client = SheetsClient(SCRIPT_URL)

    # Read pilots
    pilots = client.get_pilot_data()
    print("Pilots:", pilots)

    # Read drones
    drones = client.get_drone_data()
    print("Drones:", drones)

    # Update pilot status
    print(client.update_pilot_status("Arjun", "Inactive"))

    # Update drone status
    print(client.update_drone_status("D001", "Busy"))


if __name__ == "__main__":
    main()
