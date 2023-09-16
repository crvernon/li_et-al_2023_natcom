# Summarize flood characteristics by huc4
# Xue (Michelle) Li, xue.li@pnnl.gov
# Jan 2023

from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rioxarray as rio
from utility import *

dry_threshold = 0.15
domains = ['0108','0109','0110','0202','0203','0204','0205','0206','0207']
versions = ['present','p7','p14','f7','f14']

# base paths
input_fd = Path('../data/flood')
output_fd = Path('../data/flood/huc4')


# main process
metrics_df = pd.DataFrame()
metrics_diff_df = pd.DataFrame()
# loop
for domain in domains:
	print(domain,flush=True)
	for v in versions:
		print(v,flush=True)
		mask = rio.open_rasterio(input_fd/'water_mask'/f'{domain}_60.tif')
		h = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_h.tif')
		dhdt = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_dhdt.tif')
		he = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_he.tif')
		mask_flood = (h>dry_threshold) * mask
		unit_area = pixelArea(h)
		metrics = {'huc4':domain,
					     'version':v,
					     'n':int(mask.sum().item()),
					     'wet':int(mask_flood.sum().item()),
					     'unit_area':unit_area,              
					     'h':np.nanmean(h.where(mask_flood.values==1,np.nan)),
					     'dhdt':np.nanmean(dhdt.where(mask_flood.values==1,np.nan)),
					     'he':np.nanmean(he.where(mask_flood.values==1,np.nan))}     
		print(metrics,flush=True)          
		metrics_df = pd.concat([metrics_df,pd.DataFrame(metrics,index=[f'{domain}_{v}'])])
		if v=='present': #present scenarios
			h_ref = h
			dhdt_ref = dhdt
			he_ref = he
		else:
			if v.startswith('f'): #future scenarios
				h_diff = h-h_ref
				he_diff = he - he_ref
				dhdt_diff = dhdt - dhdt_ref
				ext_diff = compareExt(h,h_ref,dry_threshold,mask)
			else: # past scenarios
				h_diff = h_ref - h
				he_diff = he_ref - he
				dhdt_diff = dhdt_ref - dhdt
				ext_diff = compareExt(h_ref,h,dry_threshold,mask)
			mask_flood = ext_diff>0
			metrics_diff = {'huc4':domain,
						     'version':v,
						     'n':int(mask.sum().item()),
						     'over':int((ext_diff==10).sum().item()),               
						     'under':int((ext_diff==1).sum().item()), 
						     'unit_area':unit_area,
						     'h':np.nanmean(h_diff.where(mask_flood.values==1,np.nan)),
						     'dhdt':np.nanmean(dhdt_diff.where(mask_flood.values==1,np.nan)),
						     'he':np.nanmean(he_diff.where(mask_flood.values==1,np.nan))}    
			print(metrics_diff,flush=True)
			metrics_diff_df = pd.concat([metrics_diff_df,pd.DataFrame(metrics_diff,index=[f'{domain}_{v}'])]) 

metrics_df.to_csv(output_fd/'flood.csv')
metrics_diff_df.to_csv(output_fd/'diff.csv')
