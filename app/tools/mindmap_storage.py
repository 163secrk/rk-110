import json
import os
import uuid
import time
from datetime import datetime
from pathlib import Path


class MindMapStorage:
    DATA_DIR = Path.home() / ".rk110_mindmaps"

    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.maps_file = self.DATA_DIR / "maps_index.json"
        self._ensure_maps_file()

    def _ensure_maps_file(self):
        if not self.maps_file.exists():
            with open(self.maps_file, "w", encoding="utf-8") as f:
                json.dump({"maps": []}, f, ensure_ascii=False, indent=2)

    def _read_index(self):
        with open(self.maps_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_index(self, data):
        with open(self.maps_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_map_file(self, map_id):
        return self.DATA_DIR / f"{map_id}.json"

    def list_maps(self, project_filter=None, search_query=None):
        data = self._read_index()
        maps = data.get("maps", [])

        if project_filter and project_filter != "全部":
            maps = [m for m in maps if m.get("project") == project_filter]

        if search_query:
            q = search_query.lower()
            maps = [m for m in maps if q in m.get("title", "").lower()]

        return sorted(maps, key=lambda m: m.get("updated_at", 0), reverse=True)

    def list_projects(self):
        data = self._read_index()
        projects = set()
        for m in data.get("maps", []):
            p = m.get("project")
            if p:
                projects.add(p)
        return sorted(list(projects))

    def create_map(self, title, project="默认项目", creator="当前用户"):
        map_id = str(uuid.uuid4())
        now = time.time()

        root_node = {
            "id": str(uuid.uuid4()),
            "text": title,
            "x": 0,
            "y": 0,
            "color": "#3498db",
            "icon": None,
            "link": None,
            "children": []
        }

        map_data = {
            "id": map_id,
            "title": title,
            "project": project,
            "creator": creator,
            "created_at": now,
            "updated_at": now,
            "root": root_node,
            "scale": 1.0,
            "offset_x": 0,
            "offset_y": 0
        }

        map_file = self._get_map_file(map_id)
        with open(map_file, "w", encoding="utf-8") as f:
            json.dump(map_data, f, ensure_ascii=False, indent=2)

        index_data = self._read_index()
        index_entry = {
            "id": map_id,
            "title": title,
            "project": project,
            "creator": creator,
            "created_at": now,
            "updated_at": now
        }
        index_data["maps"].append(index_entry)
        self._write_index(index_data)

        return map_data

    def get_map(self, map_id):
        map_file = self._get_map_file(map_id)
        if not map_file.exists():
            return None
        with open(map_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_map(self, map_data):
        map_id = map_data["id"]
        map_data["updated_at"] = time.time()

        map_file = self._get_map_file(map_id)
        with open(map_file, "w", encoding="utf-8") as f:
            json.dump(map_data, f, ensure_ascii=False, indent=2)

        index_data = self._read_index()
        for m in index_data.get("maps", []):
            if m["id"] == map_id:
                m["title"] = map_data["title"]
                m["project"] = map_data.get("project", m.get("project"))
                m["updated_at"] = map_data["updated_at"]
                break
        self._write_index(index_data)

        return True

    def delete_map(self, map_id):
        map_file = self._get_map_file(map_id)
        if map_file.exists():
            map_file.unlink()

        index_data = self._read_index()
        index_data["maps"] = [m for m in index_data.get("maps", []) if m["id"] != map_id]
        self._write_index(index_data)

        return True

    @staticmethod
    def format_timestamp(ts):
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
