import requests
import json


class SheetsClient:
    def __init__(self, script_url: str):
        """
        script_url = Google Apps Script Web App URL
        Example:
        https://script.google.com/macros/s/AKfycbxxxxx/exec
        """
        self.script_url = script_url

    # -------------------------
    # READ SHEET DATA
    # -------------------------

    def get_pilot_data(self):
        """Reads full 'Pilots' sheet"""
        params = {"sheet": "Pilots"}
        res = requests.get(self.script_url, params=params)

        if res.status_code != 200:
            raise Exception(f"Failed to read Pilots sheet: {res.text}")

        return res.json()

    def get_drone_data(self):
        """Reads full 'Drones' sheet"""
        params = {"sheet": "Drones"}
        res = requests.get(self.script_url, params=params)

        if res.status_code != 200:
            raise Exception(f"Failed to read Drones sheet: {res.text}")

        return res.json()

    # -------------------------
    # UPDATE PILOT STATUS
    # -------------------------

    def update_pilot_status(self, pilot_name: str, status: str):
        """
        Updates pilot status based on pilot_name column match.
        Assumes sheet has columns:
        name | status
        """
        payload = {
            "sheet": "Pilots",
            "keyColumn": "name",
            "keyValue": pilot_name,
            "updateColumn": "status",
            "updateValue": status
        }

        res = requests.post(
            self.script_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )

        if res.status_code != 200:
            raise Exception(f"Failed to update pilot status: {res.text}")

        return res.json()

    # -------------------------
    # UPDATE DRONE STATUS
    # -------------------------

    def update_drone_status(self, drone_id: str, status: str):
        """
        Updates drone status based on drone_id column match.
        Assumes sheet has columns (at minimum):
        drone_id | status
        """
        payload = {
            "sheet": "Drones",
            "keyColumn": "drone_id",
            "keyValue": drone_id,
            "updateColumn": "status",
            "updateValue": status
        }

        res = requests.post(
            self.script_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )

        if res.status_code != 200:
            raise Exception(f"Failed to update drone status: {res.text}")

        return res.json()
