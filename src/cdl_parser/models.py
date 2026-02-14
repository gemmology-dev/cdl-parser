"""
CDL Data Models.

Data classes representing Crystal Description Language components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union


@dataclass
class MillerIndex:
    """Miller index representation.

    Represents crystal face orientations using Miller or Miller-Bravais notation.

    Attributes:
        h: First Miller index
        k: Second Miller index
        l: Third Miller index (fourth in Miller-Bravais)
        i: Third index for Miller-Bravais notation (hexagonal/trigonal)
           Calculated as -(h+k), only used for 4-index notation

    Examples:
        >>> MillerIndex(1, 1, 1)  # Octahedron face
        >>> MillerIndex(1, 0, 0)  # Cube face
        >>> MillerIndex(1, 0, 1, i=-1)  # Hexagonal {10-11}
    """

    h: int
    k: int
    l: int  # noqa: E741 - standard crystallographic notation
    i: int | None = None  # For Miller-Bravais (hexagonal/trigonal)

    def __post_init__(self) -> None:
        # Validate Miller-Bravais constraint: i = -(h+k)
        if self.i is not None:
            expected_i = -(self.h + self.k)
            if self.i != expected_i:
                raise ValueError(
                    f"Invalid Miller-Bravais index: i should be {expected_i}, got {self.i}"
                )

    def as_tuple(self) -> tuple[int, ...]:
        """Return as tuple (3 or 4 elements)."""
        if self.i is not None:
            return (self.h, self.k, self.i, self.l)
        return (self.h, self.k, self.l)

    def as_3index(self) -> tuple[int, int, int]:
        """Return as 3-index tuple (for calculations)."""
        return (self.h, self.k, self.l)

    def __str__(self) -> str:
        if self.i is not None:
            return f"{{{self.h}{self.k}{self.i}{self.l}}}"
        return f"{{{self.h}{self.k}{self.l}}}"

    def __repr__(self) -> str:
        if self.i is not None:
            return f"MillerIndex({self.h}, {self.k}, {self.l}, i={self.i})"
        return f"MillerIndex({self.h}, {self.k}, {self.l})"


@dataclass
class Feature:
    """A crystal feature annotation.

    Describes growth patterns, surface markings, inclusions, or color properties.

    Attributes:
        name: Feature type ('phantom', 'trigon', 'silk', 'colour', etc.)
        values: List of feature values (numbers, identifiers, color specs)
    """

    name: str
    values: list[int | float | str] = field(default_factory=list)

    def __str__(self) -> str:
        if self.values:
            val_str = ", ".join(str(v) for v in self.values)
            return f"{self.name}:{val_str}"
        return self.name


@dataclass
class CrystalForm:
    """A crystal form with Miller index and scale.

    Represents a single crystal form (set of symmetry-equivalent faces)
    with an optional distance scale for truncation.

    Attributes:
        miller: The Miller index defining the form
        scale: Distance scale (default 1.0, larger = more truncated)
        name: Original name if using named form (e.g., 'octahedron')
        features: Optional list of feature annotations
        label: Optional label for the form (e.g., 'prism' in prism:{10-10})

    Examples:
        >>> CrystalForm(MillerIndex(1, 1, 1), scale=1.0)
        >>> CrystalForm(MillerIndex(1, 0, 0), scale=1.3, name='cube')
    """

    miller: MillerIndex
    scale: float = 1.0
    name: str | None = None  # Original name if using named form
    features: list[Feature] | None = None  # Per-form features [phantom:3]
    label: str | None = None  # Form label (v1.3)

    def __str__(self) -> str:
        s = str(self.miller)
        if self.name:
            s = f"{self.name}={s}"
        if self.label:
            s = f"{self.label}:{s}"
        if self.scale != 1.0:
            s += f"@{self.scale}"
        if self.features:
            feat_str = ", ".join(str(f) for f in self.features)
            s += f"[{feat_str}]"
        return s


@dataclass
class FormGroup:
    """A group of forms with optional shared features and label.

    Represents parenthesized form groups: (form + form)[shared_features]
    """

    forms: list[FormNode]
    features: list[Feature] | None = None
    label: str | None = None

    def __str__(self) -> str:
        form_strs = [str(f) for f in self.forms]
        s = "(" + " + ".join(form_strs) + ")"
        if self.label:
            s = f"{self.label}:{s}"
        if self.features:
            feat_str = ", ".join(str(f) for f in self.features)
            s += f"[{feat_str}]"
        return s


# Type alias for form tree nodes
FormNode = Union[CrystalForm, FormGroup]


@dataclass
class Definition:
    """A named definition: @name = expression"""

    name: str
    body: list[FormNode]

    def __str__(self) -> str:
        body_str = " + ".join(str(f) for f in self.body)
        return f"@{self.name} = {body_str}"


@dataclass
class Modification:
    """A morphological modification.

    Represents transformations applied to the crystal shape.

    Attributes:
        type: Modification type ('elongate', 'truncate', 'taper', 'bevel', 'flatten')
        params: Parameters specific to the modification type

    Examples:
        >>> Modification('elongate', {'axis': 'c', 'ratio': 1.5})
        >>> Modification('truncate', {'form': MillerIndex(1,0,0), 'depth': 0.3})
    """

    type: str  # elongate, truncate, taper, bevel, flatten
    params: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        param_str = ", ".join(f"{k}:{v}" for k, v in self.params.items())
        return f"{self.type}({param_str})"


@dataclass
class TwinSpec:
    """Twin specification.

    Defines how crystal twinning should be applied.

    Attributes:
        law: Named twin law (e.g., 'spinel', 'brazil', 'japan')
        axis: Custom twin axis [x, y, z] if not using named law
        angle: Rotation angle in degrees (default 180)
        twin_type: Type of twin ('contact', 'penetration', 'cyclic')
        count: Number of twin individuals (default 2)

    Examples:
        >>> TwinSpec(law='spinel')
        >>> TwinSpec(axis=(1, 1, 1), angle=180)
        >>> TwinSpec(law='trilling', count=3)
    """

    law: str | None = None  # Named law (spinel, brazil, etc.)
    axis: tuple[float, float, float] | None = None  # Custom axis
    angle: float = 180.0
    twin_type: str = "contact"  # contact, penetration, cyclic
    count: int = 2  # Number of individuals

    def __str__(self) -> str:
        if self.law:
            if self.count != 2:
                return f"twin({self.law},{self.count})"
            return f"twin({self.law})"
        return f"twin({self.axis},{self.angle},{self.twin_type})"


@dataclass
class PhenomenonSpec:
    """Optical phenomenon specification.

    Attributes:
        type: Phenomenon type ('asterism', 'chatoyancy', 'adularescence', etc.)
        params: Dict of parameters (e.g. {'rays': 6, 'intensity': 'strong'})
    """

    type: str
    params: dict[str, int | float | str] = field(default_factory=dict)

    def __str__(self) -> str:
        parts = [self.type]
        for k, v in self.params.items():
            parts.append(f"{k}:{v}")
        return "phenomenon[" + ", ".join(parts) + "]"


def _form_node_to_dict(node: FormNode) -> dict[str, Any]:
    """Convert a FormNode to dictionary representation."""
    if isinstance(node, CrystalForm):
        return {
            "type": "form",
            "miller": node.miller.as_tuple(),
            "scale": node.scale,
            "name": node.name,
            "label": node.label,
            "features": [
                {"name": feat.name, "values": feat.values}
                for feat in node.features
            ] if node.features else None,
        }
    elif isinstance(node, FormGroup):
        return {
            "type": "group",
            "forms": [_form_node_to_dict(f) for f in node.forms],
            "label": node.label,
            "features": [
                {"name": feat.name, "values": feat.values}
                for feat in node.features
            ] if node.features else None,
        }
    return {}


@dataclass
class CrystalDescription:
    """Complete crystal description parsed from CDL.

    The main output of CDL parsing, containing all information needed
    to generate a crystal visualization.

    Attributes:
        system: Crystal system ('cubic', 'hexagonal', etc.)
        point_group: Hermann-Mauguin point group symbol ('m3m', '6/mmm', etc.)
        forms: List of form nodes (CrystalForm or FormGroup)
        modifications: List of morphological modifications
        twin: Optional twin specification
        definitions: Optional list of named definitions

    Examples:
        >>> desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        >>> desc.system
        'cubic'
        >>> len(desc.forms)
        2
    """

    system: str
    point_group: str
    forms: list[FormNode] = field(default_factory=list)
    modifications: list[Modification] = field(default_factory=list)
    twin: TwinSpec | None = None
    phenomenon: PhenomenonSpec | None = None
    doc_comments: list[str] | None = None
    definitions: list[Definition] | None = None

    def flat_forms(self) -> list[CrystalForm]:
        """Get a flat list of all CrystalForm objects (backwards compat).

        Recursively traverses FormGroup nodes to extract all CrystalForm leaves.
        Features from parent FormGroups are merged into child forms.
        """
        result: list[CrystalForm] = []
        for node in self.forms:
            result.extend(_flatten_node(node))
        return result

    def __str__(self) -> str:
        parts = [f"{self.system}[{self.point_group}]"]

        # Definitions
        if self.definitions:
            def_strs = [str(d) for d in self.definitions]
            parts = def_strs + parts

        # Forms (including features)
        form_strs = [str(f) for f in self.forms]
        parts.append(":" + " + ".join(form_strs))

        # Modifications
        if self.modifications:
            mod_strs = [str(m) for m in self.modifications]
            parts.append(" | " + ", ".join(mod_strs))

        # Twin
        if self.twin:
            parts.append(" | " + str(self.twin))

        # Phenomenon
        if self.phenomenon:
            parts.append(" | " + str(self.phenomenon))

        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "system": self.system,
            "point_group": self.point_group,
            "forms": [_form_node_to_dict(f) for f in self.forms],
            "flat_forms": [
                {
                    "miller": f.miller.as_tuple(),
                    "scale": f.scale,
                    "name": f.name,
                    "label": f.label,
                    "features": [
                        {"name": feat.name, "values": feat.values}
                        for feat in f.features
                    ] if f.features else None,
                }
                for f in self.flat_forms()
            ],
            "modifications": [{"type": m.type, "params": m.params} for m in self.modifications],
            "twin": {
                "law": self.twin.law,
                "axis": self.twin.axis,
                "angle": self.twin.angle,
                "twin_type": self.twin.twin_type,
                "count": self.twin.count,
            }
            if self.twin
            else None,
            "phenomenon": {
                "type": self.phenomenon.type,
                "params": self.phenomenon.params,
            }
            if self.phenomenon
            else None,
            "doc_comments": self.doc_comments,
            "definitions": [
                {"name": d.name, "body": [_form_node_to_dict(f) for f in d.body]}
                for d in self.definitions
            ] if self.definitions else None,
        }


def _flatten_node(
    node: FormNode, parent_features: list[Feature] | None = None
) -> list[CrystalForm]:
    """Recursively flatten a FormNode into a list of CrystalForms."""
    if isinstance(node, CrystalForm):
        if parent_features:
            merged = list(parent_features)
            if node.features:
                merged.extend(node.features)
            return [CrystalForm(
                miller=node.miller, scale=node.scale,
                name=node.name, features=merged, label=node.label,
            )]
        return [node]
    elif isinstance(node, FormGroup):
        combined_features = list(parent_features) if parent_features else []
        if node.features:
            combined_features.extend(node.features)
        result: list[CrystalForm] = []
        for child in node.forms:
            result.extend(_flatten_node(child, combined_features if combined_features else None))
        return result
    return []
