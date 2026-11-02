#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DYNATSIMO — Analyse Spatio-Temporelle des Relations entre NDVI et CHIRPS

Ce script calcule la relation statistique pixel par pixel entre l'indice de végétation (NDVI)
et les précipitations (CHIRPS) :
1. Corrélation de Pearson (Lag 0 : réponse immédiate le même mois).
2. Corrélation avec décalage temporel (Lag 1 & Lag 2 : latence de la réponse végétale 1 à 2 mois).
3. Lag optimal (le délai temporel offrant la meilleure réponse).
4. Degré de significativité statistique (p-value, test t de Student).
5. Régression linéaire : Pente (sensibilité du NDVI par mm de pluie) et R² (variance expliquée).
6. Sauvegarde des rasters bruts GeoTIFF dans le dossier 'NDVI_CHIRPS'.
7. Publication automatisée de tous les rasters et de leurs styles SLD dans GeoServer via REST API.

Usage :
    python scripts/analyse_relation_ndvi_chirps.py
    python scripts/analyse_relation_ndvi_chirps.py --publish-geoserver
    python scripts/analyse_relation_ndvi_chirps.py --start-year 2010 --end-year 2025
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

# Ignorer les avertissements sur tranches vides (pixels maritimes ou hors zone)
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Mean of empty slice.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Degrees of freedom <= 0 for slice.*")

# Forcer l'encodage UTF-8 sous Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject
import requests
from requests.auth import HTTPBasicAuth
import scipy.stats as stats

ROOT_DIR = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

CHIRPS_DIR = ROOT_DIR / "CHIRPS_data"
MODIS_DIR = ROOT_DIR / "NDVI_MODIS"
OUTPUT_DIR = ROOT_DIR / "NDVI_CHIRPS"

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


# ==============================================================================
# STYLES SLD POUR GEOSERVER
# ==============================================================================

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

SLD_PVALUE = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>style_pvalue_significativite</Name>
    <UserStyle>
      <Title>Significativité p-value</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="intervals">
              <ColorMapEntry color="#006d2c" quantity="0.01" opacity="0.9" label="Très significatif (p &lt; 0.01)"/>
              <ColorMapEntry color="#74c476" quantity="0.05" opacity="0.8" label="Significatif (p &lt; 0.05)"/>
              <ColorMapEntry color="#cccccc" quantity="1.00" opacity="0.3" label="Non significatif (p &gt;= 0.05)"/>
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

SLD_SLOPE = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>style_regression_slope</Name>
    <UserStyle>
      <Title>Sensibilité NDVI / Pluie (Pente x 100mm)</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="ramp">
              <ColorMapEntry color="#b2182b" quantity="-0.001" opacity="0.8" label="Négatif"/>
              <ColorMapEntry color="#ffffff" quantity="0.0" opacity="0.4" label="0.0"/>
              <ColorMapEntry color="#c7eae5" quantity="0.0005" opacity="0.8" label="Faible sensibilité"/>
              <ColorMapEntry color="#35978f" quantity="0.0015" opacity="0.9" label="Sensibilité moyenne"/>
              <ColorMapEntry color="#003c30" quantity="0.0030" opacity="0.95" label="Forte sensibilité"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
"""


# ==============================================================================
# FONCTIONS D'HARMONISATION ET CALCULS SCIENTIFIQUES
# ==============================================================================

def find_matched_dates(start_year: int | None = None, end_year: int | None = None) -> List[Tuple[str, str, Path, Path]]:
    """
    Associe chaque raster CHIRPS à son raster NDVI MODIS correspondant pour le même mois (AAAA, MM).
    """
    chirps_map: Dict[Tuple[str, str], Path] = {}
    for f in CHIRPS_DIR.glob("chirps-v2.0.*.*.tif"):
        m = re.search(r"chirps-v2\.0\.(\d{4})\.(\d{2})\.tif", f.name)
        if m:
            y, mm = m.groups()
            chirps_map[(y, mm)] = f

    ndvi_map: Dict[Tuple[str, str], Path] = {}
    for f in MODIS_DIR.rglob("*.tif"):
        if "RESULTATS_6_CLASSES" in f.parts:
            continue
        m = re.search(r"(\d{4})_(\d{2})", f.name)
        if m:
            y, mm = m.groups()
            ndvi_map[(y, mm)] = f

    matched = []
    common_dates = sorted(list(set(chirps_map.keys()).intersection(set(ndvi_map.keys()))))

    for y, mm in common_dates:
        yi = int(y)
        if start_year and yi < start_year:
            continue
        if end_year and yi > end_year:
            continue
        matched.append((y, mm, chirps_map[(y, mm)], ndvi_map[(y, mm)]))

    return matched


def compute_pixel_correlation(
    x_stack: np.ndarray, y_stack: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Calcule de manière vectorisée pixel par pixel :
    - Le coefficient de corrélation de Pearson r
    - La p-value (test t de Student à deux queues)
    - La pente de la régression linéaire (slope)
    - Le coefficient de détermination R²
    """
    T, H, W = x_stack.shape

    # Masque des pixels où toutes les dates ou au moins 80% sont valides
    valid_count = np.sum(~np.isnan(x_stack) & ~np.isnan(y_stack), axis=0)
    min_required = max(10, int(T * 0.5))
    mask = valid_count >= min_required

    # Remplacer les NaN temporairement par 0 pour le calcul vectorisé
    x = np.where(np.isnan(x_stack) | np.isnan(y_stack), np.nan, x_stack)
    y = np.where(np.isnan(x_stack) | np.isnan(y_stack), np.nan, y_stack)

    # Moyennes temporelles
    x_mean = np.nanmean(x, axis=0)
    y_mean = np.nanmean(y, axis=0)

    # Écarts à la moyenne
    x_dev = x - x_mean
    y_dev = y - y_mean

    # Sommes des produits croisés et des carrés
    cov = np.nansum(x_dev * y_dev, axis=0)
    var_x = np.nansum(x_dev ** 2, axis=0)
    var_y = np.nansum(y_dev ** 2, axis=0)

    # Initialisation des résultats avec NaN
    r = np.full((H, W), np.nan, dtype=np.float32)
    slope = np.full((H, W), np.nan, dtype=np.float32)
    p_val = np.full((H, W), np.nan, dtype=np.float32)
    r2 = np.full((H, W), np.nan, dtype=np.float32)

    # Calcul sur les pixels valides
    denom = np.sqrt(var_x * var_y)
    calc_mask = mask & (denom > 1e-8) & (var_y > 1e-8)

    r_calc = np.clip(cov[calc_mask] / denom[calc_mask], -1.0, 1.0)
    r[calc_mask] = r_calc
    r2[calc_mask] = r_calc ** 2
    slope[calc_mask] = cov[calc_mask] / var_y[calc_mask]

    # Test t pour la p-value
    df = valid_count[calc_mask] - 2
    t_stat = r_calc * np.sqrt(df / np.maximum(1e-7, (1.0 - r_calc ** 2)))
    p_calc = 2.0 * (1.0 - stats.t.cdf(np.abs(t_stat), df=df))
    p_val[calc_mask] = p_calc

    return r, p_val, slope, r2


def save_geotiff(
    data: np.ndarray,
    out_path: Path,
    reference_meta: dict,
    nodata: float = -9999.0,
    dtype: str = "float32"
) -> None:
    """Enregistre une matrice NumPy au format GeoTIFF géoréférencé."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    meta = reference_meta.copy()
    meta.update({
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": dtype,
        "nodata": nodata,
        "compress": "lzw"
    })

    # Convertir les NaN en valeur NoData
    out_data = np.where(np.isnan(data), nodata, data).astype(dtype)

    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(out_data, 1)

    print(f"  💾 Fichier sauvegardé : {out_path.name} ({out_path.stat().st_size / 1024:.1f} Ko)")


# ==============================================================================
# FONCTIONS DE PUBLICATION DANS GEOSERVER
# ==============================================================================

def geoserver_test_connection() -> bool:
    """Vérifie l'accès à GeoServer."""
    try:
        url = f"{GEOSERVER_URL}/rest/about/version.json"
        res = requests.get(url, auth=AUTH, headers=HEADERS_JSON, timeout=5)
        return res.status_code == 200
    except Exception:
        return False


def geoserver_ensure_workspace() -> bool:
    """Crée le workspace GeoServer s'il n'existe pas encore."""
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}.json"
    res = requests.get(url, auth=AUTH, headers=HEADERS_JSON)
    if res.status_code == 404:
        payload = f"<workspace><name>{WORKSPACE}</name></workspace>"
        c_res = requests.post(f"{GEOSERVER_URL}/rest/workspaces", data=payload, headers=HEADERS_XML, auth=AUTH)
        if c_res.status_code in (200, 201):
            ns_payload = f"<namespace><prefix>{WORKSPACE}</prefix><uri>{NAMESPACE_URI}</uri></namespace>"
            requests.put(f"{GEOSERVER_URL}/rest/namespaces/{WORKSPACE}", data=ns_payload, headers=HEADERS_XML, auth=AUTH)
            return True
        return False
    return res.status_code == 200


def geoserver_publish_style(style_name: str, sld_body: str) -> bool:
    """Téléverse un style SLD dans le workspace GeoServer."""
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles/{style_name}.json"
    res = requests.get(url, auth=AUTH, headers=HEADERS_JSON)
    if res.status_code == 404:
        create_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles?name={style_name}"
        res_post = requests.post(create_url, data=sld_body.encode("utf-8"), headers=HEADERS_SLD, auth=AUTH)
        return res_post.status_code in (200, 201)
    return True


def geoserver_publish_raster(file_path: Path, store_name: str, style_name: str | None = None) -> bool:
    """Publie un raster GeoTIFF et applique son style SLD."""
    if not file_path.exists():
        return False

    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/coveragestores/{store_name}/file.geotiff?configure=first&coverageName={store_name}"
    headers = {"Content-Type": "image/tiff"}

    try:
        with open(file_path, "rb") as f:
            res = requests.put(url, data=f, headers=headers, auth=AUTH, timeout=120)

        if res.status_code in (200, 201):
            if style_name:
                layer_url = f"{GEOSERVER_URL}/rest/layers/{WORKSPACE}:{store_name}.xml"
                layer_payload = f"""<layer>
                    <defaultStyle>
                        <name>{WORKSPACE}:{style_name}</name>
                        <workspace>{WORKSPACE}</workspace>
                    </defaultStyle>
                    <opaque>false</opaque>
                </layer>"""
                requests.put(layer_url, data=layer_payload, headers=HEADERS_XML, auth=AUTH)
            print(f"  ✓ GeoServer : Couche '{WORKSPACE}:{store_name}' publiée avec style '{style_name}'.")
            return True
        else:
            print(f"  ❌ GeoServer erreur {res.status_code} pour '{store_name}' : {res.text[:120]}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur envoi GeoServer '{store_name}' : {e}")
        return False


# ==============================================================================
# PIPELINE PRINCIPAL D'ANALYSE
# ==============================================================================

def run_analysis(
    start_year: int | None = None,
    end_year: int | None = None,
    publish_geoserver: bool = False
) -> bool:
    t_start = time.time()
    print("\n" + "=" * 75)
    print("🌾 DYNATSIMO — ANALYSE DE RELATION NDVI vs CHIRPS (PRÉCIPITATIONS)")
    print("=" * 75)

    # 1. Détection des couples de rasters
    matched = find_matched_dates(start_year, end_year)
    if not matched:
        print("❌ Aucun couple de rasters CHIRPS / NDVI trouvé pour la période spécifiée.")
        return False

    print(f"📅 Nombre de mois analysés : {len(matched)}")
    print(f"   Période : {matched[0][0]}-{matched[0][1]}  à  {matched[-1][0]}-{matched[-1][1]}")

    # Récupération de la référence spatiale (CHIRPS sert de grille cible)
    ref_chirps_path = matched[0][2]
    with rasterio.open(ref_chirps_path) as ref_c:
        ref_meta = ref_c.meta.copy()
        target_shape = ref_c.shape
        target_transform = ref_c.transform
        target_crs = ref_c.crs
        chirps_nodata = ref_c.nodata if ref_c.nodata is not None else -9999.0

    H, W = target_shape
    T = len(matched)
    print(f"📐 Grille de calcul : {H} lignes x {W} colonnes ({H * W} pixels), CRS : {target_crs}")

    # 2. Chargement et harmonisation spatiale (Rééchantillonnage de NDVI sur la grille CHIRPS)
    print("\n⏳ Étape 1/3 : Chargement et rééchantillonnage des séries temporelles...")
    chirps_stack = np.full((T, H, W), np.nan, dtype=np.float32)
    ndvi_stack = np.full((T, H, W), np.nan, dtype=np.float32)

    for idx, (y, mm, c_path, n_path) in enumerate(matched):
        # Lecture CHIRPS
        with rasterio.open(c_path) as c_src:
            c_data = c_src.read(1)
            c_valid = np.where((c_data == chirps_nodata) | (c_data < 0), np.nan, c_data)
            chirps_stack[idx] = c_valid

        # Lecture & Reprojection NDVI sur la grille CHIRPS
        with rasterio.open(n_path) as n_src:
            n_data = n_src.read(1)
            # Traiter les 0 ou valeurs aberrantes hors [-0.2, 1.0]
            n_data = np.where((n_data == 0.0) | (n_data < -0.2) | (n_data > 1.0), np.nan, n_data)
            
            reprojected_ndvi = np.full(target_shape, np.nan, dtype=np.float32)
            reproject(
                source=n_data.astype(np.float32),
                destination=reprojected_ndvi,
                src_transform=n_src.transform,
                src_crs=n_src.crs,
                dst_transform=target_transform,
                dst_crs=target_crs,
                resampling=Resampling.bilinear,
                src_nodata=np.nan,
                dst_nodata=np.nan
            )
            ndvi_stack[idx] = reprojected_ndvi

        if (idx + 1) % 50 == 0 or (idx + 1) == T:
            print(f"   → Synchronisé : {idx + 1}/{T} mois ({y}-{mm})")

    # 3. Calculs statistiques pixel par pixel
    print("\n📊 Étape 2/3 : Calculs statistiques pixel par pixel (Pearson r, Lag, P-value, Régression)...")

    # (A) Lag 0 : Végétation du mois M vs Pluie du mois M
    r_lag0, p_lag0, slope_lag0, r2_lag0 = compute_pixel_correlation(ndvi_stack, chirps_stack)

    # (B) Lag 1 : Végétation du mois M vs Pluie du mois M-1 (latence de 1 mois)
    # NDVI à partir du mois index 1, CHIRPS jusqu'à T-1
    r_lag1, p_lag1, slope_lag1, r2_lag1 = compute_pixel_correlation(ndvi_stack[1:], chirps_stack[:-1])

    # (C) Lag 2 : Végétation du mois M vs Pluie du mois M-2 (latence de 2 mois)
    r_lag2, p_lag2, slope_lag2, r2_lag2 = compute_pixel_correlation(ndvi_stack[2:], chirps_stack[:-2])

    # (D) Lag Optimal : Déterminer pour chaque pixel quel délai maximise le r
    r_stack = np.stack([
        np.nan_to_num(r_lag0, nan=-999),
        np.nan_to_num(r_lag1, nan=-999),
        np.nan_to_num(r_lag2, nan=-999)
    ], axis=0)
    lag_optimal = np.argmax(r_stack, axis=0).astype(np.float32)
    # Masquer les pixels où lag0 est NaN
    lag_optimal = np.where(np.isnan(r_lag0), np.nan, lag_optimal)

    # 4. Sauvegarde des rasters bruts dans le dossier 'NDVI_CHIRPS'
    print(f"\n📂 Étape 3/3 : Sauvegarde des rasters bruts dans '{OUTPUT_DIR.name}/'...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = [
        ("ndvi_chirps_correlation_lag0.tif", r_lag0, "style_correlation_ndvi_chirps"),
        ("ndvi_chirps_correlation_lag1.tif", r_lag1, "style_correlation_ndvi_chirps"),
        ("ndvi_chirps_lag_optimal.tif", lag_optimal, "style_lag_optimal"),
        ("ndvi_chirps_pvalue_lag0.tif", p_lag0, "style_pvalue_significativite"),
        ("ndvi_chirps_regression_slope.tif", slope_lag0, "style_regression_slope"),
        ("ndvi_chirps_r_squared.tif", r2_lag0, "style_correlation_ndvi_chirps"),
    ]

    for fname, data_arr, style in outputs:
        save_geotiff(data_arr, OUTPUT_DIR / fname, ref_meta)

    # 5. Publication dans GeoServer
    if publish_geoserver:
        print("\n🌍 Intégration et Publication dans GeoServer...")
        if not geoserver_test_connection():
            print(f"⚠ Impossible de joindre GeoServer sur {GEOSERVER_URL}. Assurez-vous que GeoServer est démarré.")
        else:
            geoserver_ensure_workspace()

            # Publication des styles SLD
            geoserver_publish_style("style_correlation_ndvi_chirps", SLD_CORRELATION)
            geoserver_publish_style("style_pvalue_significativite", SLD_PVALUE)
            geoserver_publish_style("style_lag_optimal", SLD_LAG)
            geoserver_publish_style("style_regression_slope", SLD_SLOPE)

            # Publication des rasters de résultat
            for fname, _, style in outputs:
                tif_path = OUTPUT_DIR / fname
                store_name = fname.replace(".tif", "")
                geoserver_publish_raster(tif_path, store_name, style)

    print("\n" + "=" * 75)
    print(f"✨ ANALYSE NDVI-CHIRPS TERMINÉE AVEC SUCCÈS en {time.time() - t_start:.1f} secondes !")
    print(f"📁 Tous les rasters GeoTIFF bruts sont disponibles dans : {OUTPUT_DIR}")
    print("=" * 75 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Calcul des relations spatiales NDVI vs CHIRPS et publication GeoServer")
    parser.add_argument("--start-year", type=int, default=None, help="Année de début (ex: 2000)")
    parser.add_argument("--end-year", type=int, default=None, help="Année de fin (ex: 2026)")
    parser.add_argument("--publish-geoserver", action="store_true", help="Publier automatiquement les résultats dans GeoServer")
    args = parser.parse_args()

    run_analysis(
        start_year=args.start_year,
        end_year=args.end_year,
        publish_geoserver=args.publish_geoserver
    )


if __name__ == "__main__":
    main()
