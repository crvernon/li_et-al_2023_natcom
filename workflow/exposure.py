# Evaluate flood exposure with land cover and population
# Xue (Michelle) Li, xue.li@pnnl.gov
# Jan 2023, Nov 2022

from pathlib import Path
import rioxarray as rio
import pandas as pd
import numpy as np
from utility import *

domains = ['0108','0109','0110','0202','0203','0204','0205','0206','0207']
versions = ['present','p7','p14','f7','f14']
depth_thresholds = [0.5,1,2,3,4,6,8,12] # ft

# base paths
base_fd = Path('../data/impact')

# paths
nlcd_fn = f'zip://{str(base_fd)}/landcover/nlcd/nlcd_2019_land_cover_l48_20210604.zip!nlcd_2019_land_cover_l48_20210604.img'
pop_fd = base_fd/'population/downscaled'
flood_fd = base_fd.parent/'flood/RIFT_results'
flood_fns = list(flood_fd.rglob('*_h.tif'))

# process
nlcd = rio.open_rasterio(nlcd_fn)
df_nlcd = pd.DataFrame()
df_pop = pd.DataFrame()
for f in flood_fns:
	print(f,flush=True)
	huc = f.name[0:4]
	version = f.name.split('_')[2]
	flood = rio.open_rasterio(f)
	mask = rio.open_rasterio(base_fd.parent/f'flood/water_mask/{huc}_60.tif')
	flood_masked = flood*mask
	pop = rio.open_rasterio(pop_fd/f'{huc}.tif')
	# land cover
	nlcd_flood = overlayNLCD(flood_masked,nlcd,depth_thresholds)
	nlcd_flood.insert(0,'huc4',huc)
	nlcd_flood.insert(0,'version',version)
	df_nlcd = pd.concat([df_nlcd,nlcd_flood],ignore_index=True)
	# population
	pop_flood = overlayPop(flood_masked,pop,depth_thresholds)
	pop_flood.insert(0,'huc4',huc)
	pop_flood.insert(0,'version',version)
	df_pop = pd.concat([df_pop,pop_flood],ignore_index=True)

df_nlcd.to_csv(base_fd/'landcover/summary.csv')
df_pop.to_csv(base_fd/'population/summary.csv')


