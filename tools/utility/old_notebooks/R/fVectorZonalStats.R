################################################################################
####################### fVectorZonalStats R Function ###########################
################################################################################
# This script contains a function to compute the zonal statistics of a polygon 
#   vector layer over a raster layer.
# This function uses the exact_extract function from exactextractr library
#
# Parameters:
#   vectorInput is the path to the input vector file
#   layer is the name of the layer to be imported, important only for gpkg filetype
#   out_fieldname is the output field name to be created
#   fFun is the function for aggregation and calculation. Available are:
#       min                      - the minimum defined value in any raster cell wholly or partially covered by the polygon
#       max                      - the maximum defined value in any raster cell wholly or partially covered by the polygon
#       count                    - the sum of fractions of raster cells with defined values covered by the polygon
#       sum                      - the sum of defined raster cell values, multiplied by the fraction of the cell that is covered by the polygon
#       mean                     - the mean cell value, weighted by the fraction of each cell that is covered by the polygon
#       median                   - the median cell value, weighted by the fraction of each cell that is covered by the polygon
#       quantile                 - arbitrary quantile(s) of cell values, specified in quantiles, weighted by the fraction of each cell that is covered by the polygon
#       mode                     - the most common cell value, weighted by the fraction of each cell that is covered by the polygon. Where multiple values occupy the same maximum number of weighted cells, the largest value will be returned.
#       majority                 - synonym for mode
#       minority                 - the least common cell value, weighted by the fraction of each cell that is covered by the polygon. Where multiple values occupy the same minimum number of weighted cells, the smallest value will be returned.
#       variety                  - the number of distinct values in cells that are wholly or partially covered by the polygon.
#       variance                 - the population variance of cell values, weighted by the fraction of each cell that is covered by the polygon.
#       stdev                    - the population standard deviation of cell values, weighted by the fraction of each cell that is covered by the polygon.
#       coefficient_of_variation - the population coefficient of variation of cell values, weighted by the fraction of each cell that is covered by the polygon.
#       weighted_mean            - the mean cell value, weighted by the product of the fraction of each cell covered by the polygon and the value of a second weighting raster provided as weights
#       weighted_sum             - the sum of defined raster cell values, multiplied by the fraction of each cell that is covered by the polygon and the value of a second weighting raster provided as weights
#   vWeights is the vector weights for weighted_mean or weighted_sum
#
# Author: Arthur Hrast Essenfelder
# E-mail: arthur.essenfelder@gmail.com
# 
# Version: 1.0
# Last update on: 11/12/2019
# Last modified by: Arthur Hrast Essenfelder
################################################################################
################################################################################

# Function to compute the zonal statistics over a raster layer
fVectorZonalStats = function(vectorInput, rasterInput, vectorOutput, layer=NULL, 
                             out_fieldname=NULL, fFun, vWeights=NULL, 
                             parallel=FALSE, nCores=1, verbose=FALSE) {
  
  # Getting file extension of vectorInput and the respective OSG driver 
  fExt = substr(vectorInput, nchar(vectorInput)-3, nchar(vectorInput))
  if (fExt == "gpkg") { fExt = paste(".",fExt,sep=""); driver = "GPKG" }
  if (fExt == ".shp") { driver = "ESRI Shapefile" }
  
  # Checking for missing parameters
  if (missing(vectorOutput))  { vectorOutput = sub(fExt, "_ZStats", vectorInput) }
  if (missing(out_fieldname)) { out_fieldname = "Z"; }
  if (missing(fFun))          { fFun = "mean"; }
  
  # Loading required libraries
  library(sf)
  library(exactextractr)
  library(raster); rasterOptions(chunksize=1e+07, maxmem=Inf, memfrac=.8)
  library(parallel); if (missing(nCores)) { nCores = detectCores()-1 }
  if (nCores > detectCores()) { nCores = detectCores() }
  
  # Getting vectorInput data 
  if (verbose) { message("  Reading vectorInput file...") }
  if (!is.null(layer)) { vInput = read_sf(vectorInput, layer=layer) }
  if (is.null(layer))  { vInput = read_sf(vectorInput) }
  
  # Reading the rasterInput file
  if (verbose) { message("  Reading rasterInput file...") }
  rInput = raster(rasterInput)
  
  # Checking if parallel processing or single core
  if (parallel) {
    if (verbose) { message("  Preparing vectorInput for parallel processing...") }
    # Splitting vInput into equal parts for parallel processing
    n = ceiling(NROW(vInput) / nCores)
    vInputPar = split(vInput, rep(1:ceiling(NROW(vInput)/n), each=n, length.out=NROW(vInput)))
    # Creating the parallel-friendly function for exact_extract
    exact_extractPar = function(y, x, fun, weights, verbose) { exact_extract(x=x, y=y, fun=fun, weights=weights, progress=verbose) }
    # Computing the Zonal Statistics
    if (verbose) { message("  Computing the zonal statistics in parallel mode...") }
    Z = mclapply(vInputPar, exact_extractPar, x=rInput, fun=fFun, weights=vWeights, progress=verbose, mc.cores=nCores)
    rm(vInputPar); gc()
    Z = as.numeric(as.character(unlist(Z)))
  } else {
    # Computing the Zonal Statistics
    if (verbose) { message("  Computing the zonal statistics...") }
    Z = exact_extract(rInput, vInput, fun=fFun, weights=vWeights, progress=verbose)
  }
  
  # Merging the results to a new vector file
  if (verbose) { message("  Consolidating the zonal statistics results...") }
  vOutput = cbind(vInput, Z)
  st_crs(vOutput) = projection(rInput)
  
  # Saving the results to the disk
  if (verbose) { message("  Saving the results to the disk...") }
  names(vOutput)[names(vOutput)=="Z"] = out_fieldname
  sSplitVectorOutput = strsplit(vectorOutput, "/")[[1]]
  if (length(sSplitVectorOutput) > 1) {
    sPath = paste(sSplitVectorOutput[1:(length(sSplitVectorOutput)-1)], collapse="/")
    sFile = sSplitVectorOutput[length(sSplitVectorOutput)]
  } else {
    sPath = "."
    sFile = vectorOutput
  }
  if (fExt == ".gpkg") { sFile = paste(sPath,"/",sFile,".gpkg",sep=""); write_sf(vOutput, sFile, driver = driver) }
  if (fExt == ".shp")  { write_sf(vOutput, dsn = sPath, layer = sFile, driver = driver) }
  
  # Cleaning-up
  rm(vInput, rInput, Z, vOutput); gc()
  
}