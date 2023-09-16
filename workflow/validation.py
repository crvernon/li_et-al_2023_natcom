# Validate Ida present runs against high water marks
# Xue (Michelle) Li, xue.li@pnnl.gov
# Feb. 2023, Oct. 2022

from pathlib import Path
import rioxarray as rio
import pandas as pd
import geopandas as gpd

flood_folder = Path('../data/flood/')

# read HWM
hwm_df = pd.read_csv(base_folder/'validation/hwm_312.csv').query('hwm_environment=="Riverine"')
hwm_gdf = gpd.GeoDataFrame(hwm_df,geometry=gpd.GeoSeries.from_xy(hwm_df['longitude_dd'],hwm_df['latitude_dd']),crs=4269)

# domains
domain_gdf = gpd.read_file('../data/support/domain.shp')
hwm_domain = hwm_gdf.sjoin(domain_gdf[['HUC4','geometry']],how='inner')

# extract RIFT water surface elevation values at HWM points
output = gpd.GeoDataFrame()
for huc_id in hwm_domain.HUC4.unique():
	print(huc_id)
	rift_wse = rio.open_rasterio(flood_folder/f'RIFT_results/{huc_id}_60_present_wse.tif')
	hwm_sub = hwm_domain.loc[hwm_domain.HUC4==huc_id]
	wse = []
	for i,pt in hwm_sub.iterrows():
		wse.append(rift_wse.sel(x=pt.longitude_dd,y=pt.latitude_dd,method='nearest').values[0])
	hwm_sub.insert(0,'rift_wse',wse)
	output = pd.concat([output,hwm_sub])
	
output.to_csv(flood_folder/'validation/hwm_rift.csv')	

