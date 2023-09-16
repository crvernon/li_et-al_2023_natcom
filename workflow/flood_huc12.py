# Summarize flood characteristics by huc12
# Xue (Michelle) Li, Jan 2023

from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rioxarray as rio

dry_threshold = 0.15
gdf_huc12 = gpd.read_file('../data/support/huc12.shp')
domains = ['0108','0109','0110','0202','0203','0204','0205','0206','0207']
versions = ['present','p7','p14','f7','f14']

# base paths
input_fd = Path('../data/flood')
output_fd = Path('../data/flood/huc12')
'''
# summarize flood characteristics for all simulations
def zonalStats(h,dhdt,he,zones,mask,threshold):
	metrics_df = pd.DataFrame()
	for i,z in zones.iterrows():
		#print(z.huc12)
		geo = z.geometry
		if geo.geom_type=='MultiPolygon':
			geos = geo.geoms
		else:
			geos = [geo]
		try:
			h_sub = h.squeeze('band').rio.clip(geos)
		except:
			print(f"No overlapping with {z.huc12}, skip")
			continue	
		mask_sub = mask.squeeze('band').rio.clip(geos)
		mask_flood = (h_sub>threshold) * mask_sub
		if mask_flood.sum().item() == 0:
			print(f"No flood detected in {z.huc12}, skip")
			metrics = {'huc12':z.huc12,
				       'n':int(mask_sub.sum().item()),
				       'wet':0,               
				       'h':0,
				       'dhdt':0,
				       'he':0}  
		else:
			dhdt_sub = dhdt.squeeze('band').rio.clip(geos)
			he_sub = he.squeeze('band').rio.clip(geos)		
			metrics = {'huc12':z.huc12,
						     'n':int(mask_sub.sum().item()),
						     'wet':int(mask_flood.sum().item()),               
						     'h':np.nanmean(h_sub.where(mask_flood.values==1,np.nan)),
						     'dhdt':np.nanmean(dhdt_sub.where(mask_flood.values==1,np.nan)),
						     'he':np.nanmean(he_sub.where(mask_flood.values==1,np.nan))}               
		metrics_df = pd.concat([metrics_df,pd.DataFrame(metrics,index=[z['index']])])
	return metrics_df

# loop
for v in versions:
	print(v,flush=True)
	outf = output_fd/f'{v}.csv'
	output = pd.DataFrame()
	for domain in domains:
		print(domain,flush=True)
		zones = gdf_huc12[gdf_huc12.huc4==domain]
		mask = rio.open_rasterio(input_fd/'water_mask'/f'{domain}_60.tif')
		h = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_h.tif')
		dhdt = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_dhdt.tif')
		he = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_he.tif')
		df = zonalStats(h,dhdt,he,zones,mask,dry_threshold)
		output = pd.concat([output,df])
	output.to_csv(outf)
'''
# calculate differences
def zonalStatsDiff(h_diff,dhdt_diff,he_diff,ext_diff,zones,mask):
	metrics_df = pd.DataFrame()
	for i,z in zones.iterrows():
		#print(z.huc12)
		geo = z.geometry
		if geo.geom_type=='MultiPolygon':
			geos = geo.geoms
		else:
			geos = [geo]
		try:
			h_sub = h_diff.squeeze('band').rio.clip(geos)
		except:
			print(f"No overlapping with {z.huc12}, skip")
			continue	
		mask_sub = mask.squeeze('band').rio.clip(geos)
		ext_sub = ext_diff.squeeze('band').rio.clip(geos)
		mask_flood = (ext_sub>0)
		if mask_flood.sum().item() == 0:
			#print(f"No flood detected in {z.huc12}, skip")
			metrics = {'huc12':z.huc12,
				       'n':int(mask_sub.sum().item()),
				       'over':0, 
				       'under':0,              
				       'h':0,
				       'dhdt':0,
				       'he':0}  
		else:
			dhdt_sub = dhdt_diff.squeeze('band').rio.clip(geos)
			he_sub = he_diff.squeeze('band').rio.clip(geos)		
			metrics = {'huc12':z.huc12,
						     'n':int(mask_sub.sum().item()),
						     'over':int((ext_sub==10).sum().item()), 
						     'under':int((ext_sub==1).sum().item()),              
						     'h':np.nanmean(h_sub.where(mask_flood.values==1,np.nan)),
						     'dhdt':np.nanmean(dhdt_sub.where(mask_flood.values==1,np.nan)),
						     'he':np.nanmean(he_sub.where(mask_flood.values==1,np.nan))}               
		metrics_df = pd.concat([metrics_df,pd.DataFrame(metrics,index=[z['index']])])
	return metrics_df

def compareExt(h1,h0,threshold,mask):
	ext1 = h1>threshold
	ext0 = h0>threshold
	ext_diff = (ext1*10+ext0)*mask
	return ext_diff

# loop
for v in versions[1:5]:
	print(v,flush=True)
	outf = output_fd/f'diff_{v}.csv'
	output = pd.DataFrame()
	for domain in domains:
		print(domain,flush=True)
		zones = gdf_huc12[gdf_huc12.huc4==domain]
		mask = rio.open_rasterio(input_fd/'water_mask'/f'{domain}_60.tif')
		h = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_h.tif')
		dhdt = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_dhdt.tif')
		he = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_{v}_he.tif')
		h_ref = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_present_h.tif')
		dhdt_ref = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_present_dhdt.tif')
		he_ref = rio.open_rasterio(input_fd/'RIFT_results'/f'{domain}_60_present_he.tif')
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
		df = zonalStatsDiff(h_diff,dhdt_diff,he_diff,ext_diff,zones,mask)
		output = pd.concat([output,df])
	output.to_csv(outf)
