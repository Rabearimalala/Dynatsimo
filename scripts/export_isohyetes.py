"""
Script d'exportation des Isohyètes CHIRPS pour Dynatsimo.
Génère :
1. GeoTIFFs d'isohyètes valides dans CHIRPS_data/isohyetes/
2. Calques Rasters PNG transparents dans public/data/raster/isohyetes/
3. Courbes de niveau vectorielles GeoJSON dans public/data/isohyetes/
4. Métadonnées indexées dans public/data/isohyetes_metadata.json
"""

import os
import sys
import re
import json
import time
from pathlib import Path

# Force stdout UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parents[1]
CHIRPS_DIR = ROOT_DIR / "CHIRPS_data"
ISOHYETES_TIF_DIR = CHIRPS_DIR / "isohyetes"
PUBLIC_DATA_DIR = ROOT_DIR / "public" / "data"
PUBLIC_RASTER_DIR = PUBLIC_DATA_DIR / "raster" / "isohyetes"
PUBLIC_GEOJSON_DIR = PUBLIC_DATA_DIR / "isohyetes"
METADATA_FILE = PUBLIC_DATA_DIR / "isohyetes_metadata.json"

ISOHYETES_TIF_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_RASTER_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_GEOJSON_DIR.mkdir(parents=True, exist_ok=True)

MONTH_KEYS = {
    "Jan": 1, "Fev": 2, "Mar": 3, "Avr": 4, "Mai": 5, "Jun": 6,
    "Jul": 7, "Aou": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}
MONTH_NAMES_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

def compute_decades(min_year=1981, max_year=2026):
    """Calcule les tranches de décennies dynamiquement de 1981 jusqu'à max_year."""
    decades = []
    if min_year <= 1989:
        decades.append(("1981–1989", 1981, min(1989, max_year)))
    for start in range(1990, max_year + 1, 10):
        end = min(start + 9, max_year)
        decades.append((f"{start}–{end}", start, end))
    return decades

def get_color_for_level(level_mm):
    """Retourne une couleur hex en fonction du niveau d'isohyète (6 teintes de bleu)."""
    if level_mm < 50:
        return "#dbeafe"
    elif level_mm < 100:
        return "#93c5fd"
    elif level_mm < 200:
        return "#3b82f6"
    elif level_mm < 350:
        return "#1d4ed8"
    elif level_mm < 500:
        return "#1e40af"
    else:
        return "#172554"

def process_grid_to_outputs(grid, valid, transform, base_key, label, meta_dict, save_tif_path=None, meta_profile=None, step_mm=50.0):
    """
    Convertit une grille de précipitations (mm) en :
    - PNG transparent géoréférencé
    - GeoJSON des courbes isohyètes avec intervalle constant (ex: 50 mm)
    - GeoTIFF si save_tif_path est spécifié
    """
    h, w = grid.shape
    v_min = float(np.nanmin(grid)) if np.any(valid) else 0.0
    v_max = float(np.nanmax(grid)) if np.any(valid) else 0.0
    v_mean = float(np.nanmean(grid)) if np.any(valid) else 0.0

    # 1. GeoTIFF
    if save_tif_path and meta_profile:
        try:
            iso_data = np.full(grid.shape, -9999.0, dtype=np.float32)
            iso_data[valid] = np.ceil(grid[valid] / 50.0) * 50.0
            prof = meta_profile.copy()
            prof.update(driver="GTiff", dtype="float32", count=1, nodata=-9999.0, compress="deflate")
            prof.pop("tiled", None)
            if isinstance(save_tif_path, Path):
                save_tif_path.unlink(missing_ok=True)
            elif os.path.exists(save_tif_path):
                os.remove(save_tif_path)
            with rasterio.open(save_tif_path, "w", **prof) as dst:
                dst.write(iso_data, 1)
        except Exception as err:
            pass # Si le fichier est ouvert dans QGIS ou verrouillé, continuer sans crasher

    # 2. PNG Raster
    # Palette en teintes chaudes douces (Sable, Ambre pastel, Terre cuite douce) pour faire ressortir les courbes bleues
    norm_val = np.clip(grid / max(v_max, 50.0), 0, 1)
    from matplotlib.colors import LinearSegmentedColormap
    warm_sand_cmap = LinearSegmentedColormap.from_list(
        "warm_sand",
        ["#fffbeb", "#fef3c7", "#fed7aa", "#fdba74", "#f97316", "#c2410c"]
    )
    rgba_arr = warm_sand_cmap(norm_val)
    rgba_bytes = (rgba_arr * 255).astype(np.uint8)
    rgba_bytes[~valid] = [0, 0, 0, 0] # transparent

    img = Image.fromarray(rgba_bytes, "RGBA")
    img_smooth = img.resize((w * 4, h * 4), Image.Resampling.BILINEAR)
    png_rel_path = f"/data/raster/isohyetes/{base_key}.png"
    png_file = PUBLIC_RASTER_DIR / f"{base_key}.png"
    img_smooth.save(png_file, optimize=True)

    # 3. GeoJSON Contours avec intervalle de 50 mm
    step = float(step_mm)
    start = np.ceil(v_min / step) * step
    end = np.floor(v_max / step) * step
    if end >= start:
        levels = np.arange(start, end + (step / 2.0), step)
    else:
        # Si la plage est < 50 mm (ex: mois très sec), pas de 25 ou 10 mm
        if (v_max - v_min) >= 15.0:
            sub_step = 25.0 if (v_max - v_min) >= 30.0 else 10.0
            sub_start = np.ceil(v_min / sub_step) * sub_step
            sub_end = np.floor(v_max / sub_step) * sub_step
            if sub_end >= sub_start:
                levels = np.arange(sub_start, sub_end + (sub_step / 2.0), sub_step)
            else:
                levels = np.array([])
        else:
            levels = np.array([])
    levels = [lvl for lvl in levels if lvl >= v_min and lvl <= v_max]

    xs = np.array([transform * (c + 0.5, 0.5) for c in range(w)])[:, 0]
    ys = np.array([transform * (0.5, r + 0.5) for r in range(h)])[:, 1]
    X, Y = np.meshgrid(xs, ys)

    features = []
    if len(levels) > 0:
        try:
            cs = plt.contour(X, Y, grid, levels=levels)
            for level, segs in zip(cs.levels, cs.allsegs):
                lvl_val = int(round(level)) if level == int(level) else round(float(level), 1)
                color = get_color_for_level(lvl_val)
                for seg in segs:
                    if len(seg) >= 2:
                        coords = [[round(float(pt[0]), 4), round(float(pt[1]), 4)] for pt in seg]
                        features.append({
                            "type": "Feature",
                            "geometry": {"type": "LineString", "coordinates": coords},
                            "properties": {
                                "isohyete": lvl_val,
                                "label": f"{lvl_val} mm",
                                "color": color
                            }
                        })
            plt.close()
        except Exception:
            plt.close()

    geojson = {"type": "FeatureCollection", "features": features}
    geojson_rel_path = f"/data/isohyetes/{base_key}.json"
    geojson_file = PUBLIC_GEOJSON_DIR / f"{base_key}.json"
    with open(geojson_file, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    meta_dict[base_key] = {
        "key": base_key,
        "label": label,
        "pngUrl": png_rel_path,
        "geojsonUrl": geojson_rel_path,
        "minPrecip": round(v_min, 1),
        "maxPrecip": round(v_max, 1),
        "meanPrecip": round(v_mean, 1),
        "levels": [int(l) if l == int(l) else float(l) for l in levels]
    }

def main():
    print("=" * 70)
    print("DYNATSIMO - EXPORTATION DES ISOHYÈTES CHIRPS")
    print("=" * 70)
    t0 = time.time()

    # Détection des rasters CHIRPS
    pattern = re.compile(r"^chirps-v2\.0\.(\d{4})\.(\d{2})\.tif$", re.IGNORECASE)
    monthly_rasters = {}

    for fname in sorted(os.listdir(CHIRPS_DIR)):
        m = pattern.match(fname)
        if not m:
            continue
        year, month = int(m.group(1)), int(m.group(2))
        monthly_rasters[(year, month)] = CHIRPS_DIR / fname

    if not monthly_rasters:
        print("❌ Aucun fichier CHIRPS trouvé.")
        return

    # Charger le premier pour profil & coordonnées
    first_path = list(monthly_rasters.values())[0]
    with rasterio.open(first_path) as src:
        first_profile = src.profile.copy()
        first_transform = src.transform
        b = src.bounds
        # Leaflet bounds: [[south, west], [north, east]]
        bounds_leaf = [[float(b.bottom), float(b.left)], [float(b.top), float(b.right)]]

    all_detected_years = sorted(list(set(y for y, _ in monthly_rasters.keys())))
    min_year = all_detected_years[0] if all_detected_years else 1981
    max_year = all_detected_years[-1] if all_detected_years else 2026
    decades_list = compute_decades(min_year=min_year, max_year=max_year)

    metadata = {
        "bounds": bounds_leaf,
        "years": all_detected_years,
        "decades": [d[0] for d in decades_list],
        "items": {}
    }

    print(f"✓ {len(monthly_rasters)} rasters mensuels détectés ({min_year} - {max_year}).")

    # 1. Traitement mensuel
    yearly_grids = {} # year -> list of (h, w) grids
    decade_grids = {dec_label: [] for dec_label, _, _ in decades_list}

    for (year, month), path in sorted(monthly_rasters.items()):
        with rasterio.open(path) as src:
            data = src.read(1).astype(np.float32)
            nodata = src.nodata if src.nodata is not None else -9999.0
            valid = (data != nodata) & np.isfinite(data) & (data >= 0)
            grid = np.where(valid, data, np.nan)

        if year not in yearly_grids:
            yearly_grids[year] = []
        yearly_grids[year].append(grid)

        for dec_label, d_start, d_end in decades_list:
            if d_start <= year <= d_end:
                decade_grids[dec_label].append(grid)

        base_key = f"isohyete_{year}_{month:02d}"
        label = f"{MONTH_NAMES_FR[month-1]} {year}"
        tif_path = ISOHYETES_TIF_DIR / f"isohyetes_{year}_{month:02d}.tif"

        process_grid_to_outputs(
            grid=grid,
            valid=valid,
            transform=first_transform,
            base_key=base_key,
            label=label,
            meta_dict=metadata["items"],
            save_tif_path=tif_path,
            meta_profile=first_profile
        )

    # 2. Cumul / Moyenne Annuelle pour chaque année
    for year, grids in yearly_grids.items():
        if not grids:
            continue
        stacked = np.array(grids)
        annual_sum = np.nansum(stacked, axis=0)
        valid = np.isfinite(annual_sum) & (annual_sum > 0)
        grid = np.where(valid, annual_sum, np.nan)

        base_key = f"isohyete_{year}_annual"
        label = f"Année {year} (Cumul annuel)"
        process_grid_to_outputs(
            grid=grid,
            valid=valid,
            transform=first_transform,
            base_key=base_key,
            label=label,
            meta_dict=metadata["items"],
            step_mm=50.0
        )

    # 3. Moyenne par Décennie
    for dec_label, grids in decade_grids.items():
        if not grids:
            continue
        stacked = np.array(grids)
        dec_mean = np.nanmean(stacked, axis=0) * 12.0 # cumul annuel moyen
        valid = np.isfinite(dec_mean) & (dec_mean > 0)
        grid = np.where(valid, dec_mean, np.nan)

        safe_dec = dec_label.replace("–", "_").replace("-", "_")
        base_key = f"isohyete_decade_{safe_dec}"
        label = f"Décennie {dec_label} (Moyenne annuelle)"
        process_grid_to_outputs(
            grid=grid,
            valid=valid,
            transform=first_transform,
            base_key=base_key,
            label=label,
            meta_dict=metadata["items"],
            step_mm=50.0
        )

    # Sauvegarder les métadonnées globales
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - t0
    print(f"✓ Génération terminée avec succès en {elapsed:.1f} secondes.")
    print(f"✓ Total calques générés : {len(metadata['items'])}")
    print(f"✓ Fichier métadonnées : {METADATA_FILE}")

if __name__ == "__main__":
    main()
