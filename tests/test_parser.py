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
    Definition,
    Feature,
    FormGroup,
    FormNode,
    MillerIndex,
    ParseError,
    PhenomenonSpec,
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


# =============================================================================
# Comment Tests
# =============================================================================


class TestComments:
    """Test CDL comment stripping and doc comment extraction."""

    def test_line_comment_at_start(self):
        """Line comment before CDL is stripped."""
        desc = parse_cdl("# comment\ncubic[m3m]:{111}")
        assert desc.system == "cubic"
        assert desc.doc_comments is None

    def test_inline_comment(self):
        """Inline comment after CDL is stripped."""
        desc = parse_cdl("cubic[m3m]:{111} # octahedron")
        assert desc.system == "cubic"
        assert desc.forms[0].miller.as_tuple() == (1, 1, 1)

    def test_block_comment(self):
        """Block comment is stripped."""
        desc = parse_cdl("/* block */cubic[m3m]:{111}")
        assert desc.system == "cubic"

    def test_multiline_block_comment(self):
        """Multi-line block comment is stripped."""
        desc = parse_cdl("/* multi\nline */\ncubic[m3m]:{111}")
        assert desc.system == "cubic"

    def test_doc_comment(self):
        """Doc comment (#!) is extracted."""
        desc = parse_cdl("#! Mineral: Diamond\ncubic[m3m]:{111}")
        assert desc.doc_comments == ["Mineral: Diamond"]

    def test_multiple_doc_comments(self):
        """Multiple doc comments are preserved in order."""
        cdl = "#! Mineral: Diamond\n#! Habit: Octahedral\ncubic[m3m]:{111}"
        desc = parse_cdl(cdl)
        assert desc.doc_comments == ["Mineral: Diamond", "Habit: Octahedral"]

    def test_mixed_comments(self):
        """Mix of line, block, and doc comments."""
        cdl = (
            "#! Mineral: Quartz\n"
            "# A line comment\n"
            "/* block */ trigonal[-3m]:{10-10} # inline"
        )
        desc = parse_cdl(cdl)
        assert desc.system == "trigonal"
        assert desc.doc_comments == ["Mineral: Quartz"]

    def test_comment_only_raises(self):
        """Comment-only input raises ParseError."""
        with pytest.raises(ParseError):
            parse_cdl("# just a comment\n/* block */")

    def test_cdl_v1_regression(self):
        """Existing CDL v1 strings without comments still work identically."""
        for _name, cdl in CDL_TEST_CASES:
            desc = parse_cdl(cdl)
            assert isinstance(desc, CrystalDescription)
            assert desc.doc_comments is None

    def test_doc_comments_in_to_dict(self):
        """Doc comments appear in to_dict() output."""
        desc = parse_cdl("#! Mineral: Diamond\ncubic[m3m]:{111}")
        d = desc.to_dict()
        assert d["doc_comments"] == ["Mineral: Diamond"]

    def test_no_doc_comments_in_to_dict(self):
        """to_dict() has doc_comments=None when there are none."""
        desc = parse_cdl("cubic[m3m]:{111}")
        d = desc.to_dict()
        assert d["doc_comments"] is None


# =============================================================================
# Flatten Modification Tests
# =============================================================================


class TestFlattenModification:
    """Test flatten modification parsing."""

    def test_flatten_basic(self):
        """Flatten modification parses correctly."""
        desc = parse_cdl("cubic[m3m]:{111} | flatten(a:0.5)")
        assert len(desc.modifications) == 1
        assert desc.modifications[0].type == "flatten"
        assert desc.modifications[0].params["axis"] == "a"
        assert desc.modifications[0].params["ratio"] == 0.5

    def test_flatten_float_ratio(self):
        """Flatten with float ratio."""
        desc = parse_cdl("cubic[m3m]:{111} | flatten(c:0.75)")
        assert desc.modifications[0].type == "flatten"
        assert desc.modifications[0].params["axis"] == "c"
        assert desc.modifications[0].params["ratio"] == 0.75


# =============================================================================
# Feature Tests (CDL v1.2)
# =============================================================================


class TestFeatures:
    """Test CDL v1.2 feature parsing on crystal forms."""

    def test_single_feature(self):
        """Single feature annotation on a form."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0[trigon:dense]")
        assert desc.forms[0].features is not None
        assert len(desc.forms[0].features) == 1
        assert desc.forms[0].features[0].name == "trigon"
        assert desc.forms[0].features[0].values == ["dense"]

    def test_multiple_feature_values(self):
        """Feature with multiple values."""
        desc = parse_cdl("cubic[m3m]:{111}[phantom:3, white]")
        assert desc.forms[0].features is not None
        assert len(desc.forms[0].features) == 1
        feat = desc.forms[0].features[0]
        assert feat.name == "phantom"
        assert feat.values == [3, "white"]

    def test_feature_numeric_value(self):
        """Feature with numeric value."""
        desc = parse_cdl("trigonal[32]:{10-10}@1.0[phantom:3]")
        assert desc.forms[0].features is not None
        feat = desc.forms[0].features[0]
        assert feat.name == "phantom"
        assert feat.values == [3]

    def test_feature_on_second_form(self):
        """Feature on second form only."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3[trigon:sparse]")
        assert desc.forms[0].features is None
        assert desc.forms[1].features is not None
        assert desc.forms[1].features[0].name == "trigon"
        assert desc.forms[1].features[0].values == ["sparse"]

    def test_multiple_feature_types(self):
        """Multiple distinct features on one form."""
        desc = parse_cdl("cubic[m3m]:{111}[trigon:dense, phantom:3]")
        assert desc.forms[0].features is not None
        assert len(desc.forms[0].features) == 2
        assert desc.forms[0].features[0].name == "trigon"
        assert desc.forms[0].features[0].values == ["dense"]
        assert desc.forms[0].features[1].name == "phantom"
        assert desc.forms[0].features[1].values == [3]

    def test_features_with_scale(self):
        """Features after scale value."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0[silk:dense]")
        assert desc.forms[0].scale == 1.0
        assert desc.forms[0].features is not None
        assert desc.forms[0].features[0].name == "silk"

    def test_no_features_backwards_compat(self):
        """Existing CDL without features still works."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0")
        assert desc.forms[0].features is None

    def test_feature_str_representation(self):
        """Feature __str__ method."""
        feat = Feature("trigon", ["dense"])
        assert str(feat) == "trigon:dense"
        feat2 = Feature("phantom", [3, "white"])
        assert str(feat2) == "phantom:3, white"

    def test_form_str_with_features(self):
        """CrystalForm __str__ includes features."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0[trigon:dense]")
        form_str = str(desc.forms[0])
        assert "[trigon:dense]" in form_str

    def test_features_in_to_dict(self):
        """Features appear in to_dict() output."""
        desc = parse_cdl("cubic[m3m]:{111}[phantom:3]")
        d = desc.to_dict()
        assert d["forms"][0]["features"] is not None
        assert d["forms"][0]["features"][0]["name"] == "phantom"
        assert d["forms"][0]["features"][0]["values"] == [3]

    def test_no_features_in_to_dict(self):
        """to_dict() has features=None when there are none."""
        desc = parse_cdl("cubic[m3m]:{111}")
        d = desc.to_dict()
        assert d["forms"][0]["features"] is None


# =============================================================================
# Phenomenon Tests (CDL v1.2)
# =============================================================================


class TestPhenomenon:
    """Test CDL v1.2 phenomenon parsing."""

    def test_asterism(self):
        """Asterism phenomenon with numeric value."""
        desc = parse_cdl("trigonal[-3m]:{10-11}@1.0 | phenomenon[asterism:6]")
        assert desc.phenomenon is not None
        assert desc.phenomenon.type == "asterism"
        assert desc.phenomenon.params["value"] == 6

    def test_chatoyancy(self):
        """Chatoyancy phenomenon with string intensity."""
        desc = parse_cdl("orthorhombic[mmm]:{110}@1.0 | phenomenon[chatoyancy:sharp]")
        assert desc.phenomenon is not None
        assert desc.phenomenon.type == "chatoyancy"
        assert desc.phenomenon.params["intensity"] == "sharp"

    def test_phenomenon_with_modifications(self):
        """Phenomenon after modifications."""
        desc = parse_cdl("cubic[m3m]:{111} | elongate(c:1.5) | phenomenon[asterism:6]")
        assert len(desc.modifications) == 1
        assert desc.phenomenon is not None
        assert desc.phenomenon.type == "asterism"

    def test_phenomenon_with_twin(self):
        """Phenomenon after twin."""
        desc = parse_cdl("cubic[m3m]:{111} | twin(spinel) | phenomenon[asterism:6]")
        assert desc.twin is not None
        assert desc.phenomenon is not None
        assert desc.phenomenon.type == "asterism"

    def test_phenomenon_multiple_params(self):
        """Phenomenon with multiple parameters."""
        desc = parse_cdl("trigonal[-3m]:{10-11} | phenomenon[asterism:6, intensity:strong]")
        assert desc.phenomenon is not None
        assert desc.phenomenon.type == "asterism"
        assert desc.phenomenon.params["value"] == 6
        assert desc.phenomenon.params["intensity"] == "strong"

    def test_features_and_phenomenon(self):
        """Features on form AND phenomenon on description."""
        desc = parse_cdl("trigonal[-3m]:{10-11}@1.0[silk:dense] | phenomenon[asterism:6]")
        assert desc.forms[0].features is not None
        assert desc.forms[0].features[0].name == "silk"
        assert desc.phenomenon is not None
        assert desc.phenomenon.type == "asterism"

    def test_no_phenomenon_backwards_compat(self):
        """Existing CDL without phenomenon still works."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0")
        assert desc.phenomenon is None

    def test_phenomenon_str_representation(self):
        """PhenomenonSpec __str__ method."""
        phen = PhenomenonSpec("asterism", {"value": 6})
        assert str(phen) == "phenomenon[asterism, value:6]"

    def test_description_str_with_phenomenon(self):
        """CrystalDescription __str__ includes phenomenon."""
        desc = parse_cdl("trigonal[-3m]:{10-11}@1.0 | phenomenon[asterism:6]")
        desc_str = str(desc)
        assert "phenomenon[asterism" in desc_str

    def test_phenomenon_in_to_dict(self):
        """Phenomenon appears in to_dict() output."""
        desc = parse_cdl("trigonal[-3m]:{10-11} | phenomenon[asterism:6]")
        d = desc.to_dict()
        assert d["phenomenon"] is not None
        assert d["phenomenon"]["type"] == "asterism"
        assert d["phenomenon"]["params"]["value"] == 6

    def test_no_phenomenon_in_to_dict(self):
        """to_dict() has phenomenon=None when there is none."""
        desc = parse_cdl("cubic[m3m]:{111}")
        d = desc.to_dict()
        assert d["phenomenon"] is None


# =============================================================================
# Grouping Tests (CDL v1.3)
# =============================================================================


class TestGrouping:
    """Test CDL v1.3 parenthesized form grouping."""

    def test_simple_group(self):
        """Parenthesized group of forms."""
        desc = parse_cdl("cubic[m3m]:({111} + {100})")
        assert len(desc.forms) == 1
        group = desc.forms[0]
        assert isinstance(group, FormGroup)
        assert len(group.forms) == 2

    def test_group_with_shared_features(self):
        """Group with shared features applied to all forms."""
        desc = parse_cdl("cubic[m3m]:({111}@1.0 + {100}@1.3)[phantom:3]")
        assert len(desc.forms) == 1
        group = desc.forms[0]
        assert isinstance(group, FormGroup)
        assert group.features is not None
        assert group.features[0].name == "phantom"
        # flat_forms() should merge phantom:3 into both forms
        flat = desc.flat_forms()
        assert len(flat) == 2
        for f in flat:
            assert f.features is not None
            assert any(feat.name == "phantom" for feat in f.features)

    def test_group_plus_form(self):
        """Group combined with standalone form."""
        desc = parse_cdl("cubic[m3m]:({111} + {100})[phantom:3] + {110}@0.8")
        assert len(desc.forms) == 2
        assert isinstance(desc.forms[0], FormGroup)
        assert isinstance(desc.forms[1], CrystalForm)
        flat = desc.flat_forms()
        assert len(flat) == 3

    def test_nested_group(self):
        """Nested parenthesized groups."""
        desc = parse_cdl("cubic[m3m]:(({111}) + {100})")
        flat = desc.flat_forms()
        assert len(flat) == 2
        assert flat[0].miller.as_tuple() == (1, 1, 1)
        assert flat[1].miller.as_tuple() == (1, 0, 0)

    def test_group_str_representation(self):
        """FormGroup __str__ method."""
        desc = parse_cdl("cubic[m3m]:({111} + {100})[phantom:3]")
        group = desc.forms[0]
        s = str(group)
        assert "(" in s and ")" in s
        assert "phantom:3" in s

    def test_group_in_to_dict(self):
        """Groups appear in to_dict() output."""
        desc = parse_cdl("cubic[m3m]:({111} + {100})[phantom:3]")
        d = desc.to_dict()
        assert d["forms"][0]["type"] == "group"
        assert len(d["forms"][0]["forms"]) == 2
        assert d["forms"][0]["features"][0]["name"] == "phantom"
        # flat_forms in dict
        assert len(d["flat_forms"]) == 2

    def test_group_with_scales(self):
        """Group with individually scaled forms."""
        desc = parse_cdl("cubic[m3m]:({111}@1.0 + {100}@1.3)")
        flat = desc.flat_forms()
        assert flat[0].scale == 1.0
        assert flat[1].scale == 1.3


# =============================================================================
# Form Label Tests (CDL v1.3)
# =============================================================================


class TestFormLabels:
    """Test CDL v1.3 form labels."""

    def test_labeled_miller_form(self):
        """Form with label using Miller index."""
        desc = parse_cdl("cubic[m3m]:core:{111}@1.0 + rim:{100}@1.3")
        flat = desc.flat_forms()
        assert len(flat) == 2
        assert flat[0].label == "core"
        assert flat[0].miller.as_tuple() == (1, 1, 1)
        assert flat[1].label == "rim"
        assert flat[1].miller.as_tuple() == (1, 0, 0)

    def test_labeled_group(self):
        """Group with label."""
        desc = parse_cdl("cubic[m3m]:core:({111} + {100})[phantom:3]")
        assert len(desc.forms) == 1
        group = desc.forms[0]
        assert isinstance(group, FormGroup)
        assert group.label == "core"

    def test_label_str_representation(self):
        """Label appears in __str__ output."""
        desc = parse_cdl("cubic[m3m]:core:{111}@1.0")
        flat = desc.flat_forms()
        assert "core:" in str(flat[0])

    def test_unlabeled_forms_backwards_compat(self):
        """Unlabeled forms still work identically."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        flat = desc.flat_forms()
        assert flat[0].label is None
        assert flat[1].label is None

    def test_label_in_to_dict(self):
        """Labels appear in to_dict() output."""
        desc = parse_cdl("cubic[m3m]:core:{111}@1.0")
        d = desc.to_dict()
        assert d["flat_forms"][0]["label"] == "core"

    def test_named_form_not_treated_as_label(self):
        """Named forms (like 'prism') are NOT treated as labels."""
        # 'prism' is a known NAMED_FORM, so prism:{hkl} should NOT be parsed as label
        # Instead, 'prism' alone is a named form
        desc = parse_cdl("cubic[m3m]:octahedron@1.0")
        flat = desc.flat_forms()
        assert flat[0].name == "octahedron"
        assert flat[0].label is None


# =============================================================================
# Named Reference Tests (CDL v1.3)
# =============================================================================


class TestNamedReferences:
    """Test CDL v1.3 named definitions and $references."""

    def test_simple_definition(self):
        """Simple named definition and reference."""
        desc = parse_cdl("@oct = {111}@1.0\ncubic[m3m]:$oct + {100}@1.3")
        assert len(desc.flat_forms()) == 2
        assert desc.flat_forms()[0].miller.as_tuple() == (1, 1, 1)
        assert desc.flat_forms()[0].scale == 1.0

    def test_multiple_definitions(self):
        """Multiple definitions."""
        cdl = "@prism = {10-10}@1.0\n@rhomb = {10-11}@0.8\ntrigonal[-3m]:$prism + $rhomb"
        desc = parse_cdl(cdl)
        assert len(desc.flat_forms()) == 2

    def test_definition_referencing_definition(self):
        """Definition that references another definition."""
        cdl = "@a = {111}@1.0\n@b = {100}@1.3\n@combo = $a + $b\ncubic[m3m]:$combo"
        desc = parse_cdl(cdl)
        assert len(desc.flat_forms()) == 2

    def test_definitions_stored(self):
        """Definitions are stored on the CrystalDescription."""
        desc = parse_cdl("@oct = {111}@1.0\ncubic[m3m]:$oct")
        assert desc.definitions is not None
        assert len(desc.definitions) == 1
        assert desc.definitions[0].name == "oct"

    def test_undefined_reference_error(self):
        """Undefined reference raises ParseError."""
        with pytest.raises(ParseError):
            parse_cdl("cubic[m3m]:$unknown")

    def test_definitions_with_comments(self):
        """Definitions work with comments."""
        cdl = "# Define forms\n@oct = {111}@1.0\n# Use them\ncubic[m3m]:$oct"
        desc = parse_cdl(cdl)
        assert len(desc.flat_forms()) == 1

    def test_no_definitions_backwards_compat(self):
        """CDL without definitions has definitions=None."""
        desc = parse_cdl("cubic[m3m]:{111}")
        assert desc.definitions is None

    def test_definitions_in_to_dict(self):
        """Definitions appear in to_dict() output."""
        desc = parse_cdl("@oct = {111}@1.0\ncubic[m3m]:$oct")
        d = desc.to_dict()
        assert d["definitions"] is not None
        assert len(d["definitions"]) == 1
        assert d["definitions"][0]["name"] == "oct"

    def test_no_definitions_in_to_dict(self):
        """to_dict() has definitions=None when there are none."""
        desc = parse_cdl("cubic[m3m]:{111}")
        d = desc.to_dict()
        assert d["definitions"] is None

    def test_definition_with_doc_comments(self):
        """Definitions work alongside doc comments."""
        cdl = "#! Mineral: Diamond\n@oct = {111}@1.0\ncubic[m3m]:$oct"
        desc = parse_cdl(cdl)
        assert desc.doc_comments == ["Mineral: Diamond"]
        assert desc.definitions is not None
        assert len(desc.flat_forms()) == 1

    def test_definition_with_features(self):
        """Definition body with features resolves correctly."""
        cdl = "@oct = {111}@1.0\ncubic[m3m]:$oct[phantom:3]"
        desc = parse_cdl(cdl)
        flat = desc.flat_forms()
        assert len(flat) == 1
        assert flat[0].features is not None
        assert flat[0].features[0].name == "phantom"


# =============================================================================
# flat_forms() Tests (CDL v1.3)
# =============================================================================


class TestFlatForms:
    """Test CDL v1.3 flat_forms() backwards compatibility method."""

    def test_flat_forms_simple(self):
        """flat_forms() on simple CDL returns same count as forms."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        assert len(desc.flat_forms()) == 2

    def test_flat_forms_group(self):
        """flat_forms() flattens groups."""
        desc = parse_cdl("cubic[m3m]:({111} + {100})[phantom:3]")
        flat = desc.flat_forms()
        assert len(flat) == 2
        # Both should have phantom:3 feature
        for f in flat:
            assert f.features is not None
            assert any(feat.name == "phantom" for feat in f.features)

    def test_flat_forms_mixed(self):
        """flat_forms() with mix of groups and plain forms."""
        desc = parse_cdl("cubic[m3m]:({111} + {100})[phantom:3] + {110}@0.8")
        flat = desc.flat_forms()
        assert len(flat) == 3
        # First two have phantom, third doesn't
        assert flat[0].features is not None
        assert flat[1].features is not None
        assert flat[2].features is None

    def test_flat_forms_backwards_compat(self):
        """flat_forms() works identically for v1-style CDL."""
        for _, cdl in [
            ("simple", "cubic[m3m]:{111}"),
            ("truncated", "cubic[m3m]:{111}@1.0 + {100}@1.3"),
            ("triple", "cubic[m3m]:{111}@1.0 + {100}@0.5 + {110}@0.3"),
        ]:
            desc = parse_cdl(cdl)
            flat = desc.flat_forms()
            assert len(flat) == len(desc.forms)
            for i, f in enumerate(flat):
                assert f.miller == desc.forms[i].miller
                assert f.scale == desc.forms[i].scale

    def test_flat_forms_preserves_scale(self):
        """flat_forms() preserves individual form scales."""
        desc = parse_cdl("cubic[m3m]:({111}@1.0 + {100}@1.3)[phantom:3]")
        flat = desc.flat_forms()
        assert flat[0].scale == 1.0
        assert flat[1].scale == 1.3

    def test_flat_forms_nested_groups(self):
        """flat_forms() handles nested groups."""
        desc = parse_cdl("cubic[m3m]:(({111} + {100}) + {110})")
        flat = desc.flat_forms()
        assert len(flat) == 3

    def test_flat_forms_feature_merge(self):
        """flat_forms() merges parent and child features."""
        desc = parse_cdl("cubic[m3m]:({111}[trigon:dense] + {100})[phantom:3]")
        flat = desc.flat_forms()
        assert len(flat) == 2
        # First form should have both phantom (from group) and trigon (own)
        f0_names = [feat.name for feat in flat[0].features]
        assert "phantom" in f0_names
        assert "trigon" in f0_names
        # Second form should have only phantom (from group)
        f1_names = [feat.name for feat in flat[1].features]
        assert "phantom" in f1_names
        assert len(f1_names) == 1


# =============================================================================
# Version Test (CDL v1.3)
# =============================================================================


class TestVersion:
    """Test version is updated."""

    def test_version_1_3(self):
        """Version is 1.3.0."""
        import cdl_parser
        assert cdl_parser.__version__ == "1.3.0"


# =============================================================================
# v1 Regression (CDL v1.3)
# =============================================================================


class TestV1Regression:
    """Ensure all v1/v1.2 CDL still works with v1.3 changes."""

    @pytest.mark.parametrize("name,cdl", CDL_TEST_CASES)
    def test_all_v1_cases_still_work(self, name, cdl):
        """All CDL_TEST_CASES parse successfully with v1.3."""
        desc = parse_cdl(cdl)
        assert isinstance(desc, CrystalDescription)
        # forms are still iterable and contain CrystalForm instances
        for f in desc.forms:
            assert isinstance(f, CrystalForm)
        # flat_forms() returns same as forms for v1-style CDL
        flat = desc.flat_forms()
        assert len(flat) == len(desc.forms)

    def test_v1_forms_are_crystal_form_instances(self):
        """v1-style CDL forms are CrystalForm, not FormGroup."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        for f in desc.forms:
            assert isinstance(f, CrystalForm)
            assert not isinstance(f, FormGroup)

    def test_v1_definitions_none(self):
        """v1-style CDL has no definitions."""
        desc = parse_cdl("cubic[m3m]:{111}")
        assert desc.definitions is None

    def test_v1_to_dict_has_flat_forms(self):
        """to_dict() includes flat_forms key."""
        desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        d = desc.to_dict()
        assert "flat_forms" in d
        assert len(d["flat_forms"]) == 2
