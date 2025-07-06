#! /bin/bash
# Project=("CMIP6")
# Scenario=("ssp245" "ssp245-GHG" "ssp245-aer" "ssp245-nat") 
Scenario=("historical" "hist-aer" "hist-nat" "hist-GHG") 
Var=("tas" "prw")
Realm="Amon"
# raw data dir
diri="./"

for var in ${Var[@]}
do
        for sce in ${Scenario[@]}
        do
		diro="../${sce}/"
                declare -A uniq
                for k in $(ls ${diri}${var}_${Realm}_*_${sce}_*.nc | rev | cut -d "/" -f1 | rev | cut -d "_" -f3)
                do
                        uniq[$k]=1
                done
                Model=${!uniq[@]}
                echo "Model Set: "$Model
                for model in ${Model[@]}
                do
                        declare -A uniq2
                        for k in $(ls ${diri}${var}_${Realm}_${model}_${sce}_*.nc | rev | cut -d "/" -f1 | rev | cut -d "_" -f5)
                        do
                                uniq2[$k]=1
                        done
                        Ens=${!uniq2[@]}
                        echo "Ensemble:"${Ens}
                        for ens in ${Ens[@]}
                        do
                                echo "Model: "${model}" Ensemble:"$ens
                                files=($(ls ${diri}${var}_${Realm}_${model}_${sce}_${ens}_*.nc))
                                #files=($(find "${diri}" -type f -name "${var}_${Realm}_${model}_${sce}_${ens}_*.nc"))
				grid=$(ls ${files[0]} | rev | cut -d "/" -f1 | rev | cut -d "_" -f6)
                                strtdate=$(ls ${files[0]} | rev | cut -d "/" -f1 | rev | cut -d "_" -f7 | cut -d "-" -f1)
                                lastdate=$(ls ${files[${#files[@]}-1]} | rev | cut -d "/" -f1 | rev | cut -d "_" -f7 | cut -d "-" -f2 | cut -d "." -f1)
                                # here we start to process the data:
                                echo "Start from "$strtdate" to "$lastdate". Merge?yes or no."
				# read input
				input="yes"
				if [[ $input == "no" ]]; then
                                    continue
				fi
                                files=$(ls ${diri}${var}_${Realm}_${model}_${sce}_${ens}_*.nc)
                                filo=${diro}${var}_${Realm}_${model}_${sce}_${ens}_${grid}_${strtdate}-${lastdate}.nc
				# filo=${diro}${var}_${Realm}_${model}_${sce}_${ens}_${strtdate}-${lastdate}.nc
                                echo "--------------------------------------------------------------"
                                # echo "input files:"
                                # echo ${files}
                                echo "output file:"
                                echo ${filo}

                                if [ ${#files[@]} == 1 ]
                                then
                                        echo "Only one file for "${model}". No need to merge. Just move it."
                                        echo "move?yes or no."
                                        #read input
                                        input="yes"
                                        if [[ $input == "yes" ]]; then
                                            echo "do that"
                                            mv ${files} ${filo}
                                        else
                                           echo "don't do that"
                                        fi
                                        continue
                                fi
                                cdo mergetime ${files} ${filo}
				echo "remove original file?yes or no."
				#read input
                                input="yes"
                                if [[ $input == "yes" ]]; then
                                    echo "do that"
                                    rm ${files}
                                else
                                   echo "don't do that"
                                fi

                                echo "--------------------------------------------------------------"
                        done
                        unset uniq2
                        unset Ens
                done
        done
done

