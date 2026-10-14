# 📦 Archive des Scripts DYNATSIMO

Ce dossier regroupe les scripts qui ne font plus partie du pipeline opérationnel actif du projet. Ils ont été conservés ici pour l'historique et la traçabilité sans encombrer le dossier principal `scripts/`.

---

## 📁 1. `documentation/` (Générateurs de documents & présentations)

Ces scripts ont servi à produire des documents Word (`.docx`), présentations PowerPoint (`.pptx`) et figures haute résolution (`.png`) pour la formalisation et la restitution du projet.

| Script | Description |
|---|---|
| `build_comprehensive_formalization_docx.py` | Génère les diagrammes 300 DPI et compile le document Word complet de formalisation des chaînes de traitement. |
| `build_full_document_with_figures.py` | Compile le document Word *"Chaines_de_Traitement_DYNATSIMO.docx"* avec intégration de figures graphiques. |
| `generate_chaines_traitements_docx.py` | Génère le rapport Word sur les chaînes de traitement abstraites et concrètes. |
| `generate_figures.py` | Générateur matplotlib des diagrammes conceptuels et opérationnels de traitement. |
| `generate_presentation_docx.py` | Script de génération d'un document de synthèse de présentation. |
| `generate_presentation_pptx.py` | Générateur initial des diapositives PowerPoint de présentation du projet. |
| `generate_presentation_pptx_v2.py` | Version modernisée (thème sombre/clair, design soigné) de la présentation PowerPoint. |

---

## 📁 2. `obsolete/` (Scripts obsolètes, brouillons ou dépréciés)

Ces scripts sont devenus inutiles dans le flux de production actuel car ils ont été remplacés par des versions plus robustes, intégrées au pipeline automatique (`sync_pipeline.py`).

| Script | Statut & Motif d'archivage | Script actif de remplacement |
|---|---|---|
| `cluster_ndvi_raster_VF.py` | **Obsolète** : Contenait des chemins absolus en dur (`Hanitriniala_RH/...`). | Remplacé par `export_ndvi_6classes.py` (piloté par `sync_pipeline.py`). |
| `isohyette_chirps_VF.py` | **Obsolète** : Contenait des chemins absolus en dur (`Hanitriniala_RH/...`). | Remplacé par `export_isohyetes.py` (génère GeoTIFF, PNG transparents et GeoJSON). |
| `export-data.R` | **Déprécié** : Ancien script R pour PostgreSQL issu de l'époque R Shiny. | Remplacé par l'écosystème Python `import-chirps-and-export.py` et `api-server.py`. |
| `generate-mock-data.py` | **Non utilisé** : Générateur de données fictives (mock) utilisé pendant la phase initiale de prototypage. | Inutile en environnement avec base réelle PostgreSQL et données réelles. |

---

## 🚀 Rappel : Scripts actifs conservés dans `scripts/`

Pour exécuter le pipeline ou lancer l'application, utilisez les scripts situés à la racine de `scripts/` :
- `api-server.py` : Serveur API Python (`http://127.0.0.1:8000`)
- `dev.mjs` : Démarrage simultané Frontend Vite + API Backend (`npm run dev`)
- `sync_pipeline.py` : Orchestrateur unifié de synchronisation (`npm run sync`)
- `import-chirps-and-export.py` : Ingestion CHIRPS & exports JSON
- `export_isohyetes.py` : Calcul et rendu des isohyètes (`npm run isohyetes:export`)
- `export_ndvi_6classes.py` : Classification et tuilage NDVI MODIS (`npm run ndvi:export-classes`)
- `geoserver_publisher.py` : Publication automatisée des couches GeoServer
- `download_chirps_monthly_VF.py` : Téléchargement CHIRPS (UC Santa Barbara / GEE)
- `download_ndvi_landsat_monthly_VF.py` : Téléchargement NDVI Landsat
- `download_ndvi_modis_monthly_VF.py` : Téléchargement NDVI MODIS
- `download_sentinnel_monthly_VF.py` : Téléchargement NDVI Sentinel-2
- `check_deployment.py` : Diagnostic de santé de l'environnement
- `test_authentications.py` : Validation des connexions PostgreSQL, GeoServer et Earth Engine
