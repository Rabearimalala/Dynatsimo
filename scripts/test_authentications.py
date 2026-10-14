#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DYNATSIMO — Vérification Globale des Authentifications
Teste et valide l'ensemble des identifiants et accès configurés dans le fichier .env :
1. Base de données PostgreSQL / PostGIS
2. Serveur cartographique GeoServer (REST / WMS)
3. Google Earth Engine (OAuth2 & Projet)
"""

import os
import sys
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Charger les variables du fichier .env
ROOT_DIR = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

import requests
from requests.auth import HTTPBasicAuth


def test_postgres() -> bool:
    print("\n" + "-" * 60)
    print("🐘 1. TEST POSTGRESQL / POSTGIS")
    print("-" * 60)
    host = os.getenv("DYNATSIMO_DBHOST", "localhost")
    port = os.getenv("DYNATSIMO_DBPORT", "5432")
    dbname = os.getenv("DYNATSIMO_DBNAME", "precipitation")
    user = os.getenv("DYNATSIMO_DBUSER", "postgres")
    pwd = os.getenv("DYNATSIMO_DBPASSWORD", "admin")
    
    print(f"Hôte: {host}:{port} | Base: {dbname} | Utilisateur: {user}")
    try:
        from sqlalchemy import create_engine, text
        url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}"
        engine = create_engine(url)
        with engine.connect() as conn:
            communes_cnt = conn.execute(text("SELECT count(*) FROM public.communes")).scalar()
            precip_cnt = conn.execute(text("SELECT count(*) FROM public.precipitation")).scalar()
        print(f"✓ Connexion réussie ! ({communes_cnt} communes, {precip_cnt:,} relevés de pluie)")
        return True
    except Exception as e:
        print(f"❌ Échec de connexion PostgreSQL : {e}")
        return False


def test_geoserver() -> bool:
    print("\n" + "-" * 60)
    print("🗺️ 2. TEST GEOSERVER")
    print("-" * 60)
    url = os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver").rstrip("/")
    user = os.getenv("GEOSERVER_USER", "admin")
    pwd = os.getenv("GEOSERVER_PASSWORD", "geoserver")
    ws = os.getenv("GEOSERVER_WORKSPACE", "dynatsimo")
    
    print(f"URL: {url} | Utilisateur: {user} | Espace de travail: {ws}")
    try:
        res = requests.get(f"{url}/rest/about/version.json", auth=HTTPBasicAuth(user, pwd), timeout=5)
        if res.status_code == 200:
            print(f"✓ Connexion GeoServer réussie (HTTP 200 OK) !")
            # Vérifier l'espace de travail
            ws_res = requests.get(f"{url}/rest/workspaces/{ws}.json", auth=HTTPBasicAuth(user, pwd), timeout=5)
            if ws_res.status_code == 200:
                print(f"✓ Espace de travail '{ws}' actif et accessible !")
            return True
        elif res.status_code == 401:
            print(f"❌ Erreur d'identifiants GeoServer (401 Non autorisé pour '{user}')")
            return False
        else:
            print(f"⚠ Réponse inattendue de GeoServer : Code {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Impossible de joindre GeoServer sur {url} : {e}")
        return False


def test_earth_engine() -> bool:
    print("\n" + "-" * 60)
    print("🌍 3. TEST GOOGLE EARTH ENGINE (GEE)")
    print("-" * 60)
    project = os.getenv("EE_PROJECT", "eehanitriniala")
    account = os.getenv("EE_ACCOUNT", "hanitriniala")
    print(f"Projet : {project} | Compte associé : {account}")
    
    try:
        import ee
        ee.Initialize(project=project)
        print(f"✓ Connexion réussie à Google Earth Engine sous le projet '{project}' !")
        return True
    except Exception as e:
        msg = str(e)
        if "earthengine authenticate" in msg or "credentials" in msg.lower():
            print(f"⚠ Session non encore activée pour ce compte Google.")
            print(f"  → Pour vous connecter, lancez le fichier 'authentifier_earth_engine.bat'")
        else:
            print(f"❌ Erreur d'initialisation Earth Engine : {e}")
        return False


def main():
    print("=" * 65)
    print("🔐 DYNATSIMO — DIAGNOSTIC COMPLET DES AUTHENTIFICATIONS")
    print("=" * 65)
    
    pg_ok = test_postgres()
    gs_ok = test_geoserver()
    ee_ok = test_earth_engine()
    
    print("\n" + "=" * 65)
    print("RÉSUMÉ DES ACCÈS :")
    print(f"  🐘 PostgreSQL / PostGIS   : {'✓ OPÉRATIONNEL' if pg_ok else '❌ NON OPÉRATIONNEL'}")
    print(f"  🗺️ GeoServer Cartographie : {'✓ OPÉRATIONNEL' if gs_ok else '❌ NON OPÉRATIONNEL'}")
    print(f"  🌍 Google Earth Engine    : {'✓ OPÉRATIONNEL' if ee_ok else '⚠ EN ATTENTE DE VALIDATION'}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
