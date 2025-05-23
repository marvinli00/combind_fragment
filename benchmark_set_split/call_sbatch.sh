#read all folders in the working dir
folders=$(ls)

#folder prefix
prefix="/scratch/groups/rondror/marvinli/combind_batch"
templete_dir="/scratch/groups/rondror/marvinli/combind_template/"

mkdir -p sbatch_logs
#for each folder, call the sbatch script
for folder in $folders; do
    #check if it is a directory
    if [ -d "$folder" ]; then
        #check if it contains a split_library folder
        if [ -d "$folder/split_library" ]; then
            #if it does, read all files in the split_library folder
            files=$(ls $folder/split_library)
            #for each file, call the sbatch script
            for file in $files; do
                #remove the .csv extension
                file_no_ext=$(basename $file .csv)

                subfolder=$prefix/${folder}_${file_no_ext}

                # #if subfolder exists, remove it
                # if [ -d "$subfolder" ]; then
                #     rm -rf $subfolder
                # fi

                #copy the templete directory to the new folder
                #cp -r $templete_dir $subfolder

                #copy structure files to the structures folder in the new folder 
                #cp -r $folder/structures $subfolder/
                ##cp $folder/split_library/$file $subfolder/structures/library.csv

                #also copy the helpers_pv.maegz file to the new folder
                #mkdir -p $subfolder/helpers
                #cp $folder/helpers_pv.maegz $subfolder/helpers/

                #call the sbatch script
                #sbatch --output=sbatch_logs/${folder}_${file_no_ext}_%j.out --error=sbatch_logs/${folder}_${file_no_ext}_%j.err --job-name=${folder}_${file_no_ext} sbatch.sh $subfolder $folder
                exit the loop
                exit 0
            done
        fi
    fi
done

