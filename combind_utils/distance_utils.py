import numpy as np
from scipy.spatial import KDTree

def find_closest_A_for_each_B(A, B):
    """
    For each point in set B, find its closest point in set A using Euclidean distance in 3D.
    
    Parameters:
    A: numpy array of shape (n, 3) - points in set A
    B: numpy array of shape (m, 3) - points in set B
    
    Returns:
    results: list of tuples (b_idx, a_idx, distance) for each point in B
             where a_idx is the index of the closest point in A
    """
    # Preprocessing: Build KD-tree on set A
    # Time complexity: O(|A| log |A|)
    kdtree_A = KDTree(A)
    
    # Find nearest point in A for each point in B
    # Time complexity: O(|B| log |A|)
    results = []
    
    for b_idx, b_point in enumerate(B):
        # Query the KD-tree for the nearest neighbor
        # Returns (distance, index) of nearest point
        distance, a_idx = kdtree_A.query(b_point, k=1)
        
        # Store the result
        results.append((b_idx, a_idx, distance))
    
    return results

def find_closest_atom_in_pocket_for_each_atom_in_ligand(A, B, atom_type_A = None, atom_type_B = None):
    """
    For each atom in set B, find its closest atom in set A using Euclidean distance in 3D.
    
    Parameters:
    A: Atom object
    B: Atom object
    atom_type_A: list of str
    atom_type_B: str
    
    Returns:
    results: list of tuples (b_idx, a_idx, distance) for each atom in B
             where a_idx is the index of the closest atom in A
    """
    #filter atoms by atom_type_A
    A = [atom for atom in A if atom.atom_type in atom_type_A]
    #filter atoms by atom_type_B
    B = [atom for atom in B if atom.atom_type in atom_type_B]
    #find closest atom in A for each atom in B
    results = find_closest_A_for_each_B(A, B)
    return results

