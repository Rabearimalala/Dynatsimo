required_packages <- c("DBI", "RPostgres", "dplyr", "sf", "jsonlite")
missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]

if (length(missing_packages) > 0) {
  stop(
    "Packages R manquants : ",
    paste(missing_packages, collapse = ", "),
    "\nInstalle-les avec install.packages(...) puis relance ce script.",
    call. = FALSE
  )
}

library(DBI)
library(RPostgres)
library(dplyr)
library(sf)
library(jsonlite)

output_dir <- file.path("public", "data")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

month_labels <- c(
  "1" = "Jan",
  "2" = "Fev",
  "3" = "Mar",
  "4" = "Avr",
  "5" = "Mai",
  "6" = "Jun",
  "7" = "Jul",
  "8" = "Aou",
  "9" = "Sep",
  "10" = "Oct",
  "11" = "Nov",
  "12" = "Dec"
)

calc_saison <- function(df_commune_saison, seuil_chute_mm = 50) {
  if (is.null(df_commune_saison) || nrow(df_commune_saison) == 0) {
    return(tibble(
      debut_saison = NA_integer_,
      fin_saison = NA_integer_,
      duree_saison = NA_integer_,
      mois_plus_pluvieux = NA_integer_
    ))
  }

  df_commune_saison <- df_commune_saison %>%
    arrange(if_else(Month >= 10L, Month, Month + 12L))

  p <- df_commune_saison$Precip
  months <- df_commune_saison$Month

  if (all(is.na(p)) || length(p) < 6) {
    return(tibble(
      debut_saison = NA_integer_,
      fin_saison = NA_integer_,
      duree_saison = NA_integer_,
      mois_plus_pluvieux = NA_integer_
    ))
  }

  p_clean <- p
  p_clean[is.na(p_clean)] <- 0

  debut <- NA_integer_
  mois_possibles_debut <- which(months %in% 10:12)

  if (length(mois_possibles_debut) > 0) {
    for (i in mois_possibles_debut) {
      if (
        p_clean[i] >= 50 &&
          i < length(p_clean) &&
          p_clean[i] < p_clean[i + 1]
      ) {
        debut <- months[i]
        break
      }
    }
  }

  if (is.na(debut)) {
    debut <- 10
  }

  fin <- NA_integer_
  mois_possibles_fin <- which(months %in% 1:6)

  if (length(mois_possibles_fin) > 0) {
    for (i in mois_possibles_fin) {
      if (
        i > 1 &&
          i < length(p_clean) &&
          (p_clean[i + 1] - p_clean[i] <= -seuil_chute_mm)
      ) {
        fin <- months[i]
        break
      }
    }
  }

  if (is.na(fin)) {
    fin <- 3
  }

  duree <- (12 - debut + 1) + fin
  mois_saison <- c(debut:12, 1:fin)
  mois_existants <- months[months %in% mois_saison]

  mois_max <- if (length(mois_existants) > 0) {
    months[which.max(p_clean[months %in% mois_existants])]
  } else {
    NA_integer_
  }

  tibble(
    debut_saison = debut,
    fin_saison = fin,
    duree_saison = duree,
    mois_plus_pluvieux = mois_max
  )
}

write_pretty_json <- function(data, filename) {
  write_json(
    data,
    file.path(output_dir, filename),
    auto_unbox = TRUE,
    pretty = TRUE,
    na = "null"
  )
}

con <- dbConnect(
  RPostgres::Postgres(),
  dbname = Sys.getenv("DYNATSIMO_DBNAME", "precipitation"),
  host = Sys.getenv("DYNATSIMO_DBHOST", "localhost"),
  port = as.integer(Sys.getenv("DYNATSIMO_DBPORT", "5432")),
  user = Sys.getenv("DYNATSIMO_DBUSER", "postgres"),
  password = Sys.getenv("DYNATSIMO_DBPASSWORD", "admin")
)

on.exit(dbDisconnect(con), add = TRUE)

df_raw <- dbGetQuery(
  con,
  '
  SELECT
    c."ADM3_PCODE" AS "code_Commune",
    c."ADM3_EN" AS "Commune",
    p."Year",
    p."Month",
    p."Precip"
  FROM public.precipitation p, public.communes c
  WHERE p."Commune_Id" = c."ADM3_PCODE"
  '
)

DF <- df_raw %>%
  mutate(
    Month = as.integer(Month),
    Year = as.integer(Year),
    Precip = as.numeric(Precip),
    code_Commune = trimws(toupper(code_Commune)),
    Saison = if_else(Month >= 11, Year, Year - 1L)
  ) %>%
  filter(
    Year >= 1981,
    Month >= 1,
    Month <= 12
  )

communes <- DF %>%
  distinct(code_Commune, Commune) %>%
  arrange(Commune) %>%
  transmute(
    code = code_Commune,
    nom = Commune,
    region = NA_character_
  )

annual_data <- DF %>%
  group_by(Year) %>%
  summarise(precip = round(mean(Precip, na.rm = TRUE), 2), .groups = "drop") %>%
  transmute(year = Year, precip)

saison_df <- DF %>%
  filter(Month %in% c(10:12, 1:9)) %>%
  group_by(code_Commune, Commune, Saison) %>%
  group_modify(~ calc_saison(.x)) %>%
  ungroup()

precip_saison <- DF %>%
  group_by(code_Commune, Saison) %>%
  summarise(precip = round(sum(Precip, na.rm = TRUE), 0), .groups = "drop")

saisons <- saison_df %>%
  left_join(precip_saison, by = c("code_Commune", "Saison")) %>%
  arrange(code_Commune, Saison) %>%
  transmute(
    code_commune = code_Commune,
    commune = Commune,
    saison = Saison,
    debut = unname(month_labels[as.character(debut_saison)]),
    fin = unname(month_labels[as.character(fin_saison)]),
    duree = duree_saison,
    mois_plus_pluvieux = unname(month_labels[as.character(mois_plus_pluvieux)]),
    precip
  )

monthly_climatology <- DF %>%
  group_by(Month) %>%
  summarise(precip = round(mean(Precip, na.rm = TRUE), 2), .groups = "drop") %>%
  arrange(Month) %>%
  transmute(month = unname(month_labels[as.character(Month)]), precip)

annual_total <- DF %>%
  group_by(Year) %>%
  summarise(precip_total = sum(Precip, na.rm = TRUE), .groups = "drop")

climatology_ref <- annual_total %>%
  filter(Year >= 1981, Year <= 2010) %>%
  summarise(value = mean(precip_total, na.rm = TRUE)) %>%
  pull(value)

anomalies <- annual_total %>%
  transmute(
    year = Year,
    anomaly = round(precip_total - climatology_ref, 2)
  )

deficit_crise <- DF %>%
  group_by(code_Commune, Year) %>%
  summarise(p = sum(Precip, na.rm = TRUE), .groups = "drop") %>%
  group_by(code_Commune) %>%
  mutate(
    climatologie = mean(p[Year >= 1981 & Year <= 2010], na.rm = TRUE)
  ) %>%
  filter(Year %in% 2020:2022) %>%
  group_by(code_Commune) %>%
  summarise(
    precip_crise = mean(p, na.rm = TRUE),
    climatologie = mean(climatologie, na.rm = TRUE),
    deficit = round((precip_crise - climatologie) / climatologie * 100, 2),
    .groups = "drop"
  ) %>%
  mutate(deficit = pmax(pmin(deficit, 100), -100))

map_precip <- DF %>%
  filter(Year >= max(2020, max(DF$Year, na.rm = TRUE) - 5)) %>%
  group_by(code_Commune, Year) %>%
  summarise(p = sum(Precip, na.rm = TRUE), .groups = "drop") %>%
  group_by(code_Commune) %>%
  summarise(precip = round(mean(p, na.rm = TRUE), 2), .groups = "drop")

shp_communes <- st_read(
  con,
  query = '
  SELECT
    geom,
    "ADM3_PCODE" AS "code_Commune",
    "ADM3_EN" AS "Commune",
    "ADM1_EN" AS "Region"
  FROM public.communes
  ',
  quiet = TRUE
) %>%
  mutate(code_Commune = trimws(toupper(code_Commune)))

communes_geojson <- shp_communes %>%
  left_join(map_precip, by = "code_Commune") %>%
  left_join(deficit_crise, by = "code_Commune") %>%
  transmute(
    code = code_Commune,
    nom = Commune,
    region = Region,
    precip,
    deficit,
    geometry = geom
  )

write_pretty_json(
  list(
    nb_communes = n_distinct(DF$code_Commune),
    nb_years = paste0(min(DF$Year, na.rm = TRUE), "-", max(DF$Year, na.rm = TRUE)),
    total_records = nrow(DF)
  ),
  "overview.json"
)

write_pretty_json(communes, "communes.json")
write_pretty_json(annual_data, "annual-precipitations.json")
write_pretty_json(saisons, "saisons.json")
write_pretty_json(monthly_climatology, "monthly-climatology.json")
write_pretty_json(anomalies, "anomalies.json")

st_write(
  communes_geojson,
  file.path(output_dir, "communes.geojson"),
  driver = "GeoJSON",
  delete_dsn = TRUE,
  quiet = TRUE
)

message("Export termine dans ", normalizePath(output_dir, mustWork = FALSE))
