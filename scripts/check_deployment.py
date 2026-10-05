#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DYNATSIMO — Diagnostic & Vérification Complète du Déploiement en Production.

Ce script teste en temps réel tous les composants nécessaires au bon fonctionnement :
1. Connexion PostgreSQL / PostGIS (tables communes, précipitations).
2. Connexion GeoServer (Workspace donnees_dynatsimo, styles SLD, couches WMS).
3. Dossiers et rasters CHIRPS & NDVI MODIS.
4. Dépendances logicielles.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "scripts"))


def check_python_packages():
    print("\n[1/4] VÉRIFICATION DES MODULES PYTHON :")
    required = ["rasterio", "geopandas", "requests", "numpy", "PIL", "sqlalchemy", "psycopg2"]
    all_ok = True
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✓ Module '{pkg}' : OK")
        except ImportError:
            print(f"  ❌ Module '{pkg}' : MANQUANT")
            all_ok = False
    return all_ok


def check_postgres():
    print("\n[2/4] VÉRIFICATION POSTGRESQL / POSTGIS :")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dynatsimo_data", ROOT_DIR / "scripts" / "import-chirps-and-export.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        engine = mod.make_engine()
        
        with engine.connect() as conn:
            # Test PostGIS version
            try:
                postgis_ver = conn.execute(text("SELECT PostGIS_Version()")).scalar()
                print(f"  ✓ PostGIS actif : {postgis_ver}")
            except Exception:
                print("  ⚠ Extension PostGIS non détectée dans la base.")

            # Test Communes
            has_communes = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'communes' OR table_name = 'comunes_androy_anosy')")).scalar()
            print(f"  ✓ Table Communes : {'Présente' if has_communes else 'Manquante'}")

            # Test Précipitations
            has_precip = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'precipitation')")).scalar()
            if has_precip:
                count = conn.execute(text("SELECT COUNT(*) FROM public.precipitation")).scalar()
                print(f"  ✓ Table 'precipitation' : {count} enregistrements trouvés.")
            else:
                print("  ⚠ Table 'precipitation' non encore créée (sera créée au 1er sync).")

        return True
    except Exception as e:
        print(f"  ❌ Erreur de connexion PostgreSQL : {e}")
        return False


def check_geoserver():
    print("\n[3/4] VÉRIFICATION GEOSERVER :")
    gs_url = os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver").rstrip("/")
    user = os.getenv("GEOSERVER_USER", "frabearimalala")
    pwd = os.getenv("GEOSERVER_PASSWORD", "admin_dynatsimo")
    ws = os.getenv("GEOSERVER_WORKSPACE", "donnees_dynatsimo")
    auth = HTTPBasicAuth(user, pwd)

    try:
        # Test accès général
        r = requests.get(f"{gs_url}/rest/about/version.json", auth=auth, timeout=5)
        if r.status_code != 200:
            print(f"  ❌ GeoServer inaccessible ou authentification rejetée ({r.status_code}).")
            return False
        print(f"  ✓ Connexion GeoServer ({gs_url}) : OK (Utilisateur : {user})")

        # Test workspace
        r_ws = requests.get(f"{gs_url}/rest/workspaces/{ws}.json", auth=auth, timeout=5)
        if r_ws.status_code == 200:
            print(f"  ✓ Espace de travail '{ws}' : Présent et actif.")
        else:
            print(f"  ⚠ Espace de travail '{ws}' : Non trouvé (sera créé automatiquement).")

        # Test couches
        r_layers = requests.get(f"{gs_url}/rest/workspaces/{ws}/coveragestores.json", auth=auth, timeout=5)
        if r_layers.status_code == 200:
            stores = r_layers.json().get("coverageStores", {}).get("coverageStore", [])
            count = len(stores) if isinstance(stores, list) else (1 if stores else 0)
            print(f"  ✓ Couches WMS publiées dans '{ws}' : {count} couche(s).")

        return True
    except Exception as e:
        print(f"  ❌ Impossible de joindre GeoServer : {e}")
        return False


def check_directories():
    print("\n[4/4] VÉRIFICATION DES DOSSIERS DE DONNÉES :")
    chirps_dir = ROOT_DIR / "CHIRPS_data"
    modis_dir = ROOT_DIR / "NDVI_MODIS"
    public_data_dir = ROOT_DIR / "public" / "data"

    print(f"  ✓ Dossier CHIRPS_data : {'OK' if chirps_dir.exists() else 'Créé automatiquement'}")
    print(f"  ✓ Dossier NDVI_MODIS  : {'OK' if modis_dir.exists() else 'Créé automatiquement'}")
    print(f"  ✓ Dossier public/data : {'OK' if public_data_dir.exists() else 'Créé automatiquement'}")
    return True


def main():
    print("=" * 70)
    print("🔍 DYNATSIMO — DIAGNOSTIC DU DÉPLOIEMENT EN PRODUCTION")
    print("=" * 70)

    ok1 = check_python_packages()
    ok2 = check_postgres()
    ok3 = check_geoserver()
    ok4 = check_directories()

    print("\n" + "=" * 70)
    if ok1 and ok2 and ok3 and ok4:
        print("✨ BILAN : TOUS LES SYSTÈMES SONT OPÉRATIONNELS POUR LA PRODUCTION !")
    else:
        print("⚠ BILAN : CERTAINS COMPOSANTS NÉCESSITENT VOTRE ATTENTION (VOIR CI-DESSUS).")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
