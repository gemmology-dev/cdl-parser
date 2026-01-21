# Examples

## Basic Usage

### Parsing Crystal Descriptions

```python
from cdl_parser import parse_cdl

# Parse a simple octahedron
desc = parse_cdl("cubic[m3m]:{111}")
print(f"System: {desc.system}")          # cubic
print(f"Point group: {desc.point_group}") # m3m
print(f"Forms: {len(desc.forms)}")        # 1
```

### Accessing Form Data

```python
from cdl_parser import parse_cdl

desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")

for form in desc.forms:
    miller = form.miller
    print(f"Form: ({miller.h}{miller.k}{miller.l}) @ {form.scale}")
# Output:
# Form: (111) @ 1.0
# Form: (100) @ 1.3
```

### Validation

```python
from cdl_parser import validate_cdl

# Valid input
is_valid, error = validate_cdl("cubic[m3m]:{111}")
print(f"Valid: {is_valid}")  # True

# Invalid input
is_valid, error = validate_cdl("invalid[xxx]:{111}")
print(f"Valid: {is_valid}, Error: {error}")  # False, "Unknown crystal system..."
```

## Crystal Systems

### Cubic System

```python
from cdl_parser import parse_cdl

# Octahedron
octahedron = parse_cdl("cubic[m3m]:{111}")

# Cube
cube = parse_cdl("cubic[m3m]:{100}")

# Dodecahedron
dodecahedron = parse_cdl("cubic[m3m]:{110}")

# Diamond-like (truncated octahedron)
diamond = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@0.3")

# Garnet-like (dodecahedron + trapezohedron)
garnet = parse_cdl("cubic[m3m]:{110}@1.0 + {211}@0.6")

# Fluorite cube
fluorite = parse_cdl("cubic[m3m]:{100}")
```

### Hexagonal System

```python
from cdl_parser import parse_cdl

# Hexagonal prism with pinacoid
beryl = parse_cdl("hexagonal[6/mmm]:{10-10}@1.0 + {0001}@0.5")

# Using named forms
prism = parse_cdl("hexagonal[6/mmm]:prism + basal@0.5")
```

### Trigonal System

```python
from cdl_parser import parse_cdl

# Quartz prism with rhombohedron
quartz = parse_cdl("trigonal[-3m]:{10-10}@1.0 + {10-11}@0.8")

# Simple rhombohedron
calcite = parse_cdl("trigonal[-3m]:{10-11}")
```

### Tetragonal System

```python
from cdl_parser import parse_cdl

# Zircon-like prism with pyramid
zircon = parse_cdl("tetragonal[4/mmm]:{100}@1.0 + {101}@0.8")

# Rutile prism
rutile = parse_cdl("tetragonal[4/mmm]:{110}@1.0 + {101}@0.5")
```

### Orthorhombic System

```python
from cdl_parser import parse_cdl

# Topaz-like prism with dome
topaz = parse_cdl("orthorhombic[mmm]:{110}@1.0 + {011}@0.6")
```

## Named Forms

```python
from cdl_parser import parse_cdl, NAMED_FORMS

# View available named forms
print("Available named forms:")
for name, miller in NAMED_FORMS.items():
    print(f"  {name}: {miller}")

# Use named forms in CDL
desc = parse_cdl("cubic[m3m]:octahedron")
print(desc.forms[0].miller.as_tuple())  # (1, 1, 1)

# Combine named forms
desc = parse_cdl("cubic[m3m]:cube + octahedron@0.5")
print(len(desc.forms))  # 2
```

## Twin Specifications

### Contact Twins

```python
from cdl_parser import parse_cdl

# Spinel law twin (common in spinels)
spinel_twin = parse_cdl("cubic[m3m]:{111} | twin(spinel)")
print(f"Twin law: {spinel_twin.twin.law}")  # spinel

# Brazil law quartz twin
brazil_twin = parse_cdl("trigonal[-3m]:{10-10} + {10-11} | twin(brazil)")
```

### Penetration Twins

```python
from cdl_parser import parse_cdl

# Fluorite interpenetration twin
fluorite_twin = parse_cdl("cubic[m3m]:{100} | twin(fluorite)")

# Iron cross pyrite twin
pyrite_twin = parse_cdl("cubic[m3m]:{210} | twin(iron_cross)")
```

### Cyclic Twins

```python
from cdl_parser import parse_cdl

# Three-fold cyclic twin (trilling)
trilling = parse_cdl("trigonal[-3m]:{10-11} | twin(trilling,3)")
print(f"Twin law: {trilling.twin.law}")  # trilling
print(f"Repeat: {trilling.twin.repeat}")  # 3
```

## Integration Examples

### With crystal-geometry

```python
from cdl_parser import parse_cdl
from crystal_geometry import cdl_to_geometry

# Parse CDL and generate 3D geometry
cdl = "cubic[m3m]:{111}@1.0 + {100}@1.3"
desc = parse_cdl(cdl)
geometry = cdl_to_geometry(desc)

print(f"Vertices: {len(geometry.vertices)}")
print(f"Faces: {len(geometry.faces)}")
```

### With crystal-renderer

```python
from cdl_parser import parse_cdl
from crystal_renderer import generate_cdl_svg

# Direct CDL to SVG
generate_cdl_svg(
    "cubic[m3m]:{111}@1.0 + {100}@1.3",
    "diamond.svg",
    show_axes=True
)
```

### With mineral-database

```python
from mineral_database import get_preset
from cdl_parser import parse_cdl

# Get preset CDL string
diamond = get_preset('diamond')
cdl_string = diamond['cdl']

# Parse and inspect
desc = parse_cdl(cdl_string)
print(f"Diamond forms: {len(desc.forms)}")
```

## Error Handling

```python
from cdl_parser import parse_cdl, ParseError, ValidationError

# Syntax error
try:
    desc = parse_cdl("invalid{{{")
except ParseError as e:
    print(f"Parse error at position {e.position}: {e.message}")

# Validation error
try:
    desc = parse_cdl("unknown[xxx]:{111}")
except ValidationError as e:
    print(f"Validation error: {e.message}")

# Safe validation
from cdl_parser import validate_cdl

is_valid, error = validate_cdl("some user input")
if not is_valid:
    print(f"Invalid CDL: {error}")
```

## Working with Miller Indices

```python
from cdl_parser import parse_cdl

# 3-index notation
desc = parse_cdl("cubic[m3m]:{111}")
miller = desc.forms[0].miller
print(f"3-index: ({miller.h}, {miller.k}, {miller.l})")
print(f"As tuple: {miller.as_tuple()}")  # (1, 1, 1)

# 4-index notation (hexagonal/trigonal)
desc = parse_cdl("hexagonal[6/mmm]:{10-10}")
miller = desc.forms[0].miller
print(f"4-index: ({miller.h}, {miller.k}, {miller.i}, {miller.l})")
print(f"As 3-index: {miller.as_3index()}")  # Converts to 3-index
```
