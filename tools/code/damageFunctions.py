# Importing the required packages
import numpy as np
from common import tc_region_mapping

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
def FL_damage_factor_builtup(x: np.array, region: str):
    """Damage across built-up land cover relative to water depth in meters, refit
    directly against the raw depth-damage data points published in Huizinga et al.
    (2017) - the coefficients below are NOT hand-interpolated, they come from a
    nonlinear least-squares fit (scipy.optimize.curve_fit) of the standard 4-parameter
    Huizinga logistic form a + (d-a)/(1+(x/c)**b) to that source data.

    "Built-up" is modelled as a composite of the three sectors Huizinga et al. group
    together as "buildings": Residential (70%), Commercial (15%), Industrial (15%).
    This weighting is our own assumption (JRC provides no global split of built-up
    area by building use) and can be revisited if better local data becomes
    available. Where a region's data is missing one of these sectors (e.g. Africa
    has no Commercial curve in the source), the remaining weights are renormalized
    - Africa is effectively Residential 82.4% / Industrial 17.6%. Transport and
    Infrastructure (roads) are intentionally excluded: Huizinga et al. treat those as
    a separate asset class mapped from road networks, not from built-up/settlement
    extent, so blending them in would double-count against a dedicated roads layer.

    EUROPE is now its own bucket, fit from JRC's dedicated EUROPE composite curve,
    for the EU-27 countries listed in common.eu_country_codes. GLOBAL (everyone else
    in wb_to_region's 'Other'/ECA catch-alls - North America, Japan, Korea, Australia,
    New Zealand, non-EU Europe) is refit as the mean of JRC's own EUROPE + NORTH
    AMERICA + OCEANIA composite curves, rather than the ad hoc coefficients used
    previously, which didn't match any curve in the source workbook.

    Parameters
    ----------
    x : np.array
        Flood depth in centimeters.
    region : str
        Final damage-function region bucket - 'AFRICA', 'ASIA', 'LAC', 'EUROPE' or
        'GLOBAL' - as resolved by common.resolve_flood_region(country_iso3, wb_region).
        This is NOT the raw World Bank region code.

    Values are capped between 0 and 1.

    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    (https://publications.jrc.ec.europa.eu/repository/handle/JRC105688)
    """
    x = (x/100).astype(np.float32)    # convert cm to m
    function_mapping = {
        'AFRICA': lambda x: np.maximum(0.0, np.minimum(1.0, 1.2671827203289083 + (0.00413364200087085 - 1.2671827203289083)/(1 + (x/2.057466891542489)**1.2883789088727349))),
        'ASIA': lambda x: np.maximum(0.0, np.minimum(1.0, 1.2446026534606476 + (0.002065149335395301 - 1.2446026534606476)/(1 + (x/1.4347439516379064)**1.0323864071557256))),
        'LAC': lambda x: np.maximum(0.0, np.minimum(1.0, 1.035618667757186 + (0.0008811294104793913 - 1.035618667757186)/(1 + (x/0.4894358954469605)**1.5496269301385341))),
        'EUROPE': lambda x: np.maximum(0.0, np.minimum(1.0, 1.7088514404060207 + (0.0021048967984816642 - 1.7088514404060207)/(1 + (x/4.001115592872838)**0.9441309503291869))),
        'GLOBAL': lambda x: np.maximum(0.0, np.minimum(1.0, 1.3581185158837237 + (0.050530835141520035 - 1.3581185158837237)/(1 + (x/1.9731251441067115)**0.9099528927976404))),
    }
    damage_func = function_mapping.get(region, function_mapping['GLOBAL'])
    result = damage_func(x)
    return result.astype(np.float32)


# Floods (river and coastal) impact function over Agricultural areas
def FL_damage_factor_agri(x: np.array, region: str):
    """Damage across agricultural land cover relative to water depth in meters,
    refit directly against the raw depth-damage data points published in
    Huizinga et al. (2017) via nonlinear least squares (scipy.optimize.curve_fit)
    to the standard 4-parameter Huizinga logistic form a + (d-a)/(1+(x/c)**b).
    Values are capped between 0 and 1.

    NOTE on AFRICA: the previous coefficient set was
        1.006324 + (0.01417282 - 1.006324)/(1 + (x/8621.368)**1.675571)**2665027
    Because ** binds tighter than /, the exponent 2665027 applied to the ENTIRE
    denominator (not a term inside it), producing a near step-function: ~1.4%
    damage at x=0 jumping to the 1.0 cap at any depth above ~0. The AFRICA
    coefficients below are a fresh fit to the actual 9 published Africa/agriculture
    data points (which genuinely do rise steeply, saturating near 1.0 by ~3m -
    that part of the old shape wasn't wrong, just the broken exponent handling was).

    NOTE on LAC: Huizinga et al. do not publish an agriculture curve for Latin
    America & Caribbean at all (every LAC/agriculture cell in the source workbook
    is blank). The previous LAC coefficients were therefore fabricated/interpolated
    with no source data behind them. Per Huizinga et al.'s own stated methodology
    ("if not feasible to develop a continent-specific function, Global is provided"),
    LAC now falls back to the GLOBAL curve instead of using invented numbers.

    EUROPE is now its own bucket (JRC does publish agriculture data for Europe),
    used for the EU-27 countries listed in common.eu_country_codes.

    Parameters
    ----------
    x : np.array
        Flood depth in centimeters.
    region : str
        Final damage-function region bucket - 'AFRICA', 'ASIA', 'LAC', 'EUROPE' or
        'GLOBAL' - as resolved by common.resolve_flood_region(country_iso3, wb_region).
        This is NOT the raw World Bank region code.

    References
    ----------
    Huizinga et al., 2017 - Global flood depth-damage functions: Methodology and the database. EU-JRC.
    https://publications.jrc.ec.europa.eu/repository/handle/JRC105688
    """
    x = x/100  # convert cm to m
    function_mapping = {
        'AFRICA': lambda x: np.maximum(0.0, np.minimum(1.0, 1.0108063696349077 + (0.001115088844059405 - 1.0108063696349077)/(1 + (x/0.8299357296842107)**2.8611757218195413))),
        'ASIA': lambda x: np.maximum(0.0, np.minimum(1.0, 1.0810635207406762 + (0.00016732761699327043 - 1.0810635207406762)/(1 + (x/1.5324656322983508)**1.885982369925525))),
        'EUROPE': lambda x: np.maximum(0.0, np.minimum(1.0, 1.170778235039068 + (0.0 - 1.170778235039068)/(1 + (x/1.2001969915332753)**1.1556264599993142))),
        # LAC: no source data - falls back to the GLOBAL curve (see note above).
        'LAC': lambda x: np.maximum(0.0, np.minimum(1.0, 1.1651603167369582 + (0.0 - 1.1651603167369582)/(1 + (x/1.4133544121779626)**1.2597438701651484))),
        'GLOBAL': lambda x: np.maximum(0.0, np.minimum(1.0, 1.1651603167369582 + (0.0 - 1.1651603167369582)/(1 + (x/1.4133544121779626)**1.2597438701651484))),
    }
    damage_func = function_mapping.get(region, function_mapping['GLOBAL'])
    return damage_func(x)


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

    Asigmoidal function is applied in the calibration process, based on the general impact function by Emanuel (2011).
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
