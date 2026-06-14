import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from model_builder import ModelBuilder
from parser import StructuralModel


def test_model_builder_creates_minimal_valid_model():
    builder = ModelBuilder(name="Builder Demo")
    builder.add_material("m1", E=200000.0)
    builder.add_section("s1", A=0.02, I=0.0001)
    builder.add_node(1, 0.0, 0.0)
    builder.add_node(2, 3.0, 0.0)
    builder.add_element("e1", "frame", 1, 2, "m1", "s1")
    builder.add_support(1, restrain_ux=True, restrain_uy=True, restrain_rz=True)

    model = builder.build(validate=True)

    assert model.elements["e1"].node_j is model.nodes[2]
    assert model.supports[1].restrain_rz is True


def test_model_builder_returns_existing_structural_model_instance():
    existing = StructuralModel(name="Existing")
    model = ModelBuilder(existing).build()

    assert model is existing


def test_model_builder_marks_dirty_when_supported():
    model = StructuralModel()
    model.is_dirty = False
    model.cached_K = [[1.0]]

    ModelBuilder(model).add_node(1, 0.0, 0.0)

    assert model.is_dirty is True
    assert model.cached_K is None
