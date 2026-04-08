"""Configuración global del proyecto."""

# Marca McDonald's en Rappi MX
MCDONALDS_BRAND_ID = 706

# 8 zonas representativas de CDMX (mix de poder adquisitivo)
ZONES = [
    {"name": "Polanco",          "lat": 19.43161, "lng": -99.18605, "tier": "premium"},
    {"name": "Santa Fe",         "lat": 19.35932, "lng": -99.26075, "tier": "premium"},
    {"name": "Roma Norte",       "lat": 19.41960, "lng": -99.16070, "tier": "mid-high"},
    {"name": "Del Valle",        "lat": 19.38500, "lng": -99.16500, "tier": "mid-high"},
    {"name": "Coyoacán",         "lat": 19.34980, "lng": -99.16200, "tier": "mid"},
    {"name": "Centro Histórico", "lat": 19.43260, "lng": -99.13320, "tier": "mid"},
    {"name": "Iztapalapa",       "lat": 19.35780, "lng": -99.08920, "tier": "low"},
    {"name": "Ecatepec",         "lat": 19.60110, "lng": -99.05060, "tier": "low"},
]

# Productos de referencia (los nombres exactos los descubrimos al parsear)
REFERENCE_PRODUCTS = {
    "big_mac": ["big mac"],
    "mctrio_bigmac": ["mctrío big mac", "mctrio big mac", "trío big mac"],
    "mcnuggets_10": ["mcnuggets 10", "10 mcnuggets", "nuggets 10"],
}

# Paths de stores en Uber Eats por zona (capturados manualmente)
# None = sin cobertura de McDonald's en la zona
UBEREATS_STORE_PATHS = {
    "Polanco":          "/mx/store/mcdonalds-plaza-galerias/oIEI4FlNTJ6ioOOpC-lxsQ",
    "Santa Fe":         "/mx/store/mcdonalds-santa-fe-zentrika/V77AC3JyS8-aloYvj4ag9w",
    "Roma Norte":       "/mx/store/mcdonalds-sears-insurgentes/mREIcg3yRhGnS6IUIL2GuQ",
    "Del Valle":        "/mx/store/mcdonalds-torre-manacars/2gMMR9ZRTs6NyVHd3kgJig",
    "Coyoacán":         "/mx/store/mcdonalds-oasis-coyoacan/7ElsVR4vT7S_6cueJohXUg",
    "Centro Histórico": "/mx/store/mcdonalds-palma/pKIEbILTS0Cb056hHIHz7g",
    "Iztapalapa":       "/mx/store/mcdonalds-ermita-san-miguel/wLzO28URTS-8FPipFSQbCA",
    "Ecatepec":         "/mx/store/mcdonalds-plaza-san-juan/ZymASVTHSImWnf_Znz5QRA",
}

DIDI_STORE_PATHS = {
    "Polanco":          "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-plaza-galerias/5764607793710235704/",
    "Santa Fe":         "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-zentrika/5764607765293826113/",
    "Roma Norte":       "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-zona-rosa/5764607731621953647/",
    "Del Valle":        "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-parque-hundido/5764607600071802936/",
    "Coyoacán":         "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-division-del-norte/5764607594359161056/",
    "Centro Histórico": "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-centro-palma/5764607535911534653/",
    "Iztapalapa":       "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-ermita-san-miguel/5764607562264346850/",
    "Ecatepec":         "/mx/food/ciudad-de-mexico-cdmx/mcdonalds-plaza-san-juan/5764607635190710541/",
}