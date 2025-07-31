# Importing the required packages
import numpy as np
from common import wb_to_region, tc_region_mapping

# Defining the damage functions

# Floods (river and coastal) over Population mortality
def FL_mortality_factor(x: np.array, wb_region: str = None):
    """A polynomial fit to average population mortality due to nearby flooding.
    Values are capped between 0 and 1

    References
    ----------
    Jonkman SN, 2008 - Loss of life due to floods (https://doi.org/10.1111/j.1753-318X.2008.00006.x)
    """
    x = x/100  # convert cm to m
    return np.maximum(0.0, np.minimum(1.0, 0.985 / (1 + np.exp(6.32 - 1.412 * x))))  # Floods - Global

# Floods (river and coastal) over Built-Up areas

def FL_damage_factor_builtup(x: np.array, wb_region: str):
    """A polynomial fit to average damage across builtup land cover relative to water depth in meters.

    The sectors are commercial, industry, transport, infrastructure and residential.
    Values are capped between 0 and 1
    
    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    (https://publications.jrc.ec.europa.eu/repository/handle/JRC105688)
    """
    x = (x/100).astype(np.float32)    # convert cm to m
    function_mapping = {
        'AFRICA': lambda x: np.maximum(0.0, np.minimum(1.0, 1.246282 + (0.004404681 - 1.246282)/(1 + (x/1.888094)**1.245007))),
        'ASIA': lambda x: np.maximum(0.0, np.minimum(1.0, 1.267385 + (0.002553797 - 1.267385)/(1 + (x/1.511393)**1.011526))),
        'LAC': lambda x: np.maximum(0.0, np.minimum(1.0, 1.04578 + (0.001490579 - 1.04578)/(1 + (x/0.5619431)**1.509554))),
        'GLOBAL': lambda x: np.maximum(0.0, np.minimum(1.0, 2.100049 + (-0.00003530885 - 2.100049)/(1 + (x/6.632485)**0.559315))),
    }
    # CRITICAL: Map wb_region to the actual region key first
    region = wb_to_region.get(wb_region, 'GLOBAL')
    damage_func = function_mapping.get(region)
    
    # FIXED: Actually call the function instead of returning the function object
    result = damage_func(x)
    return result.astype(np.float32)


# Floods (river and coastal) impact function over Agricultural areas

def FL_damage_factor_agri(x: np.array, wb_region: str):
    """A polynomial fit to average damage across agricultural land cover relative to water depth in meters.
    Values are capped between 0 and 1.

    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    https://publications.jrc.ec.europa.eu/repository/handle/JRC105688
    """
    x = x/100  # convert cm to m
    function_mapping = {
        'AFRICA': np.maximum(0.0, np.minimum(1.0, 1.006324 + (0.01417282 - 1.006324)/(1 + (x/8621.368)**1.675571)**2665027)),
        'ASIA': np.maximum(0.0, np.minimum(1.0, (1.672909*x)/(3.917017+x))),
        'LAC': np.maximum(0.0, np.minimum(1.0, 1.876076 + (0.01855393 - 1.876076)/(1 + (x/5.08262)**0.7629432))),
        'GLOBAL': np.maximum(0.0, np.minimum(1.0, 1.167022 + (-0.002602531 - 1.167022)/(1 + (x/1.398796)**1.246833))),
    }
    region = wb_to_region.get(wb_region, 'GLOBAL')
    return function_mapping.get(region)

# Tropical Cyclone - Regional equations

def TC_damage_factor_builtup(x: np.array, country_iso3: str):
    """Calculate damage factor for tropical cyclone wind impact on built-up areas based on region-specific vulnerability curves.

       Parameters
    ----------
    x : np.array
        Wind speed in meters per second
    country_iso3 : str
        ISO3 country code to determine regional vulnerability curve
        
    Returns
    -------
    np.array
        Damage factor between 0 and 1
    
    Asigmoidal function is applied in the calibration process, based on the general impact function by Emanuel (2011).
    While Vhalf is fitted during the calibration process, the lower threshold Vthresh is kept constant throughout the study.

    References
    ----------
    Eberenz et al., 2021 - Regional tropical cyclone impact functions for globally consistent risk assessments. CLIMADA project.
    (https://nhess.copernicus.org/articles/21/393/2021/)
    """

    # Get region from country code, default to GLOBAL if not found
    region = tc_region_mapping.get(country_iso3, 'GLOBAL')
    
    # Regional v_half values (wind speed at which 50% damage occurs)
    v_half = {
        'NA1': 59.6,   # Caribbean and Mexico
        'NA2': 91.8,   # USA and Canada
        'NI':  67.3,   # North Indian
        'OC':  54.4,   # Oceania
        'SI':  42.6,   # South Indian
        'WP1': 58.9,   # South East Asia
        'WP2': 87.6,   # Philippines
        'WP3': 86.3,   # China Mainland
        'WP4': 183.7,  # North West Pacific
        'GLOBAL': 83.7  # Global average
    }
    
    # Get Vhalf value for specified region
    Vhalf = v_half.get(region)

    # Global threshold value
    Vthres = 25.7  # m/s, below which no damage occurs
        
    # Calculate damage factor
    v = np.maximum(0.0, (x - Vthres))/(Vhalf - Vthres)
    return (v**3)/(1 + (v**3))