import requests
import json
from typing import Any, Dict, List, Optional


class SheetsClient:
    def __init__(self, script_url: str):
        """
        script_url = Google Apps Script Web App URL
        Example:
        https://script.google.com/macros/s/AKfycbxxxxx/exec
        """
        self.script_url = script_url

    # -------------------------
    # INTERNAL HELPERS
    # -------------------------

    def _normalize_table(self, data: Any) -> Any:
        """
        Normalizes Apps Script output into list[dict] format.

        Supports:
        - list[list] (first row = headers)
        - list[dict] (already correct)
        - dict (error response)
        """
        if not isinstance(data, list) or not data:
            return data

        # Already list[dict]
        if isinstance(data[0], dict):
            return data

        # list[list] format
        if isinstance(data[0], list):
            headers = [str(h).strip() for h in data[0]]
            rows = []
            for row in data[1:]:
                if not isinstance(row, list):
                    continue
                row_dict = {}
                for i, h in enumerate(headers):
                    row_dict[h] = row[i] if i < len(row) else ""
                rows.append(row_dict)
            return rows

        return data

    def _get_sheet(self, sheet_name: str) -> List[Dict[str, Any]]:
        params = {"sheet": sheet_name}
        res = requests.get(self.script_url, params=params, timeout=30)

        if res.status_code != 200:
            raise Exception(f"Failed to read sheet {sheet_name}: {res.text}")

        parsed = res.json()
        normalized = self._normalize_table(parsed)

        if isinstance(normalized, dict) and "error" in normalized:
            raise Exception(f"Apps Script error: {normalized}")

        return normalized

    def _update_cell(self, sheet: str, key_column: str, key_value: str, update_column: str, update_value: str):
        """
        Uses Apps Script POST update API.
        Requires Apps Script to support action=update.
        """
        payload = {
            "action": "update",
            "sheet": sheet,
            "keyColumn": key_column,
            "keyValue": key_value,
            "updateColumn": update_column,
            "updateValue": update_value,
        }

        res = requests.post(
            self.script_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if res.status_code != 200:
            raise Exception(f"Update failed ({sheet}): {res.text}")

        return res.json()

    # -------------------------
    # READ FUNCTIONS
    # -------------------------

    def get_pilot_data(self):
        return self._get_sheet("Pilots")

    def get_drone_data(self):
        return self._get_sheet("Drones")

    def get_mission_data(self):
        return self._get_sheet("missions")

    # -------------------------
    # UPDATE FUNCTIONS
    # -------------------------

    def update_pilot_status(self, pilot_name: str, status: str):
        return self._update_cell(
            sheet="Pilots",
            key_column="name",
            key_value=pilot_name,
            update_column="status",
            update_value=status,
        )

    def update_drone_status(self, drone_id: str, status: str):
        return self._update_cell(
            sheet="Drones",
            key_column="drone_id",
            key_value=drone_id,
            update_column="status",
            update_value=status,
        )

    # -------------------------
    # MISSIONS UPDATE FUNCTIONS
    # -------------------------

    def update_mission_assignment(self, mission_id: str, pilot_name: str, drone_id: str):
        """
        Writes assigned pilot/drone into missions sheet.
        """
        self._update_cell("missions", "mission_id", mission_id, "assigned_pilot", pilot_name)
        self._update_cell("missions", "mission_id", mission_id, "assigned_drone", drone_id)
        return self._update_cell("missions", "mission_id", mission_id, "status", "assigned")

    def update_mission_status(self, mission_id: str, status: str):
        return self._update_cell("missions", "mission_id", mission_id, "status", status)
