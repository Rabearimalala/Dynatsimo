#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DYNATSIMO — Analyse Spatio-Temporelle des Relations entre NDVI et CHIRPS (Par Mois / Année & Globale)

Ce script :
1. Calcule la relation couplée mensuelle pixel par pixel pour chaque mois et chaque année (2000 à 2026+) :
   - Indice de Couplage Agro-Climatique (Joint Drought & Vigor Index basé sur anomalies standardisées)
   - Classification en 5 états d'interaction Eau-Végétation (Sécheresse, Stress hydrique, Normal, Favorable, Vigueur max).
2. Sauvegarde tous les rasters bruts GeoTIFF par mois/année dans 'NDVI_CHIRPS/{annee}/NDVI_CHIRPS_{annee}_{mois}.tif'.
3. Génère les calques Web PNG transparents optimisés pour Leaflet dans 'public/data/raster/ndvi_chirps/{annee}/'.
4. Calcule les métriques globales multi-annuelles (Corrélation de Pearson Lag 0, Lag 1, Décalage optimal, Pente de régression, p-value).
5. Met à jour automatiquement 'public/data/ndvi_chirps_metadata.json' pour l'affichage interactif dans React.
6. Publie l'ensemble des rasters et styles SLD dans GeoServer (optionnel avec --publish-geoserver).

Usage :
    python scripts/analyse_relation_ndvi_chirps.py
    python scripts/analyse_relation_ndvi_chirps.py --publish-geoserver
    python scripts/analyse_relation_ndvi_chirps.py --start-year 2015 --end-year 2026
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

# Forcer UTF-8 sous Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
import rasterio
from rasterio.warp import Resampling, reproject
import requests
from requests.auth import HTTPBasicAuth
import scipy.stats as stats

# Ignorer les avertissements sur tranches vides (pixels maritimes ou hors zone)
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Degrees of freedom <= 0 for slice.*")

ROOT_DIR = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

CHIRPS_DIR = ROOT_DIR / "CHIRPS_data"
MODIS_DIR = ROOT_DIR / "NDVI_MODIS"
OUTPUT_DIR = ROOT_DIR / "NDVI_CHIRPS"
PUBLIC_DATA_DIR = ROOT_DIR / "public" / "data"
PUBLIC_RASTER_DIR = PUBLIC_DATA_DIR / "raster" / "ndvi_chirps"
METADATA_FILE = PUBLIC_DATA_DIR / "ndvi_chirps_metadata.json"

# Configuration GeoServer
GEOSERVER_URL = os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver").rstrip("/")
GS_USER = os.getenv("GEOSERVER_USER", "admin")
GS_PASSWORD = os.getenv("GEOSERVER_PASSWORD", "geoserver")
WORKSPACE = os.getenv("GEOSERVER_WORKSPACE", "dynatsimo")
NAMESPACE_URI = os.getenv("GEOSERVER_NAMESPACE", "http://dynatsimo")

AUTH = HTTPBasicAuth(GS_USER, GS_PASSWORD)
HEADERS_XML = {"Content-Type": "application/xml"}
HEADERS_JSON = {"Content-Type": "application/json", "Accept": "application/json"}
HEADERS_SLD = {"Content-Type": "application/vnd.ogc.sld+xml"}

MONTH_NAMES_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

MONTH_SHORT_FR = {
    1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
    5: "Mai", 6: "Juin", 7: "Juil", 8: "Août",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc"
}

# Définition des 5 classes officielles de relation NDVI-CHIRPS
RELATION_CLASSES = [
    {
        "id": 1,
        "label": "Grande sécheresse",
        "description": "Végétation très sèche, manque d'eau critique",
        "color": "#dc2626",
        "rgba": [220, 38, 38, 230]
    },
    {
        "id": 2,
        "label": "Manque d'eau",
        "description": "Peu de pluie, la végétation jaunit",
        "color": "#ea580c",
        "rgba": [234, 88, 12, 230]
    },
    {
        "id": 3,
        "label": "Situation normale",
        "description": "Pluie et verdure habituelles pour la saison",
        "color": "#eab308",
        "rgba": [234, 179, 8, 220]
    },
    {
        "id": 4,
        "label": "Bonne pousse",
        "description": "Bonnes pluies, la végétation reverdit bien",
        "color": "#16a34a",
        "rgba": [22, 163, 74, 230]
    },
    {
        "id": 5,
        "label": "Très verdoyant",
        "description": "Pluies abondantes, végétation dense et verte",
        "color": "#15803d",
        "rgba": [21, 128, 61, 240]
    }
]

# Styles SLD pour GeoServer
SLD_RELATION_5CLASSES = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>style_relation_ndvi_chirps_5classes</Name>
    <UserStyle>
      <Title>Relation Mensuelle NDVI - CHIRPS (5 Classes)</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="values">
              <ColorMapEntry color="#000000" quantity="0" opacity="0.0" label="NoData"/>
              <ColorMapEntry color="#dc2626" quantity="1" opacity="0.9" label="Grande sécheresse"/>
              <ColorMapEntry color="#ea580c" quantity="2" opacity="0.9" label="Manque d'eau"/>
              <ColorMapEntry color="#eab308" quantity="3" opacity="0.85" label="Situation normale"/>
              <ColorMapEntry color="#16a34a" quantity="4" opacity="0.9" label="Bonne pousse"/>
              <ColorMapEntry color="#15803d" quantity="5" opacity="0.95" label="Très verdoyant"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
"""

SLD_CORRELATION = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>style_correlation_ndvi_chirps</Name>
    <UserStyle>
      <Title>Corrélation NDVI vs CHIRPS (-1 à +1)</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="ramp">
              <ColorMapEntry color="#d73027" quantity="-1.0" opacity="0.9" label="-1.0 (Forte négative)"/>
              <ColorMapEntry color="#f46d43" quantity="-0.5" opacity="0.9" label="-0.5"/>
              <ColorMapEntry color="#fee08b" quantity="-0.1" opacity="0.8" label="-0.1"/>
              <ColorMapEntry color="#ffffbf" quantity="0.0" opacity="0.5" label="0.0 (Nulle)"/>
              <ColorMapEntry color="#d9ef8b" quantity="0.2" opacity="0.8" label="0.2 (Faible)"/>
              <ColorMapEntry color="#91cf60" quantity="0.5" opacity="0.9" label="0.5 (Modérée)"/>
              <ColorMapEntry color="#1a9850" quantity="0.8" opacity="0.95" label="0.8 (Forte)"/>
              <ColorMapEntry color="#006837" quantity="1.0" opacity="1.0" label="1.0 (Très forte)"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
"""

SLD_LAG = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>style_lag_optimal</Name>
    <UserStyle>
      <Title>Décalage Optimal NDVI-CHIRPS (Mois)</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="values">
              <ColorMapEntry color="#ffff33" quantity="0" opacity="0.85" label="Lag 0 (Même mois)"/>
              <ColorMapEntry color="#4daf4a" quantity="1" opacity="0.85" label="Lag 1 (1 mois de retard)"/>
              <ColorMapEntry color="#377eb8" quantity="2" opacity="0.85" label="Lag 2 (2 mois de retard)"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
"""


# ==============================================================================
# 1. HARMONISATION SPATIALE & DÉTECTION
# ==============================================================================

def find_matched_dates(start_year: int | None = None, end_year: int | None = None) -> List[Tuple[int, int, Path, Path]]:
    chirps_map: Dict[Tuple[int, int], Path] = {}
    for f in CHIRPS_DIR.glob("chirps-v2.0.*.*.tif"):
        m = re.search(r"chirps-v2\.0\.(\d{4})\.(\d{2})\.tif", f.name)
        if m:
            chirps_map[(int(m.group(1)), int(m.group(2)))] = f

    ndvi_map: Dict[Tuple[int, int], Path] = {}
    for f in MODIS_DIR.rglob("*.tif"):
        if "RESULTATS_6_CLASSES" in f.parts:
            continue
        m = re.search(r"(\d{4})_(\d{2})", f.name)
        if m:
            ndvi_map[(int(m.group(1)), int(m.group(2)))] = f

    matched = []
    common = sorted(list(set(chirps_map.keys()).intersection(set(ndvi_map.keys()))))
    for y, mm in common:
        if start_year and y < start_year:
            continue
        if end_year and y > end_year:
            continue
        matched.append((y, mm, chirps_map[(y, mm)], ndvi_map[(y, mm)]))

    return matched


def create_relation_png(classified_data: np.ndarray, out_png_path: Path) -> None:
    """Génère une image PNG transparente avec la palette des 5 classes pour Leaflet."""
    out_png_path.parent.mkdir(parents=True, exist_ok=True)
    H, W = classified_data.shape
    rgba = np.zeros((H, W, 4), dtype=np.uint8)

    for item in RELATION_CLASSES:
        mask = (classified_data == item["id"])
        rgba[mask] = item["rgba"]

    img = Image.fromarray(rgba, mode="RGBA")
    img.save(out_png_path, optimize=True)


def create_continuous_png(
    data: np.ndarray,
    out_png_path: Path,
    vmin: float = -1.0,
    vmax: float = 1.0,
    nodata: float = -9999.0,
    colormap_type: str = "correlation"
) -> None:
    """Génère un PNG transparent à rampe continue pour la corrélation ou le lag."""
    out_png_path.parent.mkdir(parents=True, exist_ok=True)
    H, W = data.shape
    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    valid_mask = ~np.isnan(data) & (data != nodata)

    if colormap_type == "lag":
        # Palette discrète : Lag 0 (Jaune), Lag 1 (Vert), Lag 2 (Bleu)
        rgba[valid_mask & (data == 0)] = [255, 255, 51, 220]
        rgba[valid_mask & (data == 1)] = [77, 175, 74, 220]
        rgba[valid_mask & (data == 2)] = [55, 126, 184, 220]
    else:
        # Corrélation -1 à +1 : RdYlGn
        norm = np.clip((data - vmin) / (vmax - vmin), 0.0, 1.0)
        for i in range(H):
            for j in range(W):
                if not valid_mask[i, j]:
                    continue
                val = norm[i, j]
                # Palette simplifiée RdYlGn
                if val < 0.35:  # Négatif -> Rouge / Orange
                    r = int(215 + (244 - 215) * (val / 0.35))
                    g = int(48 + (109 - 48) * (val / 0.35))
                    b = int(39 + (67 - 39) * (val / 0.35))
                elif val < 0.5:  # Autour de 0 -> Jaune
                    r = 254
                    g = int(224 + (255 - 224) * ((val - 0.35) / 0.15))
                    b = 139
                elif val < 0.75:  # Faible à modéré -> Vert clair
                    r = int(217 - (217 - 145) * ((val - 0.5) / 0.25))
                    g = int(239 - (239 - 207) * ((val - 0.5) / 0.25))
                    b = int(139 - (139 - 96) * ((val - 0.5) / 0.25))
                else:  # Fort -> Vert foncé
                    r = int(26 - 26 * ((val - 0.75) / 0.25))
                    g = int(152 - (152 - 104) * ((val - 0.75) / 0.25))
                    b = int(80 - (80 - 55) * ((val - 0.75) / 0.25))
                rgba[i, j] = [r, g, b, 225]

    img = Image.fromarray(rgba, mode="RGBA")
    img.save(out_png_path, optimize=True)


def save_geotiff(
    data: np.ndarray,
    out_path: Path,
    meta: dict,
    nodata: float = 0.0,
    dtype: str = "uint8"
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_meta = meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": dtype,
        "nodata": nodata,
        "compress": "lzw"
    })
    out_data = np.where(np.isnan(data), nodata, data).astype(dtype)
    with rasterio.open(out_path, "w", **out_meta) as dst:
        dst.write(out_data, 1)


# ==============================================================================
# 2. CALCULS STATISTIQUES MULTI-ANNUELS
# ==============================================================================

def compute_multiyear_correlation(
    ndvi_stack: np.ndarray, chirps_stack: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Calcule les relations multi-annuelles : Lag 0, Lag 1, Lag Optimal, Slope, P-value."""
    T, H, W = ndvi_stack.shape

    def _calc_r(x_s, y_s):
        val_cnt = np.sum(~np.isnan(x_s) & ~np.isnan(y_s), axis=0)
        calc_m = val_cnt >= max(10, int(len(x_s) * 0.5))

        x_m = np.nanmean(x_s, axis=0)
        y_m = np.nanmean(y_s, axis=0)
        x_d = x_s - x_m
        y_d = y_s - y_m

        cov = np.nansum(x_d * y_d, axis=0)
        vx = np.nansum(x_d ** 2, axis=0)
        vy = np.nansum(y_d ** 2, axis=0)

        r_res = np.full((H, W), np.nan, dtype=np.float32)
        slope_res = np.full((H, W), np.nan, dtype=np.float32)
        p_res = np.full((H, W), np.nan, dtype=np.float32)

        denom = np.sqrt(vx * vy)
        valid = calc_m & (denom > 1e-8) & (vy > 1e-8)

        r_c = np.clip(cov[valid] / denom[valid], -1.0, 1.0)
        r_res[valid] = r_c
        slope_res[valid] = cov[valid] / vy[valid]

        df = val_cnt[valid] - 2
        t_stat = r_c * np.sqrt(df / np.maximum(1e-7, (1.0 - r_c ** 2)))
        p_res[valid] = 2.0 * (1.0 - stats.t.cdf(np.abs(t_stat), df=df))

        return r_res, p_res, slope_res

    r_lag0, p_lag0, slope = _calc_r(ndvi_stack, chirps_stack)
    r_lag1, _, _ = _calc_r(ndvi_stack[1:], chirps_stack[:-1])
    r_lag2, _, _ = _calc_r(ndvi_stack[2:], chirps_stack[:-2])

    stack_lags = np.stack([
        np.nan_to_num(r_lag0, nan=-999),
        np.nan_to_num(r_lag1, nan=-999),
        np.nan_to_num(r_lag2, nan=-999)
    ], axis=0)
    lag_opt = np.argmax(stack_lags, axis=0).astype(np.float32)
    lag_opt = np.where(np.isnan(r_lag0), np.nan, lag_opt)

    return r_lag0, r_lag1, lag_opt, slope, p_lag0


# ==============================================================================
# 3. PUBLICATION GEOSERVER
# ==============================================================================

def geoserver_publish(files_to_publish: List[Tuple[Path, str, str]]) -> int:
    """Publie un ensemble de rasters et leurs styles dans GeoServer."""
    try:
        url = f"{GEOSERVER_URL}/rest/about/version.json"
        res = requests.get(url, auth=AUTH, headers=HEADERS_JSON, timeout=5)
        if res.status_code != 200:
            print("⚠ GeoServer non accessible.")
            return 0
    except Exception:
        print("⚠ GeoServer non accessible.")
        return 0

    # Workspace
    w_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}.json"
    if requests.get(w_url, auth=AUTH, headers=HEADERS_JSON).status_code == 404:
        requests.post(f"{GEOSERVER_URL}/rest/workspaces", data=f"<workspace><name>{WORKSPACE}</name></workspace>", headers=HEADERS_XML, auth=AUTH)

    # Styles
    styles = {
        "style_relation_ndvi_chirps_5classes": SLD_RELATION_5CLASSES,
        "style_correlation_ndvi_chirps": SLD_CORRELATION,
        "style_lag_optimal": SLD_LAG,
    }
    for s_name, sld in styles.items():
        st_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles/{s_name}.json"
        if requests.get(st_url, auth=AUTH, headers=HEADERS_JSON).status_code == 404:
            requests.post(f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles?name={s_name}", data=sld.encode("utf-8"), headers=HEADERS_SLD, auth=AUTH)

    published = 0
    for tif_path, store_name, style_name in files_to_publish:
        if not tif_path.exists():
            continue
        c_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/coveragestores/{store_name}/file.geotiff?configure=first&coverageName={store_name}"
        with open(tif_path, "rb") as f:
            r = requests.put(c_url, data=f, headers={"Content-Type": "image/tiff"}, auth=AUTH, timeout=120)
        if r.status_code in (200, 201):
            if style_name:
                l_url = f"{GEOSERVER_URL}/rest/layers/{WORKSPACE}:{store_name}.xml"
                l_pay = f"<layer><defaultStyle><name>{WORKSPACE}:{style_name}</name><workspace>{WORKSPACE}</workspace></defaultStyle><opaque>false</opaque></layer>"
                requests.put(l_url, data=l_pay, headers=HEADERS_XML, auth=AUTH)
            published += 1
            print(f"  ✓ GeoServer : {WORKSPACE}:{store_name} publié.")
    return published


# ==============================================================================
# 4. PIPELINE PRINCIPAL
# ==============================================================================

def run_analysis_pipeline(
    start_year: int | None = None,
    end_year: int | None = None,
    publish_geoserver: bool = False
) -> bool:
    t_start = time.time()
    print("\n" + "=" * 75)
    print("🌾 DYNATSIMO — ANALYSE RELATION NDVI vs CHIRPS PAR MOIS & ANNÉE")
    print("=" * 75)

    matched = find_matched_dates(start_year, end_year)
    if not matched:
        print("❌ Aucun couple de rasters CHIRPS/NDVI trouvé.")
        return False

    T = len(matched)
    print(f"📅 Nombre de mois analysés : {T} mois ({matched[0][0]}-{matched[0][1]:02d} à {matched[-1][0]}-{matched[-1][1]:02d})")

    # Grille de référence CHIRPS
    with rasterio.open(matched[0][2]) as ref_c:
        ref_meta = ref_c.meta.copy()
        target_shape = ref_c.shape
        target_transform = ref_c.transform
        target_crs = ref_c.crs
        chirps_nodata = ref_c.nodata if ref_c.nodata is not None else -9999.0

    H, W = target_shape
    leaflet_bounds = [
        [float(target_transform[5] + H * target_transform[4]), float(target_transform[2])],
        [float(target_transform[5]), float(target_transform[2] + W * target_transform[0])]
    ]

    # 1. Chargement et harmonisation spatiale
    print("\n⏳ Étape 1/4 : Chargement et rééchantillonnage de la pile spatio-temporelle...")
    chirps_stack = np.full((T, H, W), np.nan, dtype=np.float32)
    ndvi_stack = np.full((T, H, W), np.nan, dtype=np.float32)

    for idx, (y, mm, c_path, n_path) in enumerate(matched):
        with rasterio.open(c_path) as c_src:
            c_d = c_src.read(1)
            chirps_stack[idx] = np.where((c_d == chirps_nodata) | (c_d < 0), np.nan, c_d)

        with rasterio.open(n_path) as n_src:
            n_d = n_src.read(1)
            n_d = np.where((n_d == 0.0) | (n_d < -0.2) | (n_d > 1.0), np.nan, n_d)
            reproj_ndvi = np.full(target_shape, np.nan, dtype=np.float32)
            reproject(
                source=n_d.astype(np.float32),
                destination=reproj_ndvi,
                src_transform=n_src.transform,
                src_crs=n_src.crs,
                dst_transform=target_transform,
                dst_crs=target_crs,
                resampling=Resampling.bilinear,
                src_nodata=np.nan,
                dst_nodata=np.nan
            )
            ndvi_stack[idx] = reproj_ndvi

    # 2. Climatologie mensuelle pour le calcul des anomalies standardisées
    print("\n📊 Étape 2/4 : Calcul des anomalies standardisées et des relations mensuelles...")
    # Regrouper par mois de l'année (1 à 12) pour normaliser selon la saisonnalité
    monthly_stats = {}
    for m in range(1, 13):
        m_indices = [i for i, item in enumerate(matched) if item[1] == m]
        if m_indices:
            c_sub = chirps_stack[m_indices]
            n_sub = ndvi_stack[m_indices]
            monthly_stats[m] = {
                "c_mean": np.nanmean(c_sub, axis=0),
                "c_std": np.maximum(1e-4, np.nanstd(c_sub, axis=0)),
                "n_mean": np.nanmean(n_sub, axis=0),
                "n_std": np.maximum(1e-4, np.nanstd(n_sub, axis=0)),
            }

    # 3. Génération des rasters TIFF et PNG mensuels
    print(f"\n📂 Étape 3/4 : Sauvegarde des GeoTIFFs et PNGs mensuels dans 'NDVI_CHIRPS/{{annee}}/'...")
    periods_meta = []
    years_set = set()
    geoserver_queue = []

    for idx, (y, mm, _, _) in enumerate(matched):
        years_set.add(y)
        st = monthly_stats.get(mm)
        c_val = chirps_stack[idx]
        n_val = ndvi_stack[idx]

        valid_pix = ~np.isnan(c_val) & ~np.isnan(n_val) & ~np.isnan(st["c_mean"])

        # Anomalies standardisées Z
        z_c = np.full((H, W), np.nan, dtype=np.float32)
        z_n = np.full((H, W), np.nan, dtype=np.float32)
        z_c[valid_pix] = (c_val[valid_pix] - st["c_mean"][valid_pix]) / st["c_std"][valid_pix]
        z_n[valid_pix] = (n_val[valid_pix] - st["n_mean"][valid_pix]) / st["n_std"][valid_pix]

        # Indice combiné Joint Drought Index
        jdi = 0.5 * (z_c + z_n)

        # Classification en 5 catégories d'état Eau-Végétation
        # 1: Sévère (< -1.0) | 2: Stress (-1.0 à -0.3) | 3: Normal (-0.3 à +0.3) | 4: Favorable (+0.3 à +1.0) | 5: Vigueur max (> +1.0)
        rel_class = np.zeros((H, W), dtype=np.uint8)
        rel_class[valid_pix & (jdi < -1.0)] = 1
        rel_class[valid_pix & (jdi >= -1.0) & (jdi < -0.3)] = 2
        rel_class[valid_pix & (jdi >= -0.3) & (jdi <= 0.3)] = 3
        rel_class[valid_pix & (jdi > 0.3) & (jdi <= 1.0)] = 4
        rel_class[valid_pix & (jdi > 1.0)] = 5

        # Sauvegarde TIFF brut : NDVI_CHIRPS/{annee}/NDVI_CHIRPS_{annee}_{mois:02d}.tif
        year_tif_dir = OUTPUT_DIR / str(y)
        tif_path = year_tif_dir / f"NDVI_CHIRPS_{y}_{mm:02d}.tif"
        save_geotiff(rel_class, tif_path, ref_meta, nodata=0, dtype="uint8")

        # Sauvegarde PNG Web transparent : public/data/raster/ndvi_chirps/{annee}/ndvi_chirps_{annee}_{mois:02d}.png
        year_png_dir = PUBLIC_RASTER_DIR / str(y)
        png_path = year_png_dir / f"ndvi_chirps_{y}_{mm:02d}.png"
        create_relation_png(rel_class, png_path)

        store_name = f"ndvi_chirps_{y}_{mm:02d}"
        geoserver_queue.append((tif_path, store_name, "style_relation_ndvi_chirps_5classes"))

        period_item = {
            "key": f"{y}_{mm:02d}",
            "year": y,
            "month": mm,
            "label": f"{MONTH_NAMES_FR.get(mm, '')} {y}",
            "shortLabel": f"{MONTH_SHORT_FR.get(mm, '')} {y}",
            "pngUrl": f"/data/raster/ndvi_chirps/{y}/ndvi_chirps_{y}_{mm:02d}.png",
            "geotiffPath": str(tif_path.relative_to(ROOT_DIR)).replace("\\", "/"),
            "width": W,
            "height": H,
            "bounds": leaflet_bounds,
        }
        periods_meta.append(period_item)

        if (idx + 1) % 50 == 0 or (idx + 1) == T:
            print(f"   ✓ Traité et sauvegardé : {idx + 1}/{T} mois ({y}-{mm:02d})")

    # 4. Calculs multi-annuels globaux (Lag 0, Lag 1, Lag Optimal, Pente)
    print("\n🌐 Étape 4/4 : Calculs multi-annuels globaux et métadonnées...")
    r_lag0, r_lag1, lag_opt, slope, p_lag0 = compute_multiyear_correlation(ndvi_stack, chirps_stack)

    # Sauvegarde TIFFs globaux
    global_outputs = [
        ("ndvi_chirps_correlation_lag0.tif", r_lag0, "style_correlation_ndvi_chirps", -1.0, 1.0, "correlation"),
        ("ndvi_chirps_correlation_lag1.tif", r_lag1, "style_correlation_ndvi_chirps", -1.0, 1.0, "correlation"),
        ("ndvi_chirps_lag_optimal.tif", lag_opt, "style_lag_optimal", 0, 2, "lag"),
        ("ndvi_chirps_regression_slope.tif", slope, "style_correlation_ndvi_chirps", -0.001, 0.003, "correlation"),
        ("ndvi_chirps_pvalue_lag0.tif", p_lag0, "style_correlation_ndvi_chirps", 0.0, 1.0, "correlation"),
    ]

    global_png_dir = PUBLIC_RASTER_DIR / "global"
    for fname, data_arr, st_name, vmin, vmax, col_type in global_outputs:
        # Sauvegarde TIFF racine NDVI_CHIRPS/
        save_geotiff(data_arr, OUTPUT_DIR / fname, ref_meta, nodata=-9999.0, dtype="float32")
        # Sauvegarde PNG global
        png_name = fname.replace(".tif", ".png")
        create_continuous_png(data_arr, global_png_dir / png_name, vmin=vmin, vmax=vmax, nodata=-9999.0, colormap_type=col_type)
        geoserver_queue.append((OUTPUT_DIR / fname, fname.replace(".tif", ""), st_name))

    # Écriture du fichier de métadonnées JSON pour l'application React
    metadata = {
        "bounds": leaflet_bounds,
        "classesCount": 5,
        "classes": RELATION_CLASSES,
        "years": sorted(list(years_set)),
        "periods": periods_meta,
        "globalLayers": [
            {
                "id": "correlation_lag0",
                "label": "Corrélation Instantanée (Lag 0)",
                "description": "Liaison directe au cours du même mois (-1 à +1)",
                "pngUrl": "/data/raster/ndvi_chirps/global/ndvi_chirps_correlation_lag0.png",
                "storeName": "ndvi_chirps_correlation_lag0",
                "bounds": leaflet_bounds
            },
            {
                "id": "correlation_lag1",
                "label": "Corrélation Décalée 1 Mois (Lag 1)",
                "description": "Latence de la végétation réagissant 1 mois après la pluie (-1 à +1)",
                "pngUrl": "/data/raster/ndvi_chirps/global/ndvi_chirps_correlation_lag1.png",
                "storeName": "ndvi_chirps_correlation_lag1",
                "bounds": leaflet_bounds
            },
            {
                "id": "lag_optimal",
                "label": "Décalage Optimal de Croissance",
                "description": "Délai temporel maximisant la réponse (0 = même mois, 1 = 1 mois, 2 = 2 mois)",
                "pngUrl": "/data/raster/ndvi_chirps/global/ndvi_chirps_lag_optimal.png",
                "storeName": "ndvi_chirps_lag_optimal",
                "bounds": leaflet_bounds
            },
        ]
    }

    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"  💾 Métadonnées React sauvegardées : {METADATA_FILE.relative_to(ROOT_DIR)}")

    # 5. Publication GeoServer optionnelle
    if publish_geoserver:
        print("\n🌍 Publication dans GeoServer...")
        pub_count = geoserver_publish(geoserver_queue)
        print(f"✨ GeoServer : {pub_count} couche(s) synchronisée(s).")

    print("\n" + "=" * 75)
    print(f"✨ ANALYSE NDVI-CHIRPS PAR MOIS/ANNÉE TERMINÉE AVEC SUCCÈS ({time.time() - t_start:.1f}s) !")
    print(f"📁 Rasters TIFF bruts sauvegardés dans : {OUTPUT_DIR}/<ANNEE>/")
    print(f"🌐 Calques Web PNG prêts dans : {PUBLIC_RASTER_DIR}/")
    print("=" * 75 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Analyse spatio-temporelle NDVI vs CHIRPS par mois et année")
    parser.add_argument("--start-year", type=int, default=None, help="Année de début")
    parser.add_argument("--end-year", type=int, default=None, help="Année de fin")
    parser.add_argument("--publish-geoserver", action="store_true", help="Publier automatiquement dans GeoServer")
    args = parser.parse_args()

    run_analysis_pipeline(
        start_year=args.start_year,
        end_year=args.end_year,
        publish_geoserver=args.publish_geoserver
    )


if __name__ == "__main__":
    main()
