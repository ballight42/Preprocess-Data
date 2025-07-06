import planetary_computer
import xarray
import pystac_client
from scipy.interpolate import griddata
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

c = catalog.get_collection("conus404")
asset = c.assets["zarr-abfs"]
ds = xarray.open_zarr(asset.href,storage_options=asset.extra_fields["xarray:storage_options"],
    **asset.extra_fields["xarray:open_kwargs"])

import numpy as np
import datetime
import os
def compute_coefficients(pstar: float, pressure: xarray.DataArray) -> xarray.Dataset:

    dlev = pstar - pressure
    dloglev = np.log(pstar) - np.log(pressure)

    # get coefficients representing pressure distance left and right of pstar
    is_left = dlev == dlev.where(dlev >= 0).min("bottom_top")
    is_right = dlev == dlev.where(dlev <= 0).max("bottom_top")

    p_left = dloglev.where(is_left).sum("bottom_top")
    p_right = -dloglev.where(is_right).sum("bottom_top")

    denominator = p_left + p_right
    denominator = denominator.where(denominator > 1e-6, 1e-6)
    factor = p_left / denominator
    return xarray.Dataset(
        {
            "is_left": is_left,
            "is_right": is_right,
            "p_left": p_left,
            "p_right": p_right,
            "denominator": denominator,
            "factor": factor,
        }
    )


def interp2pressure(xda, cds):
    """Interpolate xda to pressure level used to compute coefficients in ``cds``

    Args:
        xda (xarray.DataArray): with the field to be interpolated
        cds (xarray.Dataset): with the coefficients computed by compute_coefficients

    Returns:
        xda_at_pstar (xarray.DataArray): original field interpolated to desired
        pressure level
    """
    xda_left = xda.where(cds["is_left"]).sum("bottom_top")
    xda_right = xda.where(cds["is_right"]).sum("bottom_top")

    result = xda_left + (xda_right - xda_left) * cds["factor"]

    mask = (cds["is_right"].sum("bottom_top") > 0) & (
        cds["is_left"].sum("bottom_top") > 0
    )
    return result.where(mask)


# for 3-dimensional variables

# over the SE US
x_min,x_max,y_min,y_max=0,655,722,1366

import calendar
for iyr in range(2005,2013+1):
  for imon in [3] : # 3 for March. I only want it right now.
    # Get hourly files 
     
    days_in_month = calendar.monthrange(iyr, imon)[1]
    timearr=[datetime.datetime(iyr,imon,iday,ihr).strftime('%Y-%m-%dT%H') for ihr in [0,6,12,18] for iday in range(1,days_in_month+1)]

    '''
    
    for ilevel in [1000,925,850,700,600,500,400,300,200]:
      for iday in range(1,days_in_month+1):
        timearr=[datetime.datetime(iyr,imon,iday,ihr).strftime('%Y-%m-%dT%H') for ihr in [0,6,12,18]]
      
        filo='SEUS.3d.{:d}hPa.{:04d}.{:02d}.{:02d}.6hr.nc'.format(ilevel,iyr,imon,iday)
        print(filo)
        if os.path.exists(filo):continue
        cds = compute_coefficients(pstar=ilevel*100,pressure=ds["P"].sel(time=timearr).isel(south_north=slice(x_min,x_max,10),west_east=slice(y_min,y_max,10)).load())
        for var in ['V','U','QVAPOR']:
            if os.path.exists(filo):continue
            if var=='V':
                vtemp = interp2pressure(ds[var].sel(time=timearr).isel(south_north_stag=slice(x_min,x_max,10),west_east=slice(y_min,y_max,10)).load(), cds)
            elif var=='U':
                utemp = interp2pressure(ds[var].sel(time=timearr).isel(south_north=slice(x_min,x_max,10),west_east_stag=slice(y_min,y_max,10)).load(), cds)
            else:
                temp = interp2pressure(ds[var].sel(time=timearr).isel(south_north=slice(x_min,x_max,10),west_east=slice(y_min,y_max,10)).load(), cds)
        subds = xarray.Dataset({'QVAPOR':temp,'U':utemp,'V':vtemp},coords={**temp.coords,**utemp.coords,**vtemp.coords})
        subds.to_netcdf(filo)
        print(filo)
        os.system('cdo showvar {:s}'.format(filo))

    '''
    timearr=[datetime.datetime(iyr,imon,iday,ihr).strftime('%Y-%m-%dT%H') for ihr in range(0,24) for iday in range(1,days_in_month+1)]
    for var in ['REFL_COM']:
        filo='SEUS.{:s}.{:d}.{:02d}.1hr.nc'.format(var,iyr,imon)
        if os.path.exists(filo):continue
        temp=ds[var].sel(time=timearr).isel(south_north=slice(x_min,x_max),west_east=slice(y_min,y_max)).load()
        subds = xarray.Dataset({var:temp},coords=temp.coords)
        subds.to_netcdf(filo)
        print(filo)
        os.system('cdo showvar {:s}'.format(filo))
