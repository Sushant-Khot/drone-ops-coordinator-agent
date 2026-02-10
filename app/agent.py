import re
from typing import Any, Dict, List, Optional

from app.assignment_engine import AssignmentEngine
from app.conflict_detector import ConflictDetector
from app.sheets_client import SheetsClient


class CoordinatorAgent:
    """
    Drone Ops Coordinator Agent
    Supports:
    - pilots sheet
    - drones sheet
    - missions sheet
    """

    def __init__(self, sheets_client: SheetsClient):
        self.sheets = sheets_client
        self.conflict_detector = ConflictDetector()
        self.assignment_engine = AssignmentEngine()

    # ---------------------------------------------------
    # MAIN ENTRY POINT
    # ---------------------------------------------------
    def handle_query(self, user_query: str) -> Dict[str, Any]:
        q = (user_query or "").strip()

        pilots = self.sheets.get_pilot_data()
        drones = self.sheets.get_drone_data()

        if not isinstance(pilots, list) or not isinstance(drones, list):
            return {"status": "error", "message": "Sheets returned invalid data format."}

        intent = self._detect_intent(q)

        if intent == "show_available_pilots":
            return self._show_available_pilots(q, pilots)

        if intent == "show_available_drones":
            return self._show_available_drones(q, drones)

        if intent == "update_pilot_status":
            return self._update_pilot_status(q, pilots)

        if intent == "update_drone_status":
            return self._update_drone_status(q, drones)

        if intent == "assign_mission":
            return self._assign_mission(q, pilots, drones, urgent=False)

        if intent == "urgent_assign_mission":
            return self._assign_mission(q, pilots, drones, urgent=True)

        return {
            "status": "unknown",
            "message": "❌ Sorry, I didn't understand. Try: show pilots/drones, update pilot/drone, assign mission M001."
        }

    # ---------------------------------------------------
    # INTENT DETECTION
    # ---------------------------------------------------
    def _detect_intent(self, query: str) -> str:
        q = query.lower()

        if "urgent" in q and "mission" in q:
            return "urgent_assign_mission"

        if "assign" in q and "mission" in q:
            return "assign_mission"

        if "show" in q and "pilot" in q:
            return "show_available_pilots"

        if "show" in q and "drone" in q:
            return "show_available_drones"

        if "available pilots" in q:
            return "show_available_pilots"

        if "available drones" in q:
            return "show_available_drones"

        if "update" in q and "pilot" in q:
            return "update_pilot_status"

        if "update" in q and "drone" in q:
            return "update_drone_status"

        return "unknown"

    # ---------------------------------------------------
    # SHOW PILOTS
    # ---------------------------------------------------
    def _show_available_pilots(self, query: str, pilots: List[Dict[str, Any]]) -> Dict[str, Any]:
        location = self._extract_location(query)
        required_certs = self._extract_required_certs(query)

        available = []

        for p in pilots:
            status = str(p.get("status", "")).lower()
            loc = str(p.get("location", "")).lower()
            certs = self._parse_list(p.get("certifications", ""))

            if status not in ["available", "active", "free"]:
                continue

            if location and location.lower() not in loc:
                continue

            if required_certs and not self._has_all(required_certs, certs):
                continue

            available.append(p)

        if not available:
            return {
                "status": "success",
                "message": f"❌ No available pilots found for {location or 'all locations'}."
            }

        msg = "✅ Available Pilots:\n"
        for p in available:
            msg += f"- {p.get('name')} | {p.get('location')} | {p.get('status')} | certs={p.get('certifications')}\n"

        return {"status": "success", "message": msg, "data": available}

    # ---------------------------------------------------
    # SHOW DRONES
    # ---------------------------------------------------
    def _show_available_drones(self, query: str, drones: List[Dict[str, Any]]) -> Dict[str, Any]:
        capability = self._extract_capability(query)
        location = self._extract_location(query)

        available = []

        for d in drones:
            status = str(d.get("status", "")).lower()
            caps = str(d.get("capabilities", "")).lower()
            loc = str(d.get("location", "")).lower()

            if status not in ["available", "ready", "free"]:
                continue

            if "maintenance" in status:
                continue

            if location and location.lower() not in loc:
                continue

            if capability and capability.lower() not in caps:
                continue

            available.append(d)

        if not available:
            return {
                "status": "success",
                "message": f"❌ No available drones found for {capability or 'all capabilities'}."
            }

        msg = "✅ Available Drones:\n"
        for d in available:
            msg += f"- {d.get('drone_id')} | {d.get('model')} | caps={d.get('capabilities')} | {d.get('status')}\n"

        return {"status": "success", "message": msg, "data": available}

    # ---------------------------------------------------
    # UPDATE PILOT STATUS
    # ---------------------------------------------------
    def _update_pilot_status(self, query: str, pilots: List[Dict[str, Any]]) -> Dict[str, Any]:
        pilot_name = self._extract_pilot_name(query)
        status = self._extract_status(query)

        if not pilot_name or not status:
            return {"status": "error", "message": "Example: Update pilot Ravi to On Leave"}

        pilot_exists = any(str(p.get("name", "")).lower() == pilot_name.lower() for p in pilots)
        if not pilot_exists:
            return {"status": "error", "message": f"Pilot not found: {pilot_name}"}

        result = self.sheets.update_pilot_status(pilot_name, status)

        return {"status": "success", "message": f"✅ Pilot {pilot_name} updated to {status}", "result": result}

    # ---------------------------------------------------
    # UPDATE DRONE STATUS
    # ---------------------------------------------------
    def _update_drone_status(self, query: str, drones: List[Dict[str, Any]]) -> Dict[str, Any]:
        drone_id = self._extract_drone_id(query)
        status = self._extract_status(query)

        if not drone_id or not status:
            return {"status": "error", "message": "Example: Update drone D001 to Maintenance"}

        drone_exists = any(str(d.get("drone_id", "")).lower() == drone_id.lower() for d in drones)
        if not drone_exists:
            return {"status": "error", "message": f"Drone not found: {drone_id}"}

        result = self.sheets.update_drone_status(drone_id, status)

        return {"status": "success", "message": f"✅ Drone {drone_id} updated to {status}", "result": result}

    # ---------------------------------------------------
    # ASSIGN MISSION (MAIN REQUIREMENT)
    # ---------------------------------------------------
    def _assign_mission(self, query: str, pilots: List[Dict[str, Any]], drones: List[Dict[str, Any]], urgent: bool):
        missions = self.sheets.get_mission_data()

        mission_id = self._extract_mission_id(query)
        if not mission_id:
            return {"status": "error", "message": "Mission ID missing. Example: assign mission M001"}

        # Find mission row
        mission = None
        for m in missions:
            if str(m.get("mission_id", "")).strip().lower() == mission_id.lower():
                mission = m
                break

        if not mission:
            return {"status": "error", "message": f"Mission not found: {mission_id}"}

        mission_status = str(mission.get("status", "")).lower()
        if mission_status in ["assigned", "completed"]:
            return {"status": "error", "message": f"❌ Mission {mission_id} already {mission_status}"}

        location = mission.get("location")
        required_certs = self._parse_list(mission.get("required_certs", ""))
        required_capability = mission.get("required_capability")
        project_name = mission.get("project") or mission_id

        # Match pilot + drone
        match = self.assignment_engine.find_best_match(
            pilots=pilots,
            drones=drones,
            location=location,
            urgent=urgent,
            required_certs=required_certs,
            required_capability=required_capability,
        )

        if not match:
            return {"status": "error", "message": f"❌ No match found for mission {mission_id}"}

        pilot = match["pilot"]
        drone = match["drone"]

        # Conflict detection using mission dates + certs
        conflicts = self.conflict_detector.check_conflicts(
            pilot=pilot,
            drone=drone,
            project=project_name,
            project_req={
                "location": location,
                "start_date": mission.get("start_date"),
                "end_date": mission.get("end_date"),
                "required_certs": required_certs,
            }
        )

        if conflicts:
            return {
                "status": "conflict",
                "message": f"⚠️ Conflicts found for mission {mission_id}:\n- " + "\n- ".join(conflicts),
                "match": match
            }

        # Write assignment into missions sheet
        self.sheets.update_mission_assignment(
            mission_id=mission_id,
            pilot_name=pilot.get("name"),
            drone_id=drone.get("drone_id"),
        )

        # Update pilot + drone status
        self.sheets.update_pilot_status(pilot.get("name"), f"Assigned({mission_id})")
        self.sheets.update_drone_status(drone.get("drone_id"), f"Assigned({mission_id})")

        urgent_tag = "🚨 URGENT" if urgent else "✅"

        return {
            "status": "success",
            "message": (
                f"{urgent_tag} Mission Assigned Successfully!\n"
                f"Mission ID: {mission_id}\n"
                f"Project: {project_name}\n"
                f"Pilot: {pilot.get('name')}\n"
                f"Drone: {drone.get('drone_id')}\n"
                f"Location: {location}\n"
                f"Dates: {mission.get('start_date')} to {mission.get('end_date')}\n"
                f"Reason: {match.get('reason')}"
            ),
            "match": match
        }

    # ---------------------------------------------------
    # HELPERS
    # ---------------------------------------------------
    def _extract_location(self, query: str) -> Optional[str]:
        m = re.search(r"\bin\s+([A-Za-z]+)\b", query, flags=re.IGNORECASE)
        return m.group(1) if m else None

    def _extract_mission_id(self, query: str) -> Optional[str]:
        m = re.search(r"\bM\d+\b", query, flags=re.IGNORECASE)
        return m.group(0) if m else None

    def _extract_pilot_name(self, query: str) -> Optional[str]:
        m = re.search(r"\bpilot\s+([A-Za-z]+)\b", query, flags=re.IGNORECASE)
        return m.group(1) if m else None

    def _extract_drone_id(self, query: str) -> Optional[str]:
        m = re.search(r"\bdrone\s+([A-Za-z0-9]+)\b", query, flags=re.IGNORECASE)
        return m.group(1) if m else None

    def _extract_capability(self, query: str) -> Optional[str]:
        q = query.lower()
        for cap in ["thermal", "lidar", "rgb", "camera"]:
            if cap in q:
                return cap
        return None

    def _extract_required_certs(self, query: str) -> List[str]:
        q = query.lower()
        certs = []
        if "dgca" in q:
            certs.append("DGCA")
        if "bvlos" in q:
            certs.append("BVLOS")
        if "night" in q:
            certs.append("Night Ops")
        return certs

    def _extract_status(self, query: str) -> Optional[str]:
        q = query.lower()
        if "on leave" in q:
            return "On Leave"
        if "maintenance" in q:
            return "Maintenance"
        if "available" in q:
            return "Available"
        if "busy" in q:
            return "Busy"
        if "inactive" in q:
            return "Inactive"
        if "assigned" in q:
            return "Assigned"
        return None

    def _parse_list(self, value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()]
        return [x.strip() for x in str(value).split(",") if x.strip()]

    def _has_all(self, required: List[str], actual: List[str]) -> bool:
        actual_lower = {a.strip().lower() for a in actual}
        for r in required:
            if r.strip().lower() not in actual_lower:
                return False
        return True
