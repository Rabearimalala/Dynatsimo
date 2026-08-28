# DYNATSIMO React

Prototype React pour remplacer progressivement l'application R Shiny.

## Lancer l'application

```powershell
npm install
python -m pip install -r requirements.txt
npm run dev
```

`npm run dev` lance maintenant l'API Python et Vite ensemble.
L'application React est disponible sur `http://localhost:5173/`.
L'API est disponible sur `http://127.0.0.1:8000/api/data`.

React appelle l'API Python par defaut. Si l'API ne repond pas, React retombe
automatiquement sur les fichiers statiques de `public/data`.

## Ou mettre les donnees

Les donnees sont dans `public/data`.

- `overview.json` : indicateurs de synthese
- `communes.json` : liste des communes
- `annual-precipitations.json` : serie annuelle pour la vue d'ensemble
- `saisons.json` : tableau des saisons des pluies
- `monthly-climatology.json` : climatologie mensuelle
- `anomalies.json` : anomalies annuelles
- `communes.geojson` : geometries des communes et valeurs cartographiques

React peut encore lire ces fichiers comme solution de secours. Pour les donnees
en direct, React appelle `http://127.0.0.1:8000/api/data`.

Pour l'onglet carte, `communes.geojson` doit contenir ces proprietes par commune :

```json
{
  "code": "MG001",
  "nom": "Commune A",
  "precip": 856,
  "deficit": -18
}
```

## Exporter les vraies donnees depuis PostgreSQL

Un script est fourni dans `scripts/export-data.R`.

Depuis RStudio, ouvre le projet `dynatsimo-react`, puis lance :

```r
source("scripts/export-data.R")
```

Par defaut, le script utilise :

```text
dbname   = precipitation
host     = localhost
port     = 5432
user     = postgres
password = admin
```

Pour changer la connexion avec des variables d'environnement :

```text
DYNATSIMO_DBNAME
DYNATSIMO_DBHOST
DYNATSIMO_DBPORT
DYNATSIMO_DBUSER
DYNATSIMO_DBPASSWORD
DYNATSIMO_COMMUNES_TABLE
DYNATSIMO_GEOM_COLUMN
```

Par defaut, `DYNATSIMO_COMMUNES_TABLE=public.communes` et
`DYNATSIMO_GEOM_COLUMN=geom`. Si ta table s'appelle `public.comunes_androy_anosy`,
change seulement `DYNATSIMO_COMMUNES_TABLE`.

Le script remplace automatiquement les fichiers dans `public/data`.

## Importer CHIRPS avec Python puis afficher dans React

Le script Python corrige est dans `scripts/import-chirps-and-export.py`.
Il garde le meme format que le script R :

- table communes : `public.communes`
- table precipitation : `public.precipitation` avec `"Commune_Id"`, `"Year"`, `"Month"`, `"Precip"`
- exports React : `public/data/*.json` et `public/data/communes.geojson`

Avant de lancer le script, adapte au besoin les variables d'environnement :

```text
DYNATSIMO_CHIRPS_DIR
DYNATSIMO_DBNAME
DYNATSIMO_DBHOST
DYNATSIMO_DBPORT
DYNATSIMO_DBUSER
DYNATSIMO_DBPASSWORD
```

Puis lance depuis PowerShell :

```powershell
python -m pip install -r requirements.txt
python scripts/import-chirps-and-export.py
```

Si la table `public.precipitation` est deja remplie et que tu veux seulement regenerer
les fichiers React :

```powershell
$env:DYNATSIMO_SKIP_IMPORT = "true"
python scripts/import-chirps-and-export.py
```

Ensuite demarre l'application :

```powershell
npm run dev
```

## API Python pour connecter PostgreSQL et React

Le serveur API est dans `scripts/api-server.py`.

Routes disponibles :

- `GET /api/health`
- `GET /api/data`
- `GET /api/overview`
- `GET /api/communes`
- `GET /api/annual-precipitations`
- `GET /api/saisons`
- `GET /api/monthly-climatology`
- `GET /api/anomalies`
- `GET /api/communes.geojson`

Tu peux lancer le front seul avec :

```powershell
npm run dev:web
```

Tu peux changer l'adresse de l'API cote React avec :

```powershell
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

## NDVI et Vegetation dans la base

Pour la vegetation, l'API lit en priorité une table PostgreSQL qui contient un
payload JSON complet, par exemple :

```sql
CREATE TABLE public.vegetation_payload (
  id SERIAL PRIMARY KEY,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Si cette table existe et contient un objet JSON au format attendu par React,
le front n'a plus besoin de `public/data/vegetation-data.json`.
Dans le cas contraire, l'application garde le fichier local comme secours.

## NDVI depuis des GeoTIFF

Les rasters NDVI exportes depuis GEE peuvent etre importes directement dans la
base via `scripts/import-ndvi-geotiff.py`.

Il utilise :

- la table des communes PostgreSQL pour les zonal stats
- des GeoTIFF NDVI dans un dossier local
- une table `public.ndvi_observations` pour les valeurs brutes
- une table `public.vegetation_payload` pour le JSON consomme par React

Exemple de lancement :

```powershell
$env:DYNATSIMO_NDVI_DIR = "C:\chemin\vers\tes\geotiff_ndvi"
npm run ndvi:import
```

Le script ne depend pas d'un SHP. Si ta table communes a un autre nom, reuse
`DYNATSIMO_COMMUNES_TABLE` comme pour la precipitation.
