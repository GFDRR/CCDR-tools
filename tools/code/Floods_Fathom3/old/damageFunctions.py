# Importing the required packages
import numpy as np

# Defining the damage functions

# Floods (river and coastal) over Population mortality
def mortality_factor(x):
    """A polynomial fit to average population mortality due to nearby flooding.

    References
    ----------
    Jonkman SN, 2008 - Loss of life due to floods
    """
    x = x/100  # convert cm to m if necessary
    return np.maximum(0.0, np.minimum(1.0, 0.985 / (1 + np.exp(6.32 - 1.412 * x))))  # Floods - Global

# Floods (river and coastal) over Built-Up areas

def damage_factor_builtup(x):
    """A polynomial fit to average damage across builtup land cover relative
    to water depth in meters.

    The sectors are commercial, industry, transport, infrastructure and residential.

    Values are capped between 0 and 1
    
    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    """
    x = x/100  # convert cm to m if necessary 
    # return np.maximum(0.0, np.minimum(1.0, -0.0028 * x ** 3 + 0.0362 * x ** 2 + 0.0095 * x)) # Floods - AFRICA
    return np.maximum(0.0, np.minimum(1.0, 0.00723 * x ** 3 - 0.1000 * x ** 2 + 0.5060 * x)) # Floods - ASIA
    # return np.maximum(0.0, np.minimum(1.0, 0.9981 - 0.9946*np.exp(-1.711*x))) # Floods - LAC

# Floods (river and coastal) over Agricultural areas

def damage_factor_agri(x):
    """A polynomial fit to average damage across agricultural land cover relative to water depth in meters.
    Values are capped between 0 and 1

    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    """
    x = x/100  # convert cm to m if necessary
    # return np.maximum(0.0, np.minimum(1.0, 0.0111 * x ** 3 - 0.158 * x ** 2 + 0.721 * x - 0.0418)) # Floods - AFRICA
    return np.maximum(0.0, np.minimum(1.0, 0.00455 * x ** 3 - 0.0648 * x ** 2 + 0.396 * x - 0.000049)) # Floods - ASIA
    # return np.maximum(0.0, np.minimum(1.0, 1.0244 - 1.0267*np.exp(-0.589*x))) # Floods - GLOBAL
