# Utility functions that are used across multiple scripts
# Xue (Michelle) Li, xue.li@pnnl.gov
# Aug 2022, Jan 2023

from math import cos, asin, sqrt, pi
import pandas as pd

# The below two functions work together to calculate approximate pixel area (km2) for latlon grids
def latlonDist(lat1, lon1, lat2, lon2):
  p = pi/180
  a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
  return 12742 * asin(sqrt(a))
    
def pixelArea(arr):
	ix = int(arr.x.size/2)
	iy = int(arr.y.size/2)
	dx = latlonDist(arr.y.values[iy],arr.x.values[ix],arr.y.values[iy],arr.x.values[ix+1])
	dy = latlonDist(arr.y.values[iy],arr.x.values[ix],arr.y.values[iy+1],arr.x.values[ix])
	return dx*dy

def compareExt(h1,h0,threshold,mask):
	ext1 = h1>threshold
	ext0 = h0>threshold
	ext_diff = (ext1*10+ext0)*mask
	return ext_diff

# Overlay flood layer with NLCD
def overlayNLCD(flood,nlcd,ft_thresholds):	
	bbox = flood.rio.transform_bounds(nlcd.rio.crs)
	nlcd_sub = nlcd.rio.clip_box(*bbox)
	df = pd.DataFrame()
	for depth_ft in ft_thresholds:
		depth_m = depth_ft / 3.28084
		ext = (flood>depth_m).astype('b')
		ext_reproj = ext.rio.reproject_match(nlcd_sub,nodata=0)
		nlcd_flood = nlcd_sub.where(ext_reproj==1,0)
		values,counts = np.unique(nlcd_flood.values,return_counts=True)
		rec = {'threshold':depth_ft,
					 'nlcd':values,
					 'counts':counts
					 }
		df = pd.concat([df,pd.DataFrame(rec)],ignore_index=True)
	return(df)

# Overlay flood layer with population
def overlayPop(flood,pop,ft_thresholds):	
	df = pd.DataFrame()
	for depth_ft in ft_thresholds:
		depth_m = depth_ft / 3.28084
		ext = (flood>depth_m).astype('b')
		ext_reproj = ext.rio.reproject_match(pop,nodata=0)
		pop_flood = pop.where(ext_reproj==1,0)
		rec = {'threshold':depth_ft,
					 'pop':pop_flood.sum().item()
					 }
		df = pd.concat([df,pd.DataFrame(rec,index=[0])],ignore_index=True)
	return(df)
