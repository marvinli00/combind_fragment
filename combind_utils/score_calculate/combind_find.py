import pandas as pd
import numpy as np
import click
import os
from glob import glob
import shutil
from collections import defaultdict
from schrodinger.structure import StructureReader
###############################################################################

# Defaults
#add /scratch/groups/rondror/marvinli/combind_fragment/ to the path

def screen(score_fname, root, stats_root, alpha, features):
    """
    Run ComBind screening.
    """
    from score.screen import screen, load_features_screen
    from score.statistics import read_stats

    features = 'hbond,saltbridge,contact'
    features = features.split(',')
    stats = read_stats(stats_root, features)
    single, raw = load_features_screen(features, root)

    combind_energy = screen(single, raw, stats, alpha)
    return combind_energy
    # np.save(score_fname, combind_energy)
    
def get_scores(pv, scores):
    """
    Add ComBind screening scores to a poseviewer.
    """
    name_score_glide = defaultdict(list)
    name_score_combind = defaultdict(list)
    with StructureReader(pv) as reader:
        st = next(reader)
        st.property['r_i_combind_score'] = 1000.0
        for st, score in zip(reader, scores):
            #check if the score is nan
            if np.isnan(score):
                continue
            
            name_score_glide[st.property["s_m_title"]].append(st.property["r_i_docking_score"])
            name_score_combind[st.property["s_m_title"]].append(score)
           # st.property['r_i_combind_score'] = score
    return name_score_combind, name_score_glide