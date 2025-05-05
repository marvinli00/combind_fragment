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

