from datetime import datetime


class ConflictDetector:
    def __init__(self):
        pass

    # ----------------------------
    # MAIN FUNCTION
    # ----------------------------
    def check_conflicts(self, pilot: dict, drone: dict, project: str, project_req: dict = None):
        """
        project_req example:
        {
          "location": "Bangalore",
          "start_date": "2026-02-10",
          "end_date": "2026-02-12",
          "required_certs": ["DGCA", "BVLOS"]
        }
        """

        conflicts = []

        # Defaults if no project requirements provided
        if project_req is None:
            project_req = {}

        # ----------------------------
        # 1) Drone Maintenance Conflict
        # ----------------------------
        drone_status = str(drone.get("status", "")).lower()
        if "maintenance" in drone_status:
            conflicts.append(f"Drone {drone.get('drone_id')} is under maintenance")

        # ----------------------------
        # 2) Location Mismatch Conflict
        # ----------------------------
        pilot_loc = str(pilot.get("location", "")).strip().lower()
        drone_loc = str(drone.get("location", "")).strip().lower()
        project_loc = str(project_req.get("location", "")).strip().lower()

        if pilot_loc and drone_loc and pilot_loc != drone_loc:
            conflicts.append(
                f"Pilot is in {pilot.get('location')} but drone is in {drone.get('location')}"
            )
        if project_loc:
            if pilot_loc and project_loc != pilot_loc:
                conflicts.append(f"Pilot is in {pilot.get('location')} but project is in {project_req.get('location')}")
            if drone_loc and project_loc != drone_loc:
                conflicts.append(f"Drone is in {drone.get('location')} but project is in {project_req.get('location')}")

        # ----------------------------
        # 3) Certification Mismatch
        # ----------------------------
        required_certs = project_req.get("required_certs", [])
        pilot_certs = self._parse_list(pilot.get("certifications", ""))

        for cert in required_certs:
            if cert.lower() not in [c.lower() for c in pilot_certs]:
                conflicts.append(f"Pilot {pilot.get('name')} does not have required certification: {cert}")

        # ----------------------------
        # 4) Double Booking / Busy Conflict (best-effort)
        # ----------------------------
        pilot_status = str(pilot.get("status", "")).lower()
        pilot_assignment = str(pilot.get("current_assignment", "")).strip()
        if pilot_status in {"assigned", "busy", "deployed"} and pilot_assignment and pilot_assignment != "-" and pilot_assignment.lower() != project.lower():
            conflicts.append(f"Pilot {pilot.get('name')} is already assigned to {pilot_assignment}")

        drone_assignment = str(drone.get("current_assignment", "")).strip()
        if str(drone.get("status", "")).lower() in {"assigned", "busy", "deployed"} and drone_assignment and drone_assignment != "-" and drone_assignment.lower() != project.lower():
            conflicts.append(f"Drone {drone.get('drone_id')} is already assigned to {drone_assignment}")

        return conflicts

    # ----------------------------
    # HELPERS
    # ----------------------------
    def _parse_list(self, value):
        """
        Converts comma separated string -> list
        Example: "DGCA, BVLOS" -> ["DGCA", "BVLOS"]
        """
        if not value:
            return []
        if isinstance(value, list):
            return value

        return [x.strip() for x in str(value).split(",") if x.strip()]
