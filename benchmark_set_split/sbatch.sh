#!/bin/sh
#SBATCH --ntasks=1                 # Run a single task
#SBATCH --cpus-per-task=4          # Number of CPU cores per task (8 CPUs)
#SBATCH --mem=16G                  # Job memory request (64GB)
#SBATCH --time=3-00:00:00          # Time limit (days-hours:minutes:seconds) - 1 day
#SBATCH --partition=rondror            # Use the GPU partition (change as needed)


conda init
conda deactivate
cd /scratch/groups/rondror/marvinli/combind/

module load chemistry
module load schrodinger
source /scratch/groups/rondror/marvinli/combind/schrodinger.ve/bin/activate

#read the subfolder name from the command line
subfolder=$1
protein_name=$2
cd $subfolder
echo "Running in $subfolder"
echo "Protein name: $protein_name"
export COMBINDHOME=`pwd`
export PATH=$PATH:$COMBINDHOME
export SCHRODINGER_ALLOW_UNSAFE_MULTIPROCESSING=1

#run the combind ligprep structures/library.csv --multiplex
echo "Running combind ligprep"
combind ligprep $subfolder/structures/library.csv --multiplex
#require prep protein
echo "Running combind structprep"
combind structprep
#to run the screen
echo "Running combind dock"
combind dock ligands/library/library.maegz --screen

#featurize
echo "Running combind featurize"
echo "library-to-${protein_name}/library-to-${protein_name}_pv.maegz"
combind featurize --no-mcss --screen --max-poses 100000 features_screen docking/library-to-${protein_name}/library-to-${protein_name}_pv.maegz helpers/helpers_pv.maegz

echo "Running combind screen"
combind screen screen.npy features_screen

echo "Running combind apply-scores"
combind apply-scores docking/library-to-${protein_name}/library-to-${protein_name}_pv.maegz screen.npy combind_scores_added_pv.maegz
