#! /bin/bash
#take input from the user and ask for the dataset path (from argument)
#create a healper function to check if the dataset path is valid
function check_dataset_path() {
    if [ ! -d "$1" ]; then
        echo "Invalid dataset path"
        exit 1
    fi
}

DATASET_PATH=$1
COMBINDWORKING_DIR=$2
#read all subdirectories in the dataset path
SUBDIRS=$(ls -l $DATASET_PATH | grep ^d | awk '{print $9}')

#for each subdirectory, run the redocking script
for SUBDIR in $SUBDIRS; do
    echo "Running redocking for $SUBDIR"
    #concatenate the subdirectory path with the redocking script path
    PROTEIN_DIR=$DATASET_PATH/$SUBDIR
    echo "Running redocking for $REDOCK_SCRIPT_PATH"
    #run the redocking script

    sbatch --output=sbatch_logs/${PROTEIN_DIR}_%j.out --error=sbatch_logs/${PROTEIN_DIR}_%j.err --job-name=${PROTEIN_DIR} redock_sbatch.sh $PROTEIN_DIR $COMBINDWORKING_DIR
    
done

