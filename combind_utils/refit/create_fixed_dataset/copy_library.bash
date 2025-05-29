#!/bin/bash
cd /home/pc/Documents/combind_fragment/combind_fragment/
# Get all unique subdirectories from both A and B
for subdir in $(ls -d fragment_dataset_add_bond_orders/*/ fragment_fullBinders_dataset_add_bond_orders/*/ 2>/dev/null | xargs -n1 basename | sort -u); do
    if [[ -f "fragment_dataset_add_bond_orders/$subdir/ligand_resmiles.csv" ]] && [[ -f "fragment_fullBinders_dataset_add_bond_orders/$subdir/ligand_resmiles.csv" ]]; then
        # Both files exist, merge them
        mkdir -p "fragment_fixed_dataset/$subdir"
        { head -n 1 "fragment_dataset_add_bond_orders/$subdir/ligand_resmiles.csv"; tail -n +2 "fragment_dataset_add_bond_orders/$subdir/ligand_resmiles.csv"; tail -n +2 "fragment_fullBinders_dataset_add_bond_orders/$subdir/ligand_resmiles.csv"; } > "fragment_fixed_dataset/$subdir/ligand_resmiles.csv"
        echo "Merged $subdir/ligand_resmiles.csv"
    elif [[ -f "fragment_dataset_add_bond_orders/$subdir/ligand_resmiles.csv" ]]; then
        # Only exists in A, copy it
        mkdir -p "fragment_fixed_dataset/$subdir"
        cp "fragment_dataset_add_bond_orders/$subdir/ligand_resmiles.csv" "fragment_fixed_dataset/$subdir/ligand_resmiles.csv"
        echo "Copied $subdir/ligand_resmiles.csv from A (not found in B)"
    elif [[ -f "fragment_fullBinders_dataset_add_bond_orders/$subdir/ligand_resmiles.csv" ]]; then
        # Only exists in B, copy it
        mkdir -p "fragment_fixed_dataset/$subdir"
        cp "fragment_fullBinders_dataset_add_bond_orders/$subdir/ligand_resmiles.csv" "fragment_fixed_dataset/$subdir/ligand_resmiles.csv"
        echo "Copied $subdir/ligand_resmiles.csv from B (not found in A)"
    fi
done