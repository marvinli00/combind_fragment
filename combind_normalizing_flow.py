#!/bin/env python

import pandas as pd
import numpy as np
import click
import os
from glob import glob
from schrodinger.structure import StructureReader, StructureWriter
import shutil
from utils import *

###############################################################################

# Defaults
stats_root = os.environ['COMBINDHOME']+'/stats_data/default'
mcss_version = 'mcss16'
shape_version = 'pharm_max'
ifp_version = 'rd1'


import os

def is_running_in_vscode():
    # Check for various VS Code environment variables
    vscode_indicators = [
        'VSCODE_CLI', 'VSCODE_CWD', 'VSCODE_IPC_HOOK', 
        'VSCODE_NLS_CONFIG', 'VSCODE_PID', 'TERM_PROGRAM'
    ]
    
    # for indicator in vscode_indicators:
    #     if indicator in os.environ:
    #         if indicator == 'TERM_PROGRAM' and os.environ[indicator] != 'vscode':
    #             continue
    #         breakpoint()
    #         return True
    
    # Check for VS Code debugger
    if 'DEBUGPY_LAUNCHER_PORT' in os.environ or 'PYDEVD_LOAD_VALUES_ASYNC' in os.environ:
        return True
    
    return False


@click.group()
def main():
    pass

@main.command()
@click.argument('struct', default='')
@click.option('--grid-struct')
@click.option('--root', required=True)
def structprep(struct, grid_struct, root):
    """
    Prepare structures and make a docking grid.

    "struct" specifies the name of the structure for which to make a docking
    grid. (Not the full path, generally just the PDB code.) Defaults to the
    structure with alphabetically lowest name.

    The following directory structure is required:

    \b
    structures/
        raw/
            structure_name_prot.mae
            structure_name_lig.mae
            ...
        processed/
            structure_name/structure_name_out.mae
            ...
        aligned/
            structure_name/rot-structure_name_query.mae
            ...
        proteins/
            structure_name_prot.mae
            ...
        ligands/
            structure_name_lig.mae
            ...
        grids/
            structure_name/structure_name.zip
            ...

    The process can be started from any step, e.g. if you have processed
    versions of your structures, you can place these in the processed directory.

    Files ending with _lig contain only the small molecule ligand present in the
    structure, and files ending with _prot contain everything else.
    """
    from dock.struct_align import struct_align
    from dock.struct_sort import struct_sort
    from dock.struct_process import struct_process
    from dock.grid import make_grid

    assert os.path.exists(f'{root}/structures'), 'No structures directory.'

    structs = sorted(glob(f'{root}/structures/raw/*_prot.mae*'))
    structs = [struct.split('/')[-1].split('_prot')[0] for struct in structs]
    
    #move root/structures to structures/raw_old
    # os.makedirs(f'structures/raw', exist_ok=False)
    #copy all files in root/structures to structures/raw
    # for file in os.listdir(f'{root}/structures/raw'):
    #     shutil.copy(f'{root}/structures/raw/{file}', f'structures/raw/{file}')
    
    if not struct:
        struct = structs[0]

    if not grid_struct:
        grid_struct = struct

    print(f'Processing {structs}, aligning to {struct}, and creating a docking'
          f' grid for {grid_struct}')
    
    
    
    struct_process(structs,
                   protein_in = f"{root}/structures/raw/{{pdb}}_prot.mae",
                   ligand_in = f"{root}/structures/raw/{{pdb}}_lig.mae",
                   processed_in = f"{root}/structures/processed/{{pdb}}/{{pdb}}_in.mae",
                   processed_out = f"{root}/structures/processed/{{pdb}}/{{pdb}}_out.mae",
                   processed_sh = f"{root}/structures/processed/{{pdb}}/process.sh")
    struct_align(struct, structs,
                 processed_out = f'{root}/structures/processed/{{pdb}}/{{pdb}}_out.mae',
                 align_dir = f"{root}/structures/aligned")
    struct_sort(structs, root=root)
    make_grid(grid_struct,
              PROTFILE = f"{root}/structures/proteins/{{pdb}}_prot.mae",
              LIGFILE=f'{root}/structures/ligands/{{pdb}}_lig.mae',
              CWD=f"{root}/structures/grids/{{pdb}}")
    
    # #copy all other folders in structures to root
    # for folder in os.listdir(f'structures'):
    #     shutil.copytree(f'structures/{folder}', f'{root}/structures/{folder}', dirs_exist_ok=True)
    #remove structures folder
    #shutil.rmtree(f'structures')
    

@main.command()
@click.argument('smiles')
@click.option('--root', default='ligands')
@click.option('--multiplex', is_flag=True)
@click.option('--ligand-names', default='ID')
@click.option('--ligand-smiles', default='SMILES')
@click.option('--delim', default=',')
@click.option('--processes', default=1)
def ligprep(smiles, root, multiplex, ligand_names, ligand_smiles, delim, processes):
    """
    Prepare ligands for docking, from smiles.

    Specifically, this will run Schrodinger's ligprep and then perform
    additional processing to make the ligands readable by rdkit and to assign
    atom names.

    "smiles" should be a `delim` delimited file with columns "ligand-names"
    and "ligand-smiles".
    
    "root" specifies where the processed ligands will be written. 

    By default, an individual file will be made for each ligand. If multiplex is
    set, then only one file, containing all the ligands, will be produced.

    Multiprocessing is only supported for non-multiplexed mode.
    """
    from dock.ligprep import ligprep
    mkdir(root)
    ligands = pd.read_csv(smiles, sep=delim)
    print('Prepping {} mols from {} in {}'.format(len(ligands), smiles, root))

    if multiplex:
        _name = os.path.splitext(os.path.basename(smiles))[0]
        _root = f'{root}/{_name}'
        _smiles = f'{_root}/{_name}.smi'
        _mae = os.path.splitext(_smiles)[0] + '.maegz'

        if not os.path.exists(_mae):
            mkdir(_root)
            with open(_smiles, 'w') as fp:
                for _, ligand in ligands.iterrows():
                    fp.write('{} {}\n'.format(ligand[ligand_smiles], ligand[ligand_names]))
            ligprep(_smiles)

    else:
        unfinished = []
        for _, ligand in ligands.iterrows():
            _name = ligand[ligand_names]
            _root = f'{root}/{_name}'
            _smiles = f'{_root}/{_name}.smi'
            _mae = os.path.splitext(_smiles)[0] + '.maegz'

            if not os.path.exists(_mae):
                mkdir(_root)
                with open(_smiles, 'w') as fp:
                    fp.write('{} {}\n'.format(ligand[ligand_smiles], ligand[ligand_names]))
                unfinished += [(_smiles,)]
        mp(ligprep, unfinished, processes)

@main.command()
@click.argument('ligands', nargs=-1)
@click.option('--root', default='docking')
@click.option('--grid')
@click.option('--screen', is_flag=True)
@click.option('--processes', default=1)
def dock(grid, root, ligands, screen, processes):
    """
    Dock "ligands" to "grid".

    "root" specifies where the docking results will be written.

    Setting "screen" limits the thoroughness of the pose sampling. Recommended
    for screening, but not pose prediction.

    "ligands" are paths to prepared ligand files. Multiple can be specified.
    """
    from dock.dock import dock

    if grid is None:
        grid = glob('structures/grids/*/*.zip')
        if grid:
            grid = grid[0]
        else:
            print('No grids in default location (structures/grids)'
                  ', please specify path.')
            exit()

    ligands = [os.path.abspath(lig) for lig in ligands if 'nonames' not in lig]
    grid = os.path.abspath(grid)
    root = os.path.abspath(root)
    mkdir(root)
    unfinished = []
    for ligand in ligands:
        name = '{}-to-{}'.format(basename(ligand), basename(grid))
        _root = '{}/{}'.format(root, name)
        unfinished += [(grid, ligand, _root, name, not screen)]
    mp(dock, unfinished, processes)

################################################################################

@main.command()
@click.argument('root')
@click.argument('poseviewers', nargs=-1)
@click.option('--native', default='structures/ligands/*_lig.mae')
@click.option('--ifp-version', default=ifp_version)
@click.option('--mcss-version', default=mcss_version)
@click.option('--shape-version', default=shape_version)
@click.option('--screen', is_flag=True)
@click.option('--max-poses', default=100)
@click.option('--no-mcss', is_flag=True)
@click.option('--no-shape', is_flag=True)
@click.option('--processes', default=1)
def featurize(root, poseviewers, native, ifp_version, mcss_version,
              shape_version, screen, no_mcss, no_shape, processes, max_poses):
    from features.features import Features
    
    #remove mcss and shape features for fragment based docking
    no_mcss = True
    no_shape = True
    
    native_poses = {}
    for native_path in glob(native):
        name = native_path.split('/')[-1].split('_lig')[0].lower()
        with StructureReader(native_path) as sts:
            sts = list(sts)
        assert len(sts) == 1
        native_poses[name] = sts[0]
    if is_running_in_vscode():
        print("Running in VS Code")
        # Handle wildcards manually with glob
        poseviewers = glob(poseviewers[0])

    features = Features(root, ifp_version=ifp_version, shape_version=shape_version,
                        mcss_version=mcss_version, max_poses=max_poses)
    features.compute_single_features(poseviewers, native_poses=native_poses)

    if screen:
        assert len(poseviewers) == 2
        features.compute_pair_features(poseviewers[:1],
                                       pvs2 = poseviewers[1:],
                                       mcss=not no_mcss, shape=not no_shape)
    else:
        features.compute_pair_features(poseviewers,
                                       mcss=not no_mcss, shape=not no_shape)

################################################################################

@main.command()
@click.argument('root')
@click.argument('out')
@click.argument('ligands', nargs=-1)
@click.option('--features', default='shape,mcss,hbond,saltbridge,contact')
@click.option('--alpha', default=1.0)
@click.option('--stats-root', default=stats_root)
@click.option('--restart', default=500)
@click.option('--max-iterations', default=1000)
def pose_prediction(root, out, ligands, alpha, stats_root,
                    features, restart, max_iterations):
    """
    Run ComBind pose prediction.
    """
    from score.pose_prediction import PosePrediction
    from score.statistics import read_stats
    from features.features import Features

    #remove mcss and shape features for fragment based docking
    features = 'hbond,saltbridge,contact'
    
    
    
    features = features.split(',')

    protein = Features(root)
    protein.load_features()

    if not ligands:
        ligands = set(protein.raw['name1'])
    ligands = sorted(ligands)

    data = protein.get_view(ligands, features)
    stats = read_stats(stats_root, features)
    
    ps = PosePrediction(ligands, features, data, stats, alpha)
    best_poses = ps.max_posterior(max_iterations, restart)

    with open(out, 'w') as fp:
        fp.write('ID,POSE,COMBIND_RMSD,GLIDE_RMSD,BEST_RMSD\n')
        for ligand in best_poses:
            rmsds = data['rmsd'][ligand]
            grmsd = rmsds[0]
            crmsd = rmsds[best_poses[ligand]]
            brmsd = min(rmsds)
            fp.write(','.join(map(str, [ligand.replace('_pv', ''),
                                        best_poses[ligand],
                                        crmsd, grmsd, brmsd]))+ '\n')

@main.command()
@click.argument('score-fname')
@click.argument('root')
@click.option('--stats-root', default=stats_root)
@click.option('--alpha', default=1.0)
@click.option('--features', default='shape,hbond,saltbridge,contact')
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

################################################################################

@main.command()
@click.argument('scores')
@click.argument('original_pvs', nargs=-1)
def extract_top_poses(scores, original_pvs):
    """
    Write top-scoring poses to a single file.
    """
    out = scores.replace('.csv', '_pv.maegz')
    scores = pd.read_csv(scores).set_index('ID')

    with StructureWriter(out) as writer:
        with StructureReader(original_pvs[0]) as sts:
            prot = next(sts)
            writer.append(prot)

        counts = {}
        written = []
        for pv in original_pvs:
            with StructureReader(pv) as sts:
                prot = next(sts)
                for st in sts:
                    name = st.title
                    if name not in counts:
                        counts[name] = 0
                    else:
                        # counts is zero indexed.
                        counts[name] += 1

                    if name in scores.index and scores.loc[name, 'POSE'] == counts[name]:
                        writer.append(st)
                        written += [name]

        assert len(written) == len(scores), written
        for name in scores.index:
            assert name in written

@main.command()
@click.argument('pv')
@click.argument('scores')
@click.argument('out', default=None)
def apply_scores(pv, scores, out):
    """
    Add ComBind screening scores to a poseviewer.
    """
    from score.screen import apply_scores
    if out is None:
        out = pv.replace('_pv.maegz', '_combind_pv.maegz')
    apply_scores(pv, scores, out)

@main.command()
@click.argument('pv')
@click.argument('out', default=None)
def scores_to_csv(pv, out):
    """
    Write docking and ComBind scores to text.
    """
    from score.screen import scores_to_csv
    scores_to_csv(pv, out)

main()
