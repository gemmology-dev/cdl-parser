# cdl-parser

[![PyPI version](https://badge.fury.io/py/cdl-parser.svg)](https://badge.fury.io/py/cdl-parser)
[![Python](https://img.shields.io/pypi/pyversions/cdl-parser.svg)](https://pypi.org/project/cdl-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Crystal Description Language (CDL) Parser** - A Python library for parsing compact string notation describing crystal morphology for gemmological and mineralogical visualization.

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
```

## CDL Specification

### Syntax Overview

```
system[point_group]:{form}@scale + {form}@scale | modification | twin(law)
```

### Crystal Systems

All 7 crystal systems are supported with their standard point groups:

| System | Default Point Group | All Point Groups |
|--------|---------------------|------------------|
| cubic | m3m | m3m, 432, -43m, m-3, 23 |
| hexagonal | 6/mmm | 6/mmm, 622, 6mm, -6m2, 6/m, -6, 6 |
| trigonal | -3m | -3m, 32, 3m, -3, 3 |
| tetragonal | 4/mmm | 4/mmm, 422, 4mm, -42m, 4/m, -4, 4 |
| orthorhombic | mmm | mmm, 222, mm2 |
| monoclinic | 2/m | 2/m, m, 2 |
| triclinic | -1 | -1, 1 |

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
```

## API Reference

### Core Functions

#### `parse_cdl(text: str) -> CrystalDescription`

Parse a CDL string into a structured description.

```python
from cdl_parser import parse_cdl

desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
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

Main output of CDL parsing.

```python
@dataclass
class CrystalDescription:
    system: str                          # Crystal system
    point_group: str                     # Point group symbol
    forms: List[CrystalForm]             # Crystal forms
    modifications: List[Modification]    # Morphological mods
    twin: Optional[TwinSpec]             # Twin specification
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
    CRYSTAL_SYSTEMS,      # Set of system names
    POINT_GROUPS,         # Dict[system, Set[groups]]
    DEFAULT_POINT_GROUPS, # Dict[system, default_group]
    NAMED_FORMS,          # Dict[name, (h, k, l)]
    TWIN_LAWS,            # Set of twin law names
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
from crystal_geometry import cdl_to_geometry  # Future package
from crystal_renderer import generate_svg     # Future package

# Parse CDL
desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")

# Convert to 3D geometry
geometry = cdl_to_geometry(desc)

# Render to SVG
svg = generate_svg(geometry)
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
