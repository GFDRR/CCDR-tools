# Importing the required packages
import numpy as np
from common import wb_to_region

# Defining the damage functions

# Floods (river and coastal) over Population mortality
def mortality_factor(x: np.array):
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
        'AFRICA': np.maximum(0.0, np.minimum(1.0, -0.0028*x**3 + 0.0362*x**2 + 0.0095*x)),
        'ASIA': np.maximum(0.0, np.minimum(1.0, 0.00723*x**3 - 0.1000*x**2 + 0.5060*x)),
        'LAC': np.maximum(0.0, np.minimum(1.0, 0.9981236 - 0.9946279*np.exp(-1.711056*x))), 
    }
    
    return function_mapping.get(wb_to_region.get(wb_region))

# Floods (river and coastal) over Agricultural areas

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
        'AFRICA': np.maximum(0.0, np.minimum(1.0, 0.0111 * x ** 3 - 0.158 * x ** 2 + 0.721 * x - 0.0418)),
        'ASIA': np.maximum(0.0, np.minimum(1.0, 0.00455 * x ** 3 - 0.0648 * x ** 2 + 0.396 * x - 0.000049)),
    }
    
    region = wb_to_region.get(wb_region)
    if region not in function_mapping.keys():
        return np.maximum(0.0, np.minimum(1.0, 1.0244 - 1.0267*np.exp(-0.589*x)))
    return function_mapping.get(wb_to_region.get(wb_region))

