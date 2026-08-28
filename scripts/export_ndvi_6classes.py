"""
Pipeline automatique complet pour la classification NDVI (6 classes) et l'exportation des calques Web PNG.

Fonctionnalités :
1. Détecte automatiquement TOUS les rasters dans NDVI_MODIS (y compris les nouvelles années jusqu'en 2026+).
2. Si un raster n'est pas encore classifié dans RESULTATS_6_CLASSES, le classifie automatiquement en 6 classes.
3. Convertit tous les rasters classifiés en PNGs transparents optimisés pour Leaflet.
4. Met à jour en temps réel public/data/ndvi_classes_metadata.json pour l'interface React.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import re
import time
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "NDVI_MODIS"
CLASSIFIED_DIR = RAW_DIR / "RESULTATS_6_CLASSES"
OUTPUT_RASTER_DIR = ROOT_DIR / "public" / "data" / "raster" / "ndvi_modis_6classes"
METADATA_FILE = ROOT_DIR / "public" / "data" / "ndvi_classes_metadata.json"

MONTH_NAMES = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre",
}

MONTH_SHORT_NAMES = {
    1: "Jan",
    2: "Fév",
    3: "Mar",
    4: "Avr",
    5: "Mai",
    6: "Juin",
    7: "Juil",
    8: "Aoû",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Déc",
}

# 6 Classes officielles DYNATSIMO MODIS
CLASSES_DEFINITION = [
    {
        "id": 1,
        "label": "Eau",
        "range": "< 0",
        "description": "Surfaces en eau / plans d'eau",
        "color": "#0c19ff",
        "rgba": [12, 25, 255, 255],
    },
    {
        "id": 2,
        "label": "NDVI très faible",
        "range": "0 – 0.2",
        "description": "Sol nu, sables, végétation clairsemée",
        "color": "#87360c",
        "rgba": [135, 54, 12, 255],
    },
    {
        "id": 3,
        "label": "NDVI faible",
        "range": "0.2 – 0.4",
        "description": "Fourrés dégradés, savanes herbeuses sèches",
        "color": "#c46e2d",
        "rgba": [196, 110, 45, 255],
    },
    {
        "id": 4,
        "label": "NDVI moyen",
        "range": "0.4 – 0.6",
        "description": "Fourrés arbustifs, cultures actives",
        "color": "#96aa50",
        "rgba": [150, 170, 80, 255],
    },
    {
        "id": 5,
        "label": "NDVI élevé",
        "range": "0.6 – 0.8",
        "description": "Forêt sèche, canopée dense",
        "color": "#468237",
        "rgba": [70, 130, 55, 255],
    },
    {
        "id": 6,
        "label": "NDVI très élevé",
        "range": "0.8 – 1.0",
        "description": "Végétation très dense et humide",
        "color": "#00441b",
        "rgba": [0, 68, 27, 255],
    },
]

COLORMAP_DICT = {
    0: (0, 0, 0, 0),
    1: (12, 25, 255, 255),
    2: (135, 54, 12, 255),
    3: (196, 110, 45, 255),
    4: (150, 170, 80, 255),
    5: (70, 130, 55, 255),
    6: (0, 68, 27, 255),
}

# Lookup table vectorisée (256 valeurs uint8 -> RGBA)
COLOR_LUT = np.zeros((256, 4), dtype=np.uint8)
COLOR_LUT[0] = [0, 0, 0, 0]  # 0 = NoData
for cls in CLASSES_DEFINITION:
    COLOR_LUT[cls["id"]] = cls["rgba"]


def parse_year_month(filename: str) -> tuple[int, int] | None:
    match = re.search(r"((?:19|20)\d{2})[._-](1[0-2]|0[1-9]|[1-9])(?!\d)", filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None


def classify_and_generate_png(raw_tif: Path | None, classified_tif: Path | None) -> dict | None:
    """Classifie le raster brut si nécessaire et génère le calque PNG transparent."""
    # Déterminer année et mois
    ref_name = classified_tif.name if classified_tif else raw_tif.name
    parsed = parse_year_month(ref_name)
    if not parsed:
        return None
    year, month = parsed

    # Chemins de sortie
    out_dir = OUTPUT_RASTER_DIR / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / f"ndvi_class_{year}_{month:02d}.png"

    classified_dest = CLASSIFIED_DIR / str(year) / f"NDVI_CLASS_{year}_{month:02d}.tif"
    classified_dest.parent.mkdir(parents=True, exist_ok=True)

    classified_data = None
    bounds = None
    width, height = 0, 0

    # 1. Si le raster classifié existe déjà, le lire
    if classified_tif and classified_tif.exists() and classified_tif.stat().st_size > 1000:
        try:
            with rasterio.open(classified_tif) as src:
                classified_data = src.read(1)
                width = src.width
                height = src.height
                bounds = [
                    [float(src.bounds.bottom), float(src.bounds.left)],
                    [float(src.bounds.top), float(src.bounds.right)],
                ]
        except Exception:
            classified_data = None

    # 2. Sinon, classifier à partir du raster brut
    if classified_data is None and raw_tif and raw_tif.exists() and raw_tif.stat().st_size > 1000:
        try:
            with rasterio.open(raw_tif) as src:
                raw_ndvi = src.read(1).astype(np.float32)
                width = src.width
                height = src.height
                profile = src.profile.copy()
                nodata = src.nodata

                bounds = [
                    [float(src.bounds.bottom), float(src.bounds.left)],
                    [float(src.bounds.top), float(src.bounds.right)],
                ]

                # Masque de validité
                valid_mask = np.isfinite(raw_ndvi)
                if nodata is not None:
                    valid_mask &= (raw_ndvi != nodata)

                valid_values = raw_ndvi[valid_mask]
                if len(valid_values) > 0:
                    # Facteur d'échelle MODIS
                    if np.max(valid_values) > 2.0:
                        raw_ndvi[valid_mask] /= 10000.0

                    classified_data = np.zeros(raw_ndvi.shape, dtype=np.uint8)
                    classified_data[valid_mask & (raw_ndvi < 0)] = 1
                    classified_data[valid_mask & (raw_ndvi >= 0) & (raw_ndvi <= 0.2)] = 2
                    classified_data[valid_mask & (raw_ndvi > 0.2) & (raw_ndvi <= 0.4)] = 3
                    classified_data[valid_mask & (raw_ndvi > 0.4) & (raw_ndvi <= 0.6)] = 4
                    classified_data[valid_mask & (raw_ndvi > 0.6) & (raw_ndvi <= 0.8)] = 5
                    classified_data[valid_mask & (raw_ndvi > 0.8) & (raw_ndvi <= 1.0)] = 6

                    # Sauvegarde du GeoTIFF classifié
                    profile.update(
                        dtype=rasterio.uint8,
                        count=1,
                        nodata=0,
                    )
                    with rasterio.open(classified_dest, "w", **profile) as dst:
                        dst.write(classified_data, 1)
                        try:
                            dst.write_colormap(1, COLORMAP_DICT)
                        except Exception:
                            pass
        except Exception as e:
            print(f"Erreur lors de la classification de {raw_tif}: {e}")
            return None

    if classified_data is None or bounds is None:
        return None

    # 3. Génération du PNG transparent
    rgba = COLOR_LUT[classified_data]
    img = Image.fromarray(rgba, mode="RGBA")
    img.save(out_png, format="PNG", optimize=True)

    rel_png_url = f"/data/raster/ndvi_modis_6classes/{year}/ndvi_class_{year}_{month:02d}.png"

    return {
        "key": f"{year}_{month:02d}",
        "year": year,
        "month": month,
        "label": f"{MONTH_NAMES.get(month, '')} {year}",
        "shortLabel": f"{MONTH_SHORT_NAMES.get(month, '')} {year}",
        "pngUrl": rel_png_url,
        "width": width,
        "height": height,
        "bounds": bounds,
    }


def sync_all_ndvi_rasters():
    """Scanne tous les rasters bruts et classifiés et synchronise tout le catalogue."""
    start_time = time.time()
    print("--- DYNATSIMO : Synchronisation Complète des Rasters NDVI (2000 - 2026+) ---")

    # 1. Indexer tous les rasters bruts disponibles
    raw_files = {}
    if RAW_DIR.exists():
        for path in RAW_DIR.rglob("*.tif"):
            if "RESULTATS_6_CLASSES" not in path.parts:
                parsed = parse_year_month(path.name)
                if parsed:
                    raw_files[parsed] = path

    # 2. Indexer tous les rasters classifiés existants
    classified_files = {}
    if CLASSIFIED_DIR.exists():
        for path in CLASSIFIED_DIR.rglob("*.tif"):
            parsed = parse_year_month(path.name)
            if parsed:
                classified_files[parsed] = path

    all_keys = sorted(list(set(raw_files.keys()) | set(classified_files.keys())))
    print(f"{len(all_keys)} périodes mensuelles détectées (de {all_keys[0]} à {all_keys[-1]}).")

    OUTPUT_RASTER_DIR.mkdir(parents=True, exist_ok=True)

    tasks = []
    for key in all_keys:
        raw_tif = raw_files.get(key)
        cls_tif = classified_files.get(key)
        tasks.append((raw_tif, cls_tif))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(classify_and_generate_png, raw_tif, cls_tif): (raw_tif, cls_tif)
            for raw_tif, cls_tif in tasks
        }
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    results.sort(key=lambda x: (x["year"], x["month"]))
    print(f"{len(results)} calques PNG synchronisés avec succès.")

    if not results:
        return {}

    global_bounds = results[0]["bounds"]
    available_years = sorted(list(set(r["year"] for r in results)))
    periods_map = {r["key"]: r for r in results}

    metadata = {
        "sensor": "MODIS NDVI (TERRA/AQUA 250m)",
        "classesCount": 6,
        "bounds": global_bounds,
        "classes": CLASSES_DEFINITION,
        "years": available_years,
        "periods": results,
        "periodsMap": periods_map,
        "totalRasters": len(results),
        "startPeriod": results[0]["key"],
        "endPeriod": results[-1]["key"],
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Catalogue mis à jour : {len(available_years)} années disponibles ({available_years[0]} à {available_years[-1]}).")
    print(f"Durée totale de synchronisation : {round(time.time() - start_time, 2)} s.")
    return metadata


if __name__ == "__main__":
    sync_all_ndvi_rasters()
