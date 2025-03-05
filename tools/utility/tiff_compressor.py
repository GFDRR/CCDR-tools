import os
from osgeo import gdal
from pathlib import Path
import multiprocessing as mp
from typing import List, Tuple, Optional

# Enable GDAL error messages and configure
gdal.UseExceptions()
gdal.SetCacheMax(1024 * 1024 * 512)  # 512MB cache

def get_tiff_info(file_path: Path) -> Optional[dict]:
    """Get detailed information about a TIFF file."""
    try:
        ds = gdal.Open(str(file_path))
        if ds is None:
            return None
        
        # Get band information
        band = ds.GetRasterBand(1)
        band_type = gdal.GetDataTypeName(band.DataType)
        min_val, max_val = band.ComputeRasterMinMax()
        
        info = {
            'size': (ds.RasterXSize, ds.RasterYSize),
            'bands': ds.RasterCount,
            'projection': ds.GetProjection(),
            'metadata': ds.GetMetadata(),
            'geotransform': ds.GetGeoTransform(),
            'image_structure': ds.GetMetadata('IMAGE_STRUCTURE'),
            'data_type': band_type,
            'min_value': min_val,
            'max_value': max_val
        }
        
        ds = None  # Close the dataset
        return info
    except Exception as e:
        print(f"Error getting TIFF info for {file_path}: {str(e)}")
        return None

def is_tiff_uncompressed(file_path: Path) -> bool:
    """Check if a TIFF file is uncompressed."""
    try:
        info = get_tiff_info(file_path)
        if info is None:
            return False
        
        compression = info['image_structure'].get('COMPRESSION', 'NONE')
        return compression == 'NONE'
    except Exception as e:
        print(f"Error checking compression for {file_path}: {str(e)}")
        return False

def compress_tiff(file_tuple: Tuple[Path, Path]) -> bool:
    """
    Compress a TIFF file using DEFLATE compression optimized for 8-bit data.
    
    Args:
        file_tuple: Tuple of (input_path, output_path)
    Returns:
        bool: True if compression was successful
    """
    input_path, output_path = file_tuple
    
    try:
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open input dataset
        src_ds = gdal.Open(str(input_path))
        if src_ds is None:
            print(f"Failed to open {input_path}")
            return False
            
        print(f"Processing: {input_path}")
        
        # Create the output dataset
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(str(output_path),
                          src_ds.RasterXSize,
                          src_ds.RasterYSize,
                          src_ds.RasterCount,
                          gdal.GDT_Byte,
                          options=['COMPRESS=DEFLATE',
                                 'PREDICTOR=1',
                                 'ZLEVEL=9',
                                 'BIGTIFF=YES',
                                 'TILED=YES',
                                 'BLOCKXSIZE=256',
                                 'BLOCKYSIZE=256'])
        
        if dst_ds is None:
            print(f"Failed to create output dataset {output_path}")
            return False
            
        # Copy the geotransform and projection
        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
        dst_ds.SetProjection(src_ds.GetProjection())
        
        # Copy the data
        for i in range(1, src_ds.RasterCount + 1):
            src_band = src_ds.GetRasterBand(i)
            dst_band = dst_ds.GetRasterBand(i)
            
            # Copy nodata value if it exists
            nodata = src_band.GetNoDataValue()
            if nodata is not None:
                dst_band.SetNoDataValue(nodata)
            
            # Copy the data in blocks
            for y in range(0, src_ds.RasterYSize, 1024):
                win_height = min(1024, src_ds.RasterYSize - y)
                for x in range(0, src_ds.RasterXSize, 1024):
                    win_width = min(1024, src_ds.RasterXSize - x)
                    data = src_band.ReadRaster(x, y, win_width, win_height)
                    dst_band.WriteRaster(x, y, win_width, win_height, data)
        
        # Close the datasets
        src_ds = None
        dst_ds = None
        
        print(f"Successfully compressed: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error compressing {input_path}: {str(e)}")
        gdal_error = gdal.GetLastErrorMsg()
        if gdal_error:
            print(f"GDAL Error: {gdal_error}")
        return False

def process_directory(input_dir: Path, output_dir: Path, num_processes: int = None) -> Tuple[int, int]:
    """
    Process all uncompressed TIFF files in a directory using parallel processing.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        num_processes: Number of processes to use (defaults to CPU count - 1)
    
    Returns:
        Tuple of (processed_count, error_count)
    """
    if num_processes is None:
        num_processes = max(1, mp.cpu_count() - 1)
    
    # Collect all uncompressed TIFF files
    compression_tasks = []
    
    for tiff_file in input_dir.rglob('*.tif'):
        # Skip files in the output directory
        if output_dir in tiff_file.parents:
            continue
            
        # Check if the file is uncompressed
        if not is_tiff_uncompressed(tiff_file):
            print(f"Skipping {tiff_file} (already compressed or invalid)")
            continue
        
        # Create output path
        relative_path = tiff_file.relative_to(input_dir)
        output_path = output_dir / relative_path
        
        compression_tasks.append((tiff_file, output_path))
    
    # Process files in parallel
    processed_count = 0
    error_count = 0
    
    if compression_tasks:
        print(f"\nProcessing {len(compression_tasks)} files using {num_processes} processes...")
        
        with mp.Pool(num_processes) as pool:
            results = pool.map(compress_tiff, compression_tasks)
            
            processed_count = sum(1 for x in results if x)
            error_count = sum(1 for x in results if not x)
    
    return processed_count, error_count