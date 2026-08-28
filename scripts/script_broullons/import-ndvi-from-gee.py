import os
import argparse
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
import geopandas as gpd
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
            CREATE TABLE IF NOT EXISTS public.ndvi_data (
                "commune_code" VARCHAR(50) NOT NULL,
                "sensor" VARCHAR(20) NOT NULL,
                "year" INTEGER NOT NULL,
                "month" INTEGER NOT NULL,
                "ndvi" DOUBLE PRECISION,
                PRIMARY KEY ("commune_code", "sensor", "year", "month")
            )
        """))
    print("Database table public.ndvi_data verified/created.")

def get_landsat_ndvi(img):
    scaled = img.select('SR_B.*').multiply(0.0000275).add(-0.2)
    img = img.addBands(scaled, None, True)
    bands = img.bandNames()
    
    ndvi57 = img.normalizedDifference(['SR_B4', 'SR_B3'])
    ndvi89 = img.normalizedDifference(['SR_B5', 'SR_B4'])
    
    ndvi = ee.Image(ee.Algorithms.If(bands.contains('SR_B5'), ndvi89, ndvi57))
    return ndvi.rename('NDVI').copyProperties(img, ['system:time_start'])

def process_modis(ee_fc, year, scale):
    modisNDVI = ee.ImageCollection('MODIS/061/MOD13Q1').select('NDVI')
    monthly_images = []
    months = list(range(1, 13))
    
    for month in months:
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, 'month')
        
        monthly_col = modisNDVI.filterDate(start, end)
        
        monthly_ndvi = ee.Algorithms.If(
            monthly_col.size().gt(0),
            monthly_col.mean().multiply(0.0001).rename(f"m_{month}"),
            ee.Image.constant(-9999).rename(f"m_{month}")
        )
        monthly_images.append(ee.Image(monthly_ndvi))
        
    stack = ee.ImageCollection.fromImages(monthly_images).toBands()
    return stack.rename([f"m_{m}" for m in months])

def process_landsat(ee_fc, year, scale):
    # Load Landsat collections and merge
    l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').filterBounds(ee_fc).filter(ee.Filter.lt('CLOUD_COVER', 40))
    l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(ee_fc).filter(ee.Filter.lt('CLOUD_COVER', 40))
    l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(ee_fc).filter(ee.Filter.lt('CLOUD_COVER', 40))
    l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterBounds(ee_fc).filter(ee.Filter.lt('CLOUD_COVER', 40))
    
    merged = l5.merge(l7).merge(l8).merge(l9).map(get_landsat_ndvi)
    
    monthly_images = []
    months = list(range(1, 13))
    
    for month in months:
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, 'month')
        
        monthly_col = merged.filterDate(start, end)
        
        monthly_ndvi = ee.Algorithms.If(
            monthly_col.size().gt(0),
            monthly_col.mean().rename(f"m_{month}"),
            ee.Image.constant(-9999).rename(f"m_{month}")
        )
        monthly_images.append(ee.Image(monthly_ndvi))
        
    stack = ee.ImageCollection.fromImages(monthly_images).toBands()
    return stack.rename([f"m_{m}" for m in months])

def process_sentinel(ee_fc, year, scale):
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
           .filterBounds(ee_fc) \
           .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)) \
           .select(['B4', 'B8'])
           
    monthly_images = []
    months = list(range(1, 13))
    
    for month in months:
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, 'month')
        
        monthly_col = s2.filterDate(start, end)
        
        monthly_ndvi = ee.Algorithms.If(
            monthly_col.size().gt(0),
            monthly_col.median().normalizedDifference(['B8', 'B4']).rename(f"m_{month}"),
            ee.Image.constant(-9999).rename(f"m_{month}")
        )
        monthly_images.append(ee.Image(monthly_ndvi))
        
    stack = ee.ImageCollection.fromImages(monthly_images).toBands()
    return stack.rename([f"m_{m}" for m in months])

def main():
    parser = argparse.ArgumentParser(description="Importer les données NDVI de GEE vers PostgreSQL")
    parser.add_argument("--sensor", choices=["modis", "landsat", "sentinel", "all"], default="all", help="Capteur à traiter (default: all)")
    parser.add_argument("--start", type=int, help="Année de début")
    parser.add_argument("--end", type=int, help="Année de fin")
    parser.add_argument("--scale", type=int, default=100, help="Résolution spatiale en mètres pour la réduction (default: 100m)")
    parser.add_argument("--project", default="eehanitriniala", help="Projet Google Cloud pour Earth Engine")
    
    # We allow running with custom args or standardsys.argv
    args, unknown = parser.parse_known_args()
    
    print("Initialisation de Google Earth Engine...")
    try:
        ee.Initialize(project=args.project)
        print("Initialisation GEE OK.")
    except Exception as e:
        print("Erreur initialisation GEE. Avez-vous exécuté l'authentification ?", e)
        sys.exit(1)
        
    engine = make_engine()
    setup_database(engine)
    
    print("Chargement des communes depuis la base de données...")
    try:
        gdf = gpd.read_postgis("SELECT \"ADM3_PCODE\", \"geom\" FROM public.communes", engine, geom_col="geom")
        print(f"{len(gdf)} communes chargées.")
    except Exception as e:
        print("Erreur de chargement des communes depuis la base de données:", e)
        sys.exit(1)
        
    print("Conversion des communes en ee.FeatureCollection...")
    ee_features = []
    for idx, row in gdf.iterrows():
        # Simplification pour accélérer l'import et éviter les limites de taille de payload
        simplified = row['geom'].simplify(0.001)
        g = simplified.__geo_interface__
        ee_geom = ee.Geometry(g)
        ee_feat = ee.Feature(ee_geom, {'code': row['ADM3_PCODE']})
        ee_features.append(ee_feat)
        
    ee_fc = ee.FeatureCollection(ee_features)
    print("Features GEE créées.")
    
    sensors = [args.sensor] if args.sensor != "all" else ["modis", "landsat", "sentinel"]
    
    for sensor in sensors:
        # Default years
        if sensor == "sentinel":
            start_y = args.start if args.start else 2015
            end_y = args.end if args.end else 2025
        else:
            start_y = args.start if args.start else 2000
            end_y = args.end if args.end else 2025
            
        print(f"\n--- Début du traitement pour {sensor.upper()} ({start_y} à {end_y}) ---")
        
        for year in range(start_y, end_y + 1):
            print(f"Calcul NDVI {sensor.upper()} pour l'année {year}...")
            try:
                if sensor == "modis":
                    stack = process_modis(ee_fc, year, args.scale)
                    scale_val = 250
                elif sensor == "landsat":
                    stack = process_landsat(ee_fc, year, args.scale)
                    scale_val = args.scale
                else:  # sentinel
                    stack = process_sentinel(ee_fc, year, args.scale)
                    scale_val = args.scale
                    
                reduced = stack.reduceRegions(
                    collection=ee_fc,
                    reducer=ee.Reducer.mean(),
                    scale=scale_val
                )
                
                # Fetch results from GEE
                info = reduced.getInfo()
                
                rows_to_insert = []
                for feature in info.get('features', []):
                    commune_code = feature['properties']['code']
                    props = feature['properties']
                    
                    for month in range(1, 13):
                        val_key = f"m_{month}"
                        if val_key in props:
                            val = props[val_key]
                            # GEE returns -9999 if no data
                            if val == -9999 or val is None:
                                val = None
                            rows_to_insert.append({
                                'commune_code': commune_code,
                                'sensor': sensor,
                                'year': year,
                                'month': month,
                                'ndvi': val
                            })
                
                # Write to database (UPSERT)
                if rows_to_insert:
                    with engine.begin() as conn:
                        for row in rows_to_insert:
                            conn.execute(text("""
                                INSERT INTO public.ndvi_data ("commune_code", "sensor", "year", "month", "ndvi")
                                VALUES (:commune_code, :sensor, :year, :month, :ndvi)
                                ON CONFLICT ("commune_code", "sensor", "year", "month")
                                DO UPDATE SET "ndvi" = EXCLUDED."ndvi"
                            """), row)
                    print(f"Année {year} enregistrée en BDD. ({len(rows_to_insert)} valeurs)")
                    
            except Exception as e:
                print(f"Erreur sur l'année {year}:", e)
                
    print("\nImport NDVI terminé avec succès !")

if __name__ == "__main__":
    main()
