#!/bin/bash

diro="/mnt/f/data"

# Variables
total_items=2900       # total number of items to query
step=100               # items per request
max_offset=$((total_items - step))

source_ids="CanESM5%2CIPSL-CM6A-LR%2CMIROC6%2CCNRM-CM6-1%2CCESM2%2CNorESM2-LM%2CMRI-ESM2-0%2CGISS-E2-1-G%2CACCESS-ESM1-5%2CHadGEM3-GC31-LL%2CGFDL-ESM4%2CFGOALS-g3%2CACCESS-CM2%2CBCC-CSM2-MR%2CGFDL-CM4%2CE3SM-2-0"
scenarios=("hist-GHG" "hist-aer" "hist-nat")
variables=("prw" "tas")
tables=("Amon")

# Base search URL components
base_url="https://aims2.llnl.gov/proxy/search?project=CMIP6"
# default facets, could be specified later
facets="activity_id%2C+data_node%2C+source_id%2C+institution_id%2C+source_type%2C+experiment_id%2C+sub_experiment_id%2C+nominal_resolution%2C+variant_label%2C+grid_label%2C+table_id%2C+frequency%2C+realm%2C+variable_id%2C+cf_standard_name"
common_query="type=Dataset&format=application%2Fsolr%2Bjson&facets=${facets}&latest=true&query=*"

# Start looping
for offset in $(seq 0 $step $max_offset); do
  for scenario in "${scenarios[@]}"; do
    for variable in "${variables[@]}"; do
      for table_id in "${tables[@]}"; do
        # Construct URL
        query_url="${base_url}&offset=${offset}&limit=${step}&${common_query}"
        query_url+="&experiment_id=${scenario}&source_id=${source_ids}&table_id=${table_id}&variable_id=${variable}"
        # Output file
        output_file="${output_dir}/${scenario}.${variable}.$((offset / step)).json"  
        echo "Downloading: ${scenario}, ${variable}, offset ${offset} to ${output_file}"
        wget -qO- "${query_url}" | jq '.' > "${output_file}"
      done
    done
  done
done

# Merge all ${output_dir}/${scenario}.${variable}.$((offset / step)).json into one unified "search.json"
echo "Merging all JSON files into search.json..."

jq -s 'reduce .[] as $item ({}; 
      .numFound += ($item.response.numFound // 0) |
      .response.docs += ($item.response.docs // []))' \
      "${output_dir}"/*.[0123456789][012356789].json > "${output_dir}/search.json"

echo "Merged file saved as ${output_dir}/search.json"

