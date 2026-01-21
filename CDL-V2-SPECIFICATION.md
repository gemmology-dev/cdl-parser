# Crystal Description Language (CDL) Version 2.0 Specification

**Status**: Draft Proposal
**Version**: 2.0.0
**Date**: January 2026
**Authors**: Gemmology Project Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Design Principles](#2-design-principles)
3. [Backwards Compatibility](#3-backwards-compatibility)
4. [Lexical Structure](#4-lexical-structure)
5. [Core Syntax](#5-core-syntax)
6. [Material Types](#6-material-types)
7. [Form Expressions](#7-form-expressions)
8. [Features System](#8-features-system)
9. [Block Composition](#9-block-composition)
10. [Nested Growth](#10-nested-growth)
11. [Aggregates](#11-aggregates)
12. [Modifications and Twins](#12-modifications-and-twins)
13. [Optical Phenomena](#13-optical-phenomena)
14. [Comments and Documentation](#14-comments-and-documentation)
15. [Named References](#15-named-references)
16. [Variants](#16-variants)
17. [Complete Grammar](#17-complete-grammar)
18. [Examples Library](#18-examples-library)
19. [Implementation Notes](#19-implementation-notes)
20. [Migration Guide](#20-migration-guide)

---

## 1. Introduction

### 1.1 Purpose

Crystal Description Language (CDL) is a domain-specific notation for describing crystal morphology in gemmology and mineralogy. CDL v2 extends the original language with support for:

- **Amorphous materials** (opal, obsidian, amber)
- **Complex growth habits** (scepter, phantom, skeletal)
- **Crystal aggregates** (clusters, druses, geodes)
- **Surface features** (striations, etch pits, trigons)
- **Inclusions** (needles, phantoms, color zones)
- **Block composition** for readable complex descriptions
- **Comments and documentation**
- **Named references** for reusability

### 1.2 Goals

1. **Expressiveness**: Describe any gemmological specimen
2. **Readability**: Clear syntax for complex structures
3. **Simplicity**: Simple crystals remain simple to describe
4. **Backwards Compatibility**: All v1 CDL remains valid
5. **Machine Parseable**: Unambiguous grammar for tooling

### 1.3 Example Overview

```cdl
# CDL v2 - Scepter Amethyst with Phantom Zones
# Origin: Vera Cruz, Mexico

@prism = {10-10}@1.0
@rhomb = {10-11}@0.8

trigonal[32]:(
    # Base crystal with internal features
    base:($prism + $rhomb)
        [phantom: 3, smoky]
        [striation: parallel]

    # Scepter overgrowth on termination
    > cap:($prism@0.5 + $rhomb@0.4)
        [colour: purple]

) ~ parallel[3] @2mm
  | elongate(c:1.2)
  | phenomenon[chatoyancy: moderate]
```

---

## 2. Design Principles

### 2.1 Progressive Complexity

CDL v2 uses **opt-in complexity**. Simple descriptions stay simple:

```cdl
# Level 1: Basic (v1 compatible)
cubic[m3m]:{111}

# Level 2: Multiple forms with scales
cubic[m3m]:{111}@1.0 + {100}@1.3

# Level 3: With features
cubic[m3m]:{111}@1.0[trigon:dense] + {100}@1.3

# Level 4: Grouped with shared features
cubic[m3m]:({111}@1.0 + {100}@1.3)[phantom:3]

# Level 5: Full complexity
cubic[m3m]:(
    core:{111}@1.0[inclusion:rutile]
    + ({100}@0.8 | twin(spinel))
)[growth:sector] ~ cluster[5]
```

### 2.2 Composability

Every construct can be combined with others:

- Forms can have features
- Groups can have features (shared by all forms)
- Groups can be nested
- Groups can be twinned
- Groups can be aggregated
- Aggregates can have features

### 2.3 Readability First

When in doubt, choose the more readable option:

- Multi-line is encouraged for complex descriptions
- Comments are first-class citizens
- Named references reduce repetition
- Labels document intent

---

## 3. Backwards Compatibility

### 3.1 Guarantee

**All valid CDL v1 is valid CDL v2.** The v2 parser accepts v1 syntax without modification.

### 3.2 v1 Syntax (Unchanged)

```cdl
system[point_group]:{hkl}@scale + {hkl}@scale | modification | twin(law)
```

Examples that continue to work:
```cdl
cubic[m3m]:{111}
cubic[m3m]:{111}@1.0 + {100}@1.3
trigonal[-3m]:{10-10}@1.0 + {10-11}@0.8
cubic[m3m]:{111} | elongate(c:1.5) | twin(spinel)
hexagonal[6/mmm]:{10-10}@1.0 + {0001}@0.5 | twin(japan)
```

### 3.3 Detection

The parser auto-detects v2 syntax by the presence of:
- `#` comments
- `[feature:]` syntax
- `(` grouping in form context
- `>` nested growth
- `~` aggregates
- `@identifier` definitions
- `amorphous` keyword

---

## 4. Lexical Structure

### 4.1 Character Set

CDL v2 uses ASCII with optional UTF-8 for comments.

### 4.2 Tokens

| Token | Pattern | Example |
|-------|---------|---------|
| SYSTEM | `cubic\|hexagonal\|...` | `trigonal` |
| POINT_GROUP | Hermann-Mauguin symbol | `m3m`, `-3m`, `6/mmm` |
| INTEGER | `[+-]?[0-9]+` | `111`, `-10` |
| FLOAT | `[+-]?[0-9]+\.[0-9]+` | `1.0`, `0.85` |
| IDENTIFIER | `[a-zA-Z_][a-zA-Z0-9_]*` | `prism`, `phantom` |
| MILLER_START | `{` | |
| MILLER_END | `}` | |
| LBRACKET | `[` | |
| RBRACKET | `]` | |
| LPAREN | `(` | |
| RPAREN | `)` | |
| COLON | `:` | |
| PLUS | `+` | |
| PIPE | `\|` | |
| AT | `@` | |
| COMMA | `,` | |
| GREATER | `>` | |
| TILDE | `~` | |
| SEMICOLON | `;` | |
| DOLLAR | `$` | |
| HASH | `#` | |
| NEWLINE | `\n` | |

### 4.3 Whitespace

- Spaces and tabs are ignored between tokens
- Newlines are significant only for comments
- Indentation is not significant (but encouraged for readability)

### 4.4 Comments

```cdl
# Line comment - extends to end of line
{111}@1.0  # Inline comment

/* Block comment
   spans multiple
   lines */
```

---

## 5. Core Syntax

### 5.1 Document Structure

A CDL v2 document consists of:

```
[definitions]*
material_description
```

### 5.2 Material Description

```
crystalline_description | amorphous_description
```

### 5.3 Crystalline Description

```
system [point_group]? : form_expression [aggregate_clause]? [modifier_clause]* [phenomenon_clause]?
```

### 5.4 Amorphous Description

```
amorphous [subtype]? : shape_list [property_list]?
```

---

## 6. Material Types

### 6.1 Crystalline Materials

The seven crystal systems with their point groups:

| System | Point Groups | Default |
|--------|--------------|---------|
| cubic | m3m, 432, -43m, m-3, 23 | m3m |
| hexagonal | 6/mmm, 622, 6mm, -6m2, 6/m, -6, 6 | 6/mmm |
| trigonal | -3m, 32, 3m, -3, 3 | -3m |
| tetragonal | 4/mmm, 422, 4mm, -42m, 4/m, -4, 4 | 4/mmm |
| orthorhombic | mmm, 222, mm2 | mmm |
| monoclinic | 2/m, m, 2 | 2/m |
| triclinic | -1, 1 | -1 |

```cdl
cubic[m3m]:{111}           # Explicit point group
cubic:{111}                # Uses default m3m
```

### 6.2 Amorphous Materials

For non-crystalline gems (opal, obsidian, glass, amber):

```cdl
amorphous:{shape}[properties]
amorphous[subtype]:{shape}[properties]
```

**Subtypes:**
- `opalescent` - Play of color (precious opal)
- `glassy` - Vitreous, conchoidal fracture
- `waxy` - Waxy luster
- `resinous` - Resin-like (amber)
- `cryptocrystalline` - Microcrystalline aggregate

**Shape descriptors:**
- `massive` - No defined external form
- `botryoidal` - Grape-like spherical clusters
- `reniform` - Kidney-shaped
- `stalactitic` - Hanging formations
- `mammillary` - Breast-like rounded surfaces
- `nodular` - Irregular nodules
- `conchoidal` - Shell-like fracture surfaces

**Examples:**
```cdl
# Precious opal with play of color
amorphous[opalescent]:{botryoidal}[play_of_color:intense]

# Obsidian - volcanic glass
amorphous[glassy]:{massive, conchoidal}

# Amber with inclusions
amorphous[resinous]:{nodular}[inclusion:insect]

# Chalcedony - cryptocrystalline quartz
amorphous[cryptocrystalline]:{botryoidal}[banding:agate]
```

---

## 7. Form Expressions

### 7.1 Miller Indices

**3-Index Notation** (cubic, tetragonal, orthorhombic, monoclinic, triclinic):
```cdl
{hkl}     # Standard form
{111}     # Octahedron
{100}     # Cube
{110}     # Dodecahedron
{1 1 1}   # Spaced format
{-1 1 0}  # Negative index
```

**4-Index Miller-Bravais** (hexagonal, trigonal):
```cdl
{hkil}    # Where i = -(h+k)
{10-10}   # Hexagonal prism
{10-11}   # Positive rhombohedron
{01-11}   # Negative rhombohedron
{0001}    # Basal pinacoid
```

### 7.2 Named Forms

Common crystal forms can be referenced by name:

```cdl
# Cubic system
cube           → {100}
octahedron     → {111}
dodecahedron   → {110}
trapezohedron  → {211}
tetrahexahedron → {210}
trisoctahedron → {221}
hexoctahedron  → {321}

# Hexagonal/Trigonal
prism          → {10-10}
pinacoid       → {0001}
rhombohedron   → {10-11}
dipyramid      → {10-11}

# Usage
cubic[m3m]:octahedron@1.0 + cube@1.3
```

### 7.3 Scale Factors

```cdl
{hkl}@scale    # Scale controls relative prominence
{111}@1.0      # Reference scale
{100}@1.3      # Larger = more truncation by this form
{110}@0.5      # Smaller = less prominent
```

### 7.4 Form Labels

Optional labels document form purpose:

```cdl
prism:{10-10}@1.0           # Labeled "prism"
term:{10-11}@0.8            # Labeled "term" (termination)
cap:{10-10}@0.5             # Labeled "cap" (scepter cap)
```

---

## 8. Features System

### 8.1 Feature Syntax

Features are specified in square brackets after forms or groups:

```cdl
form[feature:value]
form[feature:value, feature:value]
(group)[feature:value]
```

### 8.2 Growth Features

Describe internal growth patterns:

| Feature | Values | Description |
|---------|--------|-------------|
| `phantom` | count, color | Internal growth zones |
| `sector` | type | Sector zoning patterns |
| `zoning` | pattern | Color/composition zones |
| `skeletal` | ratio (0-1) | Skeletal/hopper growth |
| `dendritic` | density | Branching growth |

```cdl
{10-10}@1.0[phantom:3, white]      # 3 white phantom zones
{111}@1.0[sector:hourglass]        # Hourglass sector zoning
{10-10}@1.0[skeletal:0.4]          # 40% skeletal
```

### 8.3 Surface Features

Describe external surface markings:

| Feature | Values | Description |
|---------|--------|-------------|
| `striation` | direction, count | Surface striations |
| `trigon` | density | Triangular etch pits (diamond) |
| `etch_pit` | density | Dissolution features |
| `growth_hillock` | density | Growth spirals |

```cdl
{111}@1.0[trigon:dense]            # Dense trigons on octahedron
{10-10}@1.0[striation:parallel, 5] # 5 parallel striations
```

### 8.4 Inclusion Features

Describe internal inclusions:

| Feature | Values | Description |
|---------|--------|-------------|
| `inclusion` | mineral | Solid inclusions |
| `needle` | mineral, density | Needle-like inclusions |
| `silk` | pattern | Fine needle networks |
| `fluid` | type | Fluid inclusions |
| `bubble` | type | Gas/fluid bubbles |

```cdl
{10-10}@1.0[needle:rutile, 0.3]    # Rutile needles, 30% density
{111}@1.0[silk:asterism]           # Silk for star effect
```

### 8.5 Color Features

| Feature | Values | Description |
|---------|--------|-------------|
| `colour` | color name | Overall color |
| `colour_zone` | colors, count | Color banding |
| `pleochroism` | colors | Direction-dependent color |

```cdl
{10-10}@1.0[colour:purple]
{10-10}@1.0[colour_zone:pink-green-pink, 3]  # Watermelon
```

### 8.6 Feature Inheritance

Features on groups apply to all contained forms:

```cdl
# Both {111} and {100} get phantom:3
({111}@1.0 + {100}@1.3)[phantom:3]

# Mixed: group feature + individual features
({111}@1.0[trigon:dense] + {100}@1.3)[phantom:3]
# Result: {111} has trigon + phantom, {100} has phantom
```

---

## 9. Block Composition

### 9.1 Grouping with Parentheses

Parentheses `(...)` group forms for:
- Shared features
- Collective operations (twinning, aggregation)
- Readability

```cdl
# Shared features
({111}@1.0 + {100}@1.3 + {110}@0.8)[phantom:3]

# Multi-line grouping
(
    prism:{10-10}@1.0
    + pos_rhomb:{10-11}@0.8
    + neg_rhomb:{01-11}@0.7
)[colour:purple]
```

### 9.2 Labeled Groups

Labels document group purpose:

```cdl
(base: {10-10}@1.0 + {10-11}@0.8)
(termination: {10-11}@0.8 + {01-11}@0.7)
(core: {111}@1.0)[inclusion:rutile]
```

### 9.3 Nested Groups

Groups can contain groups:

```cdl
(
    (core: {111}@1.0)[colour:colourless]
    + (rim: {100}@0.5)[colour:blue]
)[phantom:2]
```

### 9.4 Operator Precedence

From highest to lowest binding:

| Precedence | Operator | Description | Associativity |
|------------|----------|-------------|---------------|
| 1 | `@` | Scale | Left |
| 2 | `[...]` | Features | Left |
| 3 | `>` | Nested growth | **Right** |
| 4 | `~` | Aggregate | Left |
| 5 | `+` | Form addition | Left |
| 6 | `\|` | Modification/twin | Left |
| 7 | `;` | Variants | N/A |

```cdl
# Precedence examples
{111}@1.0[phantom:3] + {100}@1.3
# Parses as: ({111}@1.0)[phantom:3] + {100}@1.3

base > cap > tip
# Parses as: base > (cap > tip)  [right associative]
```

---

## 10. Nested Growth

### 10.1 Overgrowth Operator `>`

The `>` operator models epitaxial overgrowth:

```cdl
base > overgrowth
```

Semantics: The overgrowth crystal grows on the termination of the base crystal.

### 10.2 Scepter Crystals

```cdl
# Basic scepter quartz
trigonal[32]:
    {10-10}@1.0 + {10-11}@0.8
    > {10-10}@0.5 + {10-11}@0.4

# Labeled for clarity
trigonal[32]:
    (base: {10-10}@1.0 + {10-11}@0.8)
    > (cap: {10-10}@0.5 + {10-11}@0.4)
```

### 10.3 Multi-Generation Growth

Right associativity allows multiple generations:

```cdl
# Three generations of growth
trigonal[32]:
    {10-10}@1.0           # First generation
    > {10-10}@0.7         # Second generation (scepter)
    > {10-10}@0.4         # Third generation (scepter on scepter)

# Equivalent explicit grouping
{10-10}@1.0 > ({10-10}@0.7 > {10-10}@0.4)
```

### 10.4 Features on Nested Growth

Each generation can have different features:

```cdl
trigonal[32]:(
    base:({10-10}@1.0 + {10-11}@0.8)[colour:smoky, phantom:2]
    > cap:({10-10}@0.5)[colour:purple]
)
```

---

## 11. Aggregates

### 11.1 Aggregate Operator `~`

The `~` operator specifies crystal arrangement:

```cdl
form ~ arrangement[count] @spacing [orientation]
```

### 11.2 Arrangement Types

| Type | Description | Use Case |
|------|-------------|----------|
| `parallel` | Aligned crystals | Stacked crystals |
| `random` | Random orientations | Natural clusters |
| `radial` | Radiating from center | Chrysanthemum stone |
| `epitaxial` | Oriented overgrowth | Rutile on quartz |
| `druse` | Lining a surface | Geode lining |
| `cluster` | 3D cluster | Crystal clusters |

### 11.3 Examples

```cdl
# Parallel growth (5 crystals, 2mm spacing)
trigonal[32]:{10-10}@1.0 ~ parallel[5] @2mm

# Random cluster (20 crystals)
cubic[m3m]:{111}@1.0 ~ cluster[20]

# Radial arrangement (12 crystals)
trigonal[-3m]:{10-10}@1.0 ~ radial[12]

# Geode/druse interior (100 crystals, 1mm spacing)
trigonal[32]:{10-10}@1.0 ~ druse[100] @1mm

# Epitaxial rutile needles in quartz
trigonal[32]:
    {10-10}@1.0  # Host quartz
    + (tetragonal[4/mmm]:{100}@0.1 ~ epitaxial[20])  # Rutile needles
```

### 11.4 Orientation Specifiers

```cdl
~ parallel[5] [aligned]      # Perfectly aligned
~ parallel[5] [offset:0.2]   # Slight offset
~ cluster[20] [random]       # Random orientations
~ radial[12] [planar]        # Radial in plane
~ radial[12] [spherical]     # Radial in 3D
```

### 11.5 Aggregate Subgroups

Different arrangements within one specimen:

```cdl
cubic[m3m]:(
    (group_a:{111}@1.0 ~ parallel[3])
    + (group_b:{111}@0.8 ~ random[5])
)
```

---

## 12. Modifications and Twins

### 12.1 Modifications

Morphological modifications use the `|` operator:

```cdl
forms | modification(params)
```

**Available modifications:**

| Modification | Parameters | Description |
|--------------|------------|-------------|
| `elongate` | axis:ratio | Stretch along axis |
| `truncate` | form:depth | Truncate with form |
| `taper` | direction:factor | Taper toward direction |
| `flatten` | axis:ratio | Compress along axis |

```cdl
cubic[m3m]:{111}@1.0 | elongate(c:1.5)
cubic[m3m]:{111}@1.0 | truncate({100}:0.3)
trigonal[32]:{10-10}@1.0 | taper(c:0.8)
```

### 12.2 Twin Laws

Twinning uses `| twin(law)`:

```cdl
forms | twin(law_name)
forms | twin([axis], angle)  # Custom twin axis
```

**Named twin laws:**

| Law | System | Description |
|-----|--------|-------------|
| `spinel` | Cubic | {111} contact twin |
| `fluorite` | Cubic | Interpenetrant twin |
| `brazil` | Trigonal | {10-10} twin |
| `dauphine` | Trigonal | 180° about c |
| `japan` | Trigonal | {11-22} contact |
| `carlsbad` | Monoclinic | [001] twin axis |
| `baveno` | Monoclinic | {021} twin |
| `manebach` | Monoclinic | {001} twin |

```cdl
cubic[m3m]:{111}@1.0 | twin(spinel)
trigonal[32]:{10-10}@1.0 | twin(japan)
cubic[m3m]:{111}@1.0 | twin([1,1,1], 60)  # Custom
```

### 12.3 Group-Level vs Crystal-Level Twins

```cdl
# Crystal-level: entire crystal is twinned
cubic[m3m]:({111}@1.0 + {100}@0.8) | twin(spinel)

# Group-level: only the group is twinned
cubic[m3m]:{110}@1.0 + ({111}@0.5 | twin(spinel))
```

### 12.4 Multiple Modifiers

```cdl
cubic[m3m]:{111}@1.0
    | elongate(c:1.3)
    | truncate({100}:0.2)
    | twin(spinel)
```

---

## 13. Optical Phenomena

### 13.1 Phenomenon Clause

Special optical effects use `| phenomenon[type:intensity]`:

```cdl
forms | phenomenon[type:intensity]
forms | phenomenon[type:intensity, param:value]
```

### 13.2 Phenomenon Types

| Phenomenon | Parameters | Description |
|------------|------------|-------------|
| `asterism` | rays (3,4,6,12) | Star effect |
| `chatoyancy` | - | Cat's eye |
| `adularescence` | - | Moonstone shimmer |
| `labradorescence` | colour | Labradorite flash |
| `play_of_color` | intensity | Opal iridescence |
| `colour_change` | colours | Alexandrite effect |
| `aventurescence` | colour | Sparkle effect |
| `iridescence` | - | Rainbow colors |

### 13.3 Examples

```cdl
# Star sapphire (6-ray)
trigonal[-3m]:{10-11}@1.0
    [silk:dense]
    | phenomenon[asterism:6, intensity:strong]

# Cat's eye chrysoberyl
orthorhombic[mmm]:{110}@1.0
    [needle:parallel]
    | phenomenon[chatoyancy:sharp]

# Moonstone
monoclinic[2/m]:{010}@1.0
    | phenomenon[adularescence:strong]

# Alexandrite
orthorhombic[mmm]:{011}@1.0
    | phenomenon[colour_change:green-red, strong]

# Opal (amorphous with phenomenon)
amorphous[opalescent]:{botryoidal}
    | phenomenon[play_of_color:intense]
```

---

## 14. Comments and Documentation

### 14.1 Line Comments

```cdl
# This is a line comment
{111}@1.0  # Inline comment after code
```

### 14.2 Block Comments

```cdl
/* This is a
   multi-line
   block comment */
```

### 14.3 Documentation Comments

Special `#!` comments for metadata:

```cdl
#! Mineral: Amethyst
#! Locality: Vera Cruz, Mexico
#! Features: Scepter growth with phantom zones
#! Quality: Museum specimen

trigonal[32]:{10-10}@1.0
```

### 14.4 Comment Best Practices

```cdl
# =============================================================================
# Scepter Amethyst - Museum Specimen
# =============================================================================
#
# This specimen shows classic scepter morphology with:
# - Smoky base crystal with 3 phantom zones
# - Purple amethyst cap
# - Japan law twinning on termination
#
#! Locality: Vera Cruz, Mexico
#! Acquired: 2024
#! Size: 12cm

@prism = {10-10}@1.0
@rhomb = {10-11}@0.8

trigonal[32]:(
    # Base crystal - smoky quartz
    base:($prism + $rhomb)
        [phantom:3, smoky]
        [striation:parallel]

    # Scepter cap - amethyst
    > cap:($prism@0.5 + $rhomb@0.4)
        [colour:purple]

) | twin(japan)
```

---

## 15. Named References

### 15.1 Definitions

Define reusable components with `@name = expression`:

```cdl
@prism = {10-10}@1.0
@rhomb = {10-11}@0.8
@quartz_base = $prism + $rhomb
@phantom_features = [phantom:3, white]
```

### 15.2 References

Use definitions with `$name`:

```cdl
trigonal[32]:$quartz_base $phantom_features
```

### 15.3 Scope

Definitions are file-scoped. They must appear before use.

### 15.4 Composition

Definitions can reference other definitions:

```cdl
@a = {111}@1.0
@b = {100}@1.3
@diamond_forms = $a + $b
@diamond_full = $diamond_forms [growth:sector]

cubic[m3m]:$diamond_full
```

### 15.5 Override Pattern

Extend definitions with additional features:

```cdl
@base = {10-10}@1.0 + {10-11}@0.8

# Use base as-is
trigonal[32]:$base

# Extend with features
trigonal[32]:$base [phantom:3]

# Extend with more forms
trigonal[32]:$base + {01-11}@0.5
```

---

## 16. Variants

### 16.1 Variant Syntax

The `;` operator separates alternative forms:

```cdl
(variant_a ; variant_b ; variant_c)
```

### 16.2 Use Cases

**Alternative dominant forms:**
```cdl
# Either octahedral or cubic habit
cubic[m3m]:(
    octahedral:{111}@1.0 + {100}@0.3
    ; cubic:{100}@1.0 + {111}@0.3
)
```

**Feature variants:**
```cdl
# With or without phantom zones
cubic[m3m]:{111}@1.0 [phantom:0 ; phantom:3 ; phantom:5]
```

**Color variants:**
```cdl
# Sapphire color varieties
trigonal[-3m]:{10-11}@1.0 [
    colour:blue ;
    colour:pink ;
    colour:yellow ;
    colour:colourless
]
```

### 16.3 Rendering Variants

Renderers may:
- Show first variant (default)
- Cycle through variants (animation)
- Show all variants (comparison view)
- Let user select variant

---

## 17. Complete Grammar

### 17.1 EBNF Grammar

```ebnf
(* CDL v2 Complete Grammar *)

document = { definition | comment }*, material_desc ;

(* Definitions *)
definition = "@", identifier, "=", expression ;
reference = "$", identifier ;

(* Comments *)
comment = "#", { any_char - newline }*, newline
        | "/*", { any_char }*, "*/" ;
doc_comment = "#!", { any_char - newline }*, newline ;

(* Material description *)
material_desc = crystalline_desc | amorphous_desc ;

(* Crystalline materials *)
crystalline_desc = system, [ "[", point_group, "]" ], ":",
                   form_expr,
                   [ aggregate_clause ],
                   { modifier_clause }*,
                   [ phenomenon_clause ] ;

system = "cubic" | "hexagonal" | "trigonal" | "tetragonal"
       | "orthorhombic" | "monoclinic" | "triclinic" ;

(* Amorphous materials *)
amorphous_desc = "amorphous", [ "[", subtype, "]" ], ":",
                 shape_list, [ feature_spec ],
                 [ phenomenon_clause ] ;

subtype = "opalescent" | "glassy" | "waxy" | "resinous" | "cryptocrystalline" ;
shape_list = shape, { ",", shape }* ;
shape = "massive" | "botryoidal" | "reniform" | "stalactitic"
      | "mammillary" | "nodular" | "conchoidal" ;

(* Form expressions *)
form_expr = form_term, { "+", form_term }* ;
form_term = variant_expr | grouped_forms | nested_growth | aggregate_expr | simple_form ;

(* Variants *)
variant_expr = "(", form_expr, ";", form_expr, { ";", form_expr }*, ")" ;

(* Grouped forms *)
grouped_forms = "(", [ label, ":" ], form_expr, ")", [ feature_spec ], [ local_modifier ] ;
label = identifier ;
local_modifier = "|", "twin", "(", twin_spec, ")" ;

(* Nested growth *)
nested_growth = form_term, ">", form_term ;

(* Aggregate expressions *)
aggregate_expr = form_term, "~", arrangement_spec ;
arrangement_spec = arrangement_type, "[", integer, "]", [ "@", dimension ], [ "[", orientation, "]" ] ;
arrangement_type = "parallel" | "random" | "radial" | "epitaxial" | "druse" | "cluster" ;
orientation = identifier, [ ":", value ] ;
dimension = number, unit ;
unit = "mm" | "cm" | "um" ;

(* Simple forms *)
simple_form = ( reference | labeled_form | miller_index | named_form ),
              [ "@", scale ], [ feature_spec ] ;
labeled_form = label, ":", ( miller_index | named_form ) ;
miller_index = "{", index, index, index, [ index ], "}" ;
index = [ "-" ], digit, { digit }* ;
named_form = "cube" | "octahedron" | "dodecahedron" | "prism" | ... ;
scale = number ;

(* Features *)
feature_spec = "[", feature, { ",", feature }*, "]" ;
feature = feature_name, ":", feature_value, { ",", feature_value }* ;
feature_name = "phantom" | "colour" | "zoning" | "inclusion" | "needle"
             | "silk" | "striation" | "trigon" | "sector" | ... ;
feature_value = number | identifier | colour_spec ;
colour_spec = identifier, [ "-", identifier ]* ;

(* Modifiers *)
modifier_clause = "|", ( modification | twin_clause ) ;
modification = mod_type, "(", param_list, ")" ;
mod_type = "elongate" | "truncate" | "taper" | "flatten" ;
param_list = param, { ",", param }* ;
param = identifier, ":", value ;

(* Twins *)
twin_clause = "twin", "(", twin_spec, ")" ;
twin_spec = twin_law | custom_twin ;
twin_law = "spinel" | "brazil" | "dauphine" | "japan" | ... ;
custom_twin = "[", number, ",", number, ",", number, "]", ",", angle ;

(* Phenomena *)
phenomenon_clause = "|", "phenomenon", "[", phenomenon_spec, "]" ;
phenomenon_spec = phenomenon_type, { ",", phenomenon_param }* ;
phenomenon_type = "asterism" | "chatoyancy" | "adularescence"
                | "labradorescence" | "play_of_color" | "colour_change" | ... ;
phenomenon_param = identifier, ":", value ;

(* Primitives *)
identifier = letter, { letter | digit | "_" }* ;
number = integer | float ;
integer = [ "-" ], digit, { digit }* ;
float = [ "-" ], digit, { digit }*, ".", digit, { digit }* ;
value = number | identifier ;
```

---

## 18. Examples Library

### 18.1 Simple Crystals (v1 Compatible)

```cdl
# Diamond - octahedron with cube truncation
cubic[m3m]:{111}@1.0 + {100}@1.3

# Quartz - hexagonal prism with rhombohedral termination
trigonal[32]:{10-10}@1.0 + {10-11}@0.8

# Garnet - dodecahedron with trapezohedron
cubic[m3m]:{110}@1.0 + {211}@0.6

# Beryl - hexagonal prism with pinacoid
hexagonal[6/mmm]:{10-10}@1.0 + {0001}@0.5

# Fluorite - cube with octahedron
cubic[m3m]:{100}@1.0 + {111}@0.8
```

### 18.2 Crystals with Features

```cdl
# Diamond with natural surface features
cubic[m3m]:{111}@1.0[trigon:dense] + {100}@1.3

# Phantom quartz
trigonal[32]:{10-10}@1.0[phantom:3, white] + {10-11}@0.8

# Rutilated quartz
trigonal[32]:{10-10}@1.0[needle:rutile, 0.3] + {10-11}@0.8

# Watermelon tourmaline
trigonal[-3m]:{10-10}@1.0[colour_zone:pink-white-green, 3] + {10-11}@0.8

# Sector-zoned sapphire
trigonal[-3m]:{10-11}@1.0[sector:hexagonal, colour:blue] + {0001}@0.5
```

### 18.3 Scepter Crystals

```cdl
# Basic scepter quartz
@prism = {10-10}@1.0
@rhomb = {10-11}@0.8

trigonal[32]:
    (base:$prism + $rhomb)
    > (cap:$prism@0.5 + $rhomb@0.4)

# Amethyst scepter with color zoning
trigonal[32]:(
    base:($prism + $rhomb)[colour:smoky]
    > cap:($prism@0.5 + $rhomb@0.4)[colour:purple]
)

# Multi-generation scepter
trigonal[32]:
    $prism > $prism@0.7 > $prism@0.4
```

### 18.4 Twinned Crystals

```cdl
# Spinel twin (octahedron)
cubic[m3m]:{111}@1.0 | twin(spinel)

# Japan law twin (quartz)
trigonal[32]:{10-10}@1.0 + {10-11}@0.8 | twin(japan)

# Partial twinning (only termination)
trigonal[32]:{10-10}@1.0 + ({10-11}@0.8 | twin(dauphine))

# Carlsbad twin (feldspar)
monoclinic[2/m]:{010}@1.0 + {110}@0.8 + {001}@0.5 | twin(carlsbad)
```

### 18.5 Aggregates

```cdl
# Quartz cluster
trigonal[32]:{10-10}@1.0 + {10-11}@0.8 ~ cluster[15]

# Amethyst geode
trigonal[32]:{10-10}@1.0 + {10-11}@0.8
    [colour:purple]
    ~ druse[100] @1mm [radial]

# Parallel growth
trigonal[32]:{10-10}@1.0 ~ parallel[5] @2mm [aligned]

# Chrysanthemum stone
trigonal[-3m]:{10-10}@1.0 ~ radial[12] [planar]
```

### 18.6 Phenomenal Gems

```cdl
# Star ruby (6-ray)
trigonal[-3m]:{10-11}@1.0 + {0001}@0.3
    [silk:dense, oriented]
    | phenomenon[asterism:6, strong]

# Cat's eye chrysoberyl
orthorhombic[mmm]:{110}@1.0 + {010}@0.8
    [needle:parallel, dense]
    | phenomenon[chatoyancy:sharp]

# Moonstone
monoclinic[2/m]:{010}@1.0 + {001}@0.5
    [lamellar:fine]
    | phenomenon[adularescence:strong, blue]

# Alexandrite
orthorhombic[mmm]:{011}@1.0 + {010}@0.8
    | phenomenon[colour_change:green-red, strong]

# Fire opal
amorphous[opalescent]:{botryoidal}
    [colour:orange]
    | phenomenon[play_of_color:moderate]
```

### 18.7 Amorphous Materials

```cdl
# Precious opal
amorphous[opalescent]:{botryoidal}
    | phenomenon[play_of_color:intense]

# Obsidian
amorphous[glassy]:{massive, conchoidal}

# Amber with insect inclusion
amorphous[resinous]:{nodular}
    [inclusion:insect, colour:golden]

# Moldavite
amorphous[glassy]:{sculpted, pitted}
    [colour:green]

# Chalcedony agate
amorphous[cryptocrystalline]:{botryoidal}
    [banding:concentric, colours:white-blue-white]
```

### 18.8 Complex Museum Specimens

```cdl
# =============================================================================
# Vera Cruz Amethyst Scepter - Museum Specimen
# =============================================================================
#! Locality: Las Vigas, Vera Cruz, Mexico
#! Size: 15cm main crystal
#! Features: Scepter with phantoms, Japan twin on termination

@prism = {10-10}@1.0
@pos_rhomb = {10-11}@0.8
@neg_rhomb = {01-11}@0.7

trigonal[32]:(
    # Base crystal - smoky quartz with phantom zones
    base:(
        $prism
        + $pos_rhomb
        + $neg_rhomb
    )[phantom:3, colour:smoky][striation:parallel]

    # Scepter cap - purple amethyst
    > cap:(
        $prism@0.5
        + $pos_rhomb@0.4
    )[colour:purple]

) ~ parallel[3] @3mm [offset:0.1]
  | elongate(c:1.2)
  | twin(japan)
```

```cdl
# =============================================================================
# Trapiche Emerald
# =============================================================================
#! Locality: Muzo, Colombia
#! Features: Six-spoke pattern from carbon inclusions

hexagonal[6/mmm]:{10-10}@1.0 + {0001}@0.3
    [sector:trapiche, 6]
    [inclusion:carbon, spoke]
    [colour:green]
```

```cdl
# =============================================================================
# Star Sapphire Cabochon
# =============================================================================
#! Locality: Sri Lanka
#! Cut: High-domed cabochon
#! Features: Sharp 6-ray star

trigonal[-3m]:{10-11}@1.0 + {0001}@0.4
    [silk:rutile, dense, 60deg]
    [colour:blue]
    | phenomenon[asterism:6, intensity:strong, sharpness:high]
```

---

## 19. Implementation Notes

### 19.1 Parser Changes (cdl-parser)

**New tokens:**
```python
class TokenType(Enum):
    # ... existing tokens ...
    GREATER = 'GREATER'      # >
    TILDE = 'TILDE'          # ~
    SEMICOLON = 'SEMICOLON'  # ;
    DOLLAR = 'DOLLAR'        # $
    HASH = 'HASH'            # #
```

**New model classes:**
```python
@dataclass
class FormGroup:
    forms: List[Union[CrystalForm, 'FormGroup', 'NestedGrowth']]
    features: List[Feature] = field(default_factory=list)
    label: Optional[str] = None

@dataclass
class NestedGrowth:
    base: Union[CrystalForm, FormGroup]
    overgrowth: Union[CrystalForm, FormGroup, 'NestedGrowth']

@dataclass
class AggregateSpec:
    form: Union[CrystalForm, FormGroup]
    arrangement: str
    count: int
    spacing: Optional[str] = None
    orientation: Optional[str] = None

@dataclass
class Feature:
    name: str
    values: List[Union[int, float, str]]

@dataclass
class AmorphousDescription:
    subtype: Optional[str]
    shapes: List[str]
    features: List[Feature] = field(default_factory=list)
    phenomenon: Optional[PhenomenonSpec] = None
```

### 19.2 LSP Integration (cdl-lsp)

**New completions:**
- Feature names and values
- Arrangement types
- Phenomenon types
- Shape descriptors for amorphous

**New diagnostics:**
- Validate feature names
- Check arrangement parameters
- Verify phenomenon compatibility

**New formatting:**
- Multi-line formatting for complex descriptions
- Indent nested groups
- Align feature lists

### 19.3 Geometry Generation (crystal-geometry)

**New generators:**
- Amorphous mesh generation (predefined shapes)
- Aggregate layout algorithms
- Nested growth positioning

**Feature visualization:**
- Phantom zone rendering (transparent layers)
- Inclusion placement
- Surface texture mapping

### 19.4 Rendering (crystal-renderer)

**New capabilities:**
- Aggregate rendering (instancing)
- Phenomenon effects (asterism rays, chatoyancy band)
- Surface feature textures
- Amorphous material shaders

---

## 20. Migration Guide

### 20.1 From v1 to v2

**No changes required.** All v1 CDL is valid v2.

### 20.2 Adopting v2 Features

**Step 1: Add comments**
```cdl
# Now with documentation!
cubic[m3m]:{111}@1.0 + {100}@1.3
```

**Step 2: Add features**
```cdl
cubic[m3m]:{111}@1.0[trigon:dense] + {100}@1.3
```

**Step 3: Use grouping for shared features**
```cdl
cubic[m3m]:({111}@1.0 + {100}@1.3)[phantom:3]
```

**Step 4: Use references for reusability**
```cdl
@octahedron = {111}@1.0
@cube = {100}@1.3
cubic[m3m]:$octahedron + $cube
```

**Step 5: Add complex structures as needed**
```cdl
@forms = {111}@1.0 + {100}@1.3
cubic[m3m]:$forms [phantom:3] ~ cluster[10] | twin(spinel)
```

### 20.3 Common Patterns

**Pattern: Base template with variations**
```cdl
@quartz_base = {10-10}@1.0 + {10-11}@0.8

# Clear quartz
trigonal[32]:$quartz_base

# Amethyst
trigonal[32]:$quartz_base [colour:purple]

# Smoky quartz with phantoms
trigonal[32]:$quartz_base [colour:smoky, phantom:3]

# Citrine
trigonal[32]:$quartz_base [colour:yellow]
```

**Pattern: Scepter template**
```cdl
@prism = {10-10}@1.0
@rhomb = {10-11}@0.8
@base = $prism + $rhomb
@cap = $prism@0.5 + $rhomb@0.4

# Basic scepter
trigonal[32]:$base > $cap

# Amethyst scepter
trigonal[32]:($base)[colour:smoky] > ($cap)[colour:purple]
```

---

## Appendix A: Quick Reference Card

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     CDL v2 QUICK REFERENCE                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ BASIC SYNTAX                                                                 ║
║   system[point_group]:{hkl}@scale                                            ║
║   cubic[m3m]:{111}@1.0 + {100}@1.3                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ BRACKETS                                                                     ║
║   {hkl}      Miller index         {111}, {10-10}                             ║
║   [pg]       Point group          [m3m], [-3m]                               ║
║   [feat]     Features             [phantom:3], [colour:blue]                 ║
║   (...)      Grouping             ({111} + {100})[shared]                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ OPERATORS                                                                    ║
║   +          Add forms            {111} + {100}                              ║
║   @          Scale                {111}@1.0                                  ║
║   >          Nested growth        base > cap                                 ║
║   ~          Aggregate            form ~ parallel[5]                         ║
║   |          Modifier/twin        forms | twin(spinel)                       ║
║   ;          Variants             (a ; b ; c)                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ FEATURES                                                                     ║
║   [phantom:count,colour]          Internal growth zones                      ║
║   [striation:dir,count]           Surface striations                         ║
║   [inclusion:mineral]             Solid inclusions                           ║
║   [colour:name]                   Crystal color                              ║
║   [colour_zone:a-b-c,count]       Color banding                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ AGGREGATES                                                                   ║
║   ~ parallel[n]                   Aligned crystals                           ║
║   ~ cluster[n]                    Random cluster                             ║
║   ~ radial[n]                     Radiating arrangement                      ║
║   ~ druse[n] @spacing             Cavity lining                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PHENOMENA                                                                    ║
║   | phenomenon[asterism:6]        Star effect                                ║
║   | phenomenon[chatoyancy]        Cat's eye                                  ║
║   | phenomenon[adularescence]     Moonstone shimmer                          ║
║   | phenomenon[play_of_color]     Opal iridescence                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ DEFINITIONS                                                                  ║
║   @name = expression              Define                                     ║
║   $name                           Reference                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ COMMENTS                                                                     ║
║   # line comment                                                             ║
║   /* block comment */                                                        ║
║   #! documentation                                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ AMORPHOUS                                                                    ║
║   amorphous[subtype]:{shape}                                                 ║
║   amorphous[opalescent]:{botryoidal}                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Appendix B: Revision History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | Jan 2026 | Initial v2 specification |
| 1.0.0 | 2024 | Original CDL specification |

---

*End of CDL v2 Specification*
