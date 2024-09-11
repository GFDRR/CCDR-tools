# Importing the required packages
import numpy as np
from common import wb_to_region

# Defining the damage functions

# Floods (river and coastal) over Population mortality
def mortality_factor(x: np.array, wb_region: str = None):
    """A polynomial fit to average population mortality due to nearby flooding.
    Values are capped between 0 and 1

    References
    ----------
    Jonkman SN, 2008 - Loss of life due to floods (https://doi.org/10.1111/j.1753-318X.2008.00006.x)
    """
    x = x/100  # convert cm to m
    return np.maximum(0.0, np.minimum(1.0, 0.985 / (1 + np.exp(6.32 - 1.412 * x))))  # Floods - Global

# Floods (river and coastal) over Built-Up areas

def damage_factor_builtup(x: np.array, wb_region: str):
    """A polynomial fit to average damage across builtup land cover relative to water depth in meters.

    The sectors are commercial, industry, transport, infrastructure and residential.
    Values are capped between 0 and 1
    
    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    (https://publications.jrc.ec.europa.eu/repository/handle/JRC105688)
    """
    x = x/100  # convert cm to m
    function_mapping = {
        'AFRICA': np.maximum(0.0, np.minimum(1.0, 1.246282 + (0.004404681 - 1.246282)/(1 + (x/1.888094)**1.245007))),
        'ASIA': np.maximum(0.0, np.minimum(1.0, 1.267385 + (0.002553797 - 1.267385)/(1 + (x/1.511393)**1.011526))),
        'LAC': np.maximum(0.0, np.minimum(1.0, 1.04578 + (0.001490579 - 1.04578)/(1 + (x/0.5619431)**1.509554))),
        'GLOBAL': np.maximum(0.0, np.minimum(1.0, 2.100049 + (-0.00003530885 - 2.100049)/(1 + (x/6.632485)**0.559315))),
    }
    region = wb_to_region.get(wb_region)
    if region not in function_mapping.keys():
        return np.maximum(0.0, np.minimum(1.0, 2.100049 + (-0.00003530885 - 2.100049)/(1 + (x/6.632485)**0.559315)))
    return function_mapping.get(wb_to_region.get(wb_region))


# Floods (river and coastal) impact function over Agricultural areas

def damage_factor_agri(x: np.array, wb_region: str):
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
        'LAC': np.maximum(0.0, np.minimum(1.0, 1.876076 + (0.01855393 - 1.876076)/(1 + (x/5.08262)^0.7629432))),
        'GLOBAL': np.maximum(0.0, np.minimum(1.0, 1.167022 + (-0.002602531 - 1.167022)/(1 + (x/1.398796)**1.246833))),
    }

    region = wb_to_region.get(wb_region)
    if region not in function_mapping.keys():
        return np.maximum(0.0, np.minimum(1.0, 1.167022 + (-0.002602531 - 1.167022)/(1 + (x/1.398796)**1.246833)))
    return function_mapping.get(wb_to_region.get(wb_region))

