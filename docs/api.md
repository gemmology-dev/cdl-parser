# API Reference

## Core Functions

### parse_cdl

Parse a CDL string into a structured description.

```python
from cdl_parser import parse_cdl

desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
```

::: cdl_parser.parse_cdl

### validate_cdl

Validate a CDL string without parsing.

```python
from cdl_parser import validate_cdl

is_valid, error = validate_cdl("cubic[m3m]:{111}")
if not is_valid:
    print(f"Error: {error}")
```

::: cdl_parser.validate_cdl

## Data Classes

### CrystalDescription

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

::: cdl_parser.CrystalDescription

### MillerIndex

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

::: cdl_parser.MillerIndex

### CrystalForm

A crystal form with scale.

```python
@dataclass
class CrystalForm:
    miller: MillerIndex
    scale: float = 1.0
    name: Optional[str] = None
```

::: cdl_parser.CrystalForm

## Constants

```python
from cdl_parser import (
    CRYSTAL_SYSTEMS,      # Set of system names
    POINT_GROUPS,         # Dict[system, Set[groups]]
    DEFAULT_POINT_GROUPS, # Dict[system, default_group]
    NAMED_FORMS,          # Dict[name, (h, k, l)]
    TWIN_LAWS,            # Set of twin law names
)
```

### CRYSTAL_SYSTEMS

Set of valid crystal system names:

- `cubic`
- `tetragonal`
- `orthorhombic`
- `hexagonal`
- `trigonal`
- `monoclinic`
- `triclinic`

### POINT_GROUPS

Dictionary mapping each crystal system to its valid point groups.

### DEFAULT_POINT_GROUPS

Dictionary mapping each crystal system to its default (highest symmetry) point group.

### NAMED_FORMS

Dictionary mapping common form names to their Miller indices:

| Name | Miller Index |
|------|-------------|
| `octahedron` | {111} |
| `cube` | {100} |
| `dodecahedron` | {110} |
| `trapezohedron` | {211} |
| `prism` | {10-10} |
| `basal` | {0001} |
| `rhombohedron` | {10-11} |

### TWIN_LAWS

Set of recognized twin law names:

- `spinel` - Spinel law (111) twin
- `brazil` - Brazil law quartz twin
- `japan` - Japan law quartz twin
- `fluorite` - Fluorite interpenetration twin
- `iron_cross` - Iron cross pyrite twin

## Exceptions

### ParseError

Raised when parsing fails due to syntax errors.

```python
from cdl_parser import ParseError

try:
    desc = parse_cdl("invalid{{{")
except ParseError as e:
    print(f"Syntax error at position {e.position}: {e.message}")
```

::: cdl_parser.ParseError

### ValidationError

Raised when validation fails due to invalid values.

```python
from cdl_parser import ValidationError

try:
    desc = parse_cdl("invalid[xxx]:{111}")
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

::: cdl_parser.ValidationError
