# Importing the required packages
import numpy as np

# Defining the damage function - Built-Up areas
def damage_factor_builtup(x):
    """A polynomial fit to average damage across builtup land cover relative
    to water depth in meters.

    The sectors are commercial, industry, transport, infrastructure and residential.

    Values are capped between 0 and 1
    
    References
    ----------
    .. [1] JRC, 2017
    """
    # return np.maximum(0.0, np.minimum(1.0, -0.0028 * x ** 3 + 0.0362 * x ** 2 + 0.0095 * x)) # Floods - AFRICA
    return np.maximum(0.0, np.minimum(1.0, 0.00723 * x ** 3 - 0.1000 * x ** 2 + 0.5060 * x)) # Floods - ASIA
    
    #Vthres = 26         # m/s, below to wihch no damage occurs - Phillipines
    #Vhalf  = 85         # m/s, where half damage occurs - Phillipines
    #v = np.maximum(0.0, (x-Vthres))/(Vhalf-Vthres)
    #return (v**3)/(1+(v**3))
    
    # return (x+999)/(x+999)

# Defining the damage function - Agriculture
def damage_factor_agri(x):
    """A polynomial fit to average damage across agricultural land cover relative
    to water depth in meters.

    Values are capped between 0 and 1

    References
    ----------
    .. [1] JRC, 2017
    """
    # return np.maximum(0.0, np.minimum(1.0, -0.0039 * x ** 3 + 0.0383 * x ** 2 + 0.0768 * x)) # Floods - AFRICA
    return np.maximum(0.0, np.minimum(1.0, 0.00723 * x ** 3 - 0.1000 * x ** 2 + 0.5060 * x)) # Floods - ASIA
    # return (x+999)/(x+999)

# Defining the damage function - Mortality
def mortality_factor(x):
    """A polynomial fit to average population mortality due to nearby flooding.
    References
    ----------
    .. [1] Jonkman et al, 2008
    """
    return np.maximum(0.0, np.minimum(1.0, 0.985 / (1 + np.exp(6.32 - 1.412 * x))))  # Floods - Global
    # return (x+999)/(x+999)
