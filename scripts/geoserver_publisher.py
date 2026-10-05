#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DYNATSIMO — Module de synchronisation et publication des rasters dans GeoServer.

Workspace : donnees_dynatsimo
Namespace URI : http://ns_dynatsimo
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import requests
from requests.auth import HTTPBasicAuth

ROOT_DIR = Path(__file__).resolve().parents[1]
CHIRPS_DIR = ROOT_DIR / "CHIRPS_data"
MODIS_DIR = ROOT_DIR / "NDVI_MODIS"

# --- Paramètres GeoServer (configurables via variables d'environnement) ---
GEOSERVER_URL = os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver").rstrip("/")
GS_USER = os.getenv("GEOSERVER_USER", "frabearimalala")
GS_PASSWORD = os.getenv("GEOSERVER_PASSWORD", "admin_dynatsimo")
WORKSPACE = os.getenv("GEOSERVER_WORKSPACE", "donnees_dynatsimo")
NAMESPACE_URI = os.getenv("GEOSERVER_NAMESPACE", "http://ns_dynatsimo")

AUTH = HTTPBasicAuth(GS_USER, GS_PASSWORD)
HEADERS_XML = {"Content-Type": "application/xml"}
HEADERS_JSON = {"Content-Type": "application/json", "Accept": "application/json"}
HEADERS_SLD = {"Content-Type": "application/vnd.ogc.sld+xml"}


# --- Styles SLD ---
SLD_CHIRPS = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>chirps_style</Name>
    <UserStyle>
      <Title>Style CHIRPS Précipitations (mm)</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="intervals">
              <ColorMapEntry color="#ffffff" quantity="0" opacity="0.0" label="0 mm"/>
              <ColorMapEntry color="#dbeafe" quantity="50" opacity="0.8" label="&lt; 50 mm"/>
              <ColorMapEntry color="#93c5fd" quantity="100" opacity="0.8" label="50 - 100 mm"/>
              <ColorMapEntry color="#3b82f6" quantity="200" opacity="0.85" label="100 - 200 mm"/>
              <ColorMapEntry color="#1d4ed8" quantity="350" opacity="0.85" label="200 - 350 mm"/>
              <ColorMapEntry color="#1e40af" quantity="500" opacity="0.9" label="350 - 500 mm"/>
              <ColorMapEntry color="#172554" quantity="2000" opacity="0.95" label="&gt; 500 mm"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
"""

SLD_NDVI_6CLASSES = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">
  <NamedLayer>
    <Name>ndvi_6classes_style</Name>
    <UserStyle>
      <Title>Style NDVI MODIS 6 Classes DYNATSIMO</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="values">
              <ColorMapEntry color="#000000" quantity="0" opacity="0.0" label="NoData"/>
              <ColorMapEntry color="#0c19ff" quantity="1" opacity="0.85" label="Eau"/>
              <ColorMapEntry color="#87360c" quantity="2" opacity="0.85" label="NDVI très faible"/>
              <ColorMapEntry color="#c46e2d" quantity="3" opacity="0.85" label="NDVI faible"/>
              <ColorMapEntry color="#96aa50" quantity="4" opacity="0.85" label="NDVI moyen"/>
              <ColorMapEntry color="#468237" quantity="5" opacity="0.85" label="NDVI élevé"/>
              <ColorMapEntry color="#194d1b" quantity="6" opacity="0.85" label="NDVI très élevé"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
"""


def test_connection() -> bool:
    """Vérifie la connexion et l'authentification avec GeoServer."""
    try:
        url = f"{GEOSERVER_URL}/rest/about/version.json"
        res = requests.get(url, auth=AUTH, headers=HEADERS_JSON, timeout=5)
        if res.status_code == 200:
            print(f"✓ Connecté avec succès à GeoServer ({GEOSERVER_URL}) en tant que '{GS_USER}'.")
            return True
        elif res.status_code == 401:
            print(f"❌ Erreur d'authentification GeoServer (401 Unauthorized) pour '{GS_USER}'.")
            return False
        else:
            print(f"⚠ Réponse inattendue de GeoServer : {res.status_code} - {res.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de joindre GeoServer sur {GEOSERVER_URL} : {e}")
        return False


def ensure_workspace() -> bool:
    """Vérifie que le workspace donnees_dynatsimo existe, sinon le crée avec son Namespace URI."""
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}.json"
    res = requests.get(url, auth=AUTH, headers=HEADERS_JSON)
    if res.status_code == 404:
        print(f"→ Création de l'espace de travail '{WORKSPACE}'...")
        payload = f"<workspace><name>{WORKSPACE}</name></workspace>"
        create_res = requests.post(f"{GEOSERVER_URL}/rest/workspaces", data=payload, headers=HEADERS_XML, auth=AUTH)
        if create_res.status_code in (200, 201):
            # Mettre à jour l'URI du Namespace
            ns_payload = f"<namespace><prefix>{WORKSPACE}</prefix><uri>{NAMESPACE_URI}</uri></namespace>"
            requests.put(f"{GEOSERVER_URL}/rest/namespaces/{WORKSPACE}", data=ns_payload, headers=HEADERS_XML, auth=AUTH)
            print(f"✓ Espace de travail '{WORKSPACE}' créé avec Namespace URI '{NAMESPACE_URI}'.")
            return True
        else:
            print(f"❌ Échec de création du workspace : {create_res.status_code} - {create_res.text}")
            return False
    elif res.status_code == 200:
        print(f"✓ Espace de travail '{WORKSPACE}' actif.")
        return True
    return False


def ensure_style(style_name: str, sld_body: str) -> bool:
    """Vérifie ou téléverse un style SLD dans le workspace."""
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles/{style_name}.json"
    res = requests.get(url, auth=AUTH, headers=HEADERS_JSON)
    if res.status_code == 404:
        print(f"→ Création du style SLD '{style_name}' dans '{WORKSPACE}'...")
        create_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles?name={style_name}"
        res_post = requests.post(create_url, data=sld_body.encode("utf-8"), headers=HEADERS_SLD, auth=AUTH)
        if res_post.status_code in (200, 201):
            print(f"✓ Style '{style_name}' publié avec succès.")
            return True
        else:
            print(f"❌ Erreur lors de la création du style '{style_name}' : {res_post.status_code} - {res_post.text}")
            return False
    elif res.status_code == 200:
        print(f"✓ Style '{style_name}' déjà existant.")
        return True
    return False


def get_existing_coveragestores() -> set[str]:
    """Récupère l'ensemble des noms de CoverageStores déjà enregistrés dans le workspace."""
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/coveragestores.json"
    try:
        res = requests.get(url, auth=AUTH, headers=HEADERS_JSON, timeout=10)
        if res.status_code == 200:
            data = res.json()
            stores_node = data.get("coverageStores", {})
            if isinstance(stores_node, dict):
                stores = stores_node.get("coverageStore", [])
                if isinstance(stores, list):
                    return {s["name"] for s in stores if "name" in s}
                elif isinstance(stores, dict) and "name" in stores:
                    return {stores["name"]}
        return set()
    except Exception as e:
        print(f"⚠ Erreur lors de la lecture des coveragestores : {e}")
        return set()


def publish_geotiff(file_path: Path, store_name: str, default_style: str | None = None) -> bool:
    """Téléverse et publie un fichier GeoTIFF dans GeoServer via REST API."""
    if not file_path.exists():
        print(f"❌ Fichier raster introuvable : {file_path}")
        return False

    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/coveragestores/{store_name}/file.geotiff?configure=first&coverageName={store_name}"
    headers = {"Content-Type": "image/tiff"}

    try:
        with open(file_path, "rb") as f:
            res = requests.put(url, data=f, headers=headers, auth=AUTH, timeout=120)

        if res.status_code in (200, 201):
            print(f"  ✓ Raster '{store_name}' publié avec succès.")

            # Appliquer le style SLD par défaut si spécifié
            if default_style:
                layer_url = f"{GEOSERVER_URL}/rest/layers/{WORKSPACE}:{store_name}.xml"
                layer_payload = f"""<layer>
                    <defaultStyle>
                        <name>{WORKSPACE}:{default_style}</name>
                        <workspace>{WORKSPACE}</workspace>
                    </defaultStyle>
                </layer>"""
                requests.put(layer_url, data=layer_payload, headers=HEADERS_XML, auth=AUTH)
            return True
        else:
            print(f"  ❌ Échec publication '{store_name}' : Code {res.status_code} - {res.text[:150]}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur pendant l'envoi du raster '{store_name}' : {e}")
        return False


def sync_geoserver(max_recent: int | None = None) -> bool:
    """
    Synchronise tous les rasters CHIRPS et NDVI MODIS vers GeoServer.
    Si max_recent est spécifié, publie les N plus récents manquants.
    """
    print("\n" + "=" * 75)
    print("🌍 DYNATSIMO — SYNCHRONISATION DES RASTERS VERS GEOSERVER")
    print("=" * 75)

    if not test_connection():
        print("⚠ Impossible d'exécuter la synchronisation GeoServer (serveur non accessible).")
        return False

    ensure_workspace()
    ensure_style("chirps_style", SLD_CHIRPS)
    ensure_style("ndvi_6classes_style", SLD_NDVI_6CLASSES)

    existing_stores = get_existing_coveragestores()
    print(f"ℹ Couches GeoServer actuellement publiées : {len(existing_stores)}")

    # 1. Traitement CHIRPS
    chirps_files = sorted(CHIRPS_DIR.glob("chirps-v2.0.*.*.tif"))
    if not chirps_files:
        chirps_files = sorted(CHIRPS_DIR.glob("chirps-v2.0.*.tif"))

    published_count = 0
    print(f"\n📂 Détection des rasters CHIRPS ({len(chirps_files)} fichiers trouvés)...")
    
    to_publish_chirps = []
    for tif in chirps_files:
        match = re.search(r"chirps-v2\.0\.(\d{4})\.(\d{2})\.tif", tif.name)
        if match:
            year, month = match.groups()
            store_name = f"chirps_{year}_{month}"
            if store_name not in existing_stores:
                to_publish_chirps.append((tif, store_name))

    if max_recent:
        to_publish_chirps = to_publish_chirps[-max_recent:]

    for tif, store_name in to_publish_chirps:
        print(f"→ Envoi CHIRPS : {tif.name} -> {WORKSPACE}:{store_name}")
        if publish_geotiff(tif, store_name, default_style="chirps_style"):
            published_count += 1

    # 2. Traitement NDVI MODIS
    ndvi_raw_files = sorted([f for f in MODIS_DIR.rglob("*.tif") if "RESULTATS_6_CLASSES" not in f.parts])
    classified_dir = MODIS_DIR / "RESULTATS_6_CLASSES"
    ndvi_6c_files = sorted(classified_dir.rglob("*.tif")) if classified_dir.exists() else []

    print(f"\n📂 Détection des rasters NDVI MODIS ({len(ndvi_raw_files)} bruts, {len(ndvi_6c_files)} classifiés)...")
    to_publish_ndvi = []

    # Priorité aux rasters 6-classes si présents, sinon rasters bruts
    target_ndvi_files = ndvi_6c_files if ndvi_6c_files else ndvi_raw_files
    for tif in target_ndvi_files:
        match = re.search(r"(\d{4})_(\d{2})", tif.name)
        if match:
            year, month = match.groups()
            store_name = f"ndvi_modis_{year}_{month}"
            if store_name not in existing_stores:
                to_publish_ndvi.append((tif, store_name))

    if max_recent:
        to_publish_ndvi = to_publish_ndvi[-max_recent:]

    for tif, store_name in to_publish_ndvi:
        print(f"→ Envoi NDVI MODIS : {tif.name} -> {WORKSPACE}:{store_name}")
        if publish_geotiff(tif, store_name, default_style="ndvi_6classes_style"):
            published_count += 1

    print("\n" + "=" * 75)
    print(f"✨ SYNCHRONISATION GEOSERVER TERMINÉE : {published_count} nouvelle(s) couche(s) publiée(s).")
    print("=" * 75 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Synchronisation GeoServer DYNATSIMO")
    parser.add_argument("--test", action="store_true", help="Tester la connexion GeoServer")
    parser.add_argument("--recent", type=int, default=None, help="Nombre de rasters récents à publier")
    args = parser.parse_args()

    if args.test:
        success = test_connection()
        sys.exit(0 if success else 1)

    success = sync_geoserver(max_recent=args.recent)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
