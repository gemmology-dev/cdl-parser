# cdl-parser

[![PyPI version](https://badge.fury.io/py/cdl-parser.svg)](https://badge.fury.io/py/cdl-parser)
[![Python](https://img.shields.io/pypi/pyversions/cdl-parser.svg)](https://pypi.org/project/cdl-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Crystal Description Language (CDL) Parser** - A Python library for parsing compact string notation describing crystal morphology for gemmological and mineralogical visualization. CDL v2.0 adds support for amorphous materials, nested growth, and crystal aggregates.

Part of the [Gemmology Project](https://gemmology.dev).

## Installation

```bash
pip install cdl-parser
```

## Quick Start

```python
from cdl_parser import parse_cdl

# Parse a simple octahedron
desc = parse_cdl("cubic[m3m]:{111}")
print(desc.system)      # 'cubic'
print(desc.point_group) # 'm3m'

# Parse a truncated octahedron (diamond-like)
desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
print(len(desc.forms))  # 2

# Parse with twin specification
desc = parse_cdl("cubic[m3m]:{111} | twin(spinel)")
print(desc.twin.law)    # 'spinel'

# Parse an amorphous material (v2.0)
desc = parse_cdl("amorphous[opalescent]:{botryoidal}")
print(desc.system)      # 'amorphous'
print(desc.subtype)     # 'opalescent'

# Parse nested growth (v2.0)
desc = parse_cdl("trigonal[32]:({10-10}@1.0 + {10-11}@0.8) > ({10-10}@0.5 + {10-11}@0.4)")

# Parse an aggregate (v2.0)
desc = parse_cdl("trigonal[32]:{10-10}@1.0 + {10-11}@0.8 ~ cluster[12]")
```

## CDL Specification

### Syntax Overview

```
# Crystalline materials
system[point_group]:{form}@scale + {form}@scale | modification | twin(law)

# Amorphous materials (v2.0)
amorphous[subtype]:{shape1, shape2}[features] | phenomenon[type]

# Nested growth (v2.0)
system[point_group]:(forms) > (overgrowth_forms)

# Aggregates (v2.0)
system[point_group]:forms ~ arrangement[count]
```

### Crystal Systems

All 7 crystal systems are supported with their standard point groups, plus amorphous materials:

| System | Default Point Group | All Point Groups |
|--------|---------------------|------------------|
| cubic | m3m | m3m, 432, -43m, m-3, 23 |
| hexagonal | 6/mmm | 6/mmm, 622, 6mm, -6m2, 6/m, -6, 6 |
| trigonal | -3m | -3m, 32, 3m, -3, 3 |
| tetragonal | 4/mmm | 4/mmm, 422, 4mm, -42m, 4/m, -4, 4 |
| orthorhombic | mmm | mmm, 222, mm2 |
| monoclinic | 2/m | 2/m, m, 2 |
| triclinic | -1 | -1, 1 |
| amorphous | none | (n/a) |

### Amorphous Materials (v2.0)

Materials without crystalline structure use the `amorphous` keyword instead of a crystal system:

```python
# Syntax: amorphous[subtype]:{shape1, shape2}[features]
"amorphous[opalescent]:{botryoidal}"
"amorphous[cryptocrystalline]:{massive, nodular}[colour:blue]"
"amorphous[waxy]:{mammillary}[banding:concentric]"
```

**Subtypes:** `opalescent`, `glassy`, `waxy`, `resinous`, `cryptocrystalline`

**Shapes:** `massive`, `botryoidal`, `reniform`, `stalactitic`, `mammillary`, `nodular`, `conchoidal`

### Nested Growth (v2.0)

The `>` operator describes overgrowth relationships (base > overgrowth), where an outer crystal grows on an inner one. Right-associative: `a > b > c` = `a > (b > c)`.

```python
# Scepter quartz — enlarged head on thin stem
"trigonal[32]:({10-10}@1.0 + {10-11}@0.8) > ({10-10}@0.5 + {10-11}@0.4)"

# Diamond phantom
"cubic[m3m]:{111}@1.0 > {111}@1.0"
```

### Aggregates (v2.0)

The `~` operator describes crystal aggregates — multiple copies of a form arranged in a spatial pattern:

```python
# Syntax: forms ~ arrangement[count]
"trigonal[32]:{10-10}@1.0 + {10-11}@0.8 ~ cluster[12]"   # Quartz cluster
"trigonal[32]:{10-10}@1.0 + {10-11}@0.8 ~ druse[50]"     # Amethyst geode
"cubic[m3m]:{100} ~ cluster[5]"                            # Pyrite cluster
"trigonal[-3m]:rhombohedron ~ parallel[3]"                  # Calcite parallel growth
```

**Arrangements:** `parallel`, `random`, `radial`, `epitaxial`, `druse`, `cluster`

**Orientations** (optional): `aligned`, `random`, `planar`, `spherical`

### Group-Level Twins (v2.0)

Twin specifications can be applied to form groups, allowing twinning of composite morphologies:

```python
# Twin a group of forms
"cubic[m3m]:({111}@1.0 + {100}@0.3) | twin(spinel)"
```

### Miller Indices

Forms are specified using Miller indices in curly braces:

```python
# 3-index notation (hkl)
"{111}"   # Octahedron face
"{100}"   # Cube face
"{110}"   # Dodecahedron face

# 4-index notation for hexagonal/trigonal (hkil where i = -(h+k))
"{10-10}" # Hexagonal prism
"{10-11}" # Rhombohedron
"{0001}"  # Basal pinacoid
```

### Named Forms

Common forms can be referenced by name:

```python
# Cubic named forms
"octahedron"      # → {111}
"cube"            # → {100}
"dodecahedron"    # → {110}
"trapezohedron"   # → {211}

# Hexagonal/Trigonal named forms
"prism"           # → {10-10}
"basal"           # → {0001}
"rhombohedron"    # → {10-11}
```

### Scale Values

The `@scale` parameter controls the relative prominence of forms:

```python
# Larger scale = form appears more (more truncation)
"{111}@1.0 + {100}@1.3"  # Cube truncates the octahedron
"{111}@1.0 + {100}@0.3"  # Octahedron with small cube facets
```

### Twin Laws

Named twin laws for common crystal twins:

```python
# Contact twins
"twin(spinel)"      # Spinel law (111) twin
"twin(brazil)"      # Brazil law quartz twin
"twin(japan)"       # Japan law quartz twin

# Penetration twins
"twin(fluorite)"    # Fluorite interpenetration twin
"twin(iron_cross)"  # Iron cross pyrite twin

# Cyclic twins
"twin(trilling,3)"  # Three-fold cyclic twin
```

### Complete Examples

```python
# Diamond (octahedron with cube truncation)
"cubic[m3m]:{111}@1.0 + {100}@0.3"

# Quartz prism with rhombohedron termination
"trigonal[-3m]:{10-10}@1.0 + {10-11}@0.8"

# Garnet (dodecahedron + trapezohedron)
"cubic[m3m]:{110}@1.0 + {211}@0.6"

# Spinel-law twinned octahedron
"cubic[m3m]:{111} | twin(spinel)"

# Fluorite cube
"cubic[m3m]:{100}"

# Opal — amorphous with play of color (v2.0)
"amorphous[opalescent]:{botryoidal} | phenomenon[play_of_color:intense]"

# Turquoise — cryptocrystalline massive (v2.0)
"amorphous[cryptocrystalline]:{massive, nodular}[colour:blue]"

# Scepter quartz — nested growth (v2.0)
"trigonal[32]:({10-10}@1.0 + {10-11}@0.8) > ({10-10}@0.5 + {10-11}@0.4)"

# Quartz cluster aggregate (v2.0)
"trigonal[32]:{10-10}@1.0 + {10-11}@0.8 ~ cluster[12]"

# Amethyst geode druse (v2.0)
"trigonal[32]:{10-10}@1.0 + {10-11}@0.8 ~ druse[50]"
```

## API Reference

### Core Functions

#### `parse_cdl(text: str) -> CrystalDescription | AmorphousDescription`

Parse a CDL string into a structured description. Returns `CrystalDescription` for crystalline materials or `AmorphousDescription` for amorphous materials.

```python
from cdl_parser import parse_cdl

# Crystalline — returns CrystalDescription
desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")

# Amorphous — returns AmorphousDescription (v2.0)
desc = parse_cdl("amorphous[opalescent]:{botryoidal}")
```

#### `validate_cdl(text: str) -> tuple[bool, str | None]`

Validate a CDL string without parsing.

```python
from cdl_parser import validate_cdl

is_valid, error = validate_cdl("cubic[m3m]:{111}")
if not is_valid:
    print(f"Error: {error}")
```

### Data Classes

#### `CrystalDescription`

Main output of CDL parsing for crystalline materials.

```python
@dataclass
class CrystalDescription:
    system: str                          # Crystal system
    point_group: str                     # Point group symbol
    forms: list[FormNode]                # Form tree (CrystalForm | FormGroup | NestedGrowth | AggregateSpec)
    modifications: list[Modification]    # Morphological mods
    twin: TwinSpec | None                # Twin specification
    phenomenon: PhenomenonSpec | None    # Optical phenomenon
    doc_comments: list[str] | None       # Doc comments (#!)
    definitions: list[Definition] | None # Named definitions (@name = ...)

    def flat_forms(self) -> list[CrystalForm]:
        """Flatten form tree into a list of CrystalForm leaves."""
```

#### `AmorphousDescription` (v2.0)

Output of CDL parsing for amorphous (non-crystalline) materials.

```python
@dataclass
class AmorphousDescription:
    subtype: str                         # 'opalescent', 'glassy', 'waxy', etc.
    shapes: list[str]                    # 'massive', 'botryoidal', etc.
    features: list[Feature] | None       # Feature annotations
    phenomenon: PhenomenonSpec | None    # Optical phenomenon
    doc_comments: list[str] | None       # Doc comments (#!)
    definitions: list[Definition] | None # Named definitions

    @property
    def system(self) -> str:             # Always returns 'amorphous'
```

#### `NestedGrowth` (v2.0)

Represents a base crystal with an overgrowth (the `>` operator).

```python
@dataclass
class NestedGrowth:
    base: FormNode                       # Base form node
    overgrowth: FormNode                 # Overgrowth form node
```

#### `AggregateSpec` (v2.0)

Represents a crystal aggregate (the `~` operator).

```python
@dataclass
class AggregateSpec:
    form: FormNode                       # Form to aggregate
    arrangement: str                     # 'parallel', 'random', 'radial', etc.
    count: int                           # Number of individuals
    spacing: str | None                  # Optional spacing value
    orientation: str | None              # Optional orientation mode
    orientation_param: float | None      # Optional orientation parameter
```

#### `MillerIndex`

Miller index representation.

```python
@dataclass
class MillerIndex:
    h: int
    k: int
    l: int
    i: Optional[int] = None  # For 4-index notation

    def as_tuple(self) -> tuple[int, ...]
    def as_3index(self) -> tuple[int, int, int]
```

#### `CrystalForm`

A crystal form with scale.

```python
@dataclass
class CrystalForm:
    miller: MillerIndex
    scale: float = 1.0
    name: Optional[str] = None
```

### Constants

```python
from cdl_parser import (
    CRYSTAL_SYSTEMS,          # Set of system names
    POINT_GROUPS,             # Dict[system, Set[groups]]
    DEFAULT_POINT_GROUPS,     # Dict[system, default_group]
    NAMED_FORMS,              # Dict[name, (h, k, l)]
    TWIN_LAWS,                # Set of twin law names
    AMORPHOUS_SUBTYPES,       # Set: opalescent, glassy, waxy, resinous, cryptocrystalline
    AMORPHOUS_SHAPES,         # Set: massive, botryoidal, reniform, stalactitic, ...
    AGGREGATE_ARRANGEMENTS,   # Set: parallel, random, radial, epitaxial, druse, cluster
    AGGREGATE_ORIENTATIONS,   # Set: aligned, random, planar, spherical
)
```

### Exceptions

```python
from cdl_parser import ParseError, ValidationError

try:
    desc = parse_cdl("invalid{{{")
except ParseError as e:
    print(f"Syntax error at position {e.position}: {e.message}")
```

## CLI Usage

```bash
# Parse and display
cdl parse "cubic[m3m]:{111}@1.0 + {100}@1.3"

# Validate
cdl validate "cubic[m3m]:{111}"

# Output as JSON
cdl parse "cubic[m3m]:{111}" --json

# List available options
cdl --list-systems
cdl --list-point-groups
cdl --list-forms
cdl --list-twins
```

## Integration with Other Packages

cdl-parser is designed to work with the Gemmology Project ecosystem:

```python
from cdl_parser import parse_cdl
from crystal_geometry import cdl_to_geometry
from crystal_renderer import generate_cdl_svg, generate_geometry_svg

# Option 1: Direct CDL string to SVG
cdl = "cubic[m3m]:{111}@1.0 + {100}@1.3"
generate_cdl_svg(cdl, "crystal.svg")

# Option 2: Parse, then generate geometry for custom processing
desc = parse_cdl(cdl)
geometry = cdl_to_geometry(desc)

# Render geometry directly
generate_geometry_svg(geometry.vertices, geometry.faces, "geometry.svg")
```

## Development

```bash
# Clone the repository
git clone https://github.com/gemmology-dev/cdl-parser.git
cd cdl-parser

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/cdl_parser

# Linting
ruff check src/cdl_parser
```

## Documentation

Full documentation is available at [cdl-parser.gemmology.dev](https://cdl-parser.gemmology.dev).

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [crystal-geometry](https://github.com/gemmology-dev/crystal-geometry) - 3D geometry from CDL
- [mineral-database](https://github.com/gemmology-dev/mineral-database) - Mineral presets
- [crystal-renderer](https://github.com/gemmology-dev/crystal-renderer) - SVG/3D rendering
- [gemmology-plugin](https://github.com/gemmology-dev/gemmology-plugin) - Claude Code plugin
