# Loading the required libraries
library(sf)
library(terra)
source("fRasterCompatible.R")
source("fVectorZonalStats.R")

# Creating the RWI raster
sFile = "tha_relative_wealth_index.csv"
sfRWI = read.csv(sFile) %>% st_as_sf(coords=c("longitude","latitude"), crs=4326)
write_sf(sfRWI, sub(".csv",".gpkg",sFile))
rRWI = terra::rasterize(sfRWI, rast(extent=ext(sfRWI), resolution=c(0.021972700, 0.021715400)), field="rwi")
rRWI_error = terra::rasterize(sfRWI, rast(extent=ext(sfRWI), resolution=c(0.021972700, 0.021715400)), field="error")
gdal = c("NUM_THREADS=ALL_CPUS", "BIGTIFF=YES", "COMPRESS=DEFLATE", "PREDICTOR=1", "ZLEVEL=9")
writeRaster(rRWI, sub(".csv","_rwi.tif",sFile), overwrite=TRUE, gdal=gdal)
writeRaster(rRWI_error, sub(".csv","_error.tif",sFile), overwrite=TRUE, gdal=gdal)

# Making RWI compatible with the pop layer
sPop = "THA_GHSPOP2020.tif"
fRasterCompatible(sub(".csv","_rwi.tif",sFile), sPop, sub(".tif","_RWI.tif",sPop), resampling_method="average")

# Normalising by ADM level POP
sADM = "THA_ADM2_FU_pop_GHSPOP2020_EAI_function.gpkg"
vADM = vect(sADM)
rRWI = rast(sub(".tif","_RWI.tif",sPop))
rPop = rast(sPop); rPop = classify(rPop, cbind(-Inf, 0, NA), right=TRUE)
rPopADM = rasterize(vADM, rPop, "ADM2_pop_GHSPOP2020")
rRWInorm = (rRWI*rPop) / rPopADM
writeRaster(rRWInorm, sub(".tif","_RWInorm.tif",sPop), overwrite=TRUE, gdal=gdal)

# Aggregating by ADM level
fVectorZonalStats(sADM, sub(".tif","_RWInorm.tif",sPop), sub(".tif","_RWInorm",sPop), 
                  out_fieldname="rwi_mean", fFun="sum")
