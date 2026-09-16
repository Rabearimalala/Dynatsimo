from __future__ import annotations

import importlib.util
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_MODULE_PATH = ROOT_DIR / "scripts" / "import-chirps-and-export.py"


def load_data_module():
    spec = importlib.util.spec_from_file_location("dynatsimo_data", DATA_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger {DATA_MODULE_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NDVI_MODULE_PATH = ROOT_DIR / "scripts" / "export_ndvi_6classes.py"


def load_ndvi_module():
    if not NDVI_MODULE_PATH.exists():
        return None
    spec = importlib.util.spec_from_file_location("dynatsimo_ndvi", NDVI_MODULE_PATH)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PIPELINE_MODULE_PATH = ROOT_DIR / "scripts" / "sync_pipeline.py"


def load_pipeline_module():
    if not PIPELINE_MODULE_PATH.exists():
        return None
    spec = importlib.util.spec_from_file_location("dynatsimo_pipeline", PIPELINE_MODULE_PATH)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


data_module = load_data_module()
engine = data_module.make_engine()

ROUTES = {
    "/api/overview": "overview",
    "/api/communes": "communes",
    "/api/annual-precipitations": "annualData",
    "/api/saisons": "seasonData",
    "/api/monthly-climatology": "monthlyClimatology",
    "/api/anomalies": "anomalies",
    "/api/precip-records": "precipRecords",
    "/api/communes.geojson": "communesGeojson",
    "/api/vegetation-data": "vegetationData",
}


class ApiHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        try:
            if path == "/api/health":
                self.send_json({"status": "ok"})
                return

            if path in ("/api/sync/all", "/api/sync/precipitation"):
                pipe_mod = load_pipeline_module()
                if pipe_mod and hasattr(pipe_mod, "run_full_pipeline"):
                    skip_ndvi = (path == "/api/sync/precipitation")
                    success = pipe_mod.run_full_pipeline(skip_download=False, skip_ndvi=skip_ndvi)
                    self.send_json({"status": "success" if success else "error", "message": "Synchronisation terminée"})
                    return
                self.send_json({"error": "Module de pipeline introuvable"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            if path in ("/api/ndvi-classes", "/api/ndvi-classes/sync"):
                meta_path = ROOT_DIR / "public" / "data" / "ndvi_classes_metadata.json"
                if path == "/api/ndvi-classes/sync" or not meta_path.exists():
                    ndvi_mod = load_ndvi_module()
                    if ndvi_mod and hasattr(ndvi_mod, "sync_all_ndvi_rasters"):
                        meta = ndvi_mod.sync_all_ndvi_rasters()
                        self.send_json(meta)
                        return

                if meta_path.exists():
                    with meta_path.open("r", encoding="utf-8") as f:
                        self.send_json(json.load(f))
                    return
                self.send_json({"error": "Fichier ndvi_classes_metadata.json introuvable"}, HTTPStatus.NOT_FOUND)
                return

            if path == "/api/isohyetes-metadata":
                iso_path = ROOT_DIR / "public" / "data" / "isohyetes_metadata.json"
                if iso_path.exists():
                    with iso_path.open("r", encoding="utf-8") as f:
                        self.send_json(json.load(f))
                    return
                self.send_json({"error": "Fichier isohyetes_metadata.json introuvable"}, HTTPStatus.NOT_FOUND)
                return

            payload = data_module.build_react_payload(engine)
            meta_path = ROOT_DIR / "public" / "data" / "ndvi_classes_metadata.json"
            if meta_path.exists():
                try:
                    with meta_path.open("r", encoding="utf-8") as f:
                        payload["ndviClasses"] = json.load(f)
                except Exception:
                    pass

            iso_path = ROOT_DIR / "public" / "data" / "isohyetes_metadata.json"
            if iso_path.exists():
                try:
                    with iso_path.open("r", encoding="utf-8") as f:
                        payload["isohyetesMeta"] = json.load(f)
                except Exception:
                    pass

            if path == "/api/data":
                self.send_json(payload)
                return

            if path in ROUTES:
                self.send_json(payload[ROUTES[path]])
                return

            self.send_json({"error": f"Route inconnue: {path}"}, HTTPStatus.NOT_FOUND)
        except Exception as error:
            self.send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def send_json(self, data, status=HTTPStatus.OK):
        body = json.dumps(
            data_module.clean_for_json(data),
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_cors_headers(self):
        origin = os.getenv("DYNATSIMO_CORS_ORIGIN", "*")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def main():
    host = os.getenv("DYNATSIMO_API_HOST", "127.0.0.1")
    port = int(os.getenv("DYNATSIMO_API_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), ApiHandler)

    print(f"API DYNATSIMO prete: http://{host}:{port}/api/data")
    print("Arrete le serveur avec Ctrl+C.")
    server.serve_forever()


if __name__ == "__main__":
    main()
