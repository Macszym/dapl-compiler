from pyexpat.errors import messages
from DAPLParser import DAPLParser
from antlr4.error.ErrorListener import ErrorListener
from errors import SyntaxError
import difflib
import re


class SyntaxErrorListener(ErrorListener):
    def __init__(self, input_lines=None):
        super().__init__()
        self.input_lines = input_lines
        self.syntax_errors = []
        self.has_errors = False

        self.keywords = [
            'if', 'else', 'while', 'for', 'return', 'int', 'double', 'bool',
            'true', 'false', 'function', 'var', 'out', 'input', 'start',
            ';','=', '+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>='
        ]

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.has_errors = True
        text = ""
        if self.input_lines and 1 <= line <= len(self.input_lines):
            text = self.input_lines[line-1]

        if re.match(r'^\s*Table\b', text):
            if '<' not in text:
                raise SyntaxError(
                    f"After generic type name 'Table' you must open parameters with '<' (line {line}, col {column})."
                )
            if '<' in text and '>' not in text:
                raise SyntaxError(
                    f"Missing '>' to close generic parameters for 'Table' (line {line}, col {column})."
                )
            inside = text.split('<', 1)[1].split('>', 1)[0]
            if not inside.strip():
                raise SyntaxError(
                    f"Generic type 'Table' requires at least one parameter inside '<>' "
                    f"(line {line}, col {column})."
                )
            for p in [p.strip() for p in inside.split(',')]:
                parts = [x.strip() for x in p.split(':', 1)]
                if len(parts) != 2 or not re.match(r'^[A-Za-z_]\w*$', parts[1]):
                    typename = parts[0]
                    raise SyntaxError(
                        f"Missing or invalid parameter name after ':' for type '{typename}' "
                        f"in generic at line {line}, column {column}."
                    )
        m = re.match(r'^\s*([A-Za-z_]\w+)\s*(filter|show|analyze|addColumn|addRow|drop|join|groupBy)\b', text)
        if m:
            table_name, op = m.groups()
            col = text.find(op) + 1
            raise SyntaxError(
                f"Missing '.' between table name '{table_name}' and operation '{op}' "
                f"(line {line}, column {col}). Did you mean '{table_name}.{op}'?"
            )
        pattern = r"missing '(.+)' at '(.+)'"
        match = re.match(pattern, msg)
        if match:
            missing_symbol = match.group(1)
            offending_token = match.group(2)

            token_stream = recognizer.getInputStream()
            current_index = offendingSymbol.tokenIndex
            previous_token = token_stream.get(current_index - 1) if current_index > 0 else None

            error_msg = f'You have forgotten "{missing_symbol}" at line {previous_token.line}, column {previous_token.column}'
            raise SyntaxError(error_msg)

        pattern = r"no viable alternative at input '(.+?)'"

        match = re.search(pattern, msg)
        if match:
            offending_input = match.group(1)
            close = difflib.get_close_matches(offending_input, self.keywords)
            if close:
                close = offending_input.replace(close[0], "")
                close = difflib.get_close_matches(close, self.keywords)
            else:
                error_msg = (
                    "Unrecognised syntax error"
                )

            if len(close) > 0:
                error_msg = f'Did you mean "{close[0]}" at line {line}, column {column}?'
                raise SyntaxError(error_msg)

        pattern = r"extraneous input '(.+?)' expecting \{(.+?)\}"
        match = re.match(pattern, msg)
        if match:
            offending_token = match.group(1)
            token_stream = recognizer.getInputStream()
            current_index = offendingSymbol.tokenIndex
            previous_token = token_stream.get(current_index - 1) if current_index > 0 else None

            offending_input = previous_token.text
            close = difflib.get_close_matches(offending_input, self.keywords)
            if close:
                close = offending_input.replace(close[0], "")
                close = difflib.get_close_matches(close, self.keywords)

            if len(close) > 0:
                error_msg = f'Did you mean "{close[0]}" at line {line}, column {column}?'
                raise SyntaxError(error_msg)

        m = re.match(r"mismatched input '(.+)' expecting (.+)", msg)
        if m:
            got, exp = m.groups()
            if got == ':' and ('NAME' in exp or 'TYPE' in exp):
                raise SyntaxError(
                    f'Missing type before colon at line {line}, column {column}.'
                )
            raise SyntaxError(
                f'Mismatched token "{got}" at line {line}, column {column}. '
                f'Expected: {exp}.'
            )

        raise SyntaxError(f'Syntax error in {line}, column {column}: {msg}')