#! /bin/bash
#take input from the user and ask for the dataset path (from argument)
#create a healper function to check if the dataset path is valid
function check_dataset_path() {
    if [ ! -d "$1" ]; then
        echo "Invalid dataset path"
        exit 1
    fi
}

DATASET_PATH=$2
COMBINDWORKING_DIR=$1
#read all subdirectories in the dataset path
SUBDIRS=$(ls -l $DATASET_PATH | grep ^d | awk '{print $9}')

RUNNING_PROTEINS=(A5H660)

#for each subdirectory, run the redocking script
for SUBDIR in $SUBDIRS; do
    #check if the subdirectory is in the running proteins list
    #if [[ ! " ${RUNNING_PROTEINS[@]} " =~ " ${SUBDIR} " ]]; then
    #    echo "Skipping $SUBDIR"
    #    continue
    #fi

    echo "Running redocking for $SUBDIR"
    #concatenate the subdirectory path with the redocking script path
    PROTEIN_DIR=$DATASET_PATH/$SUBDIR
    echo "Running redocking for $REDOCK_SCRIPT_PATH"
    #run the redocking script

    sbatch --output=sbatch_logs/${PROTEIN_DIR}_%j.out --error=sbatch_logs/${PROTEIN_DIR}_%j.err --job-name=${SUBDIR} redock_sbatch.sh $PROTEIN_DIR $COMBINDWORKING_DIR
    
done

