# summarise population exposure by svi and depth
# Xue Li, xue.li@pnnl.gov
# Feb 2023, Oct 2022
from pathlib import Path
import rioxarray as rio
import pandas as pd
import numpy as np
from utility import *

flood_fd = Path('../data/flood/')
pop_fd = Path('../data/impact/population/')

domains = ['0108','0109','0110','0202','0203','0204','0205','0206','0207']
versions = ['present','p7','p14','f7','f14']
depth_thresholds = [0.5,1,2,3,4,6,8,12] # ft
svi_levels = [0,25,50,75]

# loop through hucs
output = pd.DataFrame()
output_bg = pd.DataFrame()
for huc in domains:
	print(huc)
	pop = rio.open_rasterio(pop_fd/'downscaled'/f'{huc}.tif')
	svi = rio.open_rasterio(pop_fd/'svi'/f'{huc}.tif')
	pop_dict = {'Lowest':pop.where(np.logical_and(svi.values>=0,svi.values<0.25),0),
							'Medium_low':pop.where(np.logical_and(svi.values>=0.25,svi.values<0.5),0),
							'Medium_high':pop.where(np.logical_and(svi.values>=0.5,svi.values<0.75),0),
							'Highest':pop.where(np.logical_and(svi.values>=0.75,svi.values<1),0)}
	# summarize entire HUC
	mask = rio.open_rasterio(flood_fd/'water_mask'/f'{huc}_60.tif')
	mask_pop = mask.rio.reproject_match(svi,nodata=0)
	for key in pop_dict.keys():
		pop_total = pop_dict[key].where(mask_pop.values,0).sum().item()
		rec = pd.DataFrame({'svi':key,'pop':pop_total},
					index=[huc])
		output_bg = pd.concat([output_bg,rec])
	# loop through all flood scenarios
	for version in versions:
		print(version)
		fn = flood_fd/'RIFT_results'/f'{huc}_60_{version}_h.tif'
		flood = rio.open_rasterio(fn)	
		for key in pop_dict.keys():
			#print(key)
			pop_flood = overlayPop(flood*mask,pop_dict[key],depth_thresholds)
			pop_flood.insert(0,'huc4',huc)
			pop_flood.insert(0,'version',version)
			pop_flood.insert(0,'svi',key)
			output = pd.concat([output,pop_flood])

output.to_csv(pop_fd/'svi.csv')
output_bg.to_csv(pop_fd/'svi_bg.csv')





