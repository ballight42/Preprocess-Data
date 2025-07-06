import cdsapi
import os
dataset = "reanalysis-era5-pressure-levels"
client = cdsapi.Client()
for yr in range(1948,2025):
 for mon in ["06"]:
  for var in ["temperature","u_component_of_wind", "v_component_of_wind","vertical_velocity"]:
   for level in [950,900]:

    request = {
    "product_type": ["reanalysis"],
    "variable": [var],
    "year": [str(yr)],
    "month": [mon],
    "day": ["{:02d}".format(iday) for iday in range(1,30+1)],
    "time": ["00:00", "06:00", "12:00",        "18:00"
    ],
    "pressure_level": [str(level)],
    "data_format": "grib",
    "download_format": "unarchived",
    "area": [40, -90, 10, 0],
    "grid": [1.,1.]
    }

    if os.path.exists("TUVW."+str(level)+"hPa."+str(yr)+"."+mon+".nc"):continue
    print("TUVW."+str(level)+"hPa."+str(yr)+"."+mon+".nc")
    client.retrieve(dataset, request).download('temp')
    os.system("cdo -f nc copy temp TUVW."+str(level)+"hPa."+str(yr)+"."+mon+".nc")
    os.system("rm temp")

