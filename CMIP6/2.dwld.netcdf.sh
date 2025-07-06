
#!/bin/bash

# Download .nc based on "search.json" under the same directory

#You have to manually adjust the time intervals
histstart=1850
histend=2020
manual_step=171


# Define the data nodes
data_node=(
    "esgf-node.ornl.gov/thredds/fileServer/css03_data/CMIP6/"
    "aims3.llnl.gov/thredds/fileServer/css03_data/CMIP6/"
    "esgf-data.ucar.edu/thredds/fileServer/esg_dataroot/CMIP6/"
    "esgf-data1.llnl.gov/thredds/fileServer/css03_data/CMIP6/"
    "dpesgf03.nccs.nasa.gov/thredds/fileServer/CMIP6/"
    "esgf-data2.llnl.gov/thredds/fileServer/user_pub_work/CMIP6/"
    "aims3.llnl.gov/thredds/fileServer/css03_data/CMIP6/"
    # "esgf.ceda.ac.uk/thredds/fileServer/CMIP6/"
    # "esgf.ceda.ac.uk/thredds/fileServer/esg_cmip6/CMIP6/"
    # "esgf.nci.org.au/thredds/fileServer/replica/CMIP6/"
    # "esgf-data03.diasjp.net/thredds/fileServer/esg_dataroot/CMIP6/"
    # "esgf-data04.diasjp.net/thredds/fileServer/esg_dataroot/CMIP6/"
    # "esg.lasg.ac.cn/thredds/dodsC/esg_dataroot/CMIP6"
    # "crd-esgf-drc.ec.gc.ca/thredds/fileServer/esgA_dataroot/AR6/CMIP6/"
    # "crd-esgf-drc.ec.gc.ca/thredds/fileServer/esgD_dataroot/AR6/CMIP6/"
    # "crd-esgf-drc.ec.gc.ca/thredds/fileServer/esgH_dataroot/AR6/CMIP6/"
    # "dpesgf03.nccs.nasa.gov/thredds/fileServer/CMIP6/"
    # "esgf.bsc.es/thredds/fileServer/esg_dataroot/a36z-ScenarioMIP-r28/CMIP6/"
    # "esgf.ceda.ac.uk/thredds/fileServer/CMIP6/"
    # "esgf.ceda.ac.uk/thredds/fileServer/esg_cmip6/CMIP6/"
    # "esgf.nci.org.au/thredds/fileServer/replica/CMIP6/"
    # "esgf.nci.org.au/thredds/fileServer/master/CMIP6/"
    "esgf3.dkrz.de/thredds/fileServer/cmip6/"
    # "esgf3.dkrz.de/thredds/fileServer/cmip6_mh1007/"
    # "noresg.nird.sigma2.no/thredds/fileServer/esg_dataroot/cmor/CMIP6/"
    # "esgf-node2.cmcc.it/thredds/fileServer/esg_dataroot/CMIP6/"
)
generate_timerange() {
    local start_year=$1
    local end_year=$2
    local step=$3
    local timerange=()
    for ((year=start_year; year<=end_year; year+=step)); do

        if ((step == 1)); then
            timerange+=("${year}01-${year}12")
        else
            local end_step_year=$((year + step - 1))
            if ((end_step_year > end_year)); then
                end_step_year=$end_year
            fi
            timerange+=("${year}01-${end_step_year}12")
        fi
    done
    echo ${timerange[@]}

}




# Function to extract parameters and generate download links
generate_links() {
    local json_file=$1
    local processing=false

    while IFS= read -r line; do
        # if [[ $line =~ \"id\":\"([^\"]+)\", ]]; then
        #     id_string=${BASH_REMATCH[1]}
        #     IFS='.' read -r mip_era activity_drs institution_id source_id experiment_id member_id table_id variable_id grid_label version data_node_head <<< "$(echo $id_string | sed 's/|/./')"
        #     processing=true
        # fi
        if [[ $line =~ \"id\":\ *\"([^\"]+)\" ]]; then
            id_string=${BASH_REMATCH[1]}
            IFS='.' read -r mip_era activity_drs institution_id source_id experiment_id member_id table_id variable_id grid_label version data_node_head <<< "$(echo $id_string | sed 's/|/./')"
            processing=true
        fi
        # if $processing && [[ $line =~ \"number_of_files\":([0-9]+), ]]; then
        if $processing && [[ $line =~ \"number_of_files\":\ *([0-9]+) ]]; then
            number_of_files=${BASH_REMATCH[1]}
            processing=false
            targetfile=$(ls ../${experiment_id}/${variable_id}_${table_id}_${source_id}_${experiment_id}_${member_id}_${grid_label}_*.nc)
            echo $targetfile
            if [ ! -x "$targetfile" ]; then
                echo ${source_id}
                if [[ $experiment_id == *"hist"* ]]; then
                        start=$histstart
                        end=$histend
                elif [[ $experiment_id == *"ssp"* ]]; then
                        start=$sspstart
                        end=$sspend
                fi
                
                step=$manual_step
                timerange=($(generate_timerange $start $end $step ))
                echo $timerange
                folder="${source_id}/${experiment_id}/${member_id}/${table_id}/${variable_id}/${grid_label}/${version}/"
                for itime in ${timerange[@]}; do
                    filename="${variable_id}_${table_id}_${source_id}_${experiment_id}_${member_id}_${grid_label}_${itime}.nc"
                    for url in ${data_node[@]}; do
                        head="http://${url}${activity_drs}/${institution_id}/"
                        #echo ${head}${folder}${filename}
                        if [ ! -x "$filename" ]; then 
                            wget -c ${head}${folder}${filename}
                        fi
                    done
                done
            fi
        fi
    done < "$json_file"
}

# Call the function with the path to your JSON file
generate_links "search.json"

