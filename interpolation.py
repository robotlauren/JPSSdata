import numpy as np 
from time import time
from datetime import datetime
from scipy import spatial

global t_init 

def sort_dates(data):
	return sorted(data.iteritems(), key=lambda x: x[1]['time_num'])

def nearest_euclidean(lon,lat,lons,lats,bounds):
	vlon=np.reshape(lon,np.prod(lon.shape))
	vlat=np.reshape(lat,np.prod(lat.shape))
	rlon=np.zeros(vlon.shape)
	rlat=np.zeros(vlat.shape)
	for k in range(0,len(vlon)):
		if (vlon[k]>bounds[0]) and (vlon[k]<bounds[1]) and (vlat[k]>bounds[2]) and (vlat[k]<bounds[3]):
			dist=np.square(lons-vlon[k])+np.square(lats-vlat[k])
			ii,jj = np.unravel_index(dist.argmin(),dist.shape)
			rlon[k]=lons[ii,jj]
			rlat[k]=lats[ii,jj]
		else:
			rlon[k]=np.nan;
			rlat[k]=np.nan;	
	return (np.reshape(rlon,lon.shape),np.reshape(rlat,lat.shape))
	

def nearest_scipy(lon,lat,lons,lats,dub=np.inf):
	vlon=np.reshape(lon,np.prod(lon.shape))
	vlat=np.reshape(lat,np.prod(lat.shape))
	vlonlat=np.column_stack((vlon,vlat))
	vlons=np.reshape(lons,np.prod(lons.shape))
	vlats=np.reshape(lats,np.prod(lats.shape))
	vlonlats=np.column_stack((vlons,vlats))
	inds=spatial.cKDTree(vlonlats).query(vlonlat,distance_upper_bound=dub)[1]
	ii=(inds!=vlons.shape[0])
	ret=np.empty((vlon.shape[0],2))
	ret[:]=np.nan
	ret[ii]=vlonlats[inds[ii]]
	rlon=[x[0] for x in ret]
	rlat=[x[1] for x in ret]
	return (np.reshape(rlon,lon.shape),np.reshape(rlat,lat.shape))


if __name__ == "__main__":
	t_init = time()
	# Initialization of grids
	N=500
	(dx1,dx2)=(1,1)
	(dy1,dy2)=(3,3)
	x=np.arange(0,N,dx1)
	lons=np.repeat(x[np.newaxis,:],x.shape[0], axis=0)
	x=np.arange(0,N,dx2)
	lats=np.repeat(x[np.newaxis,:],x.shape[0], axis=0).transpose()
	bounds=[lons.min(),lons.max(),lats.min(),lats.max()]
	print 'bounds'
	print bounds
	print 'dim_mesh=(%d,%d)' % lons.shape
	y=np.arange(-N*1.432,2.432*N,dy1)
	lon=np.repeat(y[np.newaxis,:],y.shape[0], axis=0)
	y=np.arange(-N*1.432,2.432*N,dy2)
	lat=np.repeat(y[np.newaxis,:],y.shape[0], axis=0)
	print 'dim_data=(%d,%d)' % (lon.shape[0], lat.shape[0])

	# Result by Euclidean distance
	print '>>Euclidean approax<<'
	(rlon,rlat)=nearest_euclidean(lon,lat,lons,lats,bounds)
	rlon=np.reshape(rlon,np.prod(lon.shape))
	rlat=np.reshape(rlat,np.prod(lat.shape))
	vlonlatm=np.column_stack((rlon,rlat))
	print vlonlatm
	t_final = time()
	print 'Elapsed time: %ss.' % str(t_final-t_init)

	# Result by scipy.spatial.cKDTree function
	rx=np.sqrt(dx1**2+dx2**2)
	ry=np.sqrt(dy1**2+dy2**2)
	dub=max(rx,ry)
	(rlon,rlat)=nearest_scipy(lon,lat,lons,lats,dub)
	rlon=np.reshape(rlon,np.prod(lon.shape))
	rlat=np.reshape(rlat,np.prod(lat.shape))
	vlonlatm2=np.column_stack((rlon,rlat))
	print '>>cKDTree<<'
	print vlonlatm2
	t_ffinal = time()
	print 'Elapsed time: %ss.' % str(t_ffinal-t_final)

	# Comparison
	print 'Same results?'
	print (np.isclose(vlonlatm,vlonlatm2) | np.isnan(vlonlatm) | np.isnan(vlonlatm2)).all()

