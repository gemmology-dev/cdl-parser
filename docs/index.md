# CDL Parser

**Crystal Description Language (CDL) Parser** - A Python library for parsing compact string notation describing crystal morphology for gemmological and mineralogical visualization.

Part of the [Gemmology Project](https://gemmology.dev).

## Overview

CDL Parser provides a robust parser for the Crystal Description Language, a notation system for describing crystal morphology using:

- **7 Crystal Systems**: Cubic, tetragonal, orthorhombic, hexagonal, trigonal, monoclinic, triclinic
- **32 Point Groups**: Full crystallographic point group support
- **Miller Indices**: Both 3-index (hkl) and 4-index (hkil) notation
- **Named Forms**: Common forms like octahedron, cube, prism
- **Twin Laws**: Support for contact, penetration, and cyclic twins

## Installation

```bash
pip install gemmology-cdl-parser
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

## CDL Syntax

The basic syntax follows this pattern:

```
system[point_group]:{form}@scale + {form}@scale | modification | twin(law)
```

### Crystal Systems

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

### Scale Values

The `@scale` parameter controls the relative prominence of forms:

```python
# Larger scale = form appears more (more truncation)
"{111}@1.0 + {100}@1.3"  # Cube truncates the octahedron
"{111}@1.0 + {100}@0.3"  # Octahedron with small cube facets
```

## Integration

CDL Parser integrates with the Gemmology Project ecosystem:

```python
from cdl_parser import parse_cdl
from crystal_geometry import cdl_to_geometry
from crystal_renderer import generate_cdl_svg

# Parse CDL string to geometry
cdl = "cubic[m3m]:{111}@1.0 + {100}@1.3"
desc = parse_cdl(cdl)
geometry = cdl_to_geometry(desc)

# Or render directly to SVG
generate_cdl_svg(cdl, "crystal.svg")
```

## Related Packages

- [crystal-geometry](https://crystal-geometry.gemmology.dev) - 3D geometry from CDL
- [mineral-database](https://mineral-database.gemmology.dev) - Mineral presets
- [crystal-renderer](https://crystal-renderer.gemmology.dev) - SVG/3D rendering
- [cdl-lsp](https://cdl-lsp.gemmology.dev) - IDE language server

## License

MIT License - see [LICENSE](https://github.com/gemmology-dev/cdl-parser/blob/main/LICENSE) for details.
