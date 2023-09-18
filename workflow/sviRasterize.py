# Rasterize SVI polygon data to match downscaled population grid,
# using total vulnerability score (RPL_THEMES)
# Xue Li, xue.li@pnnl.gov
# Jan. 2023, Aug. 2022


from pathlib import Path
import rasterio
from rasterio import features
import geopandas as gpd

base_fd = Path('../data/impact/population')

svi_fn = base_fd/'svi/SVI2020_US.zip'
svi_gdf = gpd.read_file(f'zip://{str(svi_fn)}')

pop_fns = list((base_fd/'downscaled').glob('*.tif'))
for f in pop_fns:
	print(f)		
	vector = ((geom,value) for geom,value in zip(svi_gdf.geometry,svi_gdf.RPL_THEMES))	
	with rasterio.open(f,'r') as src:
		meta = src.meta.copy()
		meta['compress'] = 'deflate'
		svi = features.rasterize(vector,out_shape=src.shape,transform=src.transform,fill=0)
		outf = base_fd/'svi'/f.name
		with rasterio.open(outf,'w',**meta) as dst:
			dst.write(svi,1)

