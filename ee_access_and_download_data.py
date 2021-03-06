# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#
#!/usr/bin/python
#
#Script to access and downlaod data from Google Earth Engine.
#Landsat composite datasets for coastal changes studies.
#
#
# TODO:
#  - list landsat filter data by date steps
#
# Authors: Benoit Parmentier 
# Created on: 07/24/2017
# Updated on: 08/15/2017

import os, glob
import subprocess
import re, zipfile
import datetime, calendar
import ftplib
#import grass.script as gs
import argparse
import shutil
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst

import ee
import sys
import matplotlib.pyplot as plt
#import ee.mapclient #no access

################ NOW FUNCTIONS  ###################

##------------------
# Functions used in the script 
##------------------

#script_path = "/home/bparmentier/Google Drive/Data/SESYNC/earthengine_google/scripts" #bpi 
script_path ="/home/bparmentier/z_drive/Data/projects/earthengine_google/scripts" #bps 


if script_path not in sys.path:
    sys.path.append(script_path)

### Add scripts here
#from ee_acces_and_download_data_functions_07242017.py import *
from ee_access_and_download_data_functions import *

########## READ AND PARSE PARAMETERS AND ARGUMENTS ######### 

#in_dir = "/home/parmentier/Data/IPLANT_project/Maine_interpolation/DSS_SSI_data/"
in_dir ="/home/bparmentier/z_drive/Data/projects/earthengine_google/outputs" 
out_dir_google_drive = 'Data_SESYNC_earthengine'
#Input shape file used to define the zonal regions: could be town or counties in this context
shp_fname = os.path.join(in_dir,"county24.shp")
#input shp defining study area: can be the same as shp_fname or different                                       
shp_reg_outline = os.path.join(in_dir,"county24.shp")

#EPSG: http://spatialreference.org/ref/epsg/26919/proj4/ -->  

CRS_WGS84 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
#CRS_reg = "+proj=utm +zone=19 +ellps=GRS80 +datum=NAD83 +units=m +no_defs" #using EPSG 26919
CRS_reg = CRS_WGS84

file_format = ".tif"
NA_flag_val = -9999
output_type = "Float32"
out_suffix = "gee_08142017"

product_name = "LANDSAT/LT5_L1T_32DAY_TOA"
#product_name = "MODIS/MCD43A4_NDVI" #Image collection ID
#w_extent_str = "-72 48 -65 41" #minx,maxy (upper left), maxx,miny (lower right)
w_extent_str = "-80.25834 39.80676 -74.74974 35.56247"
#extent      : 1395375, 1805985, 1583085, 1986795  (xmin, xmax, ymin, ymax)
#extent      : -80.25834, -74.74974, 35.56247, 39.80676  (xmin, xmax, ymin, ymax)

max_pixels = 1000000000
scale = 30
use_reg_extent = True
os.chdir(in_dir)

out_dir = in_dir

#out_path<-"/data/project/layers/commons/data_workflow/output_data"
out_dir = "output_data_"+out_suffix
out_dir = os.path.join(in_dir,out_dir)
create_dir_and_check_existence(out_dir)
        
os.chdir(out_dir)        #set working directory

########## START SCRIPT #############


#### PART I: GET EXTENT FIRST

#Read in layers from data source,there is only one layer
#reg_area_poly = ogr.Open(shp_reg_outline).GetLayer()

#if use_reg_extent==True:
#    w_extent, reg_area_poly_wgs84 = calculate_region_extent(shp_reg_outline,out_suffix_dst,CRS_dst,out_dir)
#    #w_extent= "-71.083923738042 47.4598539782516 -66.8854440488051 42.9171281482886"
#elif use_reg_extent==False:
#    w_extent = w_extent_str #this is in WGS84
#    #end if
 
##### PART II :  ##########


ee.Initialize()

#### Let's use export to Google drive option

#https://explorer.earthengine.google.com/#detail/LANDSAT%2FLT5_L1T_TOA_FMASK
#USGS Landsat 5 TOA Reflectance (Orthorectified) with Fmask
#Data availability (time)
#Jan 1, 1984 - May 5, 2012
#https://explorer.earthengine.google.com/#detail/LANDSAT%2FLT5_L1T_ANNUAL_TOA
#32 days TOA or 

# Load a landsat image and select three bands.
#img_col_landsat = ee.ImageCollection('LANDSAT/LT5_L1T_ANNUAL_TOA')
#img_collection = ee.ImageCollection("LANDSAT/LT5_L1T_32DAY_TOA")
#img_collection = ee.ImageCollection("MODIS/MCD43A4_NDVI")
img_collection = ee.ImageCollection(product_name)
### Get elevation data for example:
#image = ee.Image('CGIAR/SRTM90_V4');

info_obj= img_collection.getInfo()
info_obj['type']
info_obj.keys()
print(info_obj)

img_collection = img_collection.filterDate('2002-01-01', '2003-01-01');

dates = ee.List(img_collection.get('date_range'));

dateRange = ee.DateRange(dates.get(0), dates.get(1));
print('Date range: ', dateRange);

size = img_collection.toList(100).length();
number_img =size.getInfo() #use getInfo if in python!!!

print("Number of image in the collection:" ,number_img)

list_img = img_collection.toList(100);
#list_img[0]

image = ee.Image(ee.List(list_img).get(0)) #select first image
image1 = ee.Image(ee.List(list_img).get(1))

time0 = img_collection.first().get('system:time_start');

#landsat = ee.Image('LANDSAT/LT5_L1T_32DAY_TOA')
#landsat.select(['B4', 'B3', 'B2']) #Green (B1), Red (B2), B3 (NIR), B
#landsat.select(['B1'])

#landsat.getInfo()

image_info = image.getInfo() #this is a dict

print "image_info['bands']: ", image_info['bands']
list_bands_info = image_info['bands']

type(list_bands_info[0])

date0 = image_info['properties']['system:index']

# Create a geometry representing an export region.


# Export the image, specifying scale and region.

#llx = -80.25834 #minx
#lly = 35.56247 #ymin
#urx = -74.74974 #xmax
#ury = 39.80676 #ymax

w_extent = w_extent_str.split() #split string into a list

llx = float(w_extent[0])#minx
lly = float(w_extent[3]) #ymin
urx = float(w_extent[2]) #xmax
ury = float(w_extent[1]) #ymax

#geometry_extent = [[llx,lly], [llx,ury], [urx,ury], [urx,lly]]
geometry_extent = [llx, lly, urx, ury]

#geometry = ee.Geometry.Rectangle([116.2621, 39.8412, 116.4849, 40.01236])
#geometry = ee.Geometry.Rectangle([-80.25834, 35.56247, -74.74974, 39.80676])
geometry = ee.Geometry.Rectangle(geometry_extent)
#geometry = ee.Geometry(geometry_extent)

geometry.getInfo()
type(geometry)
geometry_coordinates = geometry['coordinates'][0] #as list

##Export does not work with python api, need to use batch mode
scale= 1000 #for MODIS this should be 1000km
scale= 30 #for MODIS this should be 1000km

#Set the pixel max size
#Error: Export too large: specified 321945750 pixels (max: 100000000). Specify higher maxPixels value if you intend to export a large area.


### Make this loop a function!!!
### Make a functin and use map
for i in range(0,number_img):
    
    #image = ee.Image(ee.List(list_img).get(0)) #select first image
    image = ee.Image(ee.List(list_img).get(i)) #select first image
     
    date_val = image_info['properties']['system:index'] #get value

    dataset_name = os.path.basename(product_name)
    #out_filename = "".join([dataset_name,
    #                        "_"+str(scale),
    #                        "_"+str(i),
    #                        "_"+out_suffix,
    #                       file_format])
    #             #EEException: Invalid Drive file name prefix.
         
    out_filename = "".join([dataset_name,
                            "_"+date_val,
                            "_"+str(scale),
                            "_"+str(i),
                            "_"+out_suffix])

    #task = ee.batch.Export.image.toDrive(image=image,
    #                                 description="test_landsat",
    #                                 folder=out_dir_google_drive,
    #                                 region=geometry_coordinates,
    #                                 maxPixels=max_pixels,
    #                                 scale=scale)
                                     
    task = ee.batch.Export.image.toDrive(image=image,
                                     description=out_filename,
                                     folder=out_dir_google_drive,
                                     region=geometry_coordinates,
                                     maxPixels=max_pixels,
                                     scale=scale)
    
    task.start()

######################## END OF SCRIPT ##############

#https://blog.webkid.io/analysing-satellite-images-with-google-earth-engine/
#landsat = ee.Image('LANDSAT/LC8_L1T_TOA
#/LC81230322014135LGN00').select(['B4', 'B3', 'B2']);
#Create a geometry representing an export region.

#geometry = ee.Geometry.Rectangle([116.2621, 39.8412, 116.4849, 40.01236]);
#Export the image, specifying scale and region.

#export.image.toDrive({
#    image: landsat,
#    description: 'imageToDriveExample',
#    scale: 30,  
#    region: geometry
#    });

#img_col_landsat = ee.ImageCollection("LANDSAT/LT5_L1T_32DAY_TOA")


#var collection = ee.ImageCollection('LE7_L1T')
#    .filterDate('2000-04-01', '2000-07-01');
#var median = collection.median();
#var img_col_landsat = ee.ImageCollection("LANDSAT/LT5_L1T_32DAY_TOA")
#    img_col_landsat.
    
#// Clip to the output image to the Nevada and Arizona state boundaries.
#var fc = ee.FeatureCollection('ft:1fRY18cjsHzDgGiJiS2nnpUU3v9JPDc2HNaR7Xk8')
#    .filter(ee.Filter.or(
#         ee.Filter.eq('Name', 'Nevada'),
#         ee.Filter.eq('Name', 'Arizona')));
#var clipped = median.clipToCollection(fc);

#// Select the red, green and blue bands.
#var result = clipped.select('B3', 'B2', 'B1');
#Map.addLayer(result, {gain: '1.4, 1.4, 1.1'});
#Map.setCenter(-110, 40, 5);
