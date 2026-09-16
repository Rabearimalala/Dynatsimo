from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "public" / "data"

MONTH_LABELS = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Avr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Aou",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def make_engine() -> Engine:
    db_url = URL.create(
        "postgresql",
        username=env("DYNATSIMO_DBUSER", "postgres"),
        password=env("DYNATSIMO_DBPASSWORD", "admin"),
        host=env("DYNATSIMO_DBHOST", "localhost"),
        port=int(env("DYNATSIMO_DBPORT", "5432")),
        database=env("DYNATSIMO_DBNAME", "precipitation"),
    )
    return create_engine(db_url)


def clean_for_json(value):
    if value is None or value is pd.NA:
        return None
    if isinstance(value, dict):
        return {key: clean_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_for_json(item) for item in value]
    if isinstance(value, tuple):
        return [clean_for_json(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def write_pretty_json(data, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(
        json.dumps(clean_for_json(data), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_json_file(filename: str, default):
    path = OUTPUT_DIR / filename
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_static_commune_properties() -> dict[str, dict]:
    properties: dict[str, dict] = {}

    communes = load_json_file("communes.json", [])
    if isinstance(communes, list):
        for commune in communes:
            if not isinstance(commune, dict):
                continue
            code = str(commune.get("code", "")).strip().upper()
            if code:
                properties.setdefault(code, {}).update(commune)

    geojson = load_json_file("communes.geojson", {})
    if isinstance(geojson, dict):
        for feature in geojson.get("features", []):
            feature_properties = feature.get("properties", {}) if isinstance(feature, dict) else {}
            if not isinstance(feature_properties, dict):
                continue
            code = str(feature_properties.get("code", "")).strip().upper()
            if code:
                properties.setdefault(code, {}).update(feature_properties)

    return properties


def first_present(*values):
    for value in values:
        if value is None:
            continue
        try:
            if pd.isna(value):
                continue
        except (TypeError, ValueError):
            pass
        if value != "":
            return value
    return None


def parse_chirps_date(filename: str) -> tuple[int, int] | None:
    # Typical monthly CHIRPS name: chirps-v2.0.1981.01.tif
    match = re.search(r"((?:19|20)\d{2})\.(0?[1-9]|1[0-2])", filename)
    if not match:
        return None

    return int(match.group(1)), int(match.group(2))


def safe_table_name(table_name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?", table_name):
        raise RuntimeError(f"Nom de table invalide: {table_name}")
    return table_name


def quote_identifier(identifier: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise RuntimeError(f"Nom de colonne invalide: {identifier}")
    return f'"{identifier}"'


def table_exists(engine: Engine, table_name: str) -> bool:
    table_name = safe_table_name(table_name)

    with engine.connect() as conn:
        value = conn.execute(text("SELECT to_regclass(:table_name)"), {"table_name": table_name}).scalar()

    return value is not None


def table_columns(engine: Engine, table_name: str) -> list[str]:
    table_name = safe_table_name(table_name)
    if "." in table_name:
        schema_name, bare_name = table_name.split(".", 1)
    else:
        schema_name, bare_name = "public", table_name

    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = :schema_name
          AND table_name = :table_name
        ORDER BY ordinal_position
    """
    with engine.connect() as conn:
        rows = conn.execute(text(query), {"schema_name": schema_name, "table_name": bare_name}).fetchall()

    return [row[0] for row in rows]


def resolve_communes_table(engine: Engine) -> str:
    configured_table = env("DYNATSIMO_COMMUNES_TABLE", "").strip()
    if configured_table:
        return safe_table_name(configured_table)

    for table_name in ("public.communes", "public.comunes_androy_anosy"):
        if table_exists(engine, table_name):
            return table_name

    return "public.communes"


def read_communes_metadata(engine: Engine) -> pd.DataFrame:
    communes_table = resolve_communes_table(engine)
    query = f"SELECT * FROM {safe_table_name(communes_table)}"

    try:
        communes = pd.read_sql(query, engine)
    except Exception:
        if not table_exists(engine, "public.commune"):
            raise

        communes = pd.read_sql(
            """
            SELECT
              code AS "ADM3_PCODE",
              code AS "ADM3_EN",
              NULL AS "ADM1_EN"
            FROM public.commune
            """,
            engine,
        )

    if "ADM3_PCODE" not in communes.columns:
        raise RuntimeError(f"La table {communes_table} doit contenir la colonne ADM3_PCODE.")

    if "ADM3_EN" not in communes.columns:
        communes["ADM3_EN"] = communes["ADM3_PCODE"]

    if "ADM1_EN" not in communes.columns:
        communes["ADM1_EN"] = None

    communes["ADM3_PCODE"] = communes["ADM3_PCODE"].astype(str).str.strip().str.upper()
    communes["code_Commune"] = communes["ADM3_PCODE"]

    return communes


def read_communes(engine: Engine):
    import geopandas as gpd

    communes_table = resolve_communes_table(engine)
    geom_column = env("DYNATSIMO_GEOM_COLUMN", "geom")
    query = f"SELECT * FROM {safe_table_name(communes_table)}"
    communes = gpd.read_postgis(query, engine, geom_col=geom_column)
    if communes.geometry.name != "geom":
        communes = communes.rename_geometry("geom")

    if "ADM3_PCODE" not in communes.columns:
        raise RuntimeError(f"La table {communes_table} doit contenir la colonne ADM3_PCODE.")

    if "ADM3_EN" not in communes.columns:
        communes["ADM3_EN"] = communes["ADM3_PCODE"]

    if "ADM1_EN" not in communes.columns:
        communes["ADM1_EN"] = None

    communes["ADM3_PCODE"] = communes["ADM3_PCODE"].astype(str).str.strip().str.upper()
    communes["code_Commune"] = communes["ADM3_PCODE"]

    if communes.crs is None:
        communes = communes.set_crs("EPSG:4326")
    elif communes.crs.to_epsg() != 4326:
        communes = communes.to_crs(epsg=4326)

    return communes


def import_chirps_to_postgres(engine: Engine, force_rebuild: bool = False) -> pd.DataFrame:
    from rasterstats import zonal_stats

    default_chirps = ROOT_DIR / "CHIRPS_data"
    chirps_dir = Path(env("DYNATSIMO_CHIRPS_DIR", str(default_chirps)))
    if not chirps_dir.exists():
        raise FileNotFoundError(
            f"Dossier CHIRPS introuvable: {chirps_dir}. "
            "Change DYNATSIMO_CHIRPS_DIR ou verifie le dossier CHIRPS_data."
        )

    communes = read_communes(engine)
    nodata = float(env("DYNATSIMO_CHIRPS_NODATA", "-9999"))
    all_touched = env("DYNATSIMO_ALL_TOUCHED", "false").lower() == "true"

    tif_files = sorted(chirps_dir.glob("*.tif"))
    if not tif_files:
        raise FileNotFoundError(f"Aucun fichier .tif trouve dans {chirps_dir}")

    existing_dates = set()
    table_created = False

    with engine.begin() as conn:
        has_table = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'precipitation')")
        ).scalar()
        if not has_table or force_rebuild:
            conn.execute(text('DROP TABLE IF EXISTS public.precipitation'))
            conn.execute(
                text(
                    """
                    CREATE TABLE public.precipitation (
                      "Commune_Id" TEXT NOT NULL,
                      "Year" INTEGER NOT NULL,
                      "Month" INTEGER NOT NULL,
                      "Precip" DOUBLE PRECISION,
                      PRIMARY KEY ("Commune_Id", "Year", "Month")
                    )
                    """
                )
            )
            table_created = True
        else:
            dates = conn.execute(text('SELECT DISTINCT "Year", "Month" FROM public.precipitation')).fetchall()
            existing_dates = {(int(r[0]), int(r[1])) for r in dates}

    # Filter files to only process missing dates
    files_to_process = []
    for raster_path in tif_files:
        date_parts = parse_chirps_date(raster_path.name)
        if date_parts is None:
            continue
        if date_parts not in existing_dates or force_rebuild:
            files_to_process.append((date_parts[0], date_parts[1], raster_path))

    if not files_to_process:
        print(f"✓ Base PostgreSQL deja a jour ({len(existing_dates)} mois presents).")
        return pd.read_sql('SELECT * FROM public.precipitation ORDER BY "Commune_Id", "Year", "Month"', engine)

    print(f"Calcul des statistiques zonales pour {len(files_to_process)} nouveau(x) raster(s) CHIRPS...")
    rows = []
    for year, month, raster_path in files_to_process:
        print(f"  - Traitement {year}-{month:02d} ({raster_path.name})...")
        stats = zonal_stats(
            communes,
            str(raster_path),
            stats=["mean"],
            nodata=nodata,
            all_touched=all_touched,
        )

        for commune, stat in zip(communes.itertuples(), stats):
            precip = stat.get("mean")
            rows.append(
                {
                    "Commune_Id": commune.ADM3_PCODE,
                    "Year": year,
                    "Month": month,
                    "Precip": float(precip) if precip is not None else np.nan,
                }
            )

    new_precipitation = pd.DataFrame(rows)
    if not new_precipitation.empty:
        new_precipitation.to_sql(
            "precipitation",
            engine,
            schema="public",
            if_exists="append",
            index=False,
            chunksize=5000,
        )
        print(f"✓ Insertion PostgreSQL OK: {len(new_precipitation)} lignes ajoutees.")

    return pd.read_sql('SELECT * FROM public.precipitation ORDER BY "Commune_Id", "Year", "Month"', engine)


def calc_saison(df_commune_saison: pd.DataFrame, region: str = "", seuil_chute_mm: float = 50) -> dict:
    """
    Calcul agrométéorologique de la saison des pluies adapté aux 3 régions du Grand Sud de Madagascar :
    - Androy : Début en Novembre (fin nov), Période Nov -> Mars (SRAT / Monographie)
    - Anosy : Début en Novembre (parfois Oct), Période Nov -> Mars ou Avril
    - Atsimo-Andrefana : Début en Novembre (parfois Oct), Période Nov -> Mars (parfois Avril)
    """
    if df_commune_saison.empty:
        return empty_saison()

    df_sorted = df_commune_saison.copy()
    df_sorted["_ordre"] = np.where(df_sorted["Month"] >= 10, df_sorted["Month"], df_sorted["Month"] + 12)
    df_sorted = df_sorted.sort_values("_ordre")

    precip = df_sorted["Precip"].to_numpy(dtype=float)
    months = df_sorted["Month"].to_numpy(dtype=int)

    if len(precip) < 5 or np.isnan(precip).all():
        return empty_saison()

    # Dictionnaire mois -> précipitation
    p_map = {int(m): (float(p) if pd.notnull(p) else 0.0) for m, p in zip(months, precip)}

    # 1. DÉBUT DE SAISON (Grand Sud : Androy, Anosy, Atsimo-Andrefana)
    p_oct = p_map.get(10, 0.0)
    p_nov = p_map.get(11, 0.0)
    p_dec = p_map.get(12, 0.0)
    p_jan = p_map.get(1, 0.0)

    # Démarrage précoce en Octobre uniquement si pluies significatives (>= 35mm) et installation confirmée
    if p_oct >= 35.0 and (p_nov >= 30.0 or p_dec >= 60.0):
        debut = 10
    # Démarrage standard en Novembre si pluies d'installation (>= 25mm ou amorce nette vers Décembre)
    elif p_nov >= 25.0 or (p_nov >= 15.0 and p_dec >= 50.0):
        debut = 11
    # Démarrage en Décembre si Novembre très sec (< 15mm) mais Décembre pluvieux (>= 40mm)
    elif p_dec >= 40.0:
        debut = 12
    # Démarrage très tardif en Janvier en cas de retard sévère (sécheresse de début de saison)
    elif p_jan >= 50.0:
        debut = 1
    else:
        # Repli climatologique régional : Novembre
        debut = 11

    # 2. FIN DE SAISON (Retrait des pluies : Février, Mars, Avril, Mai)
    p_fev = p_map.get(2, 0.0)
    p_mar = p_map.get(3, 0.0)
    p_avr = p_map.get(4, 0.0)
    p_mai = p_map.get(5, 0.0)

    # Prolongation en Mai si pluies tardives soutenues (courant en Anosy maritime)
    if p_mai >= 40.0 and p_avr >= 40.0:
        fin = 5
    # Prolongation en Avril si Avril reste humide (>= 30mm et Mars soutenu)
    elif p_avr >= 30.0 and p_mar >= 40.0:
        fin = 4
    # Fin normale en Mars si Mars a encore des pluies significatives (>= 25mm)
    elif p_mar >= 25.0 or (p_fev >= 60.0 and p_mar >= 15.0):
        fin = 3
    # Fin précoce en Février si arrêt précoce des pluies en Mars (< 15mm)
    elif p_fev >= 30.0 and p_mar < 15.0:
        fin = 2
    elif p_jan >= 40.0 and p_fev < 20.0 and p_mar < 15.0:
        fin = 1
    else:
        # Repli climatologique régional
        if "anosy" in str(region).lower() and p_avr >= 25.0:
            fin = 4
        else:
            fin = 3

    # 3. DURÉE (en mois)
    if debut >= 10:
        duree = (12 - debut + 1) + fin
        saison_months = list(range(debut, 13)) + list(range(1, fin + 1))
    else:
        duree = (fin - debut + 1)
        saison_months = list(range(debut, fin + 1))

    if duree <= 0 or duree > 12:
        duree = max(1, min(8, duree))

    # 4. MOIS LE PLUS PLUVIEUX
    active_p = {m: p_map.get(m, 0.0) for m in saison_months}
    mois_plus_pluvieux = max(active_p, key=active_p.get) if active_p else 1

    return {
        "debut_saison": debut,
        "fin_saison": fin,
        "duree_saison": duree,
        "mois_plus_pluvieux": mois_plus_pluvieux,
    }


def empty_saison() -> dict:
    return {
        "debut_saison": None,
        "fin_saison": None,
        "duree_saison": None,
        "mois_plus_pluvieux": None,
    }


def read_precipitation_direct_schema(engine: Engine) -> pd.DataFrame:
    return pd.read_sql(
        """
        SELECT
          p."Commune_Id",
          p."Year",
          p."Month",
          p."Precip"
        FROM public.precipitation p
        """,
        engine,
    )


def read_precipitation_relational_schema(engine: Engine) -> pd.DataFrame:
    return pd.read_sql(
        """
        SELECT
          c.code AS "Commune_Id",
          a.annee AS "Year",
          m.mois AS "Month",
          p.precipitation AS "Precip"
        FROM public.precipitation p
        JOIN public.commune c
          ON p.commune_id = c.commune_id
        JOIN public.mois m
          ON p.mois_id = m.mois_id
        JOIN public.annee a
          ON m.annee_id = a.annee_id
        """,
        engine,
    )


def load_precipitation_for_export(engine: Engine) -> pd.DataFrame:
    errors = []

    try:
        df = read_precipitation_direct_schema(engine)
    except Exception as error:
        errors.append(f"schema direct: {error}")
        try:
            df = read_precipitation_relational_schema(engine)
        except Exception as relational_error:
            errors.append(f"schema relationnel: {relational_error}")
            raise RuntimeError(
                "Impossible de lire les precipitations PostgreSQL. "
                "L'API accepte soit public.precipitation avec "
                '"Commune_Id", "Year", "Month", "Precip", soit les tables '
                "public.commune/public.mois/public.annee/public.precipitation. "
                + " | ".join(errors)
            ) from relational_error

    if df.empty:
        raise RuntimeError("La table public.precipitation est vide.")

    communes = read_communes_metadata(engine)[["ADM3_PCODE", "ADM3_EN", "ADM1_EN"]].drop_duplicates()
    communes = communes.rename(
        columns={
            "ADM3_PCODE": "code_Commune",
            "ADM3_EN": "Commune",
            "ADM1_EN": "Region",
        }
    )

    df["Commune_Id"] = df["Commune_Id"].astype(str).str.strip().str.upper()
    df = df.merge(communes, left_on="Commune_Id", right_on="code_Commune", how="left")
    df["code_Commune"] = df["code_Commune"].fillna(df["Commune_Id"])
    df["Commune"] = df["Commune"].fillna(df["Commune_Id"])

    df["Month"] = df["Month"].astype(int)
    df["Year"] = df["Year"].astype(int)
    df["Precip"] = pd.to_numeric(df["Precip"], errors="coerce")
    df["code_Commune"] = df["code_Commune"].astype(str).str.strip().str.upper()
    df["Saison"] = np.where(df["Month"] >= 10, df["Year"], df["Year"] - 1)

    return df[
        (df["Year"] >= 1981)
        & (df["Month"] >= 1)
        & (df["Month"] <= 12)
    ].copy()


def build_communes_geojson(engine: Engine, map_precip: pd.DataFrame, deficit_crise: pd.DataFrame) -> dict:
    communes_table = resolve_communes_table(engine)
    geom_column = quote_identifier(env("DYNATSIMO_GEOM_COLUMN", "geom"))
    static_properties = load_static_commune_properties()
    query = f"""
        SELECT
          *,
          ST_AsGeoJSON({geom_column}) AS geometry_json
        FROM {communes_table}
    """
    try:
        communes = pd.read_sql(query, engine)
    except Exception:
        return {
            "type": "FeatureCollection",
            "features": [],
        }

    if "ADM3_PCODE" not in communes.columns:
        raise RuntimeError(f"La table {communes_table} doit contenir la colonne ADM3_PCODE.")

    if "ADM3_EN" not in communes.columns:
        communes["ADM3_EN"] = communes["ADM3_PCODE"]

    if "ADM1_EN" not in communes.columns:
        communes["ADM1_EN"] = None

    communes["code_Commune"] = communes["ADM3_PCODE"].astype(str).str.strip().str.upper()
    communes = communes.merge(map_precip, on="code_Commune", how="left")
    communes = communes.merge(deficit_crise, on="code_Commune", how="left")

    features = []
    for row in communes.to_dict("records"):
        code = row["code_Commune"]
        existing = static_properties.get(code, {})
        deficit = row.get("deficit")
        alert = existing.get("alert")
        if not alert and pd.notna(deficit):
            alert = "Alerte Rouge" if deficit < -18 else "Vigilance" if deficit < -8 else "Stable"

        geometry = json.loads(row["geometry_json"]) if row.get("geometry_json") else None
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "code": code,
                    "nom": first_present(row.get("ADM3_EN"), existing.get("nom"), code),
                    "district": first_present(row.get("ADM2_EN"), existing.get("district")),
                    "region": first_present(row.get("ADM1_EN"), existing.get("region")),
                    "ecoregion": first_present(row.get("ecoregion"), existing.get("ecoregion")),
                    "precip": row.get("precip"),
                    "deficit": row.get("deficit"),
                    "alert": alert,
                    "ndvi": existing.get("ndvi"),
                    "vegCover": existing.get("vegCover"),
                    "forestArea": existing.get("forestArea"),
                    "annualLoss": existing.get("annualLoss"),
                },
                "geometry": geometry,
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def read_latest_json_payload(engine: Engine, table_candidates: list[str], payload_column: str = "payload"):
    for table_name in table_candidates:
        if not table_exists(engine, table_name):
            continue

        columns = table_columns(engine, table_name)
        order_by = []
        for candidate in ("updated_at", "created_at", "inserted_at", "id"):
            if candidate in columns:
                order_by.append(candidate)

        query = f"""
            SELECT {quote_identifier(payload_column)} AS payload
            FROM {safe_table_name(table_name)}
        """
        if order_by:
            query += " ORDER BY " + ", ".join(f"{quote_identifier(column)} DESC" for column in order_by)
        query += " LIMIT 1"

        try:
            row = pd.read_sql(query, engine)
        except Exception:
            continue

        if row.empty:
            continue

        payload = row.iloc[0]["payload"]
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                continue
        if isinstance(payload, dict):
            return payload
        if pd.notna(payload):
            try:
                return json.loads(payload)
            except Exception:
                continue

    return None


def load_vegetation_payload(engine: Engine) -> dict:
    # 1. Load the template/static config from local json
    veg_data_path = OUTPUT_DIR / "vegetation-data.json"
    payload = {}
    if veg_data_path.exists():
        try:
            with open(veg_data_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            print(f"Error loading template: {e}")

    if not payload:
        payload = {"ecoregions": {}, "sensorComparison": {}, "timeSeries": {}}

    # 2. Query ndvi_data from database
    try:
        df_ndvi = pd.read_sql("SELECT * FROM public.ndvi_data", engine)
        if not df_ndvi.empty:
            # Clean column types
            df_ndvi['month'] = df_ndvi['month'].astype(int)
            df_ndvi['year'] = df_ndvi['year'].astype(int)
            df_ndvi['ndvi'] = pd.to_numeric(df_ndvi['ndvi'], errors='coerce')
            
            # Drop rows with null ndvi
            df_ndvi = df_ndvi.dropna(subset=['ndvi'])
            
            # Compute baseline: average ndvi per sensor, commune, and month
            df_baseline = df_ndvi.groupby(['sensor', 'commune_code', 'month'])['ndvi'].mean().reset_index(name='baseline')
            
            # Create a lookup dictionary for baseline values
            baseline_lookup = df_baseline.set_index(['sensor', 'commune_code', 'month'])['baseline'].to_dict()
            
            # Merge to compute anomalies
            df_ndvi = df_ndvi.merge(df_baseline, on=['sensor', 'commune_code', 'month'])
            df_ndvi['anomaly'] = df_ndvi['ndvi'] - df_ndvi['baseline']
            
            # Hydrological season logic:
            # Months ordered: Oct(10), Nov(11), Dec(12), Jan(1), Feb(2), Mar(3), Apr(4), May(5), Jun(6), Jul(7), Aug(8), Sep(9)
            hydro_months = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            df_ndvi['season_start_year'] = np.where(df_ndvi['month'] >= 10, df_ndvi['year'], df_ndvi['year'] - 1)
            
            # Build timeSeries dictionary
            time_series = {}
            for sensor in ['modis', 'landsat', 'sentinel']:
                time_series[sensor] = {}
                
            # Group by sensor, commune_code, season_start_year
            grouped = df_ndvi.groupby(['sensor', 'commune_code', 'season_start_year'])
            
            for (sensor, commune_code, start_year), group in grouped:
                if sensor not in time_series:
                    time_series[sensor] = {}
                if commune_code not in time_series[sensor]:
                    time_series[sensor][commune_code] = []
                    
                # Sort group by hydrological month order
                group = group.copy()
                group['_order'] = group['month'].map(lambda m: hydro_months.index(m))
                group = group.sort_values('_order')
                
                # Fill missing months with baseline
                group_dict = group.set_index('month').to_dict('index')
                
                ndvi_list = []
                cum_list = []
                anom_list = []
                baseline_list = []
                running_sum = 0.0
                
                for m in hydro_months:
                    base_val = round(baseline_lookup.get((sensor, commune_code, m), 0.3), 4)
                    
                    if m in group_dict:
                        ndvi_val = round(group_dict[m]['ndvi'], 4)
                        anom_val = round(group_dict[m]['anomaly'], 4)
                    else:
                        ndvi_val = base_val
                        anom_val = 0.0
                        
                    ndvi_list.append(ndvi_val)
                    running_sum += ndvi_val
                    cum_list.append(round(running_sum, 4))
                    anom_list.append(anom_val)
                    baseline_list.append(base_val)
                    
                time_series[sensor][commune_code].append({
                    "season": f"{start_year}-{start_year+1}",
                    "startYear": int(start_year),
                    "ndvi": ndvi_list,
                    "cumulative": cum_list,
                    "anomalies": anom_list,
                    "baseline": baseline_list,
                    "integratedProductivity": round(running_sum, 4)
                })
                
            # Sort seasons for each commune
            for sensor in time_series:
                for code in time_series[sensor]:
                    time_series[sensor][code].sort(key=lambda s: s['startYear'])
                    
            payload['timeSeries'] = time_series
            print("Successfully compiled timeSeries from PostgreSQL ndvi_data!")
            
    except Exception as e:
        print(f"Error compiling dynamic NDVI payload from database: {e}")
        
    return payload


def build_react_payload(engine: Engine) -> dict:
    df = load_precipitation_for_export(engine)
    static_properties = load_static_commune_properties()

    communes = (
        df[["code_Commune", "Commune", "Region"]]
        .drop_duplicates()
        .sort_values("Commune")
        .rename(columns={"code_Commune": "code", "Commune": "nom", "Region": "region"})
        .to_dict("records")
    )
    for commune in communes:
        existing = static_properties.get(str(commune.get("code", "")).strip().upper(), {})
        commune["district"] = first_present(commune.get("district"), existing.get("district"))
        commune["region"] = first_present(commune.get("region"), existing.get("region"))
        commune["ecoregion"] = first_present(commune.get("ecoregion"), existing.get("ecoregion"))

    yearly_commune_precip = (
        df.groupby(["code_Commune", "Year"], as_index=False)["Precip"]
        .sum()
        .rename(columns={"Precip": "p"})
    )

    annual_data = (
        yearly_commune_precip.groupby("Year", as_index=False)["p"]
        .mean()
        .assign(precip=lambda data: data["p"].round(2))
        .rename(columns={"Year": "year", "p": "precip"})[["year", "precip"]]
        .to_dict("records")
    )

    saison_rows = []
    for (code, commune, saison), group in df.groupby(["code_Commune", "Commune", "Saison"], sort=True):
        reg = str(group["Region"].iloc[0]) if "Region" in group.columns and pd.notnull(group["Region"].iloc[0]) else ""
        values = calc_saison(group, region=reg)
        saison_rows.append(
            {
                "code_commune": code,
                "commune": commune,
                "saison": int(saison),
                "debut": MONTH_LABELS.get(values["debut_saison"]),
                "fin": MONTH_LABELS.get(values["fin_saison"]),
                "duree": values["duree_saison"],
                "mois_plus_pluvieux": MONTH_LABELS.get(values["mois_plus_pluvieux"]),
            }
        )
    saisons = pd.DataFrame(saison_rows)

    precip_saison = (
        df.groupby(["code_Commune", "Saison"], as_index=False)["Precip"]
        .sum()
        .rename(columns={"code_Commune": "code_commune", "Saison": "saison", "Precip": "precip"})
    )
    precip_saison["precip"] = precip_saison["precip"].round(0).astype("Int64")

    saisons = (
        saisons.merge(precip_saison, on=["code_commune", "saison"], how="left")
        .sort_values(["code_commune", "saison"])
        .to_dict("records")
    )

    monthly_climatology = (
        df.groupby("Month", as_index=False)["Precip"]
        .mean()
        .sort_values("Month")
        .assign(
            month=lambda data: data["Month"].map(MONTH_LABELS),
            precip=lambda data: data["Precip"].round(2),
        )[["month", "precip"]]
        .to_dict("records")
    )

    annual_avg_precip = (
        yearly_commune_precip.groupby("Year", as_index=False)["p"]
        .mean()
        .rename(columns={"p": "precip_avg"})
    )
    climatology_ref = annual_avg_precip[
        (annual_avg_precip["Year"] >= 1981) & (annual_avg_precip["Year"] <= 2010)
    ]["precip_avg"].mean()
    anomalies = annual_avg_precip.assign(
        year=annual_avg_precip["Year"],
        anomaly=(annual_avg_precip["precip_avg"] - climatology_ref).round(2),
    )[["year", "anomaly"]].to_dict("records")
    climatologie = (
        yearly_commune_precip[
            (yearly_commune_precip["Year"] >= 1981) & (yearly_commune_precip["Year"] <= 2010)
        ]
        .groupby("code_Commune", as_index=False)["p"]
        .mean()
        .rename(columns={"p": "climatologie"})
    )
    crise = (
        yearly_commune_precip[yearly_commune_precip["Year"].isin([2020, 2021, 2022])]
        .groupby("code_Commune", as_index=False)["p"]
        .mean()
        .rename(columns={"p": "precip_crise"})
        .merge(climatologie, on="code_Commune", how="left")
    )
    crise["deficit"] = ((crise["precip_crise"] - crise["climatologie"]) / crise["climatologie"] * 100).round(2)
    crise["deficit"] = crise["deficit"].clip(-100, 100)
    deficit_crise = crise[["code_Commune", "deficit"]]

    max_year = int(df["Year"].max()) if not df.empty else 2025
    min_recent_year = max(2020, max_year - 5)
    map_precip = (
        yearly_commune_precip[yearly_commune_precip["Year"].between(min_recent_year, max_year)]
        .groupby("code_Commune", as_index=False)["p"]
        .mean()
        .assign(precip=lambda data: data["p"].round(2))[["code_Commune", "precip"]]
    )

    precip_records = (
        df[["code_Commune", "Year", "Month", "Precip"]]
        .rename(columns={"code_Commune": "code", "Year": "year", "Month": "month", "Precip": "precip"})
        .assign(precip=lambda d: d["precip"].round(1))
        .to_dict("records")
    )

    overview = {
        "nb_communes": int(df["code_Commune"].nunique()),
        "nb_years": f"{int(df['Year'].min())}-{int(df['Year'].max())}",
        "total_records": int(len(df)),
    }

    communes_geojson_data = build_communes_geojson(engine, map_precip, deficit_crise)

    vegetation_data = load_vegetation_payload(engine)

    return {
        "overview": overview,
        "communes": communes,
        "annualData": annual_data,
        "seasonData": saisons,
        "monthlyClimatology": monthly_climatology,
        "anomalies": anomalies,
        "precipRecords": precip_records,
        "communesGeojson": communes_geojson_data,
        "vegetationData": vegetation_data,
    }


def export_react_data(engine: Engine) -> None:
    payload = build_react_payload(engine)

    write_pretty_json(payload["overview"], "overview.json")
    write_pretty_json(payload["communes"], "communes.json")
    write_pretty_json(payload["annualData"], "annual-precipitations.json")
    write_pretty_json(payload["seasonData"], "saisons.json")
    write_pretty_json(payload["monthlyClimatology"], "monthly-climatology.json")
    write_pretty_json(payload["anomalies"], "anomalies.json")
    write_pretty_json(payload["precipRecords"], "precip-records.json")
    write_pretty_json(payload["vegetationData"], "vegetation-data.json")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_pretty_json(payload["communesGeojson"], "communes.geojson")

    print(f"Export React OK: {OUTPUT_DIR}")


def main() -> None:
    engine = make_engine()
    skip_import = env("DYNATSIMO_SKIP_IMPORT", "false").lower() == "true"

    if skip_import:
        print("Import CHIRPS ignore: DYNATSIMO_SKIP_IMPORT=true")
    else:
        import_chirps_to_postgres(engine)

    export_react_data(engine)


if __name__ == "__main__":
    main()
