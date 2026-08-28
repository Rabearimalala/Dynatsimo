"""
Import NDVI GeoTIFF rasters into PostgreSQL and refresh the vegetation payload.

This script does not use shapefiles:
- commune geometry comes from PostgreSQL
- NDVI comes from GeoTIFF files exported by GEE
- the front consumes the JSON payload from PostgreSQL through the API
"""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "public" / "data"
MONTH_ORDER = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
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


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean_for_json(data), ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_communes_table(engine: Engine) -> str:
    configured_table = env("DYNATSIMO_COMMUNES_TABLE", "").strip()
    if configured_table:
        return safe_table_name(configured_table)

    for table_name in ("public.communes", "public.comunes_androy_anosy"):
        if table_exists(engine, table_name):
            return table_name

    raise RuntimeError("Aucune table de communes trouvée.")


def read_communes(engine: Engine) -> pd.DataFrame:
    import geopandas as gpd

    communes_table = resolve_communes_table(engine)
    geom_column = env("DYNATSIMO_GEOM_COLUMN", "geom")
    communes = gpd.read_postgis(f"SELECT * FROM {communes_table}", engine, geom_col=geom_column)

    if communes.geometry.name != "geom":
        communes = communes.rename_geometry("geom")

    if "ADM3_PCODE" not in communes.columns:
        raise RuntimeError(f"La table {communes_table} doit contenir ADM3_PCODE.")

    communes["ADM3_PCODE"] = communes["ADM3_PCODE"].astype(str).str.strip().str.upper()
    if "ADM3_EN" not in communes.columns:
        communes["ADM3_EN"] = communes["ADM3_PCODE"]
    if "ADM1_EN" not in communes.columns:
        communes["ADM1_EN"] = None

    return communes


def parse_ndvi_filename(name: str) -> tuple[str, int, int] | None:
    sensor = "unknown"
    lowered = name.lower()
    for candidate in ("sentinel", "landsat", "modis"):
        if candidate in lowered:
            sensor = candidate
            break

    patterns = [
        r"((?:19|20)\d{2})[._-](0?[1-9]|1[0-2])",
        r"((?:19|20)\d{2})(0[1-9]|1[0-2])",
    ]
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            return sensor, int(match.group(1)), int(match.group(2))

    return None


def read_template_payload() -> dict:
    template = load_json(OUTPUT_DIR / "vegetation-data.json")
    if isinstance(template, dict):
        return template

    return {
        "ecoregions": {},
        "sensorComparison": {"meta": {}, "specs": [], "simulation": {}},
        "timeSeries": {},
    }


def load_vegetation_payload(engine: Engine) -> dict | None:
    if not table_exists(engine, "public.vegetation_payload"):
        return None

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT payload
                FROM public.vegetation_payload
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """
            )
        ).fetchone()

    if row is None:
        return None

    payload = row[0]
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return None

    return None


def find_ndvi_directory() -> Path | None:
    configured = env("DYNATSIMO_NDVI_DIR", "").strip()
    candidates = []

    if configured:
        candidates.append(Path(configured))
    else:
        candidates.extend(
            [
                ROOT_DIR / "ndvi_geotiff",
                ROOT_DIR.parent / "script-ndvi-GEE",
                ROOT_DIR.parent / "script-ndvi-GEE" / "exports",
                ROOT_DIR.parent / "script-ndvi-GEE" / "output",
            ]
        )

    for candidate in candidates:
        if candidate.exists():
            tif_count = len(list(candidate.rglob("*.tif"))) + len(list(candidate.rglob("*.tiff")))
            if tif_count > 0:
                return candidate

    return None


def import_ndvi_geotiffs(engine: Engine) -> pd.DataFrame:
    from rasterstats import zonal_stats

    ndvi_dir = find_ndvi_directory()
    if ndvi_dir is None:
        print(
            "Aucun dossier GeoTIFF NDVI trouvé. "
            "Place les .tif exportés depuis GEE dans un dossier et renseigne DYNATSIMO_NDVI_DIR, "
            "ou laisse le script réutiliser le payload existant."
        )
        return pd.DataFrame()

    tif_files = sorted(list(ndvi_dir.rglob("*.tif")) + list(ndvi_dir.rglob("*.tiff")))
    if not tif_files:
        print(
            f"Aucun GeoTIFF NDVI trouvé dans {ndvi_dir}. "
            "Le payload existant sera conservé."
        )
        return pd.DataFrame()

    communes = read_communes(engine)
    nodata = float(env("DYNATSIMO_NDVI_NODATA", "-9999"))
    all_touched = env("DYNATSIMO_ALL_TOUCHED", "false").lower() == "true"

    rows = []
    for raster_path in tif_files:
        parsed = parse_ndvi_filename(raster_path.name)
        if parsed is None:
            continue

        sensor, year, month = parsed
        stats = zonal_stats(
            communes,
            str(raster_path),
            stats=["mean"],
            nodata=nodata,
            all_touched=all_touched,
        )

        for commune, stat in zip(communes.itertuples(), stats):
            ndvi = stat.get("mean")
            rows.append(
                {
                    "commune_code": commune.ADM3_PCODE,
                    "year": year,
                    "month": month,
                    "sensor": sensor,
                    "ndvi": float(ndvi) if ndvi is not None else np.nan,
                    "source_file": raster_path.name,
                }
            )

    observations = pd.DataFrame(rows)
    if observations.empty:
        raise RuntimeError("Aucune observation NDVI exploitable n'a été calculée.")

    observations = observations.sort_values(["commune_code", "year", "month", "sensor"])
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS public.ndvi_observations"))
        conn.execute(
            text(
                """
                CREATE TABLE public.ndvi_observations (
                  id SERIAL PRIMARY KEY,
                  commune_code TEXT NOT NULL,
                  year INTEGER NOT NULL,
                  month INTEGER NOT NULL,
                  sensor TEXT NOT NULL,
                  ndvi DOUBLE PRECISION,
                  source_file TEXT,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        )

    observations.to_sql(
        "ndvi_observations",
        engine,
        schema="public",
        if_exists="append",
        index=False,
        chunksize=5000,
    )

    print(f"Import NDVI OK: {len(observations)} lignes dans public.ndvi_observations")
    return observations


def build_time_series(observations: pd.DataFrame, communes: pd.DataFrame, template: dict) -> dict:
    commune_meta = communes[["ADM3_PCODE", "ADM3_EN", "ADM1_EN"]].copy()
    commune_meta = commune_meta.rename(
        columns={"ADM3_PCODE": "code", "ADM3_EN": "nom", "ADM1_EN": "region"}
    )

    communes_template = load_json(OUTPUT_DIR / "communes.json")
    if isinstance(communes_template, list):
        communes_template_df = pd.DataFrame(communes_template)
        if "code" in communes_template_df.columns:
            commune_meta = commune_meta.merge(
                communes_template_df[["code", "district", "ecoregion"]],
                on="code",
                how="left",
            )

    if "ecoregion" not in commune_meta.columns:
        commune_meta["ecoregion"] = "spiny"

    commune_lookup = commune_meta.set_index("code").to_dict("index") if not commune_meta.empty else {}

    baseline_map = template.get("ecoregions", {})
    default_baseline = baseline_map.get("spiny", {}).get("baselineNdvi", [0.3] * 12)

    observations = observations.copy()
    observations["season_start"] = np.where(observations["month"] >= 10, observations["year"], observations["year"] - 1)
    observations["season"] = observations["season_start"].astype(str) + "-" + (observations["season_start"] + 1).astype(str)
    observations["month_order"] = np.where(observations["month"] >= 10, observations["month"], observations["month"] + 12)

    monthly = (
        observations.groupby(["commune_code", "season", "month"], as_index=False)["ndvi"]
        .mean()
        .sort_values(["commune_code", "season", "month"])
    )

    time_series = {}
    for code, commune_months in monthly.groupby("commune_code"):
        series = []
        for season, season_months in commune_months.groupby("season"):
            season_months = season_months.sort_values("month", key=lambda series: np.where(series >= 10, series, series + 12))
            month_values = {
                int(row.month): float(row.ndvi) if pd.notna(row.ndvi) else 0.0
                for row in season_months.itertuples()
            }

            commune_row = commune_lookup.get(code, {})
            ecoregion = commune_row.get("ecoregion") if commune_row else "spiny"
            if not ecoregion or pd.isna(ecoregion):
                ecoregion = "spiny"
            baseline = baseline_map.get(ecoregion, {}).get("baselineNdvi", default_baseline)

            ndvi_values = [round(month_values.get(month, 0.0), 3) for month in MONTH_ORDER]
            cumulative = []
            anomalies = []
            baseline_list = []
            running_total = 0.0
            for idx, month in enumerate(MONTH_ORDER):
                ndvi_value = ndvi_values[idx]
                running_total = round(running_total + ndvi_value, 3)
                cumulative.append(running_total)
                base_val = float(baseline[idx] if idx < len(baseline) else baseline[-1])
                anomalies.append(round(ndvi_value - base_val, 3))
                baseline_list.append(base_val)

            series.append(
                {
                    "season": season,
                    "startYear": int(season.split("-")[0]),
                    "ndvi": ndvi_values,
                    "cumulative": cumulative,
                    "anomalies": anomalies,
                    "baseline": baseline_list,
                    "integratedProductivity": running_total,
                }
            )

        time_series[code] = series

    template["timeSeries"] = time_series
    return template


def save_payload_to_db(engine: Engine, payload: dict) -> None:
    payload_json = json.dumps(clean_for_json(payload), ensure_ascii=False)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS public.vegetation_payload (
                  id SERIAL PRIMARY KEY,
                  payload JSONB NOT NULL,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        )
        conn.execute(text("DELETE FROM public.vegetation_payload"))
        conn.execute(
            text("INSERT INTO public.vegetation_payload (payload) VALUES (CAST(:payload AS jsonb))"),
            {"payload": payload_json},
        )


def main() -> None:
    engine = make_engine()

    observations = import_ndvi_geotiffs(engine)
    template = read_template_payload()

    if observations.empty:
        payload = load_vegetation_payload(engine) or template
        save_payload_to_db(engine, payload)
        write_json(OUTPUT_DIR / "vegetation-data.json", payload)
        print("Aucun GeoTIFF NDVI a importer, payload existant re-enregistre dans la base.")
        return

    communes = read_communes(engine)
    payload = build_time_series(observations, communes, template)

    save_payload_to_db(engine, payload)
    write_json(OUTPUT_DIR / "vegetation-data.json", payload)

    print("Payload NDVI enregistré dans public.vegetation_payload")


if __name__ == "__main__":
    main()
