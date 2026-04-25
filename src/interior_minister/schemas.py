"""Column definitions and validation schemas for each dataset."""

from __future__ import annotations

DEPARTMENTS = {
    1: "Montevideo",
    2: "Artigas",
    3: "Canelones",
    4: "Cerro Largo",
    5: "Colonia",
    6: "Durazno",
    7: "Flores",
    8: "Florida",
    9: "Lavalleja",
    10: "Maldonado",
    11: "Paysandu",
    12: "Rio Negro",
    13: "Rivera",
    14: "Rocha",
    15: "Salto",
    16: "San Jose",
    17: "Soriano",
    18: "Tacuarembo",
    19: "Treinta y Tres",
}

VALID_SEX = {"M", "F", "MASCULINO", "FEMENINO", "Masculino", "Femenino"}


DATASET_SCHEMAS: dict[str, dict] = {
    "delitos_denunciados": {
        "description": "Reported crimes including homicides, robberies, injuries, DV, theft, cattle rustling",
        "time_range": (2013, 2025),
        "key_columns": [
            "ano", "mes", "trimestre", "departamento", "seccional",
            "titulo", "subtitulo",
        ],
        "date_columns": ["fecha"],
        "categorical": {
            "departamento": set(DEPARTMENTS.values()),
        },
    },
    "violencia_domestica": {
        "description": "Domestic violence reports, victims, and electronic ankle bracelet program",
        "time_range": (2020, 2024),
        "key_columns": [
            "ano", "departamento", "titulo", "jurisdiccion",
            "sexo_victima", "sexo_agresor",
        ],
        "date_columns": ["fecha_denuncia"],
        "categorical": {
            "departamento": set(DEPARTMENTS.values()),
        },
    },
    "delitos_sexuales": {
        "description": "Major sexual crimes reported",
        "time_range": (2018, 2024),
        "key_columns": [
            "ano", "departamento", "jurisdiccion", "titulo",
            "sexo_victima",
        ],
        "date_columns": ["fecha_denuncia"],
        "categorical": {
            "departamento": set(DEPARTMENTS.values()),
        },
    },
    "homicidios_mujeres": {
        "description": "Homicides against women (domestic and gender-based violence)",
        "time_range": (2017, 2024),
        "key_columns": [
            "ano", "departamento", "vinculo",
        ],
        "date_columns": ["fecha"],
        "categorical": {
            "departamento": set(DEPARTMENTS.values()),
        },
    },
    "medidas_alternativas": {
        "description": "Alternative measures to incarceration",
        "time_range": (2018, 2025),
        "key_columns": [
            "ano", "mes", "departamento", "tipo_medida", "genero",
        ],
        "date_columns": [],
        "categorical": {
            "departamento": set(DEPARTMENTS.values()),
        },
    },
    "sistema_carcelario": {
        "description": "Prison system population and demographics",
        "time_range": (2018, 2025),
        "key_columns": [
            "ano", "mes", "establecimiento", "sexo", "grupo_edad",
        ],
        "date_columns": [],
        "categorical": {},
    },
}


def normalize_department_series(values: list[str]) -> list[str]:
    """Normalize a list of department values to canonical form. For use with Polars map."""
    return [normalize_department(v) if v else v for v in values]


def validate_year_range(year: int, dataset: str) -> bool:
    """Check if a year falls within the valid range for a dataset."""
    schema = DATASET_SCHEMAS.get(dataset)
    if schema is None:
        return True
    lo, hi = schema["time_range"]
    return lo <= year <= hi


def validate_department(name: str) -> bool:
    """Check if a department name is valid."""
    return name.upper() in {d.upper() for d in DEPARTMENTS.values()}


# Mapping of known typos/variants to canonical uppercase department names
_DEPARTMENT_FIXES: dict[str, str] = {
    "MALDONDADO": "MALDONADO",
    "TACUEREMBO": "TACUAREMBO",
    "PAYSAND\xda": "PAYSANDU",        # Paysandú
    "SAN JOS\xc9": "SAN JOSE",        # San José
    "TACUAREMB\xd3": "TACUAREMBO",    # Tacuarembó
    "R\xcdO NEGRO": "RIO NEGRO",      # Río Negro
}

# Build lookup: uppercase canonical name for each department
_CANONICAL_DEPARTMENTS: dict[str, str] = {
    d.upper(): d.upper() for d in DEPARTMENTS.values()
}
_CANONICAL_DEPARTMENTS.update(_DEPARTMENT_FIXES)


def normalize_department(name: str) -> str:
    """Normalize a department name to canonical uppercase form.

    Handles typos (MALDONDADO), accented chars (Paysandú), and mixed case.
    """
    import unicodedata

    upper = name.strip().upper()
    # Try direct lookup first (handles typos like MALDONDADO)
    if upper in _CANONICAL_DEPARTMENTS:
        return _CANONICAL_DEPARTMENTS[upper]
    # Strip accents and retry
    nfkd = unicodedata.normalize("NFKD", upper)
    stripped = "".join(c for c in nfkd if not unicodedata.combining(c))
    if stripped in _CANONICAL_DEPARTMENTS:
        return _CANONICAL_DEPARTMENTS[stripped]
    # Return accent-stripped uppercase as best effort
    return stripped
