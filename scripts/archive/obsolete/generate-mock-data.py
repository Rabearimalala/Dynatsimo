import json
import os
import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "public" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Communes specifications
communes_list = [
    # Androy
    {"code": "MG1101", "nom": "Bekily", "district": "Bekily", "region": "Androy", "ecoregion": "transition"},
    {"code": "MG1102", "nom": "Beloha", "district": "Beloha", "region": "Androy", "ecoregion": "spiny"},
    {"code": "MG1103", "nom": "Tsihombe", "district": "Tsihombe", "region": "Androy", "ecoregion": "spiny"},
    {"code": "MG1104", "nom": "Ambovombe", "district": "Ambovombe", "region": "Androy", "ecoregion": "spiny"},
    # Anosy
    {"code": "MG1201", "nom": "Betroka", "district": "Betroka", "region": "Anosy", "ecoregion": "dry"},
    {"code": "MG1202", "nom": "Amboasary Sud", "district": "Amboasary", "region": "Anosy", "ecoregion": "transition"},
    {"code": "MG1203", "nom": "Taolagnaro", "district": "Taolagnaro", "region": "Anosy", "ecoregion": "mangrove"},
    # Atsimo-Andrefana
    {"code": "MG1301", "nom": "Morombe", "district": "Morombe", "region": "Atsimo-Andrefana", "ecoregion": "mangrove"},
    {"code": "MG1302", "nom": "Toliara I", "district": "Toliara", "region": "Atsimo-Andrefana", "ecoregion": "spiny"},
    {"code": "MG1303", "nom": "Sakaraha", "district": "Sakaraha", "region": "Atsimo-Andrefana", "ecoregion": "dry"},
    {"code": "MG1304", "nom": "Betioky Sud", "district": "Betioky", "region": "Atsimo-Andrefana", "ecoregion": "spiny"},
    {"code": "MG1305", "nom": "Ampanihy", "district": "Ampanihy", "region": "Atsimo-Andrefana", "ecoregion": "spiny"},
]

# Coordinates layout to form a nice southern Madagascar map:
# Longitudes range from 43.0 to 47.5, Latitudes range from -25.6 to -21.5
boundaries = {
    "MG1301": [[43.0, -22.0], [43.6, -22.0], [43.6, -21.5], [43.0, -21.5]], # Morombe
    "MG1302": [[43.3, -23.6], [43.9, -23.6], [43.9, -23.1], [43.3, -23.1]], # Toliara I
    "MG1303": [[44.0, -23.2], [44.8, -23.2], [44.8, -22.6], [44.0, -22.6]], # Sakaraha
    "MG1201": [[45.5, -23.5], [46.3, -23.5], [46.3, -22.8], [45.5, -22.8]], # Betroka
    "MG1101": [[45.0, -24.5], [45.7, -24.5], [45.7, -23.9], [45.0, -23.9]], # Bekily
    "MG1304": [[44.0, -24.2], [44.7, -24.2], [44.7, -23.6], [44.0, -23.6]], # Betioky Sud
    "MG1305": [[44.2, -25.2], [45.0, -25.2], [45.0, -24.5], [44.2, -24.5]], # Ampanihy
    "MG1102": [[44.8, -25.4], [45.4, -25.4], [45.4, -24.8], [44.8, -24.8]], # Beloha
    "MG1103": [[45.2, -25.6], [45.7, -25.6], [45.7, -25.0], [45.2, -25.0]], # Tsihombe
    "MG1104": [[45.7, -25.3], [46.2, -25.3], [46.2, -24.8], [45.7, -24.8]], # Ambovombe
    "MG1202": [[46.1, -25.2], [46.6, -25.2], [46.6, -24.7], [46.1, -24.7]], # Amboasary Sud
    "MG1203": [[46.6, -25.1], [47.2, -25.1], [47.2, -24.6], [46.6, -24.6]], # Taolagnaro
}

# 2. Generate communes.geojson
geojson_features = []
ecoregion_attrs = {
    "spiny": {"ndvi": 0.24, "deficit": -14.2, "alert": "Vigilance", "vegCover": 38.5, "forestArea": 42000, "annualLoss": 380},
    "dry": {"ndvi": 0.46, "deficit": -4.8, "alert": "Stable", "vegCover": 58.0, "forestArea": 95000, "annualLoss": 520},
    "transition": {"ndvi": 0.33, "deficit": -22.5, "alert": "Alerte Rouge", "vegCover": 44.2, "forestArea": 61000, "annualLoss": 740},
    "mangrove": {"ndvi": 0.58, "deficit": -1.5, "alert": "Stable", "vegCover": 72.1, "forestArea": 12000, "annualLoss": 45},
}

for item in communes_list:
    code = item["code"]
    ecoregion = item["ecoregion"]
    attrs = ecoregion_attrs[ecoregion]
    
    # Add a bit of random variation to make it look organic
    h = hash(code)
    var_ndvi = (h % 9 - 4) / 100.0
    var_deficit = (h % 15 - 7) / 2.0
    var_cover = (h % 12 - 6) / 2.0
    
    ndvi_val = round(attrs["ndvi"] + var_ndvi, 3)
    deficit_val = round(attrs["deficit"] + var_deficit, 2)
    cover_val = round(attrs["vegCover"] + var_cover, 1)
    forest_area = int(attrs["forestArea"] * (1 + (h % 20 - 10)/100.0))
    loss_val = int(attrs["annualLoss"] * (1 + (h % 30 - 15)/100.0))
    
    alert_val = "Stable"
    if deficit_val < -18:
        alert_val = "Alerte Rouge"
    elif deficit_val < -8:
        alert_val = "Vigilance"
        
    coords = boundaries[code]
    # format coordinates back as closed polygon loop
    polygon_coords = coords + [coords[0]]
    
    geojson_features.append({
        "type": "Feature",
        "properties": {
            "code": code,
            "nom": item["nom"],
            "region": item["region"],
            "district": item["district"],
            "ecoregion": ecoregion,
            "precip": 450 + (h % 400), # dummy precip
            "deficit": deficit_val,
            "alert": alert_val,
            "ndvi": ndvi_val,
            "vegCover": cover_val,
            "forestArea": forest_area,
            "annualLoss": loss_val
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [polygon_coords]
        }
    })

communes_geojson = {
    "type": "FeatureCollection",
    "features": geojson_features
}

# 3. Generate vegetation-data.json
months_french = ["Oct", "Nov", "Dec", "Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep"]
ecoregion_baselines = {
    "spiny": [0.18, 0.19, 0.22, 0.25, 0.28, 0.26, 0.23, 0.21, 0.19, 0.18, 0.17, 0.18], # Oct -> Sep
    "dry": [0.33, 0.40, 0.48, 0.55, 0.58, 0.60, 0.54, 0.45, 0.38, 0.35, 0.32, 0.31],
    "transition": [0.27, 0.30, 0.34, 0.38, 0.42, 0.45, 0.40, 0.34, 0.30, 0.28, 0.26, 0.25],
    "mangrove": [0.58, 0.59, 0.60, 0.62, 0.63, 0.64, 0.62, 0.61, 0.60, 0.59, 0.58, 0.57]
}

# Time series monthly values (Oct 2018 -> Sep 2025)
time_series_data = {}
for item in communes_list:
    code = item["code"]
    ecoregion = item["ecoregion"]
    baseline = ecoregion_baselines[ecoregion]
    
    commune_series = []
    # Generate for 7 hydrological seasons: 2018-2019 to 2024-2025
    for year_idx, start_year in enumerate(range(2018, 2025)):
        season_label = f"{start_year}-{start_year+1}"
        
        # Drought index variation for specific years (2020-2021 was severe drought in South Madagascar)
        drought_factor = 1.0
        if start_year in (2019, 2020, 2021):
            if ecoregion in ("spiny", "transition"):
                drought_factor = 0.78 # 22% drop in NDVI
            else:
                drought_factor = 0.88
        elif start_year == 2023:
            drought_factor = 1.05 # good rain year
            
        ndvi_values = []
        cumulative = 0.0
        cum_series = []
        anomaly_series = []
        
        baseline_series = []
        for m_idx, m_name in enumerate(months_french):
            base_val = baseline[m_idx]
            # Add some slight noise
            noise = ((hash(code) + m_idx + start_year) % 7 - 3) / 150.0
            ndvi_val = max(0.05, round(base_val * drought_factor + noise, 3))
            ndvi_values.append(ndvi_val)
            
            cumulative = round(cumulative + ndvi_val, 3)
            cum_series.append(cumulative)
            
            # Anomaly is relative to the baseline
            anomaly = round(ndvi_val - base_val, 3)
            anomaly_series.append(anomaly)
            baseline_series.append(base_val)
            
        commune_series.append({
            "season": season_label,
            "startYear": start_year,
            "ndvi": ndvi_values,
            "cumulative": cum_series,
            "anomalies": anomaly_series,
            "baseline": baseline_series,
            "integratedProductivity": cumulative
        })
    time_series_data[code] = commune_series

# Sensor spatial pixel comparison simulation (MODIS 250m contains 8x8 Landsat pixels, and 25x25 Sentinel pixels)
# We will model a 250m x 250m bounding area that has a clearing (deforestation) in the center.
# The area is represented as a grid of 25x25 sub-pixels (10m each) for Sentinel-2.
# 1 = Dense Forest, 2 = Degraded/Clearing, 3 = Crop field, 4 = Bare soil / Path
grid_sentinel = []
for r in range(25):
    row = []
    for c in range(25):
        # Deforestation patch in the center: circle of radius 6 at center (12, 12)
        dist = math.sqrt((r - 12)**2 + (c - 12)**2)
        if dist < 4:
            row.append(4) # bare soil in the very center
        elif dist < 8:
            row.append(3) # crop/grassland surrounding clearing
        elif dist < 11:
            row.append(2) # degraded forest buffer
        else:
            row.append(1) # dense intact forest
    grid_sentinel.append(row)

# NDVI values for cover types: Dense: 0.65, Degraded: 0.42, Crop: 0.32, Bare soil: 0.15
cover_ndvi = {1: 0.65, 2: 0.42, 3: 0.32, 4: 0.15}

# Sentinel NDVI grid (25x25 pixels)
sentinel_ndvi = [[cover_ndvi[cell] for cell in row] for row in grid_sentinel]

# Landsat NDVI grid (8x8 pixels of size ~30m each)
# Each Landsat pixel averages 3x3 Sentinel pixels (with overlap)
landsat_ndvi = []
for r_l in range(8):
    row_l = []
    for c_l in range(8):
        s_r_start = min(22, r_l * 3)
        s_c_start = min(22, c_l * 3)
        # Average of 9 Sentinel subpixels
        subpixels = [sentinel_ndvi[r][c] for r in range(s_r_start, s_r_start+3) for c in range(s_c_start, s_c_start+3)]
        row_l.append(round(sum(subpixels)/len(subpixels), 3))
    landsat_ndvi.append(row_l)

# MODIS NDVI (1 single large pixel of 250m)
# Averages all 625 Sentinel subpixels
modis_ndvi = round(sum(sum(row) for row in sentinel_ndvi) / 625.0, 3)

sensor_comparison = {
    "meta": {
        "description": "Simulation d'un patch de déforestation de 120m de diamètre dans une forêt sèche.",
        "location": "Sakaraha (Atsimo-Andrefana)",
        "coordinates": "22.91° S, 44.53° E"
    },
    "specs": [
        {
            "id": "sentinel",
            "name": "Sentinel-2 (ESA)",
            "resolution": "10 mètres",
            "frequency": "5 jours",
            "bands": "13 bandes (Rouge, Proche Infrarouge à 10m)",
            "advantage": "Résolution spatiale très fine permettant de détecter les petites coupes sélectives et les limites des champs.",
            "inconvenience": "Volume de données élevé, couverture historique courte (depuis 2015)."
        },
        {
            "id": "landsat",
            "name": "Landsat-8 / 9 (NASA)",
            "resolution": "30 mètres",
            "frequency": "8-16 jours",
            "bands": "11 bandes (Rouge, Proche Infrarouge à 30m, Thermique à 100m)",
            "advantage": "Excellente couverture historique (série Landsat depuis 1972), données d'étalonnage très stables.",
            "inconvenience": "Résolution moyenne, rate les clairières de taille inférieure à 0.1 hectare."
        },
        {
            "id": "modis",
            "name": "MODIS (Terra/Aqua)",
            "resolution": "250 mètres",
            "frequency": "1-2 jours (Quotidien)",
            "bands": "36 bandes (Rouge et Proche Infrarouge à 250m)",
            "advantage": "Fréquence d'observation quasi-quotidienne idéale pour le suivi phénologique continu sans nuages.",
            "inconvenience": "Résolution spatiale grossière sujette aux pixels mixtes (mélange de forêts, cultures et sols)."
        }
    ],
    "simulation": {
        "sentinel": {
            "grid": grid_sentinel,
            "ndvi": sentinel_ndvi,
            "resolution": 10,
            "size": 25
        },
        "landsat": {
            "ndvi": landsat_ndvi,
            "resolution": 30,
            "size": 8
        },
        "modis": {
            "ndvi": [[modis_ndvi]],
            "resolution": 250,
            "size": 1
        }
    }
}

vegetation_data = {
    "ecoregions": {
        "spiny": {
            "id": "spiny",
            "name": "Forêt Épineuse du Sud",
            "description": "Zone sub-aride dominée par des plantes épineuses et succulentes (Didieraceae, Euphorbia). Phenologie hautement réactive aux pluies erratiques. Indice de référence NDVI bas.",
            "baselineNdvi": ecoregion_baselines["spiny"],
            "alertThresholds": {"vigilance": 0.85, "severe": 0.72},
            "classificationDistrib": {"foret_dense": 22, "foret_degradee": 48, "fourre": 18, "culture": 8, "sol_nu": 4}
        },
        "dry": {
            "id": "dry",
            "name": "Forêt Sèche du Sud-Ouest",
            "description": "Forêt décidue sèche sur sols sablonneux ou calcaires. Sensible à la déforestation par brûlis (hatske) et aux feux de brousse de fin de saison sèche.",
            "baselineNdvi": ecoregion_baselines["dry"],
            "alertThresholds": {"vigilance": 0.80, "severe": 0.68},
            "classificationDistrib": {"foret_dense": 42, "foret_degradee": 33, "fourre": 9, "culture": 13, "sol_nu": 3}
        },
        "transition": {
            "id": "transition",
            "name": "Fourré de Transition",
            "description": "Mosaïque de savanes arborées et de fourrés denses. Zone charnière sous forte pression anthropique (expansion agricole et pâturage).",
            "baselineNdvi": ecoregion_baselines["transition"],
            "alertThresholds": {"vigilance": 0.83, "severe": 0.70},
            "classificationDistrib": {"foret_dense": 31, "foret_degradee": 38, "fourre": 14, "culture": 14, "sol_nu": 3}
        },
        "mangrove": {
            "id": "mangrove",
            "name": "Mangroves & Végétation Littorale",
            "description": "Écosystèmes côtiers d'estuaire et cordons dunaires. Importants pour la stabilisation côtière. NDVI élevé et stable toute l'année.",
            "baselineNdvi": ecoregion_baselines["mangrove"],
            "alertThresholds": {"vigilance": 0.88, "severe": 0.75},
            "classificationDistrib": {"foret_dense": 58, "foret_degradee": 16, "fourre": 4, "culture": 2, "sol_nu": 20}
        }
    },
    "sensorComparison": sensor_comparison,
    "timeSeries": time_series_data
}

# 4. Write data to public/data directory
with open(OUTPUT_DIR / "communes.json", "w", encoding="utf-8") as f:
    json.dump(communes_list, f, ensure_ascii=False, indent=2)

with open(OUTPUT_DIR / "communes.geojson", "w", encoding="utf-8") as f:
    json.dump(communes_geojson, f, ensure_ascii=False, indent=2)

with open(OUTPUT_DIR / "vegetation-data.json", "w", encoding="utf-8") as f:
    json.dump(vegetation_data, f, ensure_ascii=False, indent=2)

# Generate other required files if they are mock or empty to ensure smooth startup of the app
overview_data = {
    "nb_communes": len(communes_list),
    "nb_years": "2018-2025",
    "total_records": len(communes_list) * 12 * 7
}
with open(OUTPUT_DIR / "overview.json", "w", encoding="utf-8") as f:
    json.dump(overview_data, f, ensure_ascii=False, indent=2)

# annual-precipitations.json
annual_precip = [{"year": y, "precip": round(480.0 + (y % 5 - 2) * 50 + (y % 3) * 15, 1)} for y in range(1981, 2026)]
with open(OUTPUT_DIR / "annual-precipitations.json", "w", encoding="utf-8") as f:
    json.dump(annual_precip, f, ensure_ascii=False, indent=2)

# monthly-climatology.json
monthly_clim = [{"month": m, "precip": round(5.0 + (i**2 * 1.8) if i < 6 else 100.0 - (i-6)**2 * 2.5, 1)} for i, m in enumerate(months_french)]
with open(OUTPUT_DIR / "monthly-climatology.json", "w", encoding="utf-8") as f:
    json.dump(monthly_clim, f, ensure_ascii=False, indent=2)

# anomalies.json
anomalies_data = [{"year": y, "anomaly": round((y % 7 - 3.5) * 22.0, 1)} for y in range(1981, 2026)]
with open(OUTPUT_DIR / "anomalies.json", "w", encoding="utf-8") as f:
    json.dump(anomalies_data, f, ensure_ascii=False, indent=2)

# saisons.json
saisons_data = []
for item in communes_list:
    for y in range(2018, 2025):
        saisons_data.append({
            "code_commune": item["code"],
            "commune": item["nom"],
            "saison": y,
            "debut": "Dec" if y % 2 == 0 else "Nov",
            "fin": "Mar" if y % 3 == 0 else "Avr",
            "duree": 5 if y % 2 == 0 else 6,
            "mois_plus_pluvieux": "Jan" if y % 2 == 0 else "Fev",
            "precip": int(420 + (hash(item["nom"]) % 150) + (y % 5 * 20))
        })
with open(OUTPUT_DIR / "saisons.json", "w", encoding="utf-8") as f:
    json.dump(saisons_data, f, ensure_ascii=False, indent=2)

print("Mock data generation completed successfully!")
