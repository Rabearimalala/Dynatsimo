#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DYNATSIMO — Pipeline Automatique Unifié de Téléchargement & Traitement des Données

Ce script orchestre l'ensemble du cycle de vie des données :
1. Téléchargement incrémental des nouveaux rasters CHIRPS manquants (UC Santa Barbara).
2. Calcul des statistiques zonales pour toutes les communes et mise à jour PostgreSQL.
3. Génération des rasters et contours vectoriels d'isohyètes CHIRPS (GeoTIFF, PNG, GeoJSON).
4. Synchronisation et classification NDVI MODIS 6-classes.
5. Exportation de tous les fichiers JSON et GeoJSON pour l'interface React.

Usage :
    python scripts/sync_pipeline.py
    python scripts/sync_pipeline.py --skip-download
    python scripts/sync_pipeline.py --force-rebuild-db
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"


def print_step_header(num: int, title: str) -> None:
    print("\n" + "=" * 75)
    print(f"[{num}/5] {title.upper()}")
    print("=" * 75)


def run_download_chirps() -> bool:
    print_step_header(1, "Téléchargement incrémental des nouveaux rasters CHIRPS")
    script_path = SCRIPTS_DIR / "download_chirps_monthly_VF.py"
    if not script_path.exists():
        print(f"❌ Script introuvable : {script_path}")
        return False

    t0 = time.time()
    try:
        res = subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"✓ Étape de téléchargement terminée en {time.time() - t0:.1f}s.")
        return res.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"⚠ Avertissement lors du téléchargement CHIRPS : {e}")
        return False
    except Exception as e:
        print(f"⚠ Erreur inattendue lors du téléchargement : {e}")
        return False


def run_postgres_import(force_rebuild: bool = False) -> bool:
    print_step_header(2, "Calcul des statistiques zonales et mise à jour PostgreSQL")
    data_script = SCRIPTS_DIR / "import-chirps-and-export.py"
    spec = importlib.util.spec_from_file_location("dynatsimo_data", data_script)
    if not spec or not spec.loader:
        print("❌ Impossible de charger import-chirps-and-export.py")
        return False

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    t0 = time.time()
    try:
        engine = module.make_engine()
        module.import_chirps_to_postgres(engine, force_rebuild=force_rebuild)
        print(f"✓ Mise à jour PostgreSQL terminée en {time.time() - t0:.1f}s.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'import PostgreSQL : {e}")
        return False


def run_export_isohyetes() -> bool:
    print_step_header(3, "Génération des Isohyètes CHIRPS (Rasters PNG & GeoJSON)")
    script_path = SCRIPTS_DIR / "export_isohyetes.py"
    spec = importlib.util.spec_from_file_location("dynatsimo_isohyetes", script_path)
    if not spec or not spec.loader:
        print("❌ Impossible de charger export_isohyetes.py")
        return False

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    t0 = time.time()
    try:
        module.main()
        print(f"✓ Isohyètes générées en {time.time() - t0:.1f}s.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'export des isohyètes : {e}")
        return False


def run_sync_ndvi() -> bool:
    print_step_header(4, "Synchronisation et classification NDVI MODIS 6-classes")
    script_path = SCRIPTS_DIR / "export_ndvi_6classes.py"
    if not script_path.exists():
        print("ℹ Pas de script NDVI trouvé, étape ignorée.")
        return True

    spec = importlib.util.spec_from_file_location("dynatsimo_ndvi", script_path)
    if not spec or not spec.loader:
        print("❌ Impossible de charger export_ndvi_6classes.py")
        return False

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    t0 = time.time()
    try:
        if hasattr(module, "sync_all_ndvi_rasters"):
            module.sync_all_ndvi_rasters()
        else:
            module.main()
        print(f"✓ Synchronisation NDVI terminée en {time.time() - t0:.1f}s.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation NDVI : {e}")
        return False


def run_export_react() -> bool:
    print_step_header(5, "Exportation des données pour l'interface React")
    data_script = SCRIPTS_DIR / "import-chirps-and-export.py"
    spec = importlib.util.spec_from_file_location("dynatsimo_data", data_script)
    if not spec or not spec.loader:
        print("❌ Impossible de charger import-chirps-and-export.py")
        return False

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    t0 = time.time()
    try:
        engine = module.make_engine()
        module.export_react_data(engine)
        print(f"✓ Export React JSON terminé en {time.time() - t0:.1f}s.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'export React : {e}")
        return False


def run_full_pipeline(skip_download: bool = False, force_rebuild_db: bool = False, skip_ndvi: bool = False) -> bool:
    print("\n" + "=" * 75)
    print("🚀 DYNATSIMO — DÉBUT DU PIPELINE GLOBAL DE SYNCHRONISATION")
    print("=" * 75)
    total_t0 = time.time()

    # 1. Download
    if not skip_download:
        run_download_chirps()
    else:
        print("\nℹ Étape 1 : Téléchargement ignoré (--skip-download).")

    # 2. Postgres
    db_ok = run_postgres_import(force_rebuild=force_rebuild_db)
    if not db_ok:
        print("❌ Échec lors de la mise à jour PostgreSQL. Arrêt du pipeline.")
        return False

    # 3. Isohyetes
    iso_ok = run_export_isohyetes()
    if not iso_ok:
        print("⚠ Avertissement : Problème lors de la génération des isohyètes.")

    # 4. NDVI
    if not skip_ndvi:
        run_sync_ndvi()
    else:
        print("\nℹ Étape 4 : NDVI ignoré (--skip-ndvi).")

    # 5. Export React
    react_ok = run_export_react()
    if not react_ok:
        print("❌ Échec lors de l'export React.")
        return False

    total_time = time.time() - total_t0
    print("\n" + "=" * 75)
    print(f"✨ PIPELINE DYNATSIMO TERMINÉ AVEC SUCCÈS EN {total_time:.1f} SECONDES !")
    print("=" * 75 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Pipeline complet de synchronisation Dynatsimo")
    parser.add_argument("--skip-download", action="store_true", help="Ne pas télécharger les rasters CHIRPS")
    parser.add_argument("--force-rebuild-db", action="store_true", help="Recalculer toute la base PostgreSQL depuis zéro")
    parser.add_argument("--skip-ndvi", action="store_true", help="Ignorer la synchronisation NDVI")
    args = parser.parse_args()

    success = run_full_pipeline(
        skip_download=args.skip_download,
        force_rebuild_db=args.force_rebuild_db,
        skip_ndvi=args.skip_ndvi,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
