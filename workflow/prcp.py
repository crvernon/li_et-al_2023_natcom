from pathlib import Path
import rioxarray

data_folder = Path("../data/prcp/original")
output_folder = Path("../data/prcp")

# original QPE hourly data
filenames = list(data_folder.glob("*.tif"))

# sum all 48 hours
for i,f in enumerate(filenames):
	data = rioxarray.open_rasterio(f)
	data_nona = data.where(data!=data.rio.nodata,0)
	if i==0:
		result = data_nona
	else:
		result = result+data_nona
		
# write
result.rio.set_nodata(0).rio.to_raster(output_folder/'present_prcp_total.tif')
