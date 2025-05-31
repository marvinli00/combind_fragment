import pandas as pd
import numpy as np
import multiprocessing as mp

def merge_hbonds(ifp):
    """
    Reads IFP file and merges hbond acceptors and donors.

    Setting the label to hbond for the hbond_donors and hbond_acceptors while
    changing the residue names allows for only donor+donor or acceptor+acceptor
    to be counted as overlapping, but them to be merged into the same similarity
    measure.
    """

    mask = ifp.label=='hbond_acceptor'
    ifp.loc[mask, 'protein_res'] = [res+'acceptor' for res in ifp.loc[mask, 'protein_res']]
    ifp.loc[mask, 'label'] = 'hbond'
    
    mask = ifp.label=='hbond_donor'
    ifp.loc[mask, 'protein_res'] = [res+'donor' for res in ifp.loc[mask, 'protein_res']]
    ifp.loc[mask, 'label'] = 'hbond'
    return ifp

def ifp_tanimoto(ifps1, ifps2, feature):
    """
    Computes the tanimoto distance between ifp1 and ifp2 for feature.
    """
    if feature == 'hbond':
        ifps1 = [merge_hbonds(ifp) for ifp in ifps1]
        ifps2 = [merge_hbonds(ifp) for ifp in ifps2]

    ifps1 = [ifp.loc[ifp.label == feature] for ifp in ifps1]
    ifps2 = [ifp.loc[ifp.label == feature] for ifp in ifps2]

    ifps1 = [ifp.set_index('protein_res') for ifp in ifps1]
    ifps2 = [ifp.set_index('protein_res') for ifp in ifps2]

    sims = np.zeros((len(ifps1), len(ifps2)))
    for i, ifp1 in enumerate(ifps1):
        for j, ifp2 in enumerate(ifps2):
            total = ifp1['score'].sum() + ifp2['score'].sum()
            overlap = ifp1.join(ifp2, rsuffix='_2', how='inner')
            overlap = overlap['score']**0.5 * overlap['score_2']**0.5
            overlap = overlap.sum()

            sims[i, j] = (1 + overlap) / (2 + total - overlap)
    return sims

def _compute_similarity_pair(args):
    """
    Helper function to compute similarity for a single pair of IFPs.
    
    Args:
        args: Tuple of (i, j, ifp1, ifp2) where i,j are indices and ifp1,ifp2 are DataFrames
        
    Returns:
        Tuple of (i, j, similarity) containing indices and computed similarity score
    """
    i, j, ifp1, ifp2 = args
    total = ifp1['score'].sum() + ifp2['score'].sum()
    overlap = ifp1.join(ifp2, rsuffix='_2', how='inner')
    overlap = overlap['score']**0.5 * overlap['score_2']**0.5
    overlap = overlap.sum()
    
    similarity = (1 + overlap) / (2 + total - overlap)
    return i, j, similarity

def _prepare_ifps_for_mp(ifps1, ifps2, feature):
    """
    Helper function to prepare IFPs for multiprocessing computation.
    
    Args:
        ifps1: List of IFP DataFrames (first set)
        ifps2: List of IFP DataFrames (second set)  
        feature: Feature type to filter on
        
    Returns:
        Tuple of (processed_ifps1, processed_ifps2) ready for similarity computation
    """
    if feature == 'hbond':
        ifps1 = [merge_hbonds(ifp) for ifp in ifps1]
        ifps2 = [merge_hbonds(ifp) for ifp in ifps2]

    ifps1 = [ifp.loc[ifp.label == feature] for ifp in ifps1]
    ifps2 = [ifp.loc[ifp.label == feature] for ifp in ifps2]

    ifps1 = [ifp.set_index('protein_res') for ifp in ifps1]
    ifps2 = [ifp.set_index('protein_res') for ifp in ifps2]
    
    return ifps1, ifps2

def ifp_tanimoto_mp(ifps1, ifps2, feature, n_processes=None):
    """
    Computes the tanimoto distance between ifp1 and ifp2 for feature using multiprocessing.
    
    Args:
        ifps1: List of IFP DataFrames (first set)
        ifps2: List of IFP DataFrames (second set)
        feature: Feature type to compute similarity for
        n_processes: Number of processes to use (None for automatic detection)
        
    Returns:
        2D numpy array of similarity scores with shape (len(ifps1), len(ifps2))
    """
    if n_processes is None:
        n_processes = mp.cpu_count()
    
    # Prepare IFPs for computation
    ifps1, ifps2 = _prepare_ifps_for_mp(ifps1, ifps2, feature)
    
    # Create all pairs for parallel processing
    pairs = [(i, j, ifps1[i], ifps2[j]) 
             for i in range(len(ifps1)) 
             for j in range(len(ifps2))]
    
    # Initialize similarity matrix
    sims = np.zeros((len(ifps1), len(ifps2)))
    
    # Use multiprocessing to compute similarities in parallel
    with mp.Pool(processes=n_processes) as pool:
        results = pool.map(_compute_similarity_pair, pairs)
    
    # Fill the similarity matrix with results
    for i, j, similarity in results:
        sims[i, j] = similarity
    
    return sims