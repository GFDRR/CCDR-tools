################################################################################
######################## fRasterCompatible R Function ##########################
################################################################################
# This script contains a function to convert a raster to a same projection, 
#   resolution, and extension of another reference raster. 
# As defined, rasterInput is converted to be compatible with rasterRef
# 
# -r <resampling_method>
#   Resampling method to use. Available methods are:
#     near: nearest neighbour resampling.
#     bilinear: bilinear resampling (default).
#     cubic: cubic resampling.
#     cubicspline: cubic spline resampling.
#     lanczos: Lanczos windowed sinc resampling.
#     average: average of all non-NODATA contributing pixels.
#     mode: value which appears most often of all the sampled points.
#     max: maximum value from all non-NODATA contributing pixels.
#     min: minimum value from all non-NODATA contributing pixels.
#     med: median value of all non-NODATA contributing pixels.
#     q1: first quartile value of all non-NODATA contributing pixels.
#     q3: third quartile value of all non-NODATA contributing pixels.
# -normalisedSum: Boolean, if TRUE, a subsequent step is done in order to have
#                 the sum pixel values of rasterInput the same as rasterOutput
# 
# Author: Arthur Hrast Essenfelder
# E-mail: arthur.essenfelder@gmail.com
# 
# Version: 1.0
# Last update on: 04/09/2019
# Last modified by: Arthur Hrast Essenfelder
################################################################################
################################################################################

# Function to convert a raster to a same projection, resolution, and extension
fRasterCompatible = function(rasterInput, rasterRef, rasterOutput, dstnodata, 
                             resampling_method, normalisedSum=FALSE) {
  
  # rasterInput will be overwritten in case rasterOutput is not defined
  if (missing(rasterOutput)) { 
    message("Warning! ",rasterInput," will be overwritten."); 
    rasterOutput = rasterInput; 
  }
  rasterOutputTmp = sub(".tif", "_tmp.tif", rasterOutput)
  if (missing(resampling_method)) { resampling_method = "bilinear"; }
  resampling_methods = c("near","bilinear","cubic","cubicspline","lanczos",
                         "average","mode","max","min","med","q1","q3")
  if (!resampling_method %in% resampling_methods) {
    message("Wrong resampling_method. Available methods are:")
    message("  near: nearest neighbour resampling.")
    message("  bilinear: bilinear resampling.")
    message("  cubic: cubic resampling.")
    message("  cubicspline: cubic spline resampling.")
    message("  lanczos: Lanczos windowed sinc resampling.")
    message("  average: average of all non-NODATA contributing pixels.")
    message("  mode: value which appears most often of all the sampled points.")
    message("  max: maximum value from all non-NODATA contributing pixels.")
    message("  min: minimum value from all non-NODATA contributing pixels.")
    message("  med: median value of all non-NODATA contributing pixels.")
    message("  q1: first quartile value of all non-NODATA contributing pixels.")
    message("  q3: third quartile value of all non-NODATA contributing pixels.")
  }
  
  # Loading required libraries
  library(gdalUtils)
  library(terra)
  
  # Getting rasterRef and rasterInput data
  rIn1 = terra::rast(rasterRef)
  rIn2 = terra::rast(rasterInput)
  sPrj = gsub(".tif", "_prj.tif", rasterInput);
  sRes = gsub(".tif", "_res.tif", rasterInput);
  
  # If dstnodata is missing, then dstnodata is defined as the same as rasterRef
  if (missing(dstnodata)) { 
    dstnodata = gdalinfo(rasterRef)
    dstnodata = strsplit(dstnodata[grepl("NoData Value", dstnodata)], "=")
    dstnodata = dstnodata[[1]][length(dstnodata[[1]])]
  }
  if (is.infinite(as.numeric(dstnodata))) { 
    dst = sign(as.numeric(dstnodata)); 
    if (dst==-1) { dst = "-" } else { dst = "" }
    dstnodata = paste(dst,"3.40282e+38",sep=""); 
  }
  
  # Checking if rasterInput needs reprojection...
  if (terra::crs(rIn1, proj=TRUE) != terra::crs(rIn2, proj=TRUE)) { bPrj = TRUE } else { bPrj = FALSE }
  
  # Checking if rasterInput needs resampling...
  if (any(c(terra::res(rIn1) != terra::res(rIn2), terra::ext(rIn1) != terra::ext(rIn2)))) { bRes = TRUE } else { bRes = FALSE }
  
  # Making rasterInput compatible to rasterRef
  if (any(c(bPrj, bRes))) {
    # Getting useful information for warping
    t_srs = terra::crs(rIn1, proj=TRUE);
    tr = terra::res(rIn1);
    te = as.vector(terra::ext(rIn1));
    te = te[c(1,3,2,4)];
    projwin = te[c(1,4,3,2)];
    # Creating the virtual warp raster
    gdalUtils::gdalwarp(rasterInput, rasterOutputTmp, of="GTiff",  t_srs=t_srs, tr=tr, te=te, 
                        r=resampling_method, dstnodata=dstnodata,
                        config=c("GDAL_NUM_THREADS ALL_CPUS", "GDAL_CACHEMAX 2048"), wm=2048,
                        co=c("NUM_THREADS=ALL_CPUS", "BIGTIFF=YES", "COMPRESS=PACKBITS"),
                        wo=c("NUM_THREADS=ALL_CPUS", "SKIP_NOSOURCE=YES"),
                        to=c("NUM_THREADS=ALL_CPUS"), oo=c("NUM_THREADS=ALL_CPUS"), doo=c("NUM_THREADS=ALL_CPUS"), 
                        overwrite=TRUE, multi=TRUE, verbose=FALSE);
    # Checking if normalisedSum is requested
    if (normalisedSum) {
      rIn2_tmp = terra::rast(rasterOutputTmp)
      rIn2_sum = terra::global(rIn2, "sum", na.rm = TRUE)
      rIn2_tmp = rIn2_tmp * (rIn2_sum$sum / terra::global(rIn2_tmp, "sum", na.rm = TRUE)$sum)
      terra::writeRaster(rIn2_tmp, rasterOutputTmp, overwrite=TRUE, 
                         gdal=c("NUM_THREADS=ALL_CPUS", "BIGTIFF=YES", "COMPRESS=PACKBITS"))
    }
    # Creating the .tif and compressing the file using gdal_translate
    gdalUtils::gdal_translate(rasterOutputTmp, rasterOutput, of="GTiff", tr=tr, projwin=projwin, projwin_srs=t_srs,
                              co=c("NUM_THREADS=ALL_CPUS", "BIGTIFF=YES", "COMPRESS=DEFLATE", "PREDICTOR=1", "ZLEVEL=9"))
    unlink(rasterOutputTmp)
    message("rasterInput was made compatible with rasterRef, named: ", rasterOutput); 
  } else { message("rasterInput is already compatible with rasterRef, nothing has been done."); }
  
  # Cleaning-up
  gc()
  
}
