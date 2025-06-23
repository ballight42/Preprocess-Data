# Preprocess-Data

To access, concatenate, and confirm data:

## CMIP6 (2025.06.23)
tools: 'os' in `python`,`wget`, `cdo`,
### 1. download json files
```python
import os
diro='/mnt/f/data'
for offset in range(0,2900,100):
    for scenario in ['hist-GHG','hist-aer','hist-nat']:
        for variable in ['prw','tas']:
            l0='wget -qO- '
            l1="https://aims2.llnl.gov/proxy/search?project=CMIP6&offset={:d}&limit=100&type=Dataset&format=application%2Fsolr%2Bjson".format(offset)
            l2="&facets=activity_id%2C+data_node%2C+source_id%2C+institution_id%2C+source_type%2C+experiment_id%2C+sub_experiment_id%2C"
            l3="+nominal_resolution%2C+variant_label%2C+grid_label%2C+table_id%2C+frequency%2C+realm%2C+variable_id%2C+cf_standard_name"
            l4="&latest=true&query=*&experiment_id={:s}&source_id=CanESM5%2CIPSL-CM6A-LR%2CMIROC6%2CCNRM-CM6-1%2CCESM2%2CNorESM2-LM%2CMRI-ESM2-0%2CGISS-E2-1-G%2CACCESS-ESM1-5%2CHadGEM3-GC31-LL%2CGFDL-ESM4%2CFGOALS-g3%2CACCESS-CM2%2CBCC-CSM2-MR%2CGFDL-CM4%2CE3SM-2-0&table_id=Amon&variable_id={:s}".format(scenario,variable)
            l5=" | jq '.' > {:s}/{:s}.{:s}.{:02d}.json".format(diro ,scenario,variable,offset//100)
            cmd=l0+'"'+l1+l2+l3+l4+'"'+l5
            print(cmd)
            os.system(cmd)
```

### 2. download data based on json files

### 3. merge and move data

## ERA5 (2025.06.23)
tools: `cdsapi` in `python`, `cdo`
### 1. single-level, hourly data

### 2. pres-level, monthly data

## JRA3Q (2025.06.23)
tools: 

## CONUS404

## MRMS

