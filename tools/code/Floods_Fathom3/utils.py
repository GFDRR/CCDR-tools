from folium import Choropleth, Map, LayerControl
from folium.plugins import MiniMap
import geopandas as gpd
from IPython.display import display
from rasterstats import zonal_stats


def zonal_stats_partial(feats, raster, stats="*", affine=None, nodata=None, all_touched=True):
    # Partial zonal stats for parallel processing on a list of features
    return zonal_stats(feats, raster, stats=stats, affine=affine, nodata=nodata, all_touched=all_touched)


def zonal_stats_parallel(args):
    # Zonal stats for a parallel processing on a list of features
    return zonal_stats_partial(*args)


def result_df_reorder_columns(result_df, RPs, exp_cat, adm_level, all_adm_codes, all_adm_names):
    """
    Reorders the columns of result_df.
    """
    # Re-ordering and dropping selected columns for better presentation of the 
    all_RPs = [f"RP{rp}" for rp in RPs]
    all_exp = [x + f"_{exp_cat}_exp" for x in all_RPs]
    all_imp = [x + f"_{exp_cat}_imp" for x in all_RPs]
    col_order = all_adm_codes + all_adm_names + [f"ADM{adm_level}_{exp_cat}"] + all_exp + all_imp + ["geometry"]
    return result_df.loc[:, col_order]


def plot_results(result_df, country, adm_level, exp_cat, analysis_type):
    # Convert result_df to GeoDataFrame if it's not already
    if not isinstance(result_df, gpd.GeoDataFrame):
        result_df = gpd.GeoDataFrame(result_df, geometry='geometry')
    
    # Determine the column to plot based on analysis_app
    if analysis_type == "Function":
        column = f'{country}_{exp_cat}_EAI'
    elif analysis_type == "Classes":
        column = f'RP10_{country}_{exp_cat}_C1'
    else:
        print("Unknown analysis approach")
        return

    # Ensure the CRS is EPSG:4326
    result_df = result_df.to_crs(epsg=4326)
    
    # Calculate the bounding box
    bounds = result_df.total_bounds  # [minx, miny, maxx, maxy]

    # Calculate the center of the bounding box
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    # Initialize the folium map centered on the GeoDataFrame extent
    m = Map(location=[center_lat, center_lon], zoom_start=5)

    # Determine the key column (replace 'ADM1_TUN_POP' with your actual key column name)
    key_column = f'HASC_{adm_level}'  # Replace with the actual column that corresponds to your features

    # Add GeoDataFrame to the map as a choropleth with a custom name
    Choropleth(
        geo_data=result_df.to_json(),  # Convert GeoDataFrame to GeoJSON format
        name=column,  # Set the name that will appear in the layer control
        data=result_df,
        columns=[key_column, column],
        key_on=f"feature.properties.{key_column}",  # Adjust to the correct key
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=column,
        use_jenks=True,
    ).add_to(m)

    # Add layer control
    LayerControl().add_to(m)
    MiniMap(toggle_display=True).add_to(m)

    # Display the map
    display(m)