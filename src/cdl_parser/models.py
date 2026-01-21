"""
CDL Data Models.

Data classes representing Crystal Description Language components.
"""

from dataclasses import dataclass, field
from typing import Any


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
class CrystalForm:
    """A crystal form with Miller index and scale.

    Represents a single crystal form (set of symmetry-equivalent faces)
    with an optional distance scale for truncation.

    Attributes:
        miller: The Miller index defining the form
        scale: Distance scale (default 1.0, larger = more truncated)
        name: Original name if using named form (e.g., 'octahedron')

    Examples:
        >>> CrystalForm(MillerIndex(1, 1, 1), scale=1.0)
        >>> CrystalForm(MillerIndex(1, 0, 0), scale=1.3, name='cube')
    """

    miller: MillerIndex
    scale: float = 1.0
    name: str | None = None  # Original name if using named form

    def __str__(self) -> str:
        s = str(self.miller)
        if self.name:
            s = f"{self.name}={s}"
        if self.scale != 1.0:
            s += f"@{self.scale}"
        return s


@dataclass
class Modification:
    """A morphological modification.

    Represents transformations applied to the crystal shape.

    Attributes:
        type: Modification type ('elongate', 'truncate', 'taper', 'bevel')
        params: Parameters specific to the modification type

    Examples:
        >>> Modification('elongate', {'axis': 'c', 'ratio': 1.5})
        >>> Modification('truncate', {'form': MillerIndex(1,0,0), 'depth': 0.3})
    """

    type: str  # elongate, truncate, taper, bevel
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
class CrystalDescription:
    """Complete crystal description parsed from CDL.

    The main output of CDL parsing, containing all information needed
    to generate a crystal visualization.

    Attributes:
        system: Crystal system ('cubic', 'hexagonal', etc.)
        point_group: Hermann-Mauguin point group symbol ('m3m', '6/mmm', etc.)
        forms: List of crystal forms with their scales
        modifications: List of morphological modifications
        twin: Optional twin specification

    Examples:
        >>> desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        >>> desc.system
        'cubic'
        >>> len(desc.forms)
        2
    """

    system: str
    point_group: str
    forms: list[CrystalForm] = field(default_factory=list)
    modifications: list[Modification] = field(default_factory=list)
    twin: TwinSpec | None = None

    def __str__(self) -> str:
        parts = [f"{self.system}[{self.point_group}]"]

        # Forms
        form_strs = [str(f.miller) + (f"@{f.scale}" if f.scale != 1.0 else "") for f in self.forms]
        parts.append(":" + " + ".join(form_strs))

        # Modifications
        if self.modifications:
            mod_strs = [str(m) for m in self.modifications]
            parts.append(" | " + ", ".join(mod_strs))

        # Twin
        if self.twin:
            parts.append(" | " + str(self.twin))

        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "system": self.system,
            "point_group": self.point_group,
            "forms": [
                {"miller": f.miller.as_tuple(), "scale": f.scale, "name": f.name}
                for f in self.forms
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
        }
