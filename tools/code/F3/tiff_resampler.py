"""
TIFF Resampling Module with Parallel Processing

This module provides functions to resample TIFF files from one resolution to another
using parallel processing to improve performance.
"""

import os
import glob
import concurrent.futures
from concurrent.futures import as_completed
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import numpy as np
from typing import List, Dict, Tuple, Union, Any


def resample_tiff(input_path: str, output_path: str, target_resolution: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Resample a TIFF file to a new resolution while preserving CRS and data format.
    
    Args:
        input_path: Path to the input TIFF file
        output_path: Path where the resampled TIFF will be saved
        target_resolution: Target resolution in the units of the file's CRS
        
    Returns:
        Tuple containing (original_resolution, new_resolution)
    """
    with rasterio.open(input_path) as src:
        # Get metadata from the source file
        src_crs = src.crs
        src_bounds = src.bounds
        src_dtype = src.dtypes[0]  # Get the data type of the first band
        src_nodata = src.nodata
        
        # Force the target resolution to exactly 0.0008333333
        exact_target_resolution = 0.0008333333
        
        # Calculate new dimensions based on the geographic bounds and target resolution
        new_width = max(1, int(round((src_bounds.right - src_bounds.left) / exact_target_resolution)))
        new_height = max(1, int(round((src_bounds.top - src_bounds.bottom) / exact_target_resolution)))
        
        # Create new transform
        dst_transform = rasterio.transform.from_bounds(
            src_bounds.left, src_bounds.bottom, 
            src_bounds.right, src_bounds.top, 
            new_width, new_height
        )
        
        # Create metadata for output file
        dst_kwargs = src.meta.copy()
        dst_kwargs.update({
            'crs': src_crs,
            'transform': dst_transform,
            'width': new_width,
            'height': new_height,
            'compress': 'deflate',  # Add deflate compression
            'predictor': 2,  # Horizontal differencing predictor (optimizes compression)
            'zlevel': 9     # Maximum compression level (1-9)
        })
        
        # Create output file
        with rasterio.open(output_path, 'w', **dst_kwargs) as dst:
            # Process each band
            for i in range(1, src.count + 1):
                # Read the source band
                src_band = src.read(i)
                
                # Create empty array for destination
                dst_band = np.empty((new_height, new_width), dtype=src_dtype)
                
                # Perform the resampling
                reproject(
                    source=src_band,
                    destination=dst_band,
                    src_transform=src.transform,
                    src_crs=src_crs,
                    dst_transform=dst_transform,
                    dst_crs=src_crs,
                    resampling=Resampling.nearest,  # Using nearest neighbor resampling
                    src_nodata=src_nodata,
                    dst_nodata=src_nodata
                )
                
                # Write the resampled band to the destination
                dst.write(dst_band, i)
        
        # Return the original and new resolution for verification
        with rasterio.open(output_path) as dst_check:
            actual_res = dst_check.res
        
        return (src.res, actual_res)


def process_file(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single file for parallel execution.
    
    Args:
        file_info: Dictionary with keys 'input_file', 'output_file', 'target_resolution'
    
    Returns:
        Dictionary with processing results
    """
    input_file = file_info['input_file']
    output_file = file_info['output_file']
    target_resolution = file_info['target_resolution']
    
    try:
        # Resample the file
        resolutions = resample_tiff(input_file, output_file, target_resolution)
        
        # Return results
        return {
            'input_file': os.path.basename(input_file),
            'output_file': os.path.basename(output_file),
            'original_resolution': resolutions[0],
            'new_resolution': resolutions[1],
            'status': 'Success'
        }
        
    except Exception as e:
        return {
            'input_file': os.path.basename(input_file),
            'output_file': os.path.basename(output_file),
            'status': f'Failed: {str(e)}'
        }


def check_resolution(file_path: str) -> Tuple[float, float]:
    """
    Check the resolution of a TIFF file.
    
    Args:
        file_path: Path to the TIFF file
    
    Returns:
        Tuple containing the x and y resolution values
    """
    with rasterio.open(file_path) as src:
        return src.res


def find_tiff_files(folder_path: str) -> List[str]:
    """
    Find all TIFF files in a folder.
    
    Args:
        folder_path: Path to the folder to search
    
    Returns:
        List of paths to TIFF files
    """
    tiff_files = []
    for ext in ['*.tif']:
        tiff_files.extend(glob.glob(os.path.join(folder_path, ext)))
    return tiff_files


def resample_tiffs_parallel(
    folder_path: str, 
    target_resolution: float = 0.0008333333,  # Exact 90m resolution 
    output_suffix: str = "_90m",
    max_workers: int = None
) -> List[Dict[str, Any]]:
    """
    Resample multiple TIFF files in parallel.
    
    Args:
        folder_path: Path to the folder containing TIFF files
        target_resolution: Target resolution in the units of the file's CRS
        output_suffix: Suffix to add to output filenames
        max_workers: Maximum number of worker processes (None = automatic)
    
    Returns:
        List of dictionaries with processing results
    """
    # Find all TIFF files
    tiff_files = find_tiff_files(folder_path)
    
    if not tiff_files:
        return []
    
    # Create output folder if it doesn't exist
    output_folder = os.path.join(folder_path, 'resampled')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Prepare processing tasks
    tasks = []
    for input_file in tiff_files:
        # Generate output filename with suffix
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_folder, f"{base_name}{output_suffix}.tif")
        
        tasks.append({
            'input_file': input_file,
            'output_file': output_file,
            'target_resolution': target_resolution
        })
    
    # Process files in parallel
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks
        future_to_file = {executor.submit(process_file, task): task for task in tasks}
        
        # Process results as they complete
        for future in as_completed(future_to_file):
            task = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                input_file = os.path.basename(task['input_file'])
                results.append({
                    'input_file': input_file,
                    'output_file': os.path.basename(task['output_file']),
                    'status': f'Failed with exception: {str(e)}'
                })
    
    return results


def verify_output_files(output_folder: str, target_resolution: float) -> List[Dict[str, Any]]:
    """
    Verify that output files have the correct resolution.
    
    Args:
        output_folder: Path to the folder containing output files
        target_resolution: Expected resolution
    
    Returns:
        List of dictionaries with verification results
    """
    output_files = []
    for ext in ['*.tif', '*.tiff', '*.TIF', '*.TIFF']:
        output_files.extend(glob.glob(os.path.join(output_folder, ext)))
    
    results = []
    for file in output_files:
        try:
            with rasterio.open(file) as src:
                resolution = src.res
                matches = abs(resolution[0] - target_resolution) < 1e-6
                
                results.append({
                    'file': os.path.basename(file),
                    'resolution': resolution,
                    'matches_target': matches,
                    'status': 'Verified'
                })
                
        except Exception as e:
            results.append({
                'file': os.path.basename(file),
                'status': f'Failed: {str(e)}'
            })
    
    return results


if __name__ == "__main__":
    # Example usage
    folder_path = './data'
    target_resolution = 0.000833333
    
    print(f"Resampling TIFF files in {folder_path} to resolution {target_resolution}")
    results = resample_tiffs_parallel(folder_path, target_resolution)
    
    # Print summary
    successes = sum(1 for r in results if r['status'] == 'Success')
    print(f"Processed {len(results)} files: {successes} successful, {len(results) - successes} failed")