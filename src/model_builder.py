"""Internal helpers for constructing StructuralModel instances without XML."""

from __future__ import annotations

from collections.abc import Iterable

from parser import (
    Element,
    LoadCase,
    LumpedMass,
    Material,
    Node,
    NodalLoad,
    PointLoad,
    Section,
    StructuralModel,
    Support,
    UniformlyDL,
)
from structural_validator import StructuralValidator


class ModelBuilder:
    """Build a StructuralModel through the existing parser dataclasses."""

    def __init__(self, model: StructuralModel | None = None, *, name: str | None = None, unit_system: str | None = None):
        self.model = model if model is not None else StructuralModel()
        if name is not None:
            self.model.name = name
            self._mark_dirty()
        if unit_system is not None:
            self.model.unit_system = unit_system
            self._mark_dirty()

    def add_material(self, id: str, E: float, alpha: float = 0.0, density: float = 0.0) -> Material:
        material = Material(id=id, E=E, alpha=alpha, density=density)
        self.model.materials[id] = material
        self._mark_dirty()
        return material

    def add_section(self, id: str, A: float, I: float = 0.0, d: float = 0.0) -> Section:
        section = Section(id=id, A=A, I=I, d=d)
        self.model.sections[id] = section
        self._mark_dirty()
        return section

    def add_node(self, id: int, x: float, y: float) -> Node:
        node = Node(id=id, x=x, y=y)
        self.model.nodes[id] = node
        self._mark_dirty()
        return node

    def add_element(
        self,
        id: str,
        type: str,
        node_i: int | Node,
        node_j: int | Node,
        material: str | Material,
        section: str | Section,
        release_start: bool = False,
        release_end: bool = False,
        is_axially_rigid: bool = False,
    ) -> Element:
        element = Element(
            id=id,
            type=type,
            node_i=self._node(node_i),
            node_j=self._node(node_j),
            material=self._material(material),
            section=self._section(section),
            release_start=release_start,
            release_end=release_end,
            is_axially_rigid=is_axially_rigid,
        )
        self.model.elements[id] = element
        self._mark_dirty()
        return element

    def add_support(
        self,
        node: int | Node,
        restrain_ux: bool = False,
        restrain_uy: bool = False,
        restrain_rz: bool = False,
        settlement_ux: float = 0.0,
        settlement_uy: float = 0.0,
        settlement_rz: float = 0.0,
    ) -> Support:
        node_ref = self._node(node)
        support = Support(
            node=node_ref,
            restrain_ux=restrain_ux,
            restrain_uy=restrain_uy,
            restrain_rz=restrain_rz,
            settlement_ux=settlement_ux,
            settlement_uy=settlement_uy,
            settlement_rz=settlement_rz,
        )
        self.model.supports[node_ref.id] = support
        self._mark_dirty()
        return support

    def add_nodal_load(
        self,
        load_case: str,
        node: int | Node,
        fx: float = 0.0,
        fy: float = 0.0,
        mz: float = 0.0,
        *,
        load_case_name: str = "",
    ) -> NodalLoad:
        nodal_load = NodalLoad(node=self._node(node), fx=fx, fy=fy, mz=mz)
        self._load_case(load_case, load_case_name).loads.append(nodal_load)
        self._mark_dirty()
        return nodal_load

    def add_member_udl(
        self,
        load_case: str,
        element: str | Element,
        wx: float = 0.0,
        wy: float = 0.0,
        *,
        load_case_name: str = "",
    ) -> UniformlyDL:
        udl = UniformlyDL(element=self._element(element), wx=wx, wy=wy)
        self._load_case(load_case, load_case_name).loads.append(udl)
        self._mark_dirty()
        return udl

    def add_member_point_load(
        self,
        load_case: str,
        element: str | Element,
        position: float,
        fx: float = 0.0,
        fy: float = 0.0,
        *,
        load_case_name: str = "",
    ) -> PointLoad:
        point_load = PointLoad(element=self._element(element), position=position, fx=fx, fy=fy)
        self._load_case(load_case, load_case_name).loads.append(point_load)
        self._mark_dirty()
        return point_load

    def add_lumped_mass(
        self,
        node: int | Node,
        mass_ux: float = 0.0,
        mass_uy: float = 0.0,
        inertia_rz: float = 0.0,
    ) -> LumpedMass:
        node_ref = self._node(node)
        mass = LumpedMass(node=node_ref, mass_ux=mass_ux, mass_uy=mass_uy, inertia_rz=inertia_rz)
        self.model.lumped_masses[node_ref.id] = mass
        self._mark_dirty()
        return mass

    def add_diaphragm_group(self, id: str, node_ids: Iterable[int | Node]) -> list[int]:
        group = [self._node(node).id for node in node_ids]
        self.model.diaphragm_ux_groups[id] = group
        self._mark_dirty()
        return group

    def build(self, validate: bool = False) -> StructuralModel:
        if validate:
            StructuralValidator(self.model).validate()
        return self.model

    def _load_case(self, id: str, name: str = "") -> LoadCase:
        if id not in self.model.load_cases:
            self.model.load_cases[id] = LoadCase(id=id, name=name)
        elif name:
            self.model.load_cases[id].name = name
        return self.model.load_cases[id]

    def _node(self, node: int | Node) -> Node:
        if isinstance(node, Node):
            return node
        try:
            return self.model.nodes[node]
        except KeyError as exc:
            raise KeyError(f"Unknown node id {node!r}.") from exc

    def _element(self, element: str | Element) -> Element:
        if isinstance(element, Element):
            return element
        try:
            return self.model.elements[element]
        except KeyError as exc:
            raise KeyError(f"Unknown element id {element!r}.") from exc

    def _material(self, material: str | Material) -> Material:
        if isinstance(material, Material):
            return material
        try:
            return self.model.materials[material]
        except KeyError as exc:
            raise KeyError(f"Unknown material id {material!r}.") from exc

    def _section(self, section: str | Section) -> Section:
        if isinstance(section, Section):
            return section
        try:
            return self.model.sections[section]
        except KeyError as exc:
            raise KeyError(f"Unknown section id {section!r}.") from exc

    def _mark_dirty(self) -> None:
        if hasattr(self.model, "mark_dirty"):
            self.model.mark_dirty()

