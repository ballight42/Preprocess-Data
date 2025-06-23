import cdsapi

level=['10','100','200', '300','400', '500',  '600', '700', '750',
        '800', '825','850', '875', '900','925', '950','1000']
month=['01', '02', '03','04', '05', '06','07', '08', '09','10', '11', '12',]
day=['01', '02', '03','04', '05', '06','07', '08', '09','10', '11', '12',
     '13', '14', '15','16', '17', '18','19', '20', '21','22', '23', '24',
     '25', '26', '27','28', '29', '30','31',]
grid=[1.0,1.0]
import os

varin=[ 'geopotential', 'u_component_of_wind', 'v_component_of_wind',
            'vertical_velocity','specific_humidity', 'temperature',]
varout={'geopotential':'hgt', 'u_component_of_wind':'uwnd', 'v_component_of_wind':'vwnd',
            'vertical_velocity':'omega','specific_humidity':'shum', 'temperature':'air'}
varname={'geopotential':'z', 'u_component_of_wind':'u', 'v_component_of_wind':'v',
            'vertical_velocity':'w','specific_humidity':'q', 'temperature':'t'}
yrstrt=2024
yrlast=2024
for var in varin[:]:
    output='{:s}.mon.mean.{:d}-{:d}.nc'.format(varout[var],yrstrt,yrlast)
    dataset = "reanalysis-era5-pressure-levels-monthly-means"
    request = {
            'product_type': 'monthly_averaged_reanalysis',
            'variable':var,
            'pressure_level': level,
            'year': ['{:04d}'.format(x) for x in range(yrstrt,yrlast+1)],
            'month': month,
            'time': '00:00',
            'grid': grid,  
            "data_format": "grib",
            "download_format": "unarchived"
        }
    client = cdsapi.Client()
    client.retrieve(dataset, request).download('temp')

    if var == 'geopotential':
        os.system('cdo -f nc copy -chname,'+varname[var]+','+varout[var]+' -divc,9.81 temp '+output)
    else:
        os.system('cdo -f nc copy -chname,'+varname[var]+','+varout[var]+' temp '+output)
    os.system('rm temp')


   

