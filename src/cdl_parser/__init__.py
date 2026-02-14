"""
CDL Parser - Crystal Description Language Parser.

A Python library for parsing compact string notation describing
crystal morphology for gemmological and mineralogical visualization.

Example:
    >>> from cdl_parser import parse_cdl
    >>> desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
    >>> desc.system
    'cubic'
    >>> len(desc.forms)
    2

CDL Syntax:
    system[point_group]:{form}@scale + {form}@scale | modification | twin

    Examples:
        cubic[m3m]:{111}                    # Simple octahedron
        cubic[m3m]:{111}@1.0 + {100}@1.3    # Truncated octahedron
        trigonal[-3m]:{10-10}@1.0           # Quartz prism (4-index notation)
        cubic[m3m]:{111} | twin(spinel)     # Spinel-law twin
"""

__version__ = "1.3.0"
__author__ = "Fabian Schuh"
__email__ = "fabian@gemmology.dev"

# Core parsing functions
# Constants
from .constants import (
    ALL_POINT_GROUPS,
    CRYSTAL_SYSTEMS,
    DEFAULT_POINT_GROUPS,
    FEATURE_NAMES,
    MODIFICATION_TYPES,
    NAMED_FORMS,
    PHENOMENON_TYPES,
    POINT_GROUPS,
    TWIN_LAWS,
    TWIN_TYPES,
)

# Exceptions
from .exceptions import CDLError, ParseError, ValidationError

# Data classes
from .models import (
    CrystalDescription,
    CrystalForm,
    Definition,
    Feature,
    FormGroup,
    FormNode,
    MillerIndex,
    Modification,
    PhenomenonSpec,
    TwinSpec,
)

# Lexer/Parser internals (for advanced use)
from .parser import Lexer, Parser, Token, TokenType, parse_cdl, strip_comments, validate_cdl

__all__ = [
    # Version
    "__version__",
    # Core functions
    "parse_cdl",
    "validate_cdl",
    # Data classes
    "CrystalDescription",
    "CrystalForm",
    "Definition",
    "Feature",
    "FormGroup",
    "FormNode",
    "MillerIndex",
    "Modification",
    "PhenomenonSpec",
    "TwinSpec",
    # Exceptions
    "CDLError",
    "ParseError",
    "ValidationError",
    # Constants
    "ALL_POINT_GROUPS",
    "CRYSTAL_SYSTEMS",
    "DEFAULT_POINT_GROUPS",
    "FEATURE_NAMES",
    "MODIFICATION_TYPES",
    "NAMED_FORMS",
    "PHENOMENON_TYPES",
    "POINT_GROUPS",
    "TWIN_LAWS",
    "TWIN_TYPES",
    # Internals
    "Lexer",
    "Parser",
    "Token",
    "TokenType",
    "strip_comments",
]
