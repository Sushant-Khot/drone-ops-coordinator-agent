import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "credentials/service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Put your Sheet name here (same as in Google Drive)
SHEET_NAME = "DroneOpsDatabase"

sheet = client.open(SHEET_NAME)

# Access Pilots tab
pilots_ws = sheet.worksheet("Pilots")
pilots_data = pilots_ws.get_all_records()

print("✅ Pilots Data:")
print(pilots_data)

# Access Drones tab
drones_ws = sheet.worksheet("Drones")
drones_data = drones_ws.get_all_records()

print("\n✅ Drones Data:")
print(drones_data)

# Test Write (Update Pilot Status)
pilots_ws.update("B2", "Active")  # Example: update cell B2

print("\n✅ Write test successful! Updated B2 in Pilots sheet.")
