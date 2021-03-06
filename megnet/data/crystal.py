from megnet.data.graph import StructureGraph, StructureGraphFixedRadius
import numpy as np
from megnet.data.graph import GaussianDistance, Converter
from monty.serialization import loadfn
from pathlib import Path
from copy import deepcopy
from pymatgen import Element
from pymatgen.analysis.local_env import NearNeighbors
from pymatgen import Structure

from typing import Union, List, Dict


MODULE_DIR = Path(__file__).parent.absolute()


class CrystalGraph(StructureGraphFixedRadius):
    """
    Convert a crystal into a graph with z as atomic feature and distance as bond feature
    one can optionally include state features
    """

    def __init__(self,
                 nn_strategy: Union[str, NearNeighbors] = 'MinimumDistanceNNAll',
                 atom_converter: Converter = None,
                 bond_converter: Converter = None,
                 cutoff: float = 5.0
                 ):
        self.cutoff = cutoff
        super().__init__(nn_strategy=nn_strategy, atom_converter=atom_converter,
                         bond_converter=bond_converter, cutoff=self.cutoff)


class CrystalGraphWithBondTypes(StructureGraph):
    """
    Overwrite the bond attributes with bond types, defined simply by
    the metallicity of the atoms forming the bond. Three types of
    scenario is considered, nonmetal-nonmetal (type 0), metal-nonmetal (type 1), and
    metal-metal (type 2)

    """

    def __init__(self,
                 nn_strategy: Union[str, NearNeighbors] = 'VoronoiNN',
                 atom_converter: Converter = None,
                 bond_converter: Converter = None):
        super().__init__(nn_strategy=nn_strategy, atom_converter=atom_converter,
                         bond_converter=bond_converter)

    def convert(self, structure: Structure, state_attributes: List = None) -> Dict:
        graph = super().convert(structure, state_attributes=state_attributes)
        return self._get_bond_type(graph)

    @staticmethod
    def _get_bond_type(graph) -> Dict:
        new_graph = deepcopy(graph)
        elements = [Element.from_Z(i) for i in graph['atom']]
        for k, (i, j) in enumerate(zip(graph['index1'], graph['index2'])):
            new_graph['bond'][k] = elements[i].is_metal + elements[j].is_metal
        return new_graph


def get_elemental_embeddings() -> Dict:
    """
    Provides the pre-trained elemental embeddings using formation energies,
    which can be used to speed up the training of other models. The embeddings
    are also extremely useful elemental descriptors that encode chemical
    similarity that may be used in other ways. See

    "Graph Networks as a Universal Machine Learning Framework for Molecules
    and Crystals", https://arxiv.org/abs/1812.05055

    :return: Dict of elemental embeddings as {symbol: length 16 string}
    """
    return loadfn(MODULE_DIR / "resources" /
                  "elemental_embedding_1MEGNet_layer.json")
