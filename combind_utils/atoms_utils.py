from schrodinger.structure import StructureReader
from schrodinger.structutils.rmsd import ConformerRmsd
import numpy as np
def get_atoms_coordinates(atom):
    x = atom.x#property["r_m_x_coord"]
    y = atom.y#property["r_m_y_coord"]
    z = atom.z#property["r_m_z_coord"]
    return x, y, z

def get_ligand_protein_path(ligands_dict,key):
    if ligands_dict[key][0].contains("lig.mae"):
        ligand = ligands_dict[key][0]
        protein = ligands_dict[key][1]
    else:
        ligand = ligands_dict[key][1]
        protein = ligands_dict[key][0]
    return ligand, protein

# This code reads predicted ligand poses from Glide docking and stores their docking scores
# The poses are read from a MAE file containing multiple docked conformations
# Each pose (except the reference structure) is stored in a dictionary with its docking score
# Lower docking scores indicate better predicted binding affinity

def read_poses_and_calculate_rmsd(poses_pred_path, poses_true_path, base_name="4bz6", top = 100):
    """
    Read predicted poses from a MAE file and calculate RMSD values against a reference structure.
    
    Args:
        poses_pred_path (str): Path to the predicted poses MAE file
        poses_true_path (str): Path to the reference structure MAE file 
        base_name (str): Base name to identify reference structure
        
    Returns:
        tuple: Dictionary of poses and their docking scores, list of RMSD values
    """
    poses_true = next(StructureReader(poses_true_path))
    
    # Dictionary to store docking poses and their scores
    poses_pred_structure_glide = {}
    rmsd_values = []
    count = 0

    # Read each model from the poses file
    with StructureReader(poses_pred_path) as reader:
        for model in reader:
            # Skip the reference structure
            if base_name in model.property["s_m_title"]:
                continue
            else:
                count += 1
                if count > top:
                    break
                # Extract the docking score for this pose
                docking_score = model.property["r_i_docking_score"]
                # Store the pose model and its docking score
                poses_pred_structure_glide[model] = docking_score
                rmsd_value = ConformerRmsd(reference_structure=poses_true,
                                         test_structure=model, asl_expr="NOT atom.element H").calculate()
                # Record rmsd value
                rmsd_values.append(rmsd_value)
    rmsd_values = np.array(rmsd_values)
    return poses_pred_structure_glide, rmsd_values
