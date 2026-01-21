# CDL Specification

Complete reference for the Crystal Description Language (CDL) syntax and semantics.

## Syntax Overview

CDL uses a compact notation to describe crystal morphology:

```
system[point_group]:{form}@scale + {form}@scale | modification | twin(law)
```

### Components

| Component | Required | Description |
|-----------|----------|-------------|
| `system` | Yes | Crystal system name |
| `[point_group]` | No | Point group (defaults to highest symmetry) |
| `:{form}` | Yes | At least one crystal form |
| `@scale` | No | Scale factor (default: 1.0) |
| `+ {form}` | No | Additional forms |
| `\| modification` | No | Shape modifications |
| `\| twin(law)` | No | Twin specification |

---

## Crystal Systems

All 7 crystal systems are supported:

| System | Axes | Angles | Default Point Group |
|--------|------|--------|---------------------|
| `cubic` | a = b = c | α = β = γ = 90° | m3m |
| `tetragonal` | a = b ≠ c | α = β = γ = 90° | 4/mmm |
| `orthorhombic` | a ≠ b ≠ c | α = β = γ = 90° | mmm |
| `hexagonal` | a = b ≠ c | α = β = 90°, γ = 120° | 6/mmm |
| `trigonal` | a = b ≠ c | α = β = 90°, γ = 120° | -3m |
| `monoclinic` | a ≠ b ≠ c | α = γ = 90°, β ≠ 90° | 2/m |
| `triclinic` | a ≠ b ≠ c | α ≠ β ≠ γ ≠ 90° | -1 |

---

## Point Groups

### Complete Reference

#### Cubic System (5 point groups)

| Point Group | Symmetry | Operations | Example Minerals |
|-------------|----------|------------|------------------|
| `m3m` | Full cubic | 48 | Diamond, garnet, fluorite |
| `432` | Rotations only | 24 | Sal ammoniac |
| `-43m` | Tetrahedral | 24 | Sphalerite, tetrahedrite |
| `m-3` | With center | 24 | Pyrite |
| `23` | Minimal cubic | 12 | Ullmannite |

#### Tetragonal System (7 point groups)

| Point Group | Symmetry | Operations | Example Minerals |
|-------------|----------|------------|------------------|
| `4/mmm` | Full tetragonal | 16 | Zircon, rutile |
| `422` | Rotations | 8 | Phosgenite |
| `4mm` | Pyramidal | 8 | Diabolite |
| `-42m` | Scalenohedral | 8 | Chalcopyrite |
| `4/m` | With center | 8 | Scheelite |
| `-4` | Tetragonal disphenoidal | 4 | Cahnite |
| `4` | Pyramidal | 4 | Wulfenite |

#### Hexagonal System (7 point groups)

| Point Group | Symmetry | Operations | Example Minerals |
|-------------|----------|------------|------------------|
| `6/mmm` | Full hexagonal | 24 | Beryl, apatite |
| `622` | Trapezoidal | 12 | High quartz |
| `6mm` | Pyramidal | 12 | Wurtzite |
| `-6m2` | Ditrigonal dipyramidal | 12 | Benitoite |
| `6/m` | Dipyramidal | 12 | Apatite |
| `-6` | Trigonal dipyramidal | 6 | - |
| `6` | Pyramidal | 6 | Nepheline |

#### Trigonal System (5 point groups)

| Point Group | Symmetry | Operations | Example Minerals |
|-------------|----------|------------|------------------|
| `-3m` | Ditrigonal scalenohedral | 12 | Calcite, corundum |
| `32` | Trapezoidal | 6 | Quartz, cinnabar |
| `3m` | Ditrigonal pyramidal | 6 | Tourmaline |
| `-3` | Rhombohedral | 6 | Dolomite |
| `3` | Trigonal pyramidal | 3 | - |

#### Orthorhombic System (3 point groups)

| Point Group | Symmetry | Operations | Example Minerals |
|-------------|----------|------------|------------------|
| `mmm` | Full orthorhombic | 8 | Topaz, olivine |
| `222` | Disphenoidal | 4 | Epsomite |
| `mm2` | Pyramidal | 4 | Hemimorphite |

#### Monoclinic System (3 point groups)

| Point Group | Symmetry | Operations | Example Minerals |
|-------------|----------|------------|------------------|
| `2/m` | Prismatic | 4 | Orthoclase, gypsum |
| `m` | Domatic | 2 | Clinohedrite |
| `2` | Sphenoidal | 2 | Sucrose |

#### Triclinic System (2 point groups)

| Point Group | Symmetry | Operations | Example Minerals |
|-------------|----------|------------|------------------|
| `-1` | Pinacoidal | 2 | Albite, turquoise |
| `1` | Pedial | 1 | - |

---

## Miller Indices

### 3-Index Notation (hkl)

Standard notation for cubic, tetragonal, orthorhombic, monoclinic, and triclinic systems:

```
{hkl}     # General form
{111}     # Octahedron in cubic
{100}     # Cube in cubic
{110}     # Dodecahedron in cubic
{211}     # Trapezohedron in cubic
```

### 4-Index Notation (hkil) - Miller-Bravais

Used for hexagonal and trigonal systems where **i = -(h+k)**:

```
{hkil}      # General form (i is redundant but conventional)
{10-10}     # Hexagonal prism (h=1, k=0, i=-1, l=0)
{0001}      # Basal pinacoid
{10-11}     # Rhombohedron
{11-20}     # Second-order prism
```

### Notation Rules

| Format | Example | Description |
|--------|---------|-------------|
| Condensed | `{111}` | Single digits concatenated |
| Spaced | `{1 1 1}` | Space-separated (multi-digit) |
| Negative | `{10-11}` | Minus before digit |
| Multi-digit | `{12 3 4}` | Space required |

### Common Cubic Forms

| Miller Index | Name | Faces |
|--------------|------|-------|
| {111} | Octahedron | 8 |
| {100} | Cube | 6 |
| {110} | Dodecahedron | 12 |
| {211} | Trapezohedron | 24 |
| {221} | Trisoctahedron | 24 |
| {311} | Tetrahexahedron | 24 |
| {210} | Tetrahexahedron | 24 |
| {321} | Hexoctahedron | 48 |

### Common Hexagonal/Trigonal Forms

| Miller Index | Name | Faces |
|--------------|------|-------|
| {0001} | Basal pinacoid | 2 |
| {10-10} | First-order prism | 6 |
| {11-20} | Second-order prism | 6 |
| {10-11} | Positive rhombohedron | 6 |
| {01-11} | Negative rhombohedron | 6 |
| {10-12} | Positive scalenohedron | 12 |
| {11-21} | Trigonal dipyramid | 6 |

---

## Named Forms

Named forms can be used instead of Miller indices:

### Cubic Named Forms

| Name | Miller Index | Description |
|------|-------------|-------------|
| `octahedron` | {111} | 8-faced regular solid |
| `cube` | {100} | 6-faced regular solid |
| `dodecahedron` | {110} | 12-faced rhombic solid |
| `trapezohedron` | {211} | 24-faced solid |
| `trisoctahedron` | {221} | 24 triangular faces |
| `tetrahexahedron` | {210} | 24 quadrilateral faces |
| `hexoctahedron` | {321} | 48-faced solid |

### Hexagonal/Trigonal Named Forms

| Name | Miller Index | Description |
|------|-------------|-------------|
| `prism` | {10-10} | Hexagonal prism |
| `prism_1` | {10-10} | First-order prism |
| `prism_2` | {11-20} | Second-order prism |
| `basal` | {0001} | Basal pinacoid |
| `pinacoid` | {0001} | Same as basal |
| `rhombohedron` | {10-11} | 6-faced form |
| `rhombohedron_r` | {10-11} | Positive rhombohedron |
| `rhombohedron_z` | {01-11} | Negative rhombohedron |
| `pyramid` | {10-11} | Hexagonal pyramid |
| `dipyramid` | {10-11} | Hexagonal dipyramid |
| `scalenohedron` | {21-31} | 12-faced form |

### Tetragonal Named Forms

| Name | Miller Index | Description |
|------|-------------|-------------|
| `prism` | {100} | Tetragonal prism |
| `prism_1` | {100} | First-order prism |
| `prism_2` | {110} | Second-order prism |
| `pyramid` | {101} | Tetragonal pyramid |
| `dipyramid` | {101} | Tetragonal dipyramid |
| `bipyramid` | {111} | Tetragonal bipyramid |

---

## Scale Values

The `@scale` parameter controls form prominence:

```python
{111}@1.0 + {100}@1.3   # Cube truncates octahedron
{111}@1.0 + {100}@0.3   # Small cube facets on octahedron
```

### Interpretation

- **Larger scale** = Face is further from center = More prominent
- **Smaller scale** = Face is closer to center = Less prominent
- **Equal scales** = Forms meet at equal distances

### Recommended Ranges

| Purpose | Scale Range |
|---------|-------------|
| Dominant form | 1.0 |
| Moderate truncation | 0.3 - 0.8 |
| Heavy truncation | 1.2 - 2.0 |
| Subtle modification | 0.1 - 0.3 |

---

## Modifications

Modifications alter the crystal shape after form generation.

### elongate

Stretch the crystal along an axis:

```
{111} | elongate(c:1.5)    # Stretch 1.5x along c-axis
{111} | elongate(a:2.0)    # Stretch 2x along a-axis
{111} | elongate(-c:0.8)   # Compress along negative c
```

**Parameters:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| axis | `a`, `b`, `c`, `+a`, `-a`, etc. | Axis direction |
| ratio | 0.1 - 10.0 | Stretch factor |

### truncate

Truncate edges or vertices:

```
{111} | truncate(vertex:0.2)   # Truncate vertices
{111} | truncate(edge:0.3)     # Truncate edges
{111} | truncate({100}:0.5)    # Truncate with specific form
```

**Parameters:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| target | `vertex`, `edge`, `{hkl}` | What to truncate |
| depth | 0.0 - 1.0 | Truncation depth |

### taper

Create a tapered crystal shape:

```
{111} | taper(+c:0.8)    # Taper toward +c direction
{111} | taper(-c:0.5)    # Taper toward -c direction
```

**Parameters:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| direction | `+a`, `-a`, `+b`, `-b`, `+c`, `-c` | Taper direction |
| factor | 0.0 - 1.0 | Taper amount (0 = no taper, 1 = point) |

### bevel

Bevel edges of the crystal:

```
{111} | bevel(all:0.1)     # Bevel all edges
{111} | bevel(top:0.2)     # Bevel top edges only
```

**Parameters:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| edges | `all`, `top`, `bottom`, `vertical` | Which edges |
| width | 0.0 - 0.5 | Bevel width |

---

## Twin Specifications

Twins are described using the `twin()` modification.

### Contact Twins

Two crystals sharing a composition plane:

```
{111} | twin(spinel)       # Spinel law twin
{10-10} | twin(japan)      # Japan law quartz twin
{10-10} | twin(brazil)     # Brazil law quartz twin
```

### Penetration Twins

Two crystals interpenetrating:

```
{100} | twin(fluorite)     # Fluorite interpenetration
{210} | twin(iron_cross)   # Pyrite iron cross
```

### Cyclic Twins

Multiple crystals in cyclic arrangement:

```
{10-11} | twin(trilling, 3)   # Three-fold cyclic twin
{10-11} | twin(sixling, 6)    # Six-fold cyclic twin
```

### Complete Twin Laws Reference

| Law | Type | System | Description |
|-----|------|--------|-------------|
| `spinel` | Contact | Cubic | Twin on {111}, common in spinel |
| `spinel_law` | Contact | Cubic | Same as spinel |
| `iron_cross` | Penetration | Cubic | {110} twin, pyrite |
| `fluorite` | Penetration | Cubic | Interpenetration twin |
| `brazil` | Contact | Trigonal | Optical twin in quartz |
| `dauphine` | Contact | Trigonal | Electrical twin in quartz |
| `japan` | Contact | Trigonal | {11-22} twin in quartz |
| `carlsbad` | Penetration | Monoclinic | Common in orthoclase |
| `baveno` | Contact | Monoclinic | {021} twin in feldspar |
| `manebach` | Contact | Monoclinic | {001} twin in feldspar |
| `albite` | Contact | Triclinic | Polysynthetic in plagioclase |
| `pericline` | Contact | Triclinic | Twin in albite |
| `gypsum_swallow` | Penetration | Monoclinic | Swallow-tail in gypsum |
| `staurolite_60` | Penetration | Monoclinic | 60° cross |
| `staurolite_90` | Penetration | Monoclinic | 90° cross |
| `trilling` | Cyclic | Any | Three individuals |

### Custom Twin Axis

Specify custom twin axis and angle:

```
{111} | twin([1,1,1], 180, contact)    # Custom axis
{111} | twin([1,0,0], 90, penetration) # 90° rotation about a-axis
```

---

## Complete Examples

### Diamond

```
cubic[m3m]:{111}@1.0 + {110}@0.2
```

Octahedron with small dodecahedron modification.

### Garnet

```
cubic[m3m]:{110}@1.0 + {211}@0.6
```

Dodecahedron with trapezohedron.

### Quartz

```
trigonal[32]:{10-10}@1.0 + {10-11}@0.8 + {01-11}@0.8
```

Prism with positive and negative rhombohedra.

### Ruby/Sapphire

```
trigonal[-3m]:{10-10}@1.0 + {0001}@0.3 + {10-11}@0.5
```

Hexagonal prism with pinacoid and rhombohedron.

### Beryl/Emerald

```
hexagonal[6/mmm]:{10-10}@1.0 + {0001}@0.5
```

Hexagonal prism with basal pinacoid.

### Spinel Twin

```
cubic[m3m]:{111} | twin(spinel)
```

Twinned octahedron (macle).

### Japan Law Quartz Twin

```
trigonal[32]:{10-10}@1.0 + {10-11}@0.8 | twin(japan)
```

---

## Grammar (EBNF)

```ebnf
cdl         = system, [point_group], ":", forms, {modification} ;
system      = "cubic" | "tetragonal" | "orthorhombic"
            | "hexagonal" | "trigonal" | "monoclinic" | "triclinic" ;
point_group = "[", symbol, "]" ;
forms       = form, {"+" , form} ;
form        = (miller | named_form), ["@", scale] ;
miller      = "{", indices, "}" ;
indices     = index, index, index, [index] ;  (* 3 or 4 indices *)
index       = ["-"], digit, {digit} ;
named_form  = letter, {letter | "_" | digit} ;
scale       = number ;
modification = "|", (mod_call | twin_call) ;
mod_call    = mod_name, "(", parameters, ")" ;
twin_call   = "twin", "(", twin_spec, ")" ;
twin_spec   = twin_law, [",", count] | custom_twin ;
custom_twin = "[", axis, "]", ",", angle, ",", twin_type ;
```

---

## Error Messages

### Parse Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Unknown crystal system" | Invalid system name | Check spelling |
| "Invalid point group for system" | Mismatch | Use correct point group |
| "Invalid Miller index" | Bad notation | Check index format |
| "Expected ':'" | Missing colon | Add colon after system |
| "Unexpected character" | Syntax error | Check special characters |

### Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "4-index constraint violated" | i ≠ -(h+k) | Fix Miller-Bravais index |
| "Unknown twin law" | Invalid twin name | Check twin law spelling |
| "Unknown modification" | Invalid mod name | Use valid modification |
