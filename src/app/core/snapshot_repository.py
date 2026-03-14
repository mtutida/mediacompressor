import os
import json
from dataclasses import asdict


class SnapshotRepository:

    def __init__(self, directory: str = "snapshots"):
        self._directory = directory
        os.makedirs(self._directory, exist_ok=True)

    def save(self, snapshot):
        file_path = os.path.join(self._directory, f"{snapshot.name}.json")
        temp_path = file_path + ".tmp"

        data = asdict(snapshot)
        data["status"] = snapshot.status.name  # Convert Enum to string

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        os.replace(temp_path, file_path)

    def load(self, job_name: str):
        file_path = os.path.join(self._directory, f"{job_name}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
