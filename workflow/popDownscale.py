# Downscale LANDSCAN 90m data to 30m
# using NLCD Imperviousness
# Xue Li, xue.li@pnnl.gov
# Jan. 2023, Aug. 2022

from pathlib import Path
import numpy as np
import xarray as xr
import rioxarray as rio
import geopandas as gpd

base_fd = Path('../data/impact')
output_fd = base_fd/'population/downscaled'
landscan = rio.open_rasterio(base_fd/'population/landscan/conus_night.tif')
imperv = rio.open_rasterio(f'zip://{str(base_fd)}/landcover/nlcd/nlcd_2019_impervious_descriptor_l48_20210604.zip!nlcd_2019_impervious_descriptor_l48_20210604.img')
gpd_domain = gpd.read_file(base_fd.parent/'support/domain.shp')

def expand2dArray(arr,scale):
	# build fine grid
	nx = arr.x.size
	ny = arr.y.size
	x0 = arr.x.values[0]
	y0 = arr.y.values[0]
	dx = arr.x.values[1]-x0
	dy = arr.y.values[1]-y0
	xs = [x0+i*dx/scale for i in range(0,nx*scale)]
	ys = [y0+i*dy/scale for i in range(0,ny*scale)]
	grid_fine = xr.DataArray(np.zeros((ny*scale,nx*scale)),coords=[ys,xs],dims=['y','x']).rio.write_crs(4269)
	arr_rep = np.repeat(np.repeat(arr,scale,axis=0),scale,axis=1)
	arr_fine = grid_fine.where(False,arr_rep.values)
	return arr_fine
	
def popDownscale(pop_sub,imperv,scale):	
	pop_fine = expand2dArray(pop_sub,scale)
	imperv_sub = imperv.rio.reproject_match(pop_fine).squeeze('band')
	# 24 - non-road mon-energy impervious, 25 - Microsoft buildings
	imperv_sub_bin = imperv_sub.where(False,0).where(imperv_sub!=24,1).where(imperv_sub!=25,1)
	imperv_total = imperv_sub_bin.coarsen(x=scale,y=scale).sum()
	total_fine = expand2dArray(imperv_total.where(imperv_total!=0,scale*scale),scale)
	bin_mod = expand2dArray(imperv_total.where(False,imperv_total==0),scale)
	pop_downscaled = pop_fine*(imperv_sub_bin.values+bin_mod.values)/total_fine.values
	return(pop_downscaled)

for i,unit in gpd_domain.iterrows():
	print(unit.HUC4)
	pop = landscan.where(landscan!=landscan.rio.nodata,0).rio.clip_box(*unit.geometry.bounds)
	output = popDownscale(pop.squeeze('band'),imperv,3)
	output.rio.to_raster(output_fd/f'{unit.HUC4}.tif',compress='deflate')




