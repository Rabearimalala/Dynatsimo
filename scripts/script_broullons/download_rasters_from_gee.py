import os
import sys
import argparse
import io
import zipfile
import json
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
import geopandas as gpd
import numpy as np
import rasterio
from PIL import Image
import ee

def env(name: str, default: str) -> str:
    return os.getenv(name, default)

def make_engine():
    db_url = URL.create(
        "postgresql",
        username=env("DYNATSIMO_DBUSER", "postgres"),
        password=env("DYNATSIMO_DBPASSWORD", "admin"),
        host=env("DYNATSIMO_DBHOST", "localhost"),
        port=int(env("DYNATSIMO_DBPORT", "5432")),
        database=env("DYNATSIMO_DBNAME", "precipitation"),
    )
    return create_engine(db_url)

def setup_database(engine):
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.rasters (
                "sensor" VARCHAR(20) NOT NULL,
                "year" INTEGER NOT NULL,
                "month" INTEGER NOT NULL,
                "tiff_path" TEXT NOT NULL,
                "png_path" TEXT NOT NULL,
                "bounds" JSONB NOT NULL,
                PRIMARY KEY ("sensor", "year", "month")
            )
        """))
    print("Database table public.rasters verified/created.")

def get_landsat_ndvi(img):
    scaled = img.select('SR_B.*').multiply(0.0000275).add(-0.2)
    img = img.addBands(scaled, None, True)
    bands = img.bandNames()
    
    ndvi57 = img.normalizedDifference(['SR_B4', 'SR_B3'])
    ndvi89 = img.normalizedDifference(['SR_B5', 'SR_B4'])
    
    ndvi = ee.Image(ee.Algorithms.If(bands.contains('SR_B5'), ndvi89, ndvi57))
    return ndvi.rename('NDVI').copyProperties(img, ['system:time_start'])

def geotiff_to_png(tif_path, png_path):
    print(f"Converting {tif_path} to colored PNG...")
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        nodata = src.nodata
        
        # Create mask for nodata or invalid values
        mask = (data == nodata) | np.isnan(data) | (data < -1) | (data > 1)
        
        rgba = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
        
        # Color mapping for NDVI:
        # <= 0.1: Transparent / Bare soil (greyish-brown)
        # 0.1 - 0.3: Light green-yellow
        # 0.3 - 0.5: Medium green
        # > 0.5: Dark green
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if mask[i, j]:
                    rgba[i, j] = [0, 0, 0, 0] # fully transparent
                else:
                    val = data[i, j]
                    if val <= 0.1:
                        rgba[i, j] = [160, 140, 120, 80] # Bare soil, high transparency
                    elif val <= 0.3:
                        rgba[i, j] = [210, 225, 140, 180] # Transition veg
                    elif val <= 0.5:
                        rgba[i, j] = [110, 190, 80, 210] # Grassland/medium canopy
                    else:
                        rgba[i, j] = [20, 110, 40, 240] # Dense canopy / forest
                        
        img = Image.fromarray(rgba, 'RGBA')
        # Resize if too large to save space (max 1000px width/height)
        max_size = 1200
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img.save(png_path, "PNG")
    print(f"PNG saved successfully at {png_path}.")

def main():
    parser = argparse.ArgumentParser(description="Download monthly NDVI Rasters from GEE and save to directories & database")
    parser.add_argument("--sensor", choices=["modis", "landsat", "sentinel", "all"], default="all", help="Capteur à traiter")
    parser.add_argument("--start-year", type=int, default=2024, help="Année de début")
    parser.add_argument("--end-year", type=int, default=2024, help="Année de fin")
    parser.add_argument("--start-month", type=int, default=1, help="Mois de début (1-12)")
    parser.add_argument("--end-month", type=int, default=12, help="Mois de fin (1-12)")
    parser.add_argument("--project", default="eehanitriniala", help="Projet Google Cloud GEE")
    
    args, unknown = parser.parse_known_args()
    
    print("Initialisation de Google Earth Engine...")
    try:
        ee.Initialize(project=args.project)
        print("GEE OK.")
    except Exception as e:
        print("Erreur d'initialisation GEE:", e)
        sys.exit(1)
        
    engine = make_engine()
    setup_database(engine)
    
    # Get exact bounding box of communes from PostGIS
    print("Calcul de l'emprise des communes...")
    try:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT ST_XMin(extent), ST_YMin(extent), ST_XMax(extent), ST_YMax(extent) 
                FROM (SELECT ST_Extent(geom) as extent FROM public.communes) as sub
            """)).fetchone()
            if not res or None in res:
                raise ValueError("BBox contains null values")
            bbox = [res[0], res[1], res[2], res[3]]
            print(f"Emprise calculée: Longitude [{bbox[0]} to {bbox[2]}], Latitude [{bbox[1]} to {bbox[3]}]")
    except Exception as e:
        print("Erreur lors du calcul de l'emprise. Utilisation d'une emprise par défaut du Sud de Madagascar.", e)
        bbox = [43.0, -25.6, 47.5, -21.5]
        
    # GEE Bounding Box geometry
    region = ee.Geometry.BBox(bbox[0], bbox[1], bbox[2], bbox[3])
    
    sensors = [args.sensor] if args.sensor != "all" else ["modis", "landsat", "sentinel"]
    
    public_dir = Path("public/data/raster") if os.path.exists("public") else Path("public/data/raster")
    
    for sensor in sensors:
        for year in range(args.start_year, args.end_year + 1):
            # Create directory for sensor/year
            dir_path = Path(f"public/data/raster/{sensor}/{year}")
            dir_path.mkdir(parents=True, exist_ok=True)
            
            for month in range(args.start_month, args.end_month + 1):
                print(f"\n--- Téléchargement Raster {sensor.upper()} - {year}/{month:02d} ---")
                
                # Filenames
                tif_filename = f"ndvi_{month:02d}.tif"
                png_filename = f"ndvi_{month:02d}.png"
                
                tif_path = dir_path / tif_filename
                png_path = dir_path / png_filename
                
                # Fetch monthly image from GEE
                start_date = ee.Date.fromYMD(year, month, 1)
                end_date = start_date.advance(1, 'month')
                
                try:
                    if sensor == "modis":
                        col = ee.ImageCollection('MODIS/061/MOD13Q1').select('NDVI').filterDate(start_date, end_date)
                        scale = 250
                        img = col.mean().multiply(0.0001)
                    elif sensor == "landsat":
                        l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterBounds(region).filter(ee.Filter.lt('CLOUD_COVER', 40))
                        l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(region).filter(ee.Filter.lt('CLOUD_COVER', 40))
                        l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(region).filter(ee.Filter.lt('CLOUD_COVER', 40))
                        l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(region).filter(ee.Filter.lt('CLOUD_COVER', 40))
                        merged = l5.merge(l7).merge(l8).merge(l9).map(get_landsat_ndvi)
                        scale = 250 # Adjust to stay under GEE's 50MB direct download request limit
                        img = merged.filterDate(start_date, end_date).mean()
                    else: # sentinel
                        col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                                .filterBounds(region) \
                                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
                                .select(['B4', 'B8'])
                        scale = 250 # Adjust to stay under GEE's 50MB direct download request limit
                        img = col.filterDate(start_date, end_date).median().normalizedDifference(['B8', 'B4'])
                        
                    # Check if image has data
                    # Let's clip to bbox
                    img = img.clip(region)
                    
                    print("Génération de l'URL de téléchargement...")
                    download_url = img.getDownloadURL({
                        'scale': scale,
                        'crs': 'EPSG:4326',
                        'region': region,
                        'format': 'GEO_TIFF'
                    })
                    
                    print(f"Téléchargement du fichier...")
                    r = requests.get(download_url, timeout=45)
                    if r.status_code != 200:
                        print(f"Erreur HTTP de téléchargement ({r.status_code}): {r.text}")
                        continue
                        
                    content = r.content
                    if content.startswith(b'PK\x03\x04'):
                        print("Format ZIP détecté. Extraction...")
                        z = zipfile.ZipFile(io.BytesIO(content))
                        tif_names = [name for name in z.namelist() if name.endswith('.tif')]
                        if not tif_names:
                            print("Aucun fichier .tif trouvé dans le zip.")
                            continue
                        tif_data = z.read(tif_names[0])
                    elif content.startswith(b'II*\x00') or content.startswith(b'MM\x00*'):
                        print("Format GeoTIFF brut détecté.")
                        tif_data = content
                    else:
                        print(f"Format inconnu ou message d'erreur. Début de réponse: {content[:200]}")
                        continue
                        
                    with open(tif_path, 'wb') as f:
                        f.write(tif_data)
                        
                    # Convert to colored PNG
                    geotiff_to_png(str(tif_path), str(png_path))
                    
                    # Read bounds using rasterio to store exact coordinates
                    with rasterio.open(str(tif_path)) as src:
                        b = src.bounds
                        leaflet_bounds = [[b.bottom, b.left], [b.top, b.right]]
                        
                    # Insert metadata in database (UPSERT)
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO public.rasters ("sensor", "year", "month", "tiff_path", "png_path", "bounds")
                            VALUES (:sensor, :year, :month, :tiff_path, :png_path, :bounds)
                            ON CONFLICT ("sensor", "year", "month")
                            DO UPDATE SET "tiff_path" = EXCLUDED."tiff_path",
                                          "png_path" = EXCLUDED."png_path",
                                          "bounds" = EXCLUDED."bounds"
                        """), {
                            'sensor': sensor,
                            'year': year,
                            'month': month,
                            'tiff_path': f"/data/raster/{sensor}/{year}/{tif_filename}",
                            'png_path': f"/data/raster/{sensor}/{year}/{png_filename}",
                            'bounds': json.dumps(leaflet_bounds)
                        })
                    print(f"Métadonnées enregistrées pour {sensor} - {year}/{month:02d}")
                    
                except Exception as e:
                    print(f"Erreur lors du traitement de {sensor} - {year}/{month:02d}:", e)
                    
    # Generate metadata.json file for frontend
    print("\nGénération du fichier de métadonnées des rasters public/data/raster_metadata.json...")
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT sensor, year, month, png_path, bounds FROM public.rasters ORDER BY sensor, year, month"))
            meta_dict = {}
            for r in res:
                sensor = r[0]
                year = r[1]
                month = r[2]
                png_path = r[3]
                bounds = r[4] # This is already a parsed list or dict if loaded as JSONB
                if isinstance(bounds, str):
                    bounds = json.loads(bounds)
                
                key = f"{sensor}_{year}_{month:02d}"
                meta_dict[key] = {
                    "sensor": sensor,
                    "year": year,
                    "month": month,
                    "png": png_path,
                    "bounds": bounds,
                    "label": f"{sensor.upper()} {year}/{month:02d}"
                }
                
        meta_file_path = Path("public/data/raster_metadata.json")
        meta_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_file_path, "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, indent=2)
        print("Métadonnées générées avec succès !")
    except Exception as e:
        print("Erreur de génération des métadonnées:", e)

if __name__ == "__main__":
    from pathlib import Path
    main()
