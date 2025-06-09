# Custom Hazard Risk Analysis Tool

## Overview

The Custom Hazard Risk Analysis Tool extends the Risk Data Library (RDL) analytics framework to support any hazard raster data, allowing users to analyze the risk and impact of custom hazard scenarios on population, built-up areas, and agricultural land.

## Features

- Upload and analyze any hazard raster file (e.g., floods, landslides, heat stress, etc.)
- Support for both single-event analysis and probabilistic multi-return period analysis
- Custom vulnerability functions through a user-defined mathematical expression
- Integration with existing exposure data (population, built-up area, agriculture)
- Output in standard formats (Excel tables, GeoPackage for GIS)
- Visualization of impact for intuitive understanding

## Requirements for Hazard Data

- GeoTIFF raster files (.tif)
- EPSG:4326 (WGS84) projection
- Values representing hazard intensity in appropriate units
- Coverage of the analysis area (country or custom boundaries)
- Consistent resolution recommended (e.g., 90m or 1km)

## Using the Tool

1. **Select Boundaries**: Choose a country and administrative level or upload custom boundaries
2. **Hazard Data**: Upload hazard raster file(s) and set parameters
   - Single hazard file: Provide one raster and its return period
   - Multiple hazard files: Enable "Multiple return periods" and upload rasters for each RP
3. **Exposure**: Select exposure categories (population, built-up, agriculture)
4. **Vulnerability Approach**:
   - Function: Use default impact functions
   - Classes: Define hazard intensity thresholds
   - Custom Function: Define your own mathematical impact function

## Custom Vulnerability Functions

The tool allows defining custom damage or impact functions by entering a mathematical expression. The function should map hazard values (X) to impact factors (Y) between 0 and 1.

Examples:
- Linear relationship: `Y = 0.05 * X` (5% damage per unit of hazard)
- Exponential relationship: `Y = 1 - exp(-0.1 * X)` (damage increases exponentially)
- Threshold-based: `Y = 0 if X < 10 else min(1, (X - 10) / 90)` (no damage below threshold of 10)

You can use a preview feature to visualize your function before running the analysis.

## Output Products

The tool generates:
- Excel file with tabular results by administrative area
- GeoPackage file with spatial results for use in GIS software
- Interactive map for preview (if enabled)
- Exposure-hazard relationship charts
- Expected Annual Impact calculations (if multiple return periods provided)

## Integration with Other Tools

The Custom Hazard Tool uses the same data structures and output formats as the Flood and Tropical Cyclone tools, allowing for:
- Comparison of different hazard types
- Combined multi-hazard analysis
- Integration with bivariate mapping for socioeconomic vulnerability analysis

## Implementation Notes

This tool extends the RDL analytics framework by:
1. Allowing user-uploaded raster files instead of predefined hazard data
2. Supporting custom vulnerability functions through mathematical expressions
3. Maintaining the same workflow and output formats for consistency

## Limitations

- Large raster files may cause memory issues
- Performance depends on the size and resolution of input data
- Custom functions must be expressible as mathematical formulas

## Error Handling

The tool includes validation for:
- File existence and format
- Mathematical expression validity
- Compatibility between hazard and boundary data
- Return period values

## References

- Based on the Risk Data Library framework
- Extends methodology from flood and tropical cyclone analysis
- Vulnerability approach based on standard impact assessment practices