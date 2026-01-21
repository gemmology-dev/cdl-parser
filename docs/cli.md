# CLI Usage

The `cdl` command-line tool provides parsing, validation, and exploration of CDL notation.

## Installation

The CLI is installed automatically with the package:

```bash
pip install gemmology-cdl-parser
```

## Commands

### Parse

Parse and display a CDL string:

```bash
cdl parse "cubic[m3m]:{111}@1.0 + {100}@1.3"
```

Output:
```
Crystal Description:
  System: cubic
  Point Group: m3m
  Forms:
    - {111} @ 1.0
    - {100} @ 1.3
```

### Validate

Validate a CDL string without parsing:

```bash
cdl validate "cubic[m3m]:{111}"
```

Output:
```
Valid CDL string
```

Invalid input:
```bash
cdl validate "invalid[xxx]:{111}"
```

Output:
```
Invalid: Unknown crystal system 'invalid'
```

### JSON Output

Output parsed result as JSON:

```bash
cdl parse "cubic[m3m]:{111}" --json
```

Output:
```json
{
  "system": "cubic",
  "point_group": "m3m",
  "forms": [
    {
      "miller": {"h": 1, "k": 1, "l": 1},
      "scale": 1.0
    }
  ],
  "modifications": [],
  "twin": null
}
```

### List Options

List available crystal systems:

```bash
cdl --list-systems
```

Output:
```
Crystal Systems:
  cubic
  tetragonal
  orthorhombic
  hexagonal
  trigonal
  monoclinic
  triclinic
```

List point groups:

```bash
cdl --list-point-groups
```

Output:
```
Point Groups by System:
  cubic: m3m, 432, -43m, m-3, 23
  tetragonal: 4/mmm, 422, 4mm, -42m, 4/m, -4, 4
  ...
```

List named forms:

```bash
cdl --list-forms
```

Output:
```
Named Forms:
  octahedron  -> {111}
  cube        -> {100}
  dodecahedron -> {110}
  ...
```

List twin laws:

```bash
cdl --list-twins
```

Output:
```
Twin Laws:
  spinel      - Spinel law (111) contact twin
  brazil      - Brazil law quartz twin
  japan       - Japan law quartz twin
  fluorite    - Fluorite interpenetration twin
  iron_cross  - Iron cross pyrite twin
```

## Examples

### Basic Parsing

```bash
# Simple octahedron
cdl parse "cubic[m3m]:{111}"

# Diamond-like truncated octahedron
cdl parse "cubic[m3m]:{111}@1.0 + {100}@1.3"

# Quartz prism with rhombohedron
cdl parse "trigonal[-3m]:{10-10}@1.0 + {10-11}@0.8"
```

### Using Named Forms

```bash
# Using named form instead of Miller index
cdl parse "cubic[m3m]:octahedron"

# Combining named forms
cdl parse "cubic[m3m]:cube + octahedron@0.5"
```

### Twin Specifications

```bash
# Spinel-law twinned octahedron
cdl parse "cubic[m3m]:{111} | twin(spinel)"

# Japan law quartz twin
cdl parse "trigonal[-3m]:{10-10} + {10-11} | twin(japan)"
```

### Scripting

Use with shell scripting:

```bash
# Validate multiple CDL strings
for cdl in "cubic[m3m]:{111}" "cubic[m3m]:{100}" "invalid"; do
    if cdl validate "$cdl" 2>/dev/null; then
        echo "$cdl: valid"
    else
        echo "$cdl: invalid"
    fi
done
```

Process JSON output with jq:

```bash
cdl parse "cubic[m3m]:{111}@1.0 + {100}@1.3" --json | jq '.forms[].miller'
```
