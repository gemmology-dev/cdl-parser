"""
CDL Constants.

Crystal systems, point groups, twin laws, and named forms for
Crystal Description Language parsing.
"""


# =============================================================================
# Crystal Systems
# =============================================================================

CRYSTAL_SYSTEMS: set[str] = {
    "cubic",
    "tetragonal",
    "orthorhombic",
    "hexagonal",
    "trigonal",
    "monoclinic",
    "triclinic",
}

# Default point group for each system
DEFAULT_POINT_GROUPS: dict[str, str] = {
    "cubic": "m3m",
    "tetragonal": "4/mmm",
    "orthorhombic": "mmm",
    "hexagonal": "6/mmm",
    "trigonal": "-3m",
    "monoclinic": "2/m",
    "triclinic": "-1",
}

# =============================================================================
# Point Groups (all 32 crystallographic point groups)
# =============================================================================

POINT_GROUPS: dict[str, set[str]] = {
    "cubic": {"m3m", "432", "-43m", "m-3", "23"},
    "hexagonal": {"6/mmm", "622", "6mm", "-6m2", "6/m", "-6", "6"},
    "trigonal": {"-3m", "32", "3m", "-3", "3"},
    "tetragonal": {"4/mmm", "422", "4mm", "-42m", "4/m", "-4", "4"},
    "orthorhombic": {"mmm", "222", "mm2"},
    "monoclinic": {"2/m", "m", "2"},
    "triclinic": {"-1", "1"},
}

# All point groups flattened
ALL_POINT_GROUPS: set[str] = set().union(*POINT_GROUPS.values())

# =============================================================================
# Twin Laws
# =============================================================================

TWIN_LAWS: set[str] = {
    # Classic twin laws
    "spinel",
    "iron_cross",
    "brazil",
    "dauphine",
    "japan",
    "carlsbad",
    "baveno",
    "manebach",
    "albite",
    "pericline",
    # Additional rendering system laws
    "spinel_law",  # Alias for spinel
    "fluorite",  # Interpenetrating cube twin
    "gypsum_swallow",  # Swallowtail twin
    "staurolite_60",  # 60-degree cross twin
    "staurolite_90",  # 90-degree cross twin
    "trilling",  # Cyclic triplet twin
}

# =============================================================================
# Named Forms (maps to Miller indices)
# =============================================================================

NAMED_FORMS: dict[str, tuple[int, int, int]] = {
    # Cubic forms
    "cube": (1, 0, 0),
    "octahedron": (1, 1, 1),
    "dodecahedron": (1, 1, 0),
    "trapezohedron": (2, 1, 1),
    "tetrahexahedron": (2, 1, 0),
    "trisoctahedron": (2, 2, 1),
    "hexoctahedron": (3, 2, 1),
    # Hexagonal/Trigonal (stored as 3-index, converted internally)
    "prism": (1, 0, 0),  # {10-10}
    "prism_1": (1, 0, 0),
    "prism_2": (1, 1, 0),  # {11-20}
    "pinacoid": (0, 0, 1),  # {0001}
    "basal": (0, 0, 1),
    "rhombohedron": (1, 0, 1),  # {10-11}
    "rhomb_pos": (1, 0, 1),
    "rhomb_neg": (0, 1, 1),  # {01-11}
    "dipyramid": (1, 0, 1),
    "dipyramid_1": (1, 0, 1),
    "dipyramid_2": (1, 1, 2),
    "scalenohedron": (2, 1, 1),
    # Tetragonal forms
    "tetragonal_prism": (1, 0, 0),
    "tetragonal_dipyramid": (1, 0, 1),
    # Orthorhombic forms
    "pinacoid_a": (1, 0, 0),
    "pinacoid_b": (0, 1, 0),
    "pinacoid_c": (0, 0, 1),
    "prism_ab": (1, 1, 0),
    "prism_ac": (1, 0, 1),
    "prism_bc": (0, 1, 1),
}

# =============================================================================
# Modification Types
# =============================================================================

MODIFICATION_TYPES: set[str] = {
    "elongate",  # Stretch along an axis
    "truncate",  # Cut off corners/edges
    "taper",  # Make narrower in one direction
    "bevel",  # Add beveled edges
}

# =============================================================================
# Twin Types
# =============================================================================

TWIN_TYPES: set[str] = {
    "contact",  # Contact twin (share composition plane)
    "penetration",  # Penetration twin (interpenetrating)
    "cyclic",  # Cyclic twin (multiple individuals)
}
