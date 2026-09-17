# This file includes common configuration elements used by the script.

import os
import re
from dotenv import dotenv_values, find_dotenv

config = dotenv_values(find_dotenv())
DATA_DIR = config["DATA_DIR"]
OUTPUT_DIR = config["OUTPUT_DIR"]
CACHE_DIR = config["CACHE_DIR"]

# Ensure output and cache dirs exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR,  exist_ok=True)

# Define the REST API URLs
rest_api_url_view = "https://services.arcgis.com/iQ1dY19aHwbSDYIF/ArcGIS/rest/services/World_Bank_Global_Administrative_Divisions_VIEW/FeatureServer"
rest_api_url_new = "https://services.arcgis.com/iQ1dY19aHwbSDYIF/ArcGIS/rest/services/World_Bank_Global_Administrative_Divisions/FeatureServer"

# Active service selection - Set to True to use new service, False for VIEW service
USE_NEW_SERVICE = True

# Set active URL based on service selection
rest_api_url = rest_api_url_new if USE_NEW_SERVICE else rest_api_url_view

worldpop_url = "https://data.worldpop.org/GIS/Population/"
stac_search_url = "https://geoservice.dlr.de/eoc/ogc/stac/v1/search"


# Mapping of administrative levels to field names for WB GAD dataset
# Field mapping adjusted based on active service
if USE_NEW_SERVICE:
    adm_field_mapping = {
        0: {'code': 'ISO_A3', 'name': 'NAM_0'},      # New service uses ISO_A3 instead of HASC_0
        1: {'code': 'ADM1CD_c', 'name': 'NAM_1'},    # New service uses ADM1CD_c instead of HASC_1
        2: {'code': 'ADM2CD_c', 'name': 'NAM_2'},    # New service uses ADM2CD_c instead of HASC_2
    }
else:
    adm_field_mapping = {
        0: {'code': 'HASC_0', 'name': 'NAM_0'},
        1: {'code': 'HASC_1', 'name': 'NAM_1'},
        2: {'code': 'HASC_2', 'name': 'NAM_2'},
        # Add mappings for additional levels as needed
    }

wb_to_region = {
    'AFR': 'AFRICA',        # Sub-Saharan Africa
    'MENA': 'AFRICA',       # Middle East and North Africa
    'EAP': 'ASIA',          # East Asia and Pacific
    'SAR': 'ASIA',          # South Asia
    'ECA': 'ASIA',          # East Europe and Central Asia - see eu_country_codes below:
                            # EU member states within ECA (e.g. Poland, Romania) are
                            # pulled out to their own EUROPE bucket by resolve_flood_region;
                            # only non-EU ECA countries (Turkey, Western Balkans, Central
                            # Asia, etc.) actually fall through to ASIA here.
    'LCR': 'LAC',           # Latin America and Caribbean
    'Other': 'GLOBAL',      # North America, Japan, Korea, Australia and New Zealand -
                            # EU member states in 'Other' (e.g. Germany, France) are also
                            # pulled out to EUROPE by resolve_flood_region.
}

# EU-27 member states (ISO3). Used to give EU countries a dedicated JRC EUROPE flood
# damage curve instead of whatever their WB_REGION happens to bucket them into - EU
# countries are split today between ECA (mapped to ASIA) and 'Other' (mapped to
# GLOBAL), neither of which reflects JRC's own Europe-specific curve.
eu_country_codes = {
    'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
    'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
    'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE',
}


def resolve_flood_region(country_iso3: str, wb_region: str) -> str:
    """Resolve the flood damage-function region bucket for a country.

    EU membership (by ISO3) takes priority over the World Bank region code,
    since WB_REGION alone can't distinguish EU from non-EU countries within
    ECA or 'Other'. Falls back to the wb_to_region mapping otherwise.
    """
    if country_iso3 in eu_country_codes:
        return 'EUROPE'
    return wb_to_region.get(wb_region, 'GLOBAL')

# Tropical cyclone regions list with constituent countries
tc_region_list = {
    'NA1': [  # Caribbean and Mexico
        'ABW', 'AIA', 'ATG', 'BHS', 'BLZ', 'BRB', 'CUB', 'CYM', 'DMA', 'DOM',
        'GRD', 'GTM', 'HND', 'HTI', 'JAM', 'KNA', 'LCA', 'MEX', 'MSR', 'NIC',
        'PRI', 'SLV', 'TCA', 'TTO', 'VCT', 'VGB', 'VIR'
    ],
    'NA2': [  # USA and Canada
        'CAN', 'USA'
    ],
    'NI': [   # North Indian
        'BGD', 'IND', 'LKA', 'MDV', 'MMR', 'OMN', 'PAK', 'YEM'
    ],
    'OC': [   # Oceania
        'AUS', 'COK', 'FJI', 'FSM', 'KIR', 'MHL', 'NCL', 'NFK', 'NIU', 'NRU',
        'NZL', 'PCN', 'PLW', 'PNG', 'SLB', 'TKL', 'TON', 'TUV', 'VUT', 'WLF',
        'WSM'
    ],
    'SI': [   # South Indian
        'COM', 'MDG', 'MOZ', 'MUS', 'MYT', 'REU', 'SYC', 'TZA'
    ],
    'WP1': [  # South East Asia
        'BRN', 'IDN', 'KHM', 'LAO', 'MYS', 'SGP', 'THA', 'TLS', 'VNM'
    ],
    'WP2': [  # Philippines and Taiwan
        'PHL', 'TWN'
    ],
    'WP3': [  # China Mainland
        'CHN', 'HKG', 'MAC'
    ],
    'WP4': [  # North West Pacific
        'JPN', 'KOR', 'PRK'
    ]
}

# Create the reverse mapping for TC regions (country to region)
tc_region_mapping = {
    country: region
    for region, countries in tc_region_list.items()
    for country in countries
}


def list_boundary_layers(file_path):
    """Return the list of layer names in a vector file (e.g. a multi-layer
    GeoPackage), or [] if the format doesn't support multiple layers or the
    file can't be introspected (e.g. a plain shapefile, or a path that
    doesn't exist yet while the user is still typing it in the GUI).

    Shared by runAnalysis.py, custom_hazard_analysis.py, and the GUI custom-
    boundaries file pickers - a GPKG with multiple layers previously had
    gpd.read_file() silently pick whichever layer GDAL considers "default",
    ignoring the ADM level the user actually selected (confirmed against a
    real Fiji file: a 1417-feature ADM4 layer got loaded instead of the
    intended 15-feature ADM2 layer in the same file).
    """
    import geopandas as gpd
    try:
        return gpd.list_layers(file_path)['name'].tolist()
    except Exception:
        return []


def match_adm_level_layer(layers, adm_level):
    """Return the single layer name matching "ADM{adm_level}" as a whole
    token (e.g. 'ADM2', 'ADM02'), or None if there isn't exactly one such
    match. Used as a convenience default when picking among a multi-layer
    file's layers - never picks silently when the match is ambiguous (e.g.
    both 'FJI_ADM4' and 'FJI_ADM4_fix' match 'ADM4')."""
    if adm_level is None:
        return None
    matches = [lyr for lyr in layers if re.search(rf'adm0*{adm_level}(?!\d)', lyr, re.IGNORECASE)]
    return matches[0] if len(matches) == 1 else None


def safe_reproject_to_4326(gdf):
    """Reproject a GeoDataFrame to EPSG:4326 for output, unless doing so
    would produce degenerate antimeridian-wrapped geometries.

    A polygon that is contiguous in a working CRS centered on the
    antimeridian (e.g. the local Mercator CRS used for antimeridian-crossing
    countries - see input_utils.normalize_antimeridian_raster) becomes
    invalid-by-shape once converted back to plain lon/lat: each vertex's
    longitude gets independently wrapped into [-180, 180], scattering a ring
    that was contiguous in the source CRS across both extremes. shapely does
    not flag the result as topologically invalid (it's still a simple,
    non-self-intersecting ring in raw coordinate terms), but its bounding box
    ends up spanning close to the full 360 degrees of longitude - no real
    administrative unit is actually that wide, so that's the signal used
    here to detect it (confirmed against a real Fiji province: reprojecting
    Lau this way produced a "polygon" 359.8 degrees wide).

    When detected, the geometries are left in their original working CRS
    instead - valid, correctly shaped, and rendered/analyzed correctly by any
    GIS tool that reads the file's own CRS (which every mainstream one does),
    just not literally EPSG:4326. Properly splitting these polygons at the
    antimeridian before reprojecting is possible but out of scope here.
    """
    if gdf.crs is None:
        return gdf.set_crs(epsg=4326, allow_override=True)
    if gdf.crs.to_epsg() == 4326:
        return gdf
    original_crs = gdf.crs
    reprojected = gdf.to_crs(epsg=4326)
    minx, miny, maxx, maxy = reprojected.total_bounds
    if (maxx - minx) > 180:
        print(f"WARNING: reprojecting to EPSG:4326 would wrap geometries across "
              f"the antimeridian (bounding box {maxx - minx:.1f} degrees wide - "
              f"no real administrative unit is that wide). Keeping the output in "
              f"its working CRS ({original_crs}) instead, which is valid and "
              f"renders correctly in GIS software, just not literally EPSG:4326.")
        return gdf
    return reprojected