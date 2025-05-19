# Run this before anything else
cd /home/pc/Documents/combind_fragment/combind_fragment/
export COMBINDHOME=`pwd`
export PATH=$PATH:$COMBINDHOME
export SCHRODINGER_ALLOW_UNSAFE_MULTIPROCESSING=1

# Set the maximum number of parallel processes
MAX_PROCESSES=16

# Function to wait until there are fewer than MAX_PROCESSES running
wait_for_processes() {
    while [ $(jobs -p | wc -l) -ge $MAX_PROCESSES ]; do
        sleep 1
    done
}

# Read all folders in the fragment_dataset_add_bond_orders folder
folders=$(ls -l fragment_fullBinders_dataset_add_bond_orders | grep ^d | awk '{print $9}')

# For each folder, run combind structprep in parallel
for folder in $folders; do
    echo "Running structprep for $folder"
    wait_for_processes
    combind structprep --root fragment_fullBinders_dataset_add_bond_orders/$folder/ &
done

# Wait for all background processes to complete
wait
echo "All structprep jobs completed"
