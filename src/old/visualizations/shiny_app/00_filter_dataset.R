library(sf)
library(tidyverse)
library(jsonlite)

#Here i will actually have to put in as input the documents and merge their geo column from land parcels

metadata <- read_csv("../../../data/proc/building_plans/metadata/building_plans_metadata.csv")

geo_data <- read_sf("../../../data/final/bavaria_geodata.geojson")
