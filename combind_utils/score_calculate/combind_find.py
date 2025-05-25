import pandas as pd
import numpy as np
import click
import os
from glob import glob
import shutil
from utils import *

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
    np.save(score_fname, combind_energy)