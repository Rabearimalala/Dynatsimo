# -*- coding: utf-8 -*-
import sys

# 1. Update scripts/api-server.py
with open("scripts/api-server.py", "rb") as f:
    api_code = f.read()

api_code_norm = api_code.replace(b"\r\n", b"\n")

old_routes = b"""ROUTES = {
    "/api/overview": "overview",
    "/api/communes": "communes",
    "/api/annual-precipitations": "annualData",
    "/api/saisons": "seasonData",
    "/api/monthly-climatology": "monthlyClimatology",
    "/api/anomalies": "anomalies",
    "/api/precip-records": "precipRecords",
    "/api/communes.geojson": "communesGeojson",
    "/api/vegetation-data": "vegetationData",
}"""

new_routes = b"""ROUTES = {
    "/api/overview": "overview",
    "/api/communes": "communes",
    "/api/annual-precipitations": "annualData",
    "/api/saisons": "seasonData",
    "/api/monthly-climatology": "monthlyClimatology",
    "/api/anomalies": "anomalies",
    "/api/precip-records": "precipRecords",
    "/api/communes.geojson": "communesGeojson",
    "/api/vegetation-data": "vegetationData",
    "/api/correlation-ndvi-chirps": "correlationNdviChirps",
}"""

old_payload_inject = b"""            iso_path = ROOT_DIR / "public" / "data" / "isohyetes_metadata.json"
            if iso_path.exists():
                try:
                    with iso_path.open("r", encoding="utf-8") as f:
                        payload["isohyetesMeta"] = json.load(f)
                except Exception:
                    pass"""

new_payload_inject = b"""            iso_path = ROOT_DIR / "public" / "data" / "isohyetes_metadata.json"
            if iso_path.exists():
                try:
                    with iso_path.open("r", encoding="utf-8") as f:
                        payload["isohyetesMeta"] = json.load(f)
                except Exception:
                    pass

            corr_path = ROOT_DIR / "public" / "data" / "correlation_ndvi_chirps.json"
            if corr_path.exists():
                try:
                    with corr_path.open("r", encoding="utf-8") as f:
                        payload["correlationNdviChirps"] = json.load(f)
                except Exception:
                    pass"""

assert old_routes in api_code_norm, "old_routes not found in api-server.py"
assert old_payload_inject in api_code_norm, "old_payload_inject not found in api-server.py"

api_code_norm = api_code_norm.replace(old_routes, new_routes, 1)
api_code_norm = api_code_norm.replace(old_payload_inject, new_payload_inject, 1)

with open("scripts/api-server.py", "wb") as f:
    f.write(api_code_norm.replace(b"\n", b"\r\n"))
print("SUCCESS: api-server.py updated with correlation route & payload!")
