import glob
dir_prefix = "/scratch/groups/rondror/marvinli/combind_fragment"#"/home/pc/Documents/combind_fragment/combind_fragment"
dataset_name = "fragment_dataset"
source_dir = f"{dir_prefix}/{dataset_name}/*/structures/ligands"
#dest_dir = f"{dir_prefix}/{dataset_name}_redocking"

source_dir_list = glob.glob(source_dir)
#breakpoint()
import numpy as np
import schrodinger
#try to read the mae file
from schrodinger.structure import StructureReader
from tqdm import tqdm
from schrodinger.structutils import rmsd
from rdkit import Chem
from rdkit import Chem
from rdkit.Chem import AllChem
import pandas as pd

import re

def flatten_smiles(smiles_string):
    """
    Flatten a SMILES expression by removing:
    - Isotope specifications (numbers before atoms)
    - Stereochemistry indicators (@, @@, /, \)
    - Atom charges (+, -)
    - Atom classes (:[0-9]+)
    - Explicit hydrogen counts ([nH], [CH3], etc.)
    - Simplifying bracketed atoms to their basic form
    
    Args:
        smiles_string (str): The SMILES string to flatten
        
    Returns:
        str: The flattened SMILES string
    """
    # Remove isotope specifications (numbers before atoms)
    flattened = re.sub(r'(?<=\[)[0-9]+', '', smiles_string)
    
    # Remove stereochemistry indicators
    flattened = re.sub(r'@{1,2}', '', flattened)  # Remove @ and @@
    flattened = re.sub(r'[/\\]', '', flattened)   # Remove / and \
    
    # Remove atom charges and their associated numbers
    flattened = re.sub(r'[-+][0-9]*', '', flattened)
    
    # Remove atom classes
    flattened = re.sub(r':[0-9]+', '', flattened)
    
    # Handle explicit hydrogens in brackets
    flattened = re.sub(r'\[([A-Za-z])H[0-9]*\]', r'\1', flattened)
    
    # Handle bracketed atoms more generally
    # Extract single atoms from brackets when they don't have special notations
    pattern = r'\[([A-Za-z])\]'
    while re.search(pattern, flattened):
        flattened = re.sub(pattern, r'\1', flattened)
    
    # Clean up the H notation in brackets when attached to other atoms
    flattened = re.sub(r'([A-Za-z])\[H\]', r'\1', flattened)
    
    # Clean up any empty brackets that might remain
    flattened = re.sub(r'\[\]', '', flattened)
    
    return flattened

for source_dir in source_dir_list:
    #dest_dir = source_dir.replace("structures/ligands", "structures/ligands_redocking")
    
    ligands_path = f"{source_dir}/*"
    ligands_path = glob.glob(ligands_path)
    
    #extract the  * part from the source_dir
    protein_name = source_dir.replace(f"{dir_prefix}/{dataset_name}/","")
    protein_name = protein_name.replace("/structures/ligands","")
    dest_dir = f"{dir_prefix}/{dataset_name}_redocking/{protein_name}"

    ligand_smiles = pd.DataFrame(columns=["ID", "SMILES"])
    for ligand_path in ligands_path:
        ligand = next(StructureReader(ligand_path))
        ligand.write("temp.pdb")
        try:
            mol = Chem.MolFromPDBFile("temp.pdb")
            mol = Chem.RemoveAllHs(mol)  # Remove hydrogens for cleaner SMILES
            AllChem.SanitizeMol(mol)     # Sanitize the molecule
        except:
            print(f"Error: {ligand_path}")
            continue
        # Convert to SMILES
        smiles = Chem.MolToSmiles(mol)
        #print(ligand_path.split("/")[-1].replace(".mae",""))
        #print(flatten_smiles(smiles))
        new_row = pd.DataFrame({"ID": [ligand_path.split("/")[-1].replace(".mae","")], 
                            "SMILES": [flatten_smiles(smiles)]})
        ligand_smiles = pd.concat([ligand_smiles, new_row], ignore_index=True)

    ligand_smiles.to_csv(f"{dest_dir}/ligand_resmiles.csv", index=False)
