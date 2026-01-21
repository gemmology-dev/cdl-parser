"""
Comprehensive test suite for cdl-parser.

Tests CDL parsing, validation, models, and CLI functionality.
"""

import pytest

from cdl_parser import (
    CRYSTAL_SYSTEMS,
    NAMED_FORMS,
    POINT_GROUPS,
    CrystalDescription,
    CrystalForm,
    MillerIndex,
    ParseError,
    ValidationError,
    parse_cdl,
    validate_cdl,
)

# =============================================================================
# Test Data
# =============================================================================

CDL_TEST_CASES = [
    ("simple_octahedron", "cubic[m3m]:{111}"),
    ("truncated_octahedron", "cubic[m3m]:{111}@1.0 + {100}@1.3"),
    ("cube_octahedron", "cubic[m3m]:{100}@1.0 + {111}@0.7"),
    ("garnet_combo", "cubic[m3m]:{110}@1.0 + {211}@0.6"),
    ("simple_cube", "cubic[m3m]:{100}"),
    ("dodecahedron", "cubic[m3m]:{110}"),
    ("trapezohedron", "cubic[m3m]:{211}"),
    ("triple_form", "cubic[m3m]:{111}@1.0 + {100}@0.5 + {110}@0.3"),
]

INVALID_CDL_CASES = [
    ("invalid_syntax", "invalid{{{syntax"),
    ("missing_system", "[m3m]:{111}"),
    ("missing_forms", "cubic[m3m]"),
    ("invalid_system", "notasystem[m3m]:{111}"),
]


# =============================================================================
# Miller Index Tests
# =============================================================================


class TestMillerIndex:
    """Test Miller index data class."""

    def test_create_3index(self):
        """Test creating 3-index Miller notation."""
        mi = MillerIndex(1, 1, 1)
        assert mi.h == 1
        assert mi.k == 1
        assert mi.l == 1
        assert mi.i is None

    def test_create_4index(self):
        """Test creating 4-index Miller-Bravais notation."""
        mi = MillerIndex(1, 0, 1, i=-1)
        assert mi.h == 1
        assert mi.k == 0
        assert mi.l == 1
        assert mi.i == -1

    def test_4index_validation(self):
        """Test Miller-Bravais constraint i = -(h+k)."""
        # Valid
        MillerIndex(1, 0, 1, i=-1)  # -1 = -(1+0)
        MillerIndex(1, 1, 2, i=-2)  # -2 = -(1+1)

        # Invalid
        with pytest.raises(ValueError, match="Invalid Miller-Bravais"):
            MillerIndex(1, 0, 1, i=0)  # Should be -1

    def test_as_tuple_3index(self):
        """Test as_tuple for 3-index."""
        mi = MillerIndex(1, 1, 1)
        assert mi.as_tuple() == (1, 1, 1)

    def test_as_tuple_4index(self):
        """Test as_tuple for 4-index."""
        mi = MillerIndex(1, 0, 1, i=-1)
        assert mi.as_tuple() == (1, 0, -1, 1)

    def test_as_3index(self):
        """Test as_3index always returns 3 elements."""
        mi_3 = MillerIndex(1, 1, 1)
        mi_4 = MillerIndex(1, 0, 1, i=-1)
        assert mi_3.as_3index() == (1, 1, 1)
        assert mi_4.as_3index() == (1, 0, 1)

    def test_str_3index(self):
        """Test string representation for 3-index."""
        mi = MillerIndex(1, 1, 1)
        assert str(mi) == "{111}"

    def test_str_4index(self):
        """Test string representation for 4-index."""
        mi = MillerIndex(1, 0, 1, i=-1)
        assert str(mi) == "{10-11}"


# =============================================================================
# Crystal Form Tests
# =============================================================================


class TestCrystalForm:
    """Test CrystalForm data class."""

    def test_create_basic(self):
        """Test creating basic form."""
        mi = MillerIndex(1, 1, 1)
        form = CrystalForm(miller=mi)
        assert form.miller == mi
        assert form.scale == 1.0
        assert form.name is None

    def test_create_with_scale(self):
        """Test creating form with scale."""
        mi = MillerIndex(1, 0, 0)
        form = CrystalForm(miller=mi, scale=1.3)
        assert form.scale == 1.3

    def test_create_with_name(self):
        """Test creating form with name."""
        mi = MillerIndex(1, 1, 1)
        form = CrystalForm(miller=mi, name="octahedron")
        assert form.name == "octahedron"

    def test_str_basic(self):
        """Test string representation."""
        mi = MillerIndex(1, 1, 1)
        form = CrystalForm(miller=mi)
        assert str(form) == "{111}"

    def test_str_with_scale(self):
        """Test string with scale."""
        mi = MillerIndex(1, 0, 0)
        form = CrystalForm(miller=mi, scale=1.3)
        assert str(form) == "{100}@1.3"


# =============================================================================
# Parser Tests
# =============================================================================


class TestParseSimple:
    """Test basic CDL parsing."""

    def test_parse_simple_octahedron(self):
        """Test parsing simple octahedron."""
        desc = parse_cdl("cubic[m3m]:{111}")
        assert desc.system == "cubic"
        assert desc.point_group == "m3m"
        assert len(desc.forms) == 1
        assert desc.forms[0].miller.as_tuple() == (1, 1, 1)

    def test_parse_simple_cube(self):
        """Test parsing simple cube."""
        desc = parse_cdl("cubic[m3m]:{100}")
        assert desc.system == "cubic"
        assert len(desc.forms) == 1
        assert desc.forms[0].miller.as_tuple() == (1, 0, 0)

    def test_parse_default_point_group(self):
        """Test that default point group is used."""
        desc = parse_cdl("cubic:{111}")
        assert desc.point_group == "m3m"

        desc = parse_cdl("hexagonal:{0001}")
        assert desc.point_group == "6/mmm"

    def test_parse_truncated_octahedron(self):
        """Test parsing truncated octahedron with two forms."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        assert len(desc.forms) == 2
        assert desc.forms[0].miller.as_tuple() == (1, 1, 1)
        assert desc.forms[0].scale == 1.0
        assert desc.forms[1].miller.as_tuple() == (1, 0, 0)
        assert desc.forms[1].scale == 1.3

    def test_parse_triple_form(self):
        """Test parsing three forms."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@0.5 + {110}@0.3")
        assert len(desc.forms) == 3

    @pytest.mark.parametrize("name,cdl", CDL_TEST_CASES)
    def test_all_cdl_cases(self, name, cdl):
        """Test all CDL test cases parse successfully."""
        desc = parse_cdl(cdl)
        assert isinstance(desc, CrystalDescription)
        assert desc.system in CRYSTAL_SYSTEMS


class TestParseSystems:
    """Test parsing all crystal systems."""

    def test_cubic(self):
        """Test cubic system."""
        desc = parse_cdl("cubic[m3m]:{111}")
        assert desc.system == "cubic"

    def test_hexagonal(self):
        """Test hexagonal system with 4-index notation."""
        desc = parse_cdl("hexagonal[6/mmm]:{10-10}")
        assert desc.system == "hexagonal"
        assert desc.forms[0].miller.i == -1

    def test_trigonal(self):
        """Test trigonal system."""
        desc = parse_cdl("trigonal[-3m]:{10-11}")
        assert desc.system == "trigonal"

    def test_tetragonal(self):
        """Test tetragonal system."""
        desc = parse_cdl("tetragonal[4/mmm]:{101}")
        assert desc.system == "tetragonal"

    def test_orthorhombic(self):
        """Test orthorhombic system."""
        desc = parse_cdl("orthorhombic[mmm]:{110}")
        assert desc.system == "orthorhombic"

    def test_monoclinic(self):
        """Test monoclinic system."""
        desc = parse_cdl("monoclinic[2/m]:{100}")
        assert desc.system == "monoclinic"

    def test_triclinic(self):
        """Test triclinic system."""
        desc = parse_cdl("triclinic[-1]:{100}")
        assert desc.system == "triclinic"


class TestParsePointGroups:
    """Test parsing point groups."""

    @pytest.mark.parametrize("system,groups", list(POINT_GROUPS.items()))
    def test_all_point_groups(self, system, groups):
        """Test all point groups for each system."""
        for pg in groups:
            cdl = f"{system}[{pg}]:{{100}}"
            desc = parse_cdl(cdl)
            assert desc.point_group == pg

    def test_invalid_point_group_for_system(self):
        """Test that invalid point group raises error."""
        with pytest.raises((ParseError, ValidationError)):
            parse_cdl("cubic[6/mmm]:{111}")  # 6/mmm is hexagonal


class TestParseNamedForms:
    """Test parsing named forms."""

    @pytest.mark.parametrize("name,miller", list(NAMED_FORMS.items())[:10])
    def test_named_forms(self, name, miller):
        """Test parsing named forms."""
        cdl = f"cubic[m3m]:{name}"
        desc = parse_cdl(cdl)
        assert desc.forms[0].name == name
        assert desc.forms[0].miller.as_3index() == miller

    def test_octahedron(self):
        """Test octahedron named form."""
        desc = parse_cdl("cubic[m3m]:octahedron")
        assert desc.forms[0].name == "octahedron"
        assert desc.forms[0].miller.as_tuple() == (1, 1, 1)

    def test_cube(self):
        """Test cube named form."""
        desc = parse_cdl("cubic[m3m]:cube")
        assert desc.forms[0].name == "cube"
        assert desc.forms[0].miller.as_tuple() == (1, 0, 0)


class TestParseTwins:
    """Test parsing twin specifications."""

    @pytest.mark.parametrize("law", ["spinel", "brazil", "japan", "carlsbad"])
    def test_named_twin_laws(self, law):
        """Test parsing named twin laws."""
        cdl = f"cubic[m3m]:{{111}} | twin({law})"
        desc = parse_cdl(cdl)
        assert desc.twin is not None
        assert desc.twin.law == law

    def test_twin_with_count(self):
        """Test twin with count parameter."""
        desc = parse_cdl("cubic[m3m]:{111} | twin(trilling,3)")
        assert desc.twin.law == "trilling"
        assert desc.twin.count == 3

    def test_custom_twin_axis(self):
        """Test twin with custom axis."""
        desc = parse_cdl("cubic[m3m]:{111} | twin([1,1,1],180)")
        assert desc.twin.axis == (1.0, 1.0, 1.0)
        assert desc.twin.angle == 180.0


class TestParseModifications:
    """Test parsing modifications."""

    def test_elongate(self):
        """Test parsing elongate modification."""
        desc = parse_cdl("cubic[m3m]:{111} | elongate(c:1.5)")
        assert len(desc.modifications) == 1
        assert desc.modifications[0].type == "elongate"
        assert desc.modifications[0].params["axis"] == "c"
        assert desc.modifications[0].params["ratio"] == 1.5


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Test CDL validation."""

    def test_valid_cdl(self):
        """Test valid CDL strings."""
        valid, error = validate_cdl("cubic[m3m]:{111}")
        assert valid is True
        assert error is None

    def test_invalid_cdl(self):
        """Test invalid CDL strings."""
        valid, error = validate_cdl("invalid{{{")
        assert valid is False
        assert error is not None

    @pytest.mark.parametrize("name,cdl", INVALID_CDL_CASES)
    def test_invalid_cases(self, name, cdl):
        """Test that invalid CDL cases fail validation."""
        valid, error = validate_cdl(cdl)
        assert valid is False


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Test serialization and string representation."""

    def test_to_dict(self):
        """Test converting to dictionary."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        d = desc.to_dict()
        assert d["system"] == "cubic"
        assert d["point_group"] == "m3m"
        assert len(d["forms"]) == 2

    def test_str_roundtrip(self):
        """Test string representation can be re-parsed."""
        original = "cubic[m3m]:{111}@1.0 + {100}@1.3"
        desc = parse_cdl(original)
        reconstructed = str(desc)
        desc2 = parse_cdl(reconstructed)
        assert desc.system == desc2.system
        assert desc.point_group == desc2.point_group
        assert len(desc.forms) == len(desc2.forms)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_whitespace_handling(self):
        """Test whitespace is handled correctly."""
        desc1 = parse_cdl("cubic[m3m]:{111}")
        desc2 = parse_cdl("  cubic  [  m3m  ]  :  { 111 }  ")
        # Both should parse (though whitespace inside braces may differ)
        assert desc1.system == desc2.system

    def test_negative_indices(self):
        """Test negative Miller indices."""
        desc = parse_cdl("hexagonal[6/mmm]:{10-10}")
        # The -1 is the i index
        assert desc.forms[0].miller.i == -1

    def test_large_scale_values(self):
        """Test large scale values."""
        desc = parse_cdl("cubic[m3m]:{111}@2.5 + {100}@3.7")
        assert desc.forms[0].scale == 2.5
        assert desc.forms[1].scale == 3.7

    def test_many_forms(self):
        """Test parsing many forms."""
        forms = " + ".join([f"{{11{i}}}" for i in range(5)])
        cdl = f"cubic[m3m]:{forms}"
        desc = parse_cdl(cdl)
        assert len(desc.forms) == 5


# =============================================================================
# Exception Tests
# =============================================================================


class TestExceptions:
    """Test exception handling."""

    def test_parse_error_message(self):
        """Test ParseError contains useful message."""
        with pytest.raises(ParseError) as exc_info:
            parse_cdl("invalid{{{")
        assert (
            "position" in str(exc_info.value).lower() or "unexpected" in str(exc_info.value).lower()
        )

    def test_validation_error_fields(self):
        """Test ValidationError with field info."""
        error = ValidationError("Invalid point group", field="point_group", value="xyz")
        assert "point_group" in str(error)
        assert "xyz" in str(error)


# =============================================================================
# CLI Tests
# =============================================================================


class TestCLI:
    """Test CLI functionality."""

    def test_cli_parse(self):
        """Test CLI parse command."""
        from cdl_parser.cli import main

        result = main(["parse", "cubic[m3m]:{111}"])
        assert result == 0

    def test_cli_validate_valid(self):
        """Test CLI validate with valid CDL."""
        from cdl_parser.cli import main

        result = main(["validate", "cubic[m3m]:{111}"])
        assert result == 0

    def test_cli_validate_invalid(self):
        """Test CLI validate with invalid CDL."""
        from cdl_parser.cli import main

        result = main(["validate", "invalid{{{"])
        assert result == 1

    def test_cli_list_systems(self):
        """Test CLI list-systems."""
        from cdl_parser.cli import main

        result = main(["--list-systems"])
        assert result == 0

    def test_cli_list_point_groups(self):
        """Test CLI list-point-groups."""
        from cdl_parser.cli import main

        result = main(["--list-point-groups"])
        assert result == 0

    def test_cli_list_forms(self):
        """Test CLI list-forms."""
        from cdl_parser.cli import main

        result = main(["--list-forms"])
        assert result == 0

    def test_cli_list_twins(self):
        """Test CLI list-twins."""
        from cdl_parser.cli import main

        result = main(["--list-twins"])
        assert result == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for real-world usage."""

    def test_diamond_cdl(self):
        """Test CDL for diamond crystal."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@0.3")
        assert desc.system == "cubic"
        assert len(desc.forms) == 2
        # Octahedron with cube truncation
        assert desc.forms[0].miller.as_tuple() == (1, 1, 1)
        assert desc.forms[1].miller.as_tuple() == (1, 0, 0)

    def test_quartz_cdl(self):
        """Test CDL for quartz crystal."""
        desc = parse_cdl("trigonal[-3m]:{10-10}@1.0 + {10-11}@0.8")
        assert desc.system == "trigonal"
        assert len(desc.forms) == 2
        # Hexagonal prism with rhombohedron
        assert desc.forms[0].miller.i == -1
        assert desc.forms[1].miller.i == -1

    def test_garnet_cdl(self):
        """Test CDL for garnet crystal."""
        desc = parse_cdl("cubic[m3m]:{110}@1.0 + {211}@0.6")
        assert desc.system == "cubic"
        # Dodecahedron with trapezohedron
        assert desc.forms[0].miller.as_tuple() == (1, 1, 0)
        assert desc.forms[1].miller.as_tuple() == (2, 1, 1)

    def test_fluorite_twin_cdl(self):
        """Test CDL for fluorite twin."""
        desc = parse_cdl("cubic[m3m]:{111} | twin(fluorite)")
        assert desc.twin is not None
        assert desc.twin.law == "fluorite"
