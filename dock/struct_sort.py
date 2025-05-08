import os
from schrodinger.structure import StructureReader

def split_complex(st, pdb_id, root=None):
    
    
    if root is None:
        os.system('mkdir -p structures/proteins structures/ligands')
        lig_path = 'structures/ligands/{}_lig.mae'.format(pdb_id)
        prot_path = 'structures/proteins/{}_prot.mae'.format(pdb_id)
    else:
        os.system(f'mkdir -p {root}/structures/proteins {root}/structures/ligands')
        lig_path = '{}/structures/ligands/{}_lig.mae'.format(root, pdb_id)
        prot_path = '{}/structures/proteins/{}_prot.mae'.format(root,pdb_id)

    if not os.path.exists(lig_path) and len([a.index for a in st.atom if a.chain == 'L']) > 0:
        lig_st = st.extract([a.index for a in st.atom if a.chain == 'L'])
        lig_st.title = '{}_lig'.format(pdb_id)
        lig_st.write(lig_path)
    
    if not os.path.exists(prot_path):
        prot_st = st.extract([a.index for a in st.atom if a.chain != 'L'])
        prot_st.title = '{}_prot'.format(pdb_id)
        prot_st.write(prot_path)

def struct_sort(structs, root=None):
    for struct in structs:
        if root is None:
            opt_complex = 'structures/aligned/{}/rot-{}_query.mae'.format(struct, struct)
        else:
            opt_complex = '{}/structures/aligned/{}/rot-{}_query.mae'.format(root, struct, struct)

        if os.path.exists(opt_complex):
            comp_st = next(StructureReader(opt_complex))
            split_complex(comp_st, struct, root)
