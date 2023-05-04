# This script is used to generate bivariate risk-poverty maps. For more details, check the CCDR-tools documentation: https://gfdrr.github.io/CCDR-tools/docs/risk-poverty.html

# Loading the required libraries
library(sf)
library(biscale)
library(ggplot2)
library(cowplot)
library(caret)
library(stringr)
library(knitr)
library(ggrepel)

# Select bivariate plot type - either quantile or manual classes
#sPlotType = "quantile"
sPlotType = "user-defined"

# Select bivariate plot color
sColor = "DkViolet2" # Standard: DkViolet; other: "Bluegill", "BlueGold", "BlueOr", 
# "BlueYl", "Brown"/"Brown2", "DkBlue"/"DkBlue2", "DkCyan"/"DkCyan2", 
# "DkViolet"/"DkViolet2", "GrPink"/"GrPink2", "PinkGrn", "PurpleGrn", or "PurpleOr"
sColor = c(
  "1-1" = "#f2e6da", # f2e6da low poverty, low hazard
  "2-1" = "#ecd28f", # ecd28f
  "3-1" = "#d4ac48", # daa520 high poverty, low hazard
  "1-2" = "#7f7fff", # 7f7fff
  "2-2" = "#b66987", # b66987 medium poverty, medium hazard
  "3-2" = "#c2572b", # ec5210
  "1-3" = "#3636e0", # 0000ff low poverty, high hazard
  "2-3" = "#781f78", # 7f007f
  "3-3" = "#cf2121"  # ff0000 high poverty, high hazard
)
sColor = bi_pal(pal = sColor, dim = 3, preview = FALSE)

# Loading the spatial file (updated) and defining the name of the column with the poverty data
sfPoverty = read_sf("IND_RWI.gpkg", "IND_RWI_ADM2")
sColPov   = "rwi_mean"
sfPoverty$tmpColPov = -1*sfPoverty[[sColPov]] # inverting RWI so higher values indicate higher poverty
# Hcr_upper (%)  -> Head count rate(index) in percent using upper poverty lines. 
# Se_upper (%)   -> Standard error of the poverty estimates in percent using upper poverty lines . 
# Status (code)  -> A : affected upazila/thana (some parts of this upazila were removed and included in the newly created upazila/thana). 
#                -> N : newly created upazila/thana 
#                -> O : original/old upazila/thana

# Defining the data files to be processed
sFileCSV = "IND_ADM2_RSK.csv"
dfHazard = read.csv(sFileCSV, header = TRUE, dec=".")
#dfHazard = read.table(sFileCSV, header=TRUE, sep=",", dec=".", stringsAsFactors=F, na.strings=c("", "-"))
# names(dfHazard)[1:6] = c("ID_0","ID_1","ID_2","NAME_0","NAME_1","NAME_2")

# Merging impact data with poverty data
dfResults = merge(sfPoverty, dfHazard, all.x=TRUE, 
                  by=c("ADM0_CODE","ADM1_CODE","ADM2_CODE","ADM0_NAME","ADM1_NAME","ADM2_NAME"))
                  #by=c("ADM0_CODE","ADM1_CODE","ADM2_CODE","ADM3_CODE","ADM0_NAME","ADM1_NAME","ADM2_NAME","ADM3_NAME"))

# Manually defining the column name, threshold, title, subtitle, type of analysis, file name
colNames = c("FLU_pop_GHSPOP2020_EAI",           # Expected mortality from river floods (population count)
             "FLU_builtup_WSF19_EAI",            # Expected damage on builtup from river floods (hectares)
             "FLU_agri_ESA21_agri_C1_EAE",       # Expected damage on agricultural land from river floods (hectares)
             "CF_pop_GHSPOP2020_EAI",            # Expected mortality from coastal floods (population count)
             "CF_builtup_WSF19_EAI",             # Expected damage on builtup from coastal floods (hectares)
             "CF_agri_ESA21_agri_C1_EAE",        # Expected damage on agricultural land from coastal floods (hectares)
             "LS_pop_GHSPOP2020_C2_exp",         # Population exposed to high landslide hazard (population count)
             "LS_builtup_WSF19_C2_exp",          # Builtup exposed to high landslide hazard (Builtup count)
             "TC_pop_GHSPOP2020_C4_EAE",         # Expected population exposed to tropical cyclones winds (population count)
             "TC_builtup_WSF19_C4_EAE",          # Expected builtup exposed to tropical cyclones winds (hectares)
             "TC_agri_ESA21_agri_C4_EAE",        # Expected agricultural land to tropical cyclones winds (hectares)
             "DR.S1.30p_agri_ESA21_agri_C3_exp", # Agricultural land exposed to drought affecting at least 30% of arable land during growing season 1 at 25% frequency during period 1984-2022 (hectares)
             #"DR.S1.50p_agri_ESA20_agri_freq",   # Agricultural land exposed to drought affecting at least 50% of arable land during growing season 1 at 25% frequency during period 1984-2022 (hectares)
             "HS_pop_GHSPOP2020_C3_EAE",         # Expected population exposed to very strong heat stress hazard (population count)
             "AP_pop_GHSPOP2020_C4_exp")         # Expected population exposed to high air pollution hazard (population count)
sTitles = c("River Flooding: Impact on Population and Poverty", 
            "River Flooding: Impact on Built-Up Assets and Poverty", 
            "River Flooding: Exposure of Agricultural Land and Poverty", 
            "Coastal Flooding: Impact on Population and Poverty", 
            "Coastal Flooding: Impact on Built-Up Assets and Poverty", 
            "Coastal Flooding: Exposure of Agricultural Land and Poverty", 
            "Landslides: Exposure of Population and Poverty", 
            "Landslides: Exposure of Built-Up Assets and Poverty",
            "Tropical Cyclone: Exposure of Population and Poverty", 
            "Tropical Cyclone: Exposure of Built-Up Assets and Poverty", 
            "Tropical Cyclone: Exposure of Agricultural Land and Poverty", 
            "Drought: S1 Agricultural Land Exposure and Poverty",
            #"Drought: S2 Agricultural Land Exposure and Poverty",
            "Heat Stress: Exposure of Population and Poverty", 
            "Air Pollution: Exposure of Population and Poverty")
sSubTitles = c("EAI classes: <'tv1' people, 'tv1'-'tv2' people, >'tv2' people", 
               "EAI classes: <'tv1'ha, 'tv1'-'tv2'ha, >'tv2'ha",
               "EAE classes: <'tv1'ha, 'tv1'-'tv2'ha, >'tv2'ha", 
               "EAI classes: <'tv1' people, 'tv1'-'tv2' people, >'tv2' people", 
               "EAI classes: <'tv1'ha, 'tv1'-'tv2'ha, >'tv2'ha",
               "EAE classes: <'tv1'ha, 'tv1'-'tv2'ha, >'tv2'ha", 
               "EAE classes: <'tv1' people, 'tv1'-'tv2' people, >'tv2' people", 
               "EAE classes: <'tv1'ha, 'tv1'-'tv2'ha, >'tv2'ha",
               "EAE classes: <'tv1' peopla, 'tv1'-'tv2' people, >'tv2' people", 
               "EAE classes: <'tv1'ha, 'tv1'-'tv2'ha, >'tv2'ha", 
               "EAE classes: <'tv1'ha, 'tv1'-'tv2'ha, >'tv2'ha", 
               "Exposure classes: <'tv1'% of years, 'tv1'-'tv2'% of years, >'tv2'% of years", 
               #"Exposure classes: <'tv1'% of years, 'tv1'-'tv2'% of years, >'tv2'% of years",
               "EAE classes: <'tv1' people, 'tv1'-'tv2' people, >'tv2' people", 
               "EAE classes: <'tv1' people, 'tv1'-'tv2' people, >'tv2' people")
sAnalysisTypes = matrix(unlist(strsplit(sTitles, ": ")), nrow=length(sTitles), byrow=TRUE)[,2]
sAnalysisTypes = stringr::word(sAnalysisTypes, 1)
sFileNames = paste("bivariatePlot_", sPlotType, "_", colNames, ".png", sep="")
if (sPlotType == "quantile") { sSubTitles = rep("Quantile classes", length(sSubTitles))
} else if (sPlotType == "user-defined") {
  vThresholds = rbind(c(0.001, 20, 1000),          # FLU pop EAI - NA < 0.01; 1Class 0.01 e 1; 2Class 1 - 100; 3Class > 100
                      c(0.001, 10, 200),           # FLU builtup EAI
                      c(0.001, 1000, 20000),       # FLU agri
                      c(0.001, 5, 50),             # CF pop EAI
                      c(0.001, 1, 5),              # CF builtup EAI
                      c(0.001, 50, 500),           # CF agri
                      c(0.001, 5000, 200000),      # LS pop
                      c(0.001, 100, 1000),         # LS builtup
                      c(0.001, 100, 5000),         # TC pop
                      c(0.001, 1, 10),             # TC builtup
                      c(0.001, 10, 500),           # TC agri
                      c(0.001, 10000, 500000),     # DR.S1.30
                      #c(0.001, 20000, 500000),    # DR.S1.50
                      c(0.001, 100000, 1000000),   # HS pop
                      c(0.001, 1000000, 5000000))  # AP pop
  sThresholds = formatC(vThresholds, format="f", big.mark=",", digits=0)
  sThresholds[vThresholds<1] = vThresholds[vThresholds<1]
  for (i in 1:length((sSubTitles))) { sSubTitles[i] = gsub("'tv1'", sThresholds[i,2], sSubTitles[i]) }
  for (i in 1:length((sSubTitles))) { sSubTitles[i] = gsub("'tv2'", sThresholds[i,3], sSubTitles[i]) }
}

# Creating the maps for every colNames
for (i in 1:length(colNames)) {
  
  # Creating the classes for the bivariate maps
  if (sPlotType == "quantile") {
    dfResults$dataPlot = dfResults[[colNames[i]]]
    bvClasses = bi_class(dfResults, x=tmpColPov, y=dataPlot, style="quantile", dim=3)
  } else if (sPlotType == "user-defined") {
    bvClasses = bi_class(dfResults, x=tmpColPov, y=tmpColPov, style="quantile", dim=3)
    bvClasses[[colNames[i]]] = as.numeric(as.character(bvClasses[[colNames[i]]]))
    bvClasses$bi_class_tmp = 0
    bvClasses$bi_class_tmp[bvClasses[[colNames[i]]] <  vThresholds[i,2]] = "1"
    bvClasses$bi_class_tmp[bvClasses[[colNames[i]]] >= vThresholds[i,2]] = "2"
    bvClasses$bi_class_tmp[bvClasses[[colNames[i]]] >= vThresholds[i,3]] = "3"
    bvClasses$bi_class = substr(bvClasses$bi_class, 1, 2)
    bvClasses$bi_class = paste(bvClasses$bi_class, bvClasses$bi_class_tmp, sep="")
    bvClasses$bi_class[bvClasses[[colNames[i]]] < vThresholds[i,1]] = NA
    bvClasses$bi_class[is.na(bvClasses[[colNames[i]]])] = NA
  }
  
  # Creating the legend for the bivariate plot
  bvLegend = bi_legend(pal=sColor, dim=3, xlab="Higher poverty", ylab=paste("Higher",sAnalysisTypes[i]), size = 7)
  
  # Defining the top nADMs affected ADM units
  nADMs = 3
  # bvClasses[['top']] = (scale(rank(bvClasses[[colNames[i]]]))*as.numeric(substr(bvClasses$bi_class, start=1, stop=1))) + 
  #   (scale(rank(bvClasses$tmpColPov))*as.numeric(substr(bvClasses$bi_class, start=3, stop=3)))
  bvClasses[['top']] = (1.01*as.numeric(substr(bvClasses$bi_class, start=1, stop=1))) +
   (1.05*as.numeric(substr(bvClasses$bi_class, start=3, stop=3)))
  bvTopADM = bvClasses[order(bvClasses$top,decreasing=TRUE)[1:nADMs],,drop=FALSE]
  bvTopADM = cbind(bvTopADM,as.data.frame(sf::st_coordinates(sf::st_centroid(bvTopADM))))
  
  # Creating the map
  bvPlot = ggplot() + 
    geom_sf(data = bvClasses, mapping = aes(fill = bi_class),  color = "white", linewidth = 0.1, show.legend = FALSE) +
    geom_sf(data = bvTopADM, mapping = aes(fill = bi_class),  color = "black", linewidth = 0.6, show.legend = FALSE) +
    geom_text_repel(data = bvTopADM, aes(X, Y, label=ADM2_NAME), 
                    #force_pull=1.0, force=0.0, 
                    max.overlaps=Inf, max.time=1, max.iter=1e5,
                    segment.size=1, segment.color="black",
                    fontface="bold", size=3.4, colour="white", bg.colour="black", bg.r=.15) + 
    bi_scale_fill(pal = sColor, dim = 3) + 
    labs(title = sTitles[i], subtitle=sSubTitles[i], size=4, xlab="", ylab="") +
    bi_theme(base_size = 8) +
    theme(plot.subtitle=element_text(size=7), 
          axis.title.x = element_blank(), 
          axis.title.y = element_blank())
  
  # combine map with legend
  bvPlotLegend = ggdraw() + draw_plot(bvPlot, 0, 0, 1, 1) + draw_plot(bvLegend, 0.52, 0.10, 0.25, 0.25)
  
  # Save plot to disk
  ggsave(sFileNames[i], bvPlotLegend, width=2400, height=1500, dpi=280, units="px")
  knitr::plot_crop(sFileNames[i])
}

