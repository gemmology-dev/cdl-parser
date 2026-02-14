"""
CDL Parser.

Lexer and parser for Crystal Description Language strings.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .constants import (
    ALL_POINT_GROUPS,
    CRYSTAL_SYSTEMS,
    DEFAULT_POINT_GROUPS,
    NAMED_FORMS,
    POINT_GROUPS,
    TWIN_LAWS,
)
from .exceptions import ParseError, ValidationError
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


def strip_comments(text: str) -> tuple[str, list[str]]:
    """Strip comments from CDL text before lexing.

    Extracts doc comments (#! Key: Value) and removes block (/* ... */)
    and line (# ...) comments.

    Args:
        text: Raw CDL string possibly containing comments.

    Returns:
        Tuple of (cleaned text with comments removed, list of doc comment strings).
    """
    doc_comments: list[str] = []

    # Extract doc comments (#! ...) before stripping anything else.
    # Process line-by-line so we can identify #! lines.
    lines = text.split("\n")
    processed_lines: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#!"):
            # Doc comment — capture the content after "#! " or "#!"
            content = stripped[2:].strip()
            doc_comments.append(content)
            # Don't include this line in the CDL text
        else:
            processed_lines.append(line)

    text = "\n".join(processed_lines)

    # Strip block comments (/* ... */), which may span multiple lines
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

    # Strip line comments (# to end of line)
    text = re.sub(r"#[^\n]*", "", text)

    return text, doc_comments

# =============================================================================
# Token Types
# =============================================================================


class TokenType(Enum):
    """Token types for CDL lexer."""

    SYSTEM = "SYSTEM"
    POINT_GROUP = "POINT_GROUP"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COLON = "COLON"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    PLUS = "PLUS"
    PIPE = "PIPE"
    AT = "AT"
    COMMA = "COMMA"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    IDENTIFIER = "IDENTIFIER"
    DOLLAR = "DOLLAR"
    EQUALS = "EQUALS"
    EOF = "EOF"


@dataclass
class Token:
    """A lexer token."""

    type: TokenType
    value: Any
    position: int
    raw: str | None = None  # Original text (for preserving leading zeros)


# =============================================================================
# Lexer
# =============================================================================


class Lexer:
    """Tokenizer for CDL strings.

    Converts a CDL string into a sequence of tokens for parsing.
    """

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def _skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1

    def _read_number(self) -> Token:
        """Read integer or float, preserving raw text for leading zeros."""
        start = self.pos
        has_decimal = False

        if self.text[self.pos] == "-":
            self.pos += 1

        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch.isdigit():
                self.pos += 1
            elif ch == "." and not has_decimal:
                has_decimal = True
                self.pos += 1
            else:
                break

        value_str = self.text[start : self.pos]
        if has_decimal:
            return Token(TokenType.FLOAT, float(value_str), start, raw=value_str)
        # Store raw string to preserve leading zeros (important for Miller indices)
        return Token(TokenType.INTEGER, int(value_str), start, raw=value_str)

    def _read_identifier_or_point_group(self) -> Token:
        """Read identifier (system, point group, form name, etc.).

        Point groups can contain '/', '-', and digits (e.g., 6/mmm, -43m, 4/m)
        """
        start = self.pos

        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch.isalnum() or ch in "_/-":
                self.pos += 1
            else:
                break

        value = self.text[start : self.pos]
        value_lower = value.lower()

        # Check if it's a crystal system
        if value_lower in CRYSTAL_SYSTEMS:
            return Token(TokenType.SYSTEM, value_lower, start)

        # Check if it's a point group
        if value in ALL_POINT_GROUPS:
            return Token(TokenType.POINT_GROUP, value, start)

        return Token(TokenType.IDENTIFIER, value, start)

    def next_token(self) -> Token:
        """Get next token."""
        self._skip_whitespace()

        if self.pos >= self.length:
            return Token(TokenType.EOF, None, self.pos)

        ch = self.text[self.pos]
        start = self.pos

        # Single character tokens
        single_char_tokens = {
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ":": TokenType.COLON,
            "+": TokenType.PLUS,
            "|": TokenType.PIPE,
            "@": TokenType.AT,
            ",": TokenType.COMMA,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "$": TokenType.DOLLAR,
            "=": TokenType.EQUALS,
        }

        if ch in single_char_tokens:
            self.pos += 1
            return Token(single_char_tokens[ch], ch, start)

        # Check if this might be a point group starting with digit
        if ch.isdigit():
            temp_pos = self.pos
            while temp_pos < self.length and (
                self.text[temp_pos].isalnum() or self.text[temp_pos] in "/-"
            ):
                temp_pos += 1
            potential = self.text[self.pos : temp_pos]

            if potential in ALL_POINT_GROUPS:
                # Check what follows - if decimal point, this is a number
                if temp_pos < self.length and self.text[temp_pos] == ".":
                    return self._read_number()
                self.pos = temp_pos
                return Token(TokenType.POINT_GROUP, potential, start)
            return self._read_number()

        # Numbers with leading negative (could be point group like -43m)
        if ch == "-" and self.pos + 1 < self.length and self.text[self.pos + 1].isdigit():
            temp_pos = self.pos
            while temp_pos < self.length and (
                self.text[temp_pos].isalnum() or self.text[temp_pos] in "/-"
            ):
                temp_pos += 1
            potential = self.text[self.pos : temp_pos]

            if potential in ALL_POINT_GROUPS:
                if temp_pos < self.length and self.text[temp_pos] == ".":
                    return self._read_number()
                self.pos = temp_pos
                return Token(TokenType.POINT_GROUP, potential, start)
            return self._read_number()

        # Identifiers
        if ch.isalpha() or ch == "_":
            return self._read_identifier_or_point_group()

        raise ParseError(f"Unexpected character '{ch}'", position=self.pos)

    def tokenize(self) -> list[Token]:
        """Tokenize entire string."""
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens


# =============================================================================
# Definition Pre-processing
# =============================================================================


def _preprocess_definitions(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Extract @name = expression definitions and resolve $name references.

    Args:
        text: Comment-stripped CDL text (may be multi-line).

    Returns:
        Tuple of (resolved CDL body text, list of (name, raw_body) definition pairs).
    """
    lines = text.split("\n")
    definitions: list[tuple[str, str]] = []  # (name, raw_body)
    body_lines: list[str] = []

    # First pass: extract definition lines
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@"):
            # Parse @name = expression
            match = re.match(r"@(\w+)\s*=\s*(.+)", stripped)
            if match:
                name = match.group(1)
                body = match.group(2).strip()
                definitions.append((name, body))
                continue
        body_lines.append(line)

    # Build name -> body mapping, resolving forward references within definitions
    resolved: dict[str, str] = {}
    for name, body in definitions:
        # Resolve $references within this definition body
        resolved_body = body
        for prev_name, prev_body in resolved.items():
            resolved_body = re.sub(r"\$" + prev_name + r"(?!\w)", prev_body, resolved_body)
        resolved[name] = resolved_body

    # Second pass: resolve $references in the main body
    body_text = "\n".join(body_lines)
    for name, resolved_body in resolved.items():
        body_text = re.sub(r"\$" + name + r"(?!\w)", resolved_body, body_text)

    # Check for unresolved $references
    unresolved = re.findall(r"\$(\w+)", body_text)
    if unresolved:
        raise ParseError(f"Undefined reference: ${unresolved[0]}", position=-1)

    return body_text, definitions


def _parse_definition_bodies(
    definitions: list[tuple[str, str]],
) -> list[Definition]:
    """Parse raw definition bodies into Definition objects.

    Each definition body is parsed as a form list.
    """
    result: list[Definition] = []
    resolved_bodies: dict[str, str] = {}

    for name, raw_body in definitions:
        # Resolve references within this body
        body = raw_body
        for prev_name, prev_resolved in resolved_bodies.items():
            body = re.sub(r"\$" + prev_name + r"(?!\w)", prev_resolved, body)
        resolved_bodies[name] = body

        # Parse the resolved body as a form list
        lexer = Lexer(body)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        forms = parser._parse_form_list()
        result.append(Definition(name=name, body=forms))

    return result


# =============================================================================
# Parser
# =============================================================================


class Parser:
    """Parser for CDL strings.

    Parses a sequence of tokens into a CrystalDescription.
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _advance(self) -> Token:
        token = self._current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        token = self._current()
        if token.type != token_type:
            raise ParseError(
                f"Expected {token_type.value}, got {token.type.value}", position=token.position
            )
        return self._advance()

    def parse(self) -> CrystalDescription:
        """Parse CDL string to CrystalDescription."""
        # Parse system
        system_token = self._expect(TokenType.SYSTEM)
        system = system_token.value

        # Parse optional point group
        point_group = DEFAULT_POINT_GROUPS[system]
        if self._current().type == TokenType.LBRACKET:
            self._advance()  # consume [
            pg_token = self._expect(TokenType.POINT_GROUP)
            point_group = pg_token.value
            self._expect(TokenType.RBRACKET)

            # Validate point group for system
            if point_group not in POINT_GROUPS[system]:
                raise ValidationError(
                    f"Point group '{point_group}' not valid for {system} system",
                    field="point_group",
                    value=point_group,
                )

        # Expect colon
        self._expect(TokenType.COLON)

        # Parse forms
        forms = self._parse_form_list()

        # Parse optional modifications
        modifications = []
        if self._current().type == TokenType.PIPE:
            self._advance()  # consume |
            # Check if it's modifications, twin, or phenomenon
            if self._current().type == TokenType.IDENTIFIER:
                ident = self._current().value.lower()
                if ident == "twin":
                    pass  # It's a twin, not modifications
                elif ident == "phenomenon":
                    pass  # It's a phenomenon, not modifications
                elif ident in {"elongate", "truncate", "taper", "bevel", "flatten"}:
                    modifications = self._parse_modifications()

        # Parse optional twin
        twin = None
        if self._current().type == TokenType.PIPE:
            self._advance()  # consume |
        if self._current().type == TokenType.IDENTIFIER and self._current().value.lower() == "twin":
            twin = self._parse_twin()

        # Parse optional phenomenon
        phenomenon = None
        if self._current().type == TokenType.PIPE:
            self._advance()  # consume |
        if self._current().type == TokenType.IDENTIFIER and self._current().value.lower() == "phenomenon":
            phenomenon = self._parse_phenomenon()

        return CrystalDescription(
            system=system,
            point_group=point_group,
            forms=forms,
            modifications=modifications,
            twin=twin,
            phenomenon=phenomenon,
        )

    def _parse_form_list(self) -> list[FormNode]:
        """Parse form_list = form_or_group ('+' form_or_group)*"""
        forms: list[FormNode] = [self._parse_form_or_group()]

        while self._current().type == TokenType.PLUS:
            self._advance()  # consume +
            forms.append(self._parse_form_or_group())

        return forms

    def _parse_form_or_group(self) -> FormNode:
        """Parse either a parenthesized group or a single form.

        Handles:
        - (form + form)[features] - group
        - label:(form + form)[features] - labeled group
        - label:{hkl}@scale[features] - labeled form
        - {hkl}@scale[features] - plain form
        - named_form@scale[features] - named form
        """
        label = None

        # Check for label: identifier followed by COLON, then LBRACE or LPAREN
        if self._current().type == TokenType.IDENTIFIER:
            ident = self._current().value
            if self._peek().type == TokenType.COLON:
                # Look at what follows the colon
                after_colon = self._peek(2)
                if after_colon.type == TokenType.LPAREN:
                    # label:(group)
                    label = ident
                    self._advance()  # consume identifier
                    self._advance()  # consume colon
                elif after_colon.type == TokenType.LBRACE:
                    # Could be label:{hkl} - but only if identifier is NOT a named form
                    # If it IS a named form, we'd need a different syntax.
                    # Named forms use: octahedron (no colon) - so label:{hkl} is unambiguous
                    # when the identifier is NOT a known crystal system
                    ident_lower = ident.lower()
                    if ident_lower not in NAMED_FORMS:
                        label = ident
                        self._advance()  # consume identifier
                        self._advance()  # consume colon

        if self._current().type == TokenType.LPAREN:
            return self._parse_group(label)
        else:
            return self._parse_form(label)

    def _parse_group(self, label: str | None = None) -> FormGroup:
        """Parse a parenthesized group: (form + form)[features]"""
        self._advance()  # consume (

        forms = self._parse_form_list()

        self._expect(TokenType.RPAREN)

        # Optional features
        features = None
        if self._current().type == TokenType.LBRACKET:
            features = self._parse_features()

        return FormGroup(forms=forms, features=features, label=label)

    def _parse_form(self, label: str | None = None) -> CrystalForm:
        """Parse form = (form_name | miller_index) ['@' scale] ['[' features ']']"""
        name = None
        miller = None

        if self._current().type == TokenType.IDENTIFIER:
            # Named form
            name_token = self._advance()
            name = name_token.value.lower()
            if name not in NAMED_FORMS:
                raise ParseError(f"Unknown form name: {name}", position=name_token.position)
            hkl = NAMED_FORMS[name]
            miller = MillerIndex(hkl[0], hkl[1], hkl[2])
        elif self._current().type == TokenType.LBRACE:
            # Miller index
            miller = self._parse_miller_index()
        else:
            raise ParseError(
                "Expected form name or Miller index", position=self._current().position
            )

        # Optional scale
        scale = 1.0
        if self._current().type == TokenType.AT:
            self._advance()  # consume @
            scale_token = self._current()
            if scale_token.type == TokenType.FLOAT:
                scale = self._advance().value
            elif scale_token.type == TokenType.INTEGER:
                scale = float(self._advance().value)
            else:
                raise ParseError("Expected scale value after @", position=scale_token.position)

        # Optional features [feature:value, ...]
        features = None
        if self._current().type == TokenType.LBRACKET:
            features = self._parse_features()

        return CrystalForm(miller=miller, scale=scale, name=name, features=features, label=label)

    def _parse_miller_index(self) -> MillerIndex:
        """Parse Miller index {hkl} or {hkil}.

        Handles both formats:
        - Separated: {1, 1, 1} or {1 1 1}
        - Condensed: {111}, {001}, {100} (single digits only)
        - 4-index Miller-Bravais: {10-10}, {10-11} (for hexagonal/trigonal)
        """
        self._expect(TokenType.LBRACE)

        indices = []

        # Collect all integers (may need to split condensed notation)
        while self._current().type == TokenType.INTEGER:
            token = self._advance()
            value = token.value
            raw = token.raw or str(value)

            # Use raw string to preserve leading zeros and handle condensed notation
            if raw.startswith("-"):
                sign = -1
                raw_digits = raw[1:]
            else:
                sign = 1
                raw_digits = raw

            # Split multi-digit numbers into individual indices
            if len(raw_digits) >= 2:
                for i, ch in enumerate(raw_digits):
                    if i == 0:
                        indices.append(sign * int(ch))
                    else:
                        indices.append(int(ch))
            else:
                indices.append(value)

        self._expect(TokenType.RBRACE)

        if len(indices) == 3:
            return MillerIndex(indices[0], indices[1], indices[2])
        elif len(indices) == 4:
            return MillerIndex(indices[0], indices[1], indices[3], i=indices[2])
        else:
            raise ParseError(
                f"Miller index must have 3 or 4 components, got {len(indices)}: {indices}. "
                f"Use separated format: {{1 1 1}} or {{1, 1, 1}}",
                position=self._current().position,
            )

    def _parse_modifications(self) -> list[Modification]:
        """Parse mod_list = modification (',' modification)*"""
        mods = [self._parse_modification()]

        while self._current().type == TokenType.COMMA:
            self._advance()  # consume ,
            mods.append(self._parse_modification())

        return mods

    def _parse_modification(self) -> Modification:
        """Parse a single modification."""
        mod_token = self._current()
        mod_type = self._expect(TokenType.IDENTIFIER).value.lower()

        if mod_type not in {"elongate", "truncate", "taper", "bevel", "flatten"}:
            raise ParseError(f"Unknown modification type: {mod_type}", position=mod_token.position)

        self._expect(TokenType.LPAREN)

        params = {}

        # Parse parameters based on type
        if mod_type == "elongate":
            # elongate(axis:ratio)
            axis = self._expect(TokenType.IDENTIFIER).value.lower()
            self._expect(TokenType.COLON)
            ratio = self._parse_number()
            params = {"axis": axis, "ratio": ratio}
        elif mod_type == "truncate":
            # truncate(form:depth)
            if self._current().type == TokenType.LBRACE:
                form = self._parse_miller_index()
            else:
                form = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.COLON)
            depth = self._parse_number()
            params = {"form": form, "depth": depth}
        elif mod_type == "taper":
            # taper(direction:factor)
            direction = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.COLON)
            factor = self._parse_number()
            params = {"direction": direction, "factor": factor}
        elif mod_type == "bevel":
            # bevel(edges:width)
            edges = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.COLON)
            width = self._parse_number()
            params = {"edges": edges, "width": width}
        elif mod_type == "flatten":
            # flatten(axis:ratio)
            axis = self._expect(TokenType.IDENTIFIER).value.lower()
            self._expect(TokenType.COLON)
            ratio = self._parse_number()
            params = {"axis": axis, "ratio": ratio}

        self._expect(TokenType.RPAREN)

        return Modification(type=mod_type, params=params)

    def _parse_twin(self) -> TwinSpec:
        """Parse twin specification."""
        self._expect(TokenType.IDENTIFIER)  # consume 'twin'
        self._expect(TokenType.LPAREN)

        law = None
        axis = None
        angle = 180.0
        twin_type = "contact"
        count = 2

        # Check if it's a named law or custom axis
        if self._current().type == TokenType.IDENTIFIER:
            ident = self._current().value.lower()
            if ident in TWIN_LAWS:
                law = self._advance().value.lower()
                # Optional count
                if self._current().type == TokenType.COMMA:
                    self._advance()
                    count = self._parse_int_or_point_group()
            else:
                raise ParseError(f"Unknown twin law: {ident}", position=self._current().position)
        elif self._current().type == TokenType.LBRACKET:
            # Custom axis [x,y,z]
            self._advance()
            x = self._parse_number()
            self._expect(TokenType.COMMA)
            y = self._parse_number()
            self._expect(TokenType.COMMA)
            z = self._parse_number()
            self._expect(TokenType.RBRACKET)
            axis = (x, y, z)

            self._expect(TokenType.COMMA)
            angle = self._parse_number()

            if self._current().type == TokenType.COMMA:
                self._advance()
                twin_type = self._expect(TokenType.IDENTIFIER).value.lower()

        self._expect(TokenType.RPAREN)

        return TwinSpec(law=law, axis=axis, angle=angle, twin_type=twin_type, count=count)

    def _parse_features(self) -> list[Feature]:
        """Parse feature list [name:value, name:value, ...]"""
        self._advance()  # consume [
        features = []

        while self._current().type != TokenType.RBRACKET and self._current().type != TokenType.EOF:
            # Parse feature name
            name_token = self._expect(TokenType.IDENTIFIER)
            name = name_token.value.lower()

            # Expect colon
            self._expect(TokenType.COLON)

            # Parse values until comma or ]
            values: list[int | float | str] = []
            values.append(self._parse_feature_value())

            # Check for more values separated by comma
            # But distinguish "next value" from "next feature"
            # Next feature = IDENTIFIER followed by COLON
            while self._current().type == TokenType.COMMA:
                next_tok = self._peek(1)
                next_next = self._peek(2)
                if next_tok.type == TokenType.IDENTIFIER and next_next.type == TokenType.COLON:
                    break  # It's a new feature
                self._advance()  # consume comma
                values.append(self._parse_feature_value())

            features.append(Feature(name=name, values=values))

            # Consume comma between features
            if self._current().type == TokenType.COMMA:
                self._advance()

        self._expect(TokenType.RBRACKET)
        return features

    def _parse_feature_value(self) -> int | float | str:
        """Parse a single feature value (number or identifier)."""
        token = self._current()
        if token.type == TokenType.INTEGER:
            return int(self._advance().value)
        elif token.type == TokenType.FLOAT:
            return float(self._advance().value)
        elif token.type == TokenType.IDENTIFIER:
            return self._advance().value.lower()
        elif token.type == TokenType.POINT_GROUP:
            # Handle numeric point groups like '1', '3' as values
            value = token.value
            try:
                result = int(value)
                self._advance()
                return result
            except ValueError:
                pass
            return self._advance().value
        raise ParseError("Expected feature value", position=token.position)

    def _parse_phenomenon(self) -> PhenomenonSpec:
        """Parse phenomenon[type:value, param:value, ...]"""
        self._expect(TokenType.IDENTIFIER)  # consume 'phenomenon'
        self._expect(TokenType.LBRACKET)

        # First token is the phenomenon type
        phen_type = self._expect(TokenType.IDENTIFIER).value.lower()

        params: dict[str, int | float | str] = {}

        # Check for :value after type (e.g., asterism:6)
        if self._current().type == TokenType.COLON:
            self._advance()
            val = self._parse_feature_value()
            # Store as the primary value
            if isinstance(val, (int, float)):
                params["value"] = val
            else:
                params["intensity"] = val

        # Parse additional comma-separated params
        while self._current().type == TokenType.COMMA:
            self._advance()
            if self._current().type == TokenType.IDENTIFIER:
                key = self._advance().value.lower()
                if self._current().type == TokenType.COLON:
                    self._advance()
                    params[key] = self._parse_feature_value()
                else:
                    # Bare identifier value
                    params[key] = True
            elif self._current().type in (TokenType.INTEGER, TokenType.FLOAT, TokenType.POINT_GROUP):
                val = self._parse_feature_value()
                params["value"] = val

        self._expect(TokenType.RBRACKET)
        return PhenomenonSpec(type=phen_type, params=params)

    def _parse_number(self) -> float:
        """Parse a number (int or float).

        Also handles the case where a single digit (like 1, 3) is tokenized
        as a POINT_GROUP since those are valid point group symbols.
        """
        token = self._current()
        if token.type == TokenType.INTEGER:
            return float(self._advance().value)
        elif token.type == TokenType.FLOAT:
            return float(self._advance().value)
        elif token.type == TokenType.POINT_GROUP:
            # Handle numeric point groups like '1', '3', '-1'
            value = token.value
            try:
                result = float(value)
                self._advance()
                return result
            except ValueError:
                pass
        raise ParseError("Expected number", position=token.position)

    def _parse_int_or_point_group(self) -> int:
        """Parse an integer, also accepting point groups that are just numbers."""
        token = self._current()
        if token.type == TokenType.INTEGER:
            return int(self._advance().value)
        elif token.type == TokenType.POINT_GROUP:
            value = token.value
            if value.lstrip("-").isdigit():
                self._advance()
                return int(value)
            raise ParseError(
                f"Expected integer but got point group '{value}'", position=token.position
            )
        else:
            raise ParseError("Expected integer", position=token.position)


# =============================================================================
# Public API
# =============================================================================


def parse_cdl(text: str) -> CrystalDescription:
    """Parse a CDL string to CrystalDescription.

    Args:
        text: CDL string like "cubic[m3m]:{111}@1.0 + {100}@0.3"

    Returns:
        CrystalDescription object

    Raises:
        ParseError: If parsing fails due to syntax error
        ValidationError: If validation fails (e.g., invalid point group)

    Examples:
        >>> desc = parse_cdl("cubic[m3m]:{111}")
        >>> desc.system
        'cubic'
        >>> desc.forms[0].miller.as_tuple()
        (1, 1, 1)

        >>> desc = parse_cdl("cubic[m3m]:{111}@1.0 + {100}@1.3")
        >>> len(desc.forms)
        2

        >>> desc = parse_cdl("trigonal[-3m]:{10-10}@1.0 + {10-11}@0.8")
        >>> desc.forms[0].miller.i
        -1
    """
    cleaned, doc_comments = strip_comments(text)
    cleaned = cleaned.strip()
    if not cleaned:
        raise ParseError("Empty CDL string after stripping comments", position=0)

    # Pre-process definitions (@name = expression) and resolve $references
    body_text, raw_definitions = _preprocess_definitions(cleaned)
    body_text = body_text.strip()
    if not body_text:
        raise ParseError("Empty CDL string after extracting definitions", position=0)

    # Parse definition bodies into Definition objects
    definitions = _parse_definition_bodies(raw_definitions) if raw_definitions else None

    lexer = Lexer(body_text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    desc = parser.parse()
    desc.doc_comments = doc_comments if doc_comments else None
    desc.definitions = definitions
    return desc


def validate_cdl(text: str) -> tuple[bool, str | None]:
    """Validate a CDL string.

    Args:
        text: CDL string to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_cdl("cubic[m3m]:{111}")
        (True, None)

        >>> valid, error = validate_cdl("invalid{{{")
        >>> valid
        False
    """
    try:
        parse_cdl(text)
        return True, None
    except (ParseError, ValidationError) as e:
        return False, str(e)
