import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from model_builder import ModelBuilder
from banded_solver import UnstableStructureError
from parser import StructuralModel
import pytest


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


def test_model_builder_validate_raises_without_supports():
    builder = ModelBuilder()
    builder.add_material("m1", E=200000.0)
    builder.add_section("s1", A=0.02, I=0.0001)
    builder.add_node(1, 0.0, 0.0)
    builder.add_node(2, 3.0, 0.0)
    builder.add_element("e1", "frame", 1, 2, "m1", "s1")

    with pytest.raises(UnstableStructureError, match="No boundary conditions"):
        builder.build(validate=True)


def test_model_builder_validate_raises_on_floating_unsupported_substructure():
    builder = ModelBuilder()
    builder.add_material("m1", E=200000.0)
    builder.add_section("s1", A=0.02, I=0.0001)
    for node_id, x in [(1, 0.0), (2, 3.0), (3, 10.0), (4, 13.0)]:
        builder.add_node(node_id, x, 0.0)
    builder.add_element("supported", "frame", 1, 2, "m1", "s1")
    builder.add_element("floating", "frame", 3, 4, "m1", "s1")
    builder.add_support(1, restrain_ux=True, restrain_uy=True, restrain_rz=True)

    with pytest.raises(UnstableStructureError, match="floating"):
        builder.build(validate=True)


def test_model_builder_validate_false_returns_incomplete_model():
    builder = ModelBuilder()
    builder.add_material("m1", E=200000.0)
    builder.add_section("s1", A=0.02, I=0.0001)
    builder.add_node(1, 0.0, 0.0)
    builder.add_node(2, 3.0, 0.0)
    builder.add_element("e1", "frame", 1, 2, "m1", "s1")

    model = builder.build(validate=False)

    assert model is builder.model
    assert model.supports == {}
