from schrodinger.structure import MaestroReader, MaestroWriter
from schrodinger.structutils import analyze
from schrodinger import structure
from schrodinger.structure import StructureReader
from schrodinger.structutils import assignbondorders

import glob
ligands = "/home/pc/Documents/combind_fragment/combind_fragment/fragment_fullBinders_dataset_add_bond_orders/*/structures/raw/*_lig.mae"
ligands = glob.glob(ligands)

for ligand in ligands:
    with StructureReader(ligand) as reader:
        st = next(reader)
    assignbondorders.assign_st(st)
    
    with MaestroWriter(ligand) as writer:
        writer.append(st)

