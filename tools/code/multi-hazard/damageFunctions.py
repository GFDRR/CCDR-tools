# Importing the required packages
import numpy as np

# Defining the damage functions
# Floods (river and coastal) over Built-Up areas

def damage_factor_FL_builtup(x):
    """A polynomial fit to average damage across builtup land cover relative
    to water depth in meters.

    The sectors are commercial, industry, transport, infrastructure and residential.

    Values are capped between 0 and 1
    
    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    """
    # return np.maximum(0.0, np.minimum(1.0, -0.0028 * x ** 3 + 0.0362 * x ** 2 + 0.0095 * x)) # Floods - AFRICA
    return np.maximum(0.0, np.minimum(1.0, 0.00723 * x ** 3 - 0.1000 * x ** 2 + 0.5060 * x)) # Floods - ASIA

# Tropical cyclones over Built-Up areas

def damage_factor_TC_builtup(x):
    """
    Tropical Cyclone - Global equation from Climada
    """
    #Vhalf  = 59.6         # m/s, where half damage occurs - NA1 - Caribbean and Mexico
    #Vhalf  = 91.8         # m/s, where half damage occurs - NA2 - USA and Canada
    Vhalf  = 67.3         # m/s, where half damage occurs - NI  - North Indian
    #Vhalf  = 54.4         # m/s, where half damage occurs - OC  - Oceania
    #Vhalf  = 42.6         # m/s, where half damage occurs - SI  - South Indian
    #Vhalf  = 58.9         # m/s, where half damage occurs - WP1 - South East Asia
    #Vhalf  = 87.6         # m/s, where half damage occurs - WP2 - Philippines
    #Vhalf  = 86.3         # m/s, where half damage occurs - WP3 - China Mainland
    #Vhalf  = 183.7        # m/s, where half damage occurs - WP4 - North West Pacific
    Vthres = 25.7         # m/s, below to wihch no damage occurs - Global
    v = np.maximum(0.0, (x-Vthres))/(Vhalf-Vthres)
    return (v**3)/(1+(v**3)) # Tropical Cyclone - Global equation

# Flood over Agricultural areas

def damage_factor_agri(x):
    """A polynomial fit to average damage across agricultural land cover relative
    to water depth in meters.

    Values are capped between 0 and 1

    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    Point fitting by cubic regression (R2 = 0.98)
    """
    # return (x+999)/(x+999) # For Agri exposure
    # return (x)             # For DR impacts
    # return np.maximum(0.0, np.minimum(1.0, 0.01108 * x ** 3 + 0.1578 * x ** 2 + 0.7209 * x - 0.042)) # Floods - AFRICA
    return np.maximum(0.0, np.minimum(1.0, 0.00455 * x ** 3 - 0.0648 * x ** 2 + 0.3960 * x - 0.000049)) # Floods - ASIA
    # return np.maximum(0.0, np.minimum(1.0, 0.00833 * x ** 3 - 0.1131 * x ** 2 + 0.5468 * x - 0.00611)) # Floods - GLOBAL


# Flood over Population mortality
def mortality_factor(x):
    """A polynomial fit to average population mortality due to nearby flooding.

    References
    ----------
    Jonkman SN, 2008 - Loss of life due to floods
    """
    return np.maximum(0.0, np.minimum(1.0, 0.985 / (1 + np.exp(6.32 - 1.412 * x))))  # Floods - Global