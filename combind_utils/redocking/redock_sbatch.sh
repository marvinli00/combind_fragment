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

PROTEIN_DIR=$1
COMBINDWORKING_DIR=$2
cd $COMBINDWORKING_DIR
export COMBINDHOME=`pwd`
export PATH=$PATH:$COMBINDHOME
export SCHRODINGER_ALLOW_UNSAFE_MULTIPROCESSING=1
echo "Running structprep"
combind structprep --root $PROTEIN_DIR
echo "Running ligprep"
combind ligprep $PROTEIN_DIR/ligand_resmiles.csv --root $PROTEIN_DIR/ligands --processes=$(nproc)
echo "Running dock"
combind dock $PROTEIN_DIR/ligands/*/*.maegz --root $PROTEIN_DIR/docking --processes=$(nproc) --grid $PROTEIN_DIR/structures/grids/*/*.zip
echo "Running featurize"
#native argument must use =
combind featurize $PROTEIN_DIR/features $PROTEIN_DIR/docking/*/*_pv.maegz --native=$PROTEIN_DIR/structures/ligands/*_lig.mae
echo "Running pose-prediction"
combind pose-prediction $PROTEIN_DIR/features $PROTEIN_DIR/features/poses.csv
