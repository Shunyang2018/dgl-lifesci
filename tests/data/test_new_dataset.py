# -*- coding: utf-8 -*-
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import pandas as pd

from dgllife.data.csv_dataset import *
from dgllife.data.smiles_inference import *
from dgllife.utils.featurizers import *
from dgllife.utils.mol_to_graph import *
from joblib import cpu_count
from python.dgllife.utils.mol_to_graph import MolToBigraph

def test_data_frame1():
    data = [['CCO', 0, 1], ['CO', 2, 3]]
    df = pd.DataFrame(data, columns = ['smiles', 'task1', 'task2'])

    return df

def test_data_frame2():
    data = []
    for _ in range(500):
        data.extend([['CCO', 0, 1], ['CO', 2, 3]])
    df = pd.DataFrame(data, columns = ['smiles', 'task1', 'task2'])

    return df

def remove_file(fname):
    if os.path.isfile(fname):
        try:
            os.remove(fname)
        except OSError:
            pass

def test_mol_csv():
    df = test_data_frame1()
    fname = './test.bin'
    dataset = MoleculeCSVDataset(df=df, smiles_to_graph=smiles_to_bigraph,
                                 node_featurizer=CanonicalAtomFeaturizer(),
                                 edge_featurizer=CanonicalBondFeaturizer(),
                                 smiles_column='smiles',
                                 cache_file_path=fname)
    assert dataset.task_names == ['task1', 'task2']
    smiles, graph, label, mask = dataset[0]
    assert label.shape[0] == 2
    assert mask.shape[0] == 2
    assert 'h' in graph.ndata
    assert 'e' in graph.edata

    # Test task_names
    dataset = MoleculeCSVDataset(df=df, smiles_to_graph=smiles_to_bigraph,
                                 node_featurizer=None,
                                 edge_featurizer=None,
                                 smiles_column='smiles',
                                 cache_file_path=fname,
                                 task_names=['task1'])
    assert dataset.task_names == ['task1']

    # Test load
    dataset = MoleculeCSVDataset(df=df, smiles_to_graph=smiles_to_bigraph,
                                 node_featurizer=CanonicalAtomFeaturizer(),
                                 edge_featurizer=None,
                                 smiles_column='smiles',
                                 cache_file_path=fname)
    smiles, graph, label, mask = dataset[0]
    assert 'h' in graph.ndata
    assert 'e' not in graph.edata

    dataset = MoleculeCSVDataset(df=df, smiles_to_graph=smiles_to_bigraph,
                                 node_featurizer=CanonicalAtomFeaturizer(),
                                 edge_featurizer=None,
                                 smiles_column='smiles',
                                 cache_file_path=fname,
                                 load=False)
    smiles, graph, label, mask = dataset[0]
    assert 'h' in graph.ndata
    assert 'e' not in graph.edata

    df2 = test_data_frame2()
    fname = './test.bin'
    dataset = MoleculeCSVDataset(df=df2, smiles_to_graph=smiles_to_bigraph,
                                 node_featurizer=CanonicalAtomFeaturizer(),
                                 edge_featurizer=CanonicalBondFeaturizer(),
                                 smiles_column='smiles',
                                 cache_file_path=fname,
                                 load=False,
                                 n_jobs=cpu_count() - 1)
    assert dataset.task_names == ['task1', 'task2']
    smiles, graph, label, mask = dataset[0]
    assert label.shape[0] == 2
    assert mask.shape[0] == 2
    assert 'h' in graph.ndata
    assert 'e' in graph.edata

    remove_file(fname)

def test_unlabeled_smiles():
    smiles = ['CCO', 'CO']
    mol_to_g = MolToBigraph(node_featurizer=CanonicalAtomFeaturizer(),
                            edge_featurizer=CanonicalBondFeaturizer())
    dataset = UnlabeledSMILES(smiles, mol_to_graph=mol_to_g)
    assert len(dataset) == 2
    smiles, graph = dataset[0]
    assert 'h' in graph.ndata
    assert 'e' in graph.edata

if __name__ == '__main__':
    test_mol_csv()
    test_unlabeled_smiles()
