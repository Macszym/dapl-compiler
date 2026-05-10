import csv

from antlr4.tree.Tree import TerminalNodeImpl
from pathlib import Path
from DAPLVisitor import DAPLVisitor
from DAPLParser import DAPLParser
from errors import *
from VariableListner import FunctionDefinition

class FirstVisitor(DAPLVisitor):
    MAX_DAPL_RECURSION_DEPTH = 30
    def __init__(self, variables: dict, constants: dict, tables: dict,
                 tables_to_heap: dict, heap: dict, functions: dict, source_lines: list, library_functions: list):
        self.global_variables = variables
        self.constants = constants
        self.tables = tables
        self.tables_to_heap = tables_to_heap
        self.heap = heap
        self.functions: dict[str, FunctionDefinition] = functions
        self.source_lines = source_lines
        self.scope_stack: list[dict] = [self.global_variables.copy()]
        self.function_frame_indices: list[int] = []
        self.current_function_stack: list[FunctionDefinition] = []
        self._in_function_call_depth = 0
        self.current_table = None
        self.library_functions = library_functions

    def _get_node_column(self, node_with_symbol):
        if hasattr(node_with_symbol, 'getSymbol') and node_with_symbol.getSymbol() is not None:
            return node_with_symbol.getSymbol().column
        elif isinstance(node_with_symbol, TerminalNodeImpl) and node_with_symbol.symbol is not None:
            return node_with_symbol.symbol.column
        return 0

    # --- Scope Management ---
    def _get_current_scope(self) -> dict:
        return self.scope_stack[-1]

    def _push_scope(self):
        self.scope_stack.append({})

    def _pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
        else:
            print("CRITICAL ERROR: Attempted to pop the global scope from stack!")

    def _find_variable_info(self, name: str, depth: int) -> ():
        
        try:
            if depth == 0:
                for scope in reversed(self.scope_stack):
                    if name in scope:
                        return scope[name], scope
            else:
                if self.current_function_stack:
                    current_function = self.current_function_stack[-1]
                    lexical_scope_depth = current_function.lexical_scope_depth

                    max_scope_index = min(lexical_scope_depth - 1, len(self.scope_stack) - 1)
                    
                    for i in range(max_scope_index, -1, -1):
                        scope = self.scope_stack[i]
                        if name in scope:
                            return scope[name], scope
                else:
                    for scope in reversed(self.scope_stack[:depth]):
                        if name in scope:
                            return scope[name], scope

            if name in self.constants:
                return self.constants[name], self.constants
        except:
            return None, None

        return None, None

    def _set_variable_value(self, name: str, value, depth: int, line: int, column: int, is_declaration: bool = False):
        if depth == 0:
            var_info = None
            scope_found_in = None

            if self.current_function_stack:
                function_frame_index = self.function_frame_indices[-1]
                function_scope = self.scope_stack[function_frame_index]
                if name in function_scope:
                    var_info = function_scope[name]
                    scope_found_in = function_scope

            if not var_info and name in self.scope_stack[0] and self.current_function_stack:
                current_scope = self._get_current_scope()
                global_var = self.scope_stack[0][name]
                current_scope[name] = global_var.copy() if hasattr(global_var, 'copy') else list(global_var)
                var_info = current_scope[name]
                scope_found_in = current_scope
            elif not var_info and name in self.scope_stack[0]:
                var_info = self.scope_stack[0][name]
                scope_found_in = self.scope_stack[0]

            if not var_info:
                var_info, scope_found_in = self._find_variable_info(name, depth)
            
            if not var_info and name in self.constants:
                var_info = self.constants[name]
                scope_found_in = self.constants
        else:
            var_info, scope_found_in = self._find_variable_info(name, depth)
            
        if var_info:
            if scope_found_in is self.constants:
                raise ConstantOperationExcpetion(name, line, column)

            declared_type = var_info[0]
            value_to_assign, error = self._coerce_value_to_type(value, declared_type, name, line, column)
            if error:
                raise error
            var_info[2] = value_to_assign
        else:
            raise UknownNameException(name, line, column)

    def _coerce_value_to_type(self, value, target_type_str, name_for_error, line_for_error, column_for_error):
        current_value_type_str = self._get_value_type_str(value)

        if target_type_str == current_value_type_str:
            return value, None

        if value is None and target_type_str != "null":
            pass

        try:
            if target_type_str == "int":
                if isinstance(value, float) and value.is_integer(): return int(value), None
                if isinstance(value, str):  # Allow string to int conversion
                    return int(value), None
                return int(value), None
            elif target_type_str == "double":
                if isinstance(value, int): return float(value), None
                if isinstance(value, str):  # Allow string to double conversion
                    return float(value), None
                return float(value), None
            elif target_type_str == "string":
                if isinstance(value, bool):  # "true"/"false" for bool to string
                    return "true" if value else "false", None
                if isinstance(value, int) or isinstance(value, float): return str(value), None
                return str(value), None
            elif target_type_str == "bool":
                if isinstance(value, str):
                    if value.lower() == "true": return True, None
                    if value.lower() == "false": return False, None
                if isinstance(value, int) or isinstance(value, float): return bool(value), None
                # No other implicit conversions to bool for now from numbers
        except (ValueError, TypeError):
            return None, WrongTypeException(name_for_error, target_type_str, line_for_error, column_for_error,
                                            gotType=current_value_type_str)

        return None, WrongTypeException(name_for_error, target_type_str, line_for_error, column_for_error, gotType=current_value_type_str)

    def _get_value_type_str(self, value) -> str:
        if isinstance(value, bool): return "bool"
        if isinstance(value, int): return "int"
        if isinstance(value, float): return "double"
        if isinstance(value, str): return "string"
        if value is None: return "null"
        return "unknown"

    # --- Visiting Productions ---
    def visitStart(self, ctx: DAPLParser.StartContext):  #
        return self.visitChildren(ctx)

    def visitValue(self, ctx:DAPLParser.ValueContext):
        value = self.visitChildren(ctx)
        if ctx.getText() == "null":
            value = "null"
        return value

    def visitValueExpr(self, ctx:DAPLParser.ValueExprContext):
        value = self.visit(ctx.expr())
        if isinstance(value, bool):
            if value:
                value = "true"
            else:
                value = "false"

        return value

    def visitValueText(self, ctx: DAPLParser.ValueTextContext):
        return ctx.getText()[1:-1]  # Remove quotes

    def visitValueBoolExpr(self, ctx: DAPLParser.ValueBoolExprContext):
        return self.visit(ctx.boolExpr())

    def visitNull(self, ctx:DAPLParser.NullContext):
        return "null"

    def visitParent(self, ctx:DAPLParser.ParentContext):
        counter = ctx.getText().count('^')
        name = ctx.NAME().getText()

        if counter >= len(self.scope_stack):
            raise UknownNameException(name, ctx.NAME().getSymbol().line, self._get_node_column(ctx.NAME()))

        target_scope_index = len(self.scope_stack) - 1 - counter

        if self.current_function_stack:
            current_function = self.current_function_stack[-1]
            lexical_scope_depth = current_function.lexical_scope_depth

            current_call_start = len(self.scope_stack) - 1
            while current_call_start > 0 and current_call_start not in self.function_frame_indices:
                current_call_start -= 1

            for i in range(target_scope_index, -1, -1):
                if i >= current_call_start:
                    scope = self.scope_stack[i]
                    if name in scope:
                        return scope[name][2]
                elif i < lexical_scope_depth:
                    is_in_other_function = any(frame_start <= i < current_call_start for frame_start in self.function_frame_indices if frame_start != current_call_start)
                    if not is_in_other_function:
                        scope = self.scope_stack[i]
                        if name in scope:
                            return scope[name][2]
        else:
            for i in range(target_scope_index, -1, -1):
                scope = self.scope_stack[i]
                if name in scope:
                    return scope[name][2]

        if name in self.constants:
            return self.constants[name][2]

        raise UknownNameException(name, ctx.NAME().getSymbol().line, self._get_node_column(ctx.NAME()))

    def visitVarDecInitValue(self, ctx: DAPLParser.VarDecInitValueContext):
        name = ctx.NAME().getText()
        declared_type = ctx.type_().getText()
        initial_value_expr = self.visit(ctx.value())

        current_scope = self._get_current_scope()
        is_global_context = (current_scope is self.scope_stack[0])

        if is_global_context:
            if name not in current_scope:
                print(f"INTERNAL ERROR: Global variable '{name}' at line {ctx.start.line} missing from global scope.")
                current_scope[name] = [declared_type, ctx.start.line, None]

            var_info_global = current_scope[name]
            if var_info_global[0] != declared_type:
                print(
                    f"WARNING: Type mismatch for global var '{name}' between listener and declaration. Using current: {declared_type}")
                # Or raise error: raise WrongTypeException(name, var_info_global[0], ctx.start.line, gotType=declared_type)

            coerced_value, error = self._coerce_value_to_type(initial_value_expr, declared_type, name, ctx.start.line, (ctx.start.column + ctx.stop.column)//2)
            if error:
                raise error
            var_info_global[0] = declared_type
            var_info_global[1] = ctx.start.line
            var_info_global[2] = coerced_value
        else:
            if name in current_scope:
                prev_line = current_scope[name][1]
                raise DoubleDeclarationError(name, prev_line, ctx.start.line, ctx.NAME().getSymbol().column)

            coerced_value, error = self._coerce_value_to_type(initial_value_expr, declared_type, name, ctx.start.line, (ctx.start.column + ctx.stop.column)//2)
            if error:
                raise error
            current_scope[name] = [declared_type, ctx.start.line, coerced_value]

    def visitVarDecDefaultValue(self, ctx: DAPLParser.VarDecDefaultValueContext):
        name = ctx.NAME().getText()
        declared_type = ctx.type_().getText()

        default_value = None
        if declared_type == "int":
            default_value = 0
        elif declared_type == "double":
            default_value = 0.0
        elif declared_type == "string":
            default_value = ""
        elif declared_type == "bool":
            default_value = False
        elif declared_type == "char":
            default_value = '\0'
        else:
            raise InvalidOperationException(ctx.start.line, f"Unknown type '{declared_type}' for default value.")

        current_scope = self._get_current_scope()
        is_global_context = (current_scope is self.scope_stack[0])

        if is_global_context:
            if name not in current_scope:
                print(
                    f"INTERNAL ERROR: Global variable '{name}' (default init) at line {ctx.start.line} missing from global scope.")
                current_scope[name] = [declared_type, ctx.start.line, None]

            var_info_global = current_scope[name]
            if var_info_global[0] != declared_type:
                print(
                    f"WARNING: Type mismatch for global var '{name}' between listener and declaration. Using current: {declared_type}")

            var_info_global[0] = declared_type
            var_info_global[1] = ctx.start.line
            var_info_global[2] = default_value
        else:
            if name in current_scope:
                prev_line = current_scope[name][1]
                raise DoubleDeclarationError(name, prev_line, ctx.start.line, ctx.NAME().getSymbol().column)
            current_scope[name] = [declared_type, ctx.start.line, default_value]

    def visitConstDec(self, ctx: DAPLParser.ConstDecContext):
        name = ctx.NAME().getText()
        declared_type = ctx.type_().getText()
        initial_value = self.visit(ctx.value())

        const_info = self.constants.get(name)
        if const_info:
            if const_info[2] is not None:
                print(f"INTERNAL WARNING: Constant '{name}' already initialized.")
            coerced_value, error = self._coerce_value_to_type(initial_value, declared_type, name, ctx.start.line, (ctx.start.column + ctx.stop.column) //2)
            if error:
                raise error
            const_info[2] = coerced_value
        else:
            print(f"INTERNAL ERROR: Constant {name} not found during init by listener.")

    def visitPrint(self, ctx: DAPLParser.PrintContext):
        value = self.visit(ctx.value())
        if value is None:
            print("null")
        elif isinstance(value, bool):
            print("true" if value else "false")
        else:
            print(value)
        return None

    def _render(self, v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return f'"{v}"'
        return str(v)

    # Expressions
    def visitInt(self, ctx: DAPLParser.IntContext):  #
        return int(ctx.getText())

    def visitDouble(self, ctx: DAPLParser.DoubleContext):  #
        return float(ctx.getText())

    def visitNameExpr(self, ctx: DAPLParser.NameExprContext):
        name = ctx.NAME().getText()
        var_info, scope = self._find_variable_info(name, 0)

        if var_info:
            value = var_info[2]
            if value is None and scope is not self.constants:
                pass
            return value
        else:
            raise UknownNameException(name, ctx.start.line, (ctx.start.column + ctx.stop.column)//2)

    def visitExpr(self, ctx: DAPLParser.ExprContext):
        value = self.visitChildren(ctx)
        return value

    def visitParens(self, ctx: DAPLParser.ParensContext):  #
        return self.visit(ctx.expr())

    def visitMinusExpr(self, ctx: DAPLParser.MinusExprContext):  #
        val = self.visit(ctx.expr())
        if not isinstance(val, (int, float)):
            raise InvalidOperationException(ctx.start.line, "Unary minus only applicable to numbers.")
        return -val

    def visitPlusExpr(self, ctx: DAPLParser.MinusExprContext):  #
        val = self.visit(ctx.expr())
        if not isinstance(val, (int, float)):
            raise InvalidOperationException(ctx.start.line, "Unary minus only applicable to numbers.")
        return val

    def visitMulDiv(self, ctx: DAPLParser.MulDivContext):  #
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))

        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            if ctx.op.text == '*' and ((isinstance(left, str) and isinstance(right, int)) or \
                                       (isinstance(left, int) and isinstance(right, str))):
                return left * right
            raise InvalidOperationException(ctx.start.line,
                                            "Multiplication/Division operands must be numbers (or string*int for '*').")

        if isinstance(left, float) or isinstance(right, float):
            left = float(left)
            right = float(right)

        if ctx.op.text == '*':
            return left * right
        elif ctx.op.text == '/':
            if right == 0 or right == 0.0:
                raise ZeroDivisionException(ctx.start.line)
            # DAPL division: if both are ints and division is exact, result is int. Otherwise float.
            if isinstance(left, int) and isinstance(right, int) and left % right == 0:
                return left // right
            return float(left) / float(right)
        else:
            if right == 0 or right == 0.0:
                raise ZeroDivisionException(ctx.start.line)
            # DAPL division: if both are ints and division is exact, result is int. Otherwise float.
            if isinstance(left, int) and isinstance(right, int) and left % right == 0:
                return left // right
            return int(float(left) // float(right))

    def visitAddSub(self, ctx: DAPLParser.AddSubContext):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))

        if isinstance(left, str) or isinstance(right, str):
            if ctx.op.text == '+':
                s_left = "true" if left is True else "false" if left is False else str(left)
                s_right = "true" if right is True else "false" if right is False else str(right)
                return s_left + s_right
            else:
                raise InvalidOperationException(ctx.start.line, "Subtraction not defined for strings.")

        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise InvalidOperationException(ctx.start.line,
                                            "Addition/Subtraction operands must be numbers or strings for '+' concatenation.")

        if isinstance(left, float) or isinstance(right, float):
            left = float(left)
            right = float(right)

        if ctx.op.text == '+':
            return left + right
        else:
            return left - right

    def visitModulo(self, ctx: DAPLParser.ModuloContext):  #
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        if not isinstance(left, int) or not isinstance(right, int):
            raise InvalidOperationException(ctx.start.line, "Modulo operator requires integer operands.")
        if right == 0:
            raise ZeroDivisionException(ctx.start.line)
        return left % right

    def _perform_assignment(self, name_node_text: str, value, depth: int, line: int, column: int):  # name_node_text is str
        name = name_node_text
        self._set_variable_value(name, value, depth, line, column)

    def visitAssign(self, ctx:DAPLParser.AssignContext):
        name = ctx.NAME().getText()
        value = self.visit(ctx.value())
        line = ctx.value().start.line
        column = ctx.value().start.column
        counter = ctx.getText().count("^") - ctx.value().getText().count("^")

        self._perform_assignment(name, value, counter, line, column)

        return self.visitChildren(ctx)

    def visitBool(self, ctx:DAPLParser.BoolContext):
        return ctx.getText() == "true"

    def visitBoolExpr(self, ctx: DAPLParser.BoolExprContext):
        val = self.visit(ctx.orExpr())
        return bool(val)

    def visitOrExpr(self, ctx: DAPLParser.OrExprContext):  #
        # Grammar: orExpr: andExpr (OR andExpr)* ;
        left_val = self.visit(ctx.andExpr(0))
        if not isinstance(left_val, bool):
            raise InvalidOperationException(ctx.andExpr(0).start.line, "OR operand must be boolean.")
        if left_val:
            return True

        current_result = left_val
        for i in range(len(ctx.OR())):
            if current_result:
                return True
            right_val_ctx = ctx.andExpr(i + 1)
            right_val = self.visit(right_val_ctx)
            if not isinstance(right_val, bool):
                raise InvalidOperationException(right_val_ctx.start.line, "OR operand must be boolean.")
            current_result = current_result or right_val

        return current_result

    def visitAndExpr(self, ctx: DAPLParser.AndExprContext):  #
        left_val = self.visit(ctx.notExpr(0))
        if not isinstance(left_val, bool):
            raise InvalidOperationException(ctx.notExpr(0).start.line, "AND operand must be boolean.")
        if not left_val:
            return False

        current_result = left_val
        for i in range(len(ctx.AND())):
            if not current_result:
                return False
            right_val_ctx = ctx.notExpr(i + 1)
            right_val = self.visit(right_val_ctx)
            if not isinstance(right_val, bool):
                raise InvalidOperationException(right_val_ctx.start.line, "AND operand must be boolean.")
            current_result = current_result and right_val

        return current_result

    def visitNotExpr(self, ctx: DAPLParser.NotExprContext):  #
        val = self.visit(ctx.primaryBoolExpr())
        if not isinstance(val, bool):
            raise InvalidOperationException(ctx.start.line, "! operator requires boolean operand.")
        if ctx.NOT():
            return not val
        return val

    def visitPrimaryBoolExpr(self, ctx: DAPLParser.PrimaryBoolExprContext):
        if ctx.bool_():
            return self.visit(ctx.bool_())
        elif ctx.NAME() and len(ctx.children) > 1 and ctx.getChild(1).getText() == '(':
            # Function call: NAME '(' (value (',' value)*)? ')'
            func_name = ctx.NAME().getText()
            call_line = ctx.start.line
            call_column = (ctx.start.column + ctx.stop.column)//2

            if func_name in self.library_functions:
                if func_name == "startsWith":
                    actual_arg_values = []
                    for i in range(2, len(ctx.children) - 1):
                        child = ctx.getChild(i)
                        if hasattr(child, 'getText') and child.getText() != ',':
                            actual_arg_values.append(child.getText().strip('"'))
                    
                    if len(actual_arg_values) != 2:
                        raise ArgumentCountException(func_name, 2, len(actual_arg_values), call_line)
                    
                    return actual_arg_values[0].startswith(actual_arg_values[1])

                if func_name == "length":
                    return 0

            if func_name not in self.functions:
                raise FunctionNotFoundException(func_name, call_line)

            func_def = self.functions[func_name]

            actual_arg_values = []
            
            expected_arg_count = len(func_def.param_names_types)
            if len(actual_arg_values) != expected_arg_count:
                raise ArgumentCountException(func_name, expected_arg_count, len(actual_arg_values), call_line)

            self._in_function_call_depth += 1
            returned_value = None
            fret_exception = None
            pushed_scope = False
    
            try:
                if self._in_function_call_depth > self.MAX_DAPL_RECURSION_DEPTH:
                    raise MaxRecursionDepthExceededError(func_name, call_line, self.MAX_DAPL_RECURSION_DEPTH)

                self._push_scope()
                self.function_frame_indices.append(len(self.scope_stack) - 1)
                self.current_function_stack.append(func_def)
                pushed_scope = True
                local_scope = self._get_current_scope()
                
                for i, (param_name, param_type_str) in enumerate(func_def.param_names_types):
                    if i < len(actual_arg_values):
                        arg_val = actual_arg_values[i]
                        coerced_arg_val, error = self._coerce_value_to_type(arg_val, param_type_str, param_name, call_line, call_column)
                        if error:
                            raise ArgumentTypeException(func_name, param_name, param_type_str,
                                                        self._get_value_type_str(arg_val), call_line, i)
                        local_scope[param_name] = [param_type_str, call_line, coerced_arg_val]

                for line_ctx in func_def.body_ctx_list:
                    self.visit(line_ctx)

            except FunctionReturnException as e:
                returned_value = e.value
                fret_exception = e
            finally:
                if pushed_scope:
                    self._pop_scope()
                    if self.function_frame_indices:
                        self.function_frame_indices.pop()
                    if self.current_function_stack:
                        self.current_function_stack.pop()
                self._in_function_call_depth -= 1

            if func_def.return_type_str == 'void':
                if fret_exception and returned_value is not None:
                    raise VoidFunctionReturnsValueException(func_name, fret_exception.line if fret_exception and fret_exception.line else call_line)
                return False
            else:
                if not fret_exception:
                    raise MissingReturnValueException(func_name, func_def.return_type_str, func_def.definition_line)

                final_returned_value, error = self._coerce_value_to_type(returned_value, func_def.return_type_str,
                                                                         f"return value of {func_name}",
                                                                         fret_exception.line if fret_exception and fret_exception.line else call_line, call_column)
                if error:
                    raise ReturnTypeMismatchException(func_name, func_def.return_type_str,
                                                      self._get_value_type_str(returned_value),
                                                      fret_exception.line if fret_exception and fret_exception.line else call_line)
                val = final_returned_value

                if not isinstance(val, bool):
                    if isinstance(val, int):
                        val = bool(val)
                    elif isinstance(val, float):
                        val = bool(val)
                    else:
                        raise WrongTypeException(func_name, "bool", ctx.NAME().getSymbol().line,
                                                 ctx.NAME().getSymbol().column,
                                                 gotType=self._get_value_type_str(val))


                return final_returned_value
                
        elif ctx.NAME():
            name_token = ctx.NAME()
            var_name = name_token.getText()
            var_value_info, _ = self._find_variable_info(var_name, 0)
            if not var_value_info:
                raise UknownNameException(var_name, name_token.getSymbol().line, self._get_node_column(ctx.NAME()))

            val = var_value_info[2]
            if not isinstance(val, bool):
                if isinstance(val, int):
                    val = bool(val)
                elif isinstance(val, float):
                    val = bool(val)
                else:
                    raise WrongTypeException(var_name, "bool", name_token.getSymbol().line, name_token.getSymbol().column,
                                         gotType=self._get_value_type_str(val))
            return val
        elif ctx.comparasion():
            return self.visit(ctx.comparasion())
        elif ctx.boolExpr():
            return self.visit(ctx.boolExpr())
        else:
            print("??? Unhandled primaryBoolExpr case")
        raise NotImplementedError(f"Unhandled primaryBoolExpr case at line {ctx.start.line}")

    def visitComparasion(self, ctx: DAPLParser.ComparasionContext):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        op = ctx.operator().getText()

        l_type = self._get_value_type_str(left)
        r_type = self._get_value_type_str(right)

        # Handle null comparisons first
        if op == "==":
            if left is None and right is None: return True
            if left is None or right is None: return False
        elif op == "!=":
            if left is None and right is None: return False
            if left is None or right is None: return True

        if (left is None or right is None) and op not in ["==", "!="]:
            raise InvalidOperationException(ctx.start.line,
                                            f"Cannot compare {l_type} with {r_type} using '{op}' when one is null.")

        valid_comparison = False
        if l_type == r_type and l_type not in ["unknown"]:  # unknown type cannot be compared
            valid_comparison = True
        elif (l_type == "int" and r_type == "double") or \
                (l_type == "double" and r_type == "int"):
            left = float(left)  # Promote for comparison
            right = float(right)
            valid_comparison = True

        if not valid_comparison:
            raise InvalidOperationException(ctx.start.line,
                                            f"Cannot compare {l_type} with {r_type} using '{op}'. Types must be compatible.")

        if op == "==": return left == right
        if op == "!=": return left != right

        if not isinstance(left, (int, float, str)):  # bool comparison < > <= >= is not typical
            raise InvalidOperationException(ctx.start.line, f"Order comparison '{op}' not supported for type {l_type}.")

        if op == "<":  return left < right
        if op == ">":  return left > right
        if op == "<=": return left <= right
        if op == ">=": return left >= right

        raise NotImplementedError(f"Unknown comparison operator: {op}")

    def visitOperator(self, ctx:DAPLParser.OperatorContext):
        return ctx.getText()

    def visitScope(self, ctx:DAPLParser.ScopeContext):
        self._push_scope()
        try:
            self.visitChildren(ctx)
        except FunctionReturnException:
            raise
        finally:
            self._pop_scope()

    def visitIfStatement(self, ctx: DAPLParser.IfStatementContext):
        condition = self.visit(ctx.boolExpr())
        if not isinstance(condition, bool):
            raise InvalidOperationException(ctx.boolExpr().start.line, "If condition must be a boolean expression.")

        executed_branch = False
        try:
            if condition:
                executed_branch = True
                for line_ctx in ctx.line(): self.visit(line_ctx)
            else:
                for elif_ctx in ctx.elifStatement():
                    elif_condition = self.visit(elif_ctx.boolExpr())
                    if not isinstance(elif_condition, bool):
                        raise InvalidOperationException(elif_ctx.boolExpr().start.line,
                                                        "Elif condition must be boolean.")
                    if elif_condition:
                        executed_branch = True
                        for line_ctx in elif_ctx.line(): self.visit(line_ctx)
                        break
                if not executed_branch and ctx.elseStatement():
                    for line_ctx in ctx.elseStatement().line(): self.visit(line_ctx)
        except FunctionReturnException:
            raise
        return None

    def visitWhileStatement(self, ctx: DAPLParser.WhileStatementContext):  #
        try:
            while True:
                condition = self.visit(ctx.boolExpr())
                if not isinstance(condition, bool):
                    raise InvalidOperationException(ctx.boolExpr().start.line, "While condition must be boolean.")
                if not condition:
                    break
                for line_ctx in ctx.line():
                    self.visit(line_ctx)
        except FunctionReturnException:
            raise
        return None

    def visitForStatement(self, ctx: DAPLParser.ForStatementContext):
        self._push_scope()
        try:
            loop_var_type = ctx.type_().getText()
            loop_var_name = ctx.NAME(0).getText()
            init_val_ctx = ctx.expr(0)
            init_val = self.visit(init_val_ctx)

            coerced_init_val, error = self._coerce_value_to_type(init_val, loop_var_type, loop_var_name,
                                                                 init_val_ctx.start.line, init_val_ctx.start.column)
            if error: raise error

            self._get_current_scope()[loop_var_name] = [loop_var_type, ctx.start.line, coerced_init_val]

            while True:
                condition_ctx = ctx.boolExpr()
                condition = self.visit(condition_ctx)
                if not isinstance(condition, bool):
                    raise InvalidOperationException(condition_ctx.start.line, "For loop condition must be boolean.")
                if not condition:
                    break

                current_loop_var_value = self._get_current_scope()[loop_var_name]
                
                self._push_scope()
                try:
                    iteration_loop_var = current_loop_var_value.copy()
                    self._get_current_scope()[loop_var_name] = iteration_loop_var
                    
                    for line_ctx in ctx.line():
                        self.visit(line_ctx)

                    current_loop_var_value[2] = iteration_loop_var[2]
                finally:
                    self._pop_scope()

                update_var_name_node = ctx.NAME(1)
                if update_var_name_node.getText() != loop_var_name:
                    raise InvalidOperationException(update_var_name_node.getSymbol().line,
                                                    f"For loop update must modify the loop variable '{loop_var_name}'.")

                update_val_expr_ctx = ctx.expr(1)
                update_val = self.visit(update_val_expr_ctx)

                self._set_variable_value(loop_var_name, update_val, 0,
                                         update_var_name_node.getSymbol().line,
                                         update_var_name_node.getSymbol().column)
        except FunctionReturnException:
            self._pop_scope()
            raise
        finally:
            self._pop_scope()
        return None

    def visitFuncDec(self, ctx: DAPLParser.FuncDecContext):  #
        return None

    def visitFuncCallExpr(self, ctx: DAPLParser.FuncCallExprContext):
        func_name = ctx.NAME().getText()
        call_line = ctx.start.line
        call_column = (ctx.start.column + ctx.stop.column)//2

        if func_name in self.library_functions:
            if func_name == "startsWith":
                actual_arg_values = []
                if ctx.value():
                    for val_ctx in ctx.value():
                        actual_arg_values.append(self.visit(val_ctx))
                if len(actual_arg_values) != 2:
                    raise ArgumentCountException(func_name, 2, len(actual_arg_values), call_line)
                param_name = ctx.value(0).getText()
                param_type_str= self._get_value_type_str(self.visit(ctx.value(0)))
                param_type_str2= self._get_value_type_str(self.visit(ctx.value(1)))

                if param_type_str2 != "string":
                    raise ArgumentTypeException(func_name, param_name, "string", param_type_str2, call_line,
                                                self._get_node_column(ctx.value(1)))

                if '"' in param_name:
                    value = param_name
                    value = value.replace('"', '')

                    if param_type_str != "string":
                        raise ArgumentTypeException(func_name, param_name, "string", param_type_str, call_line,
                                                    self._get_node_column(ctx.argList().value(0)))
                    return value[:len(self.visit(ctx.value(1)))] == self.visit(ctx.value(1))
                else:
                    value = self.visit(ctx.value(0))
                    return value[:len(self.visit(ctx.value(1)))] == self.visit(ctx.value(1))

            if func_name == "length":
                actual_arg_values = []
                if ctx.value():
                    for val_ctx in ctx.value():
                        actual_arg_values.append(self.visit(val_ctx))
                if len(actual_arg_values) != 1:
                    raise ArgumentCountException(func_name, 1, len(actual_arg_values), call_line)
                param_name = ctx.value(0).getText()
                param_type_str= self._get_value_type_str(self.visit(ctx.value(0)))

                if param_type_str != "string":
                    raise ArgumentTypeException(func_name, param_name, "string", param_type_str, call_line,
                                                self._get_node_column(ctx.value(0)))

                if '"' in param_name:
                    value = param_name
                    value = value.replace('"', '')

                    if param_type_str != "string":
                        raise ArgumentTypeException(func_name, param_name, "string", param_type_str, call_line,
                                                    self._get_node_column(ctx.argList().value()))
                    return len(value)
                else:
                    value = self.visit(ctx.value(0))
                    return len(value)

        if func_name not in self.functions:
            raise FunctionNotFoundException(func_name, call_line)

        func_def: FunctionDefinition = self.functions[func_name]
        actual_arg_values = []
        if ctx.value():
            for val_ctx in ctx.value():
                actual_arg_values.append(self.visit(val_ctx))

        expected_arg_count = len(func_def.param_names_types)
        if len(actual_arg_values) != expected_arg_count:
            raise ArgumentCountException(func_name, expected_arg_count, len(actual_arg_values), call_line)

        self._in_function_call_depth += 1
        returned_value = None
        fret_exception = None
        pushed_scope = False

        try:
            if self._in_function_call_depth > self.MAX_DAPL_RECURSION_DEPTH:
                raise MaxRecursionDepthExceededError(func_name, call_line, self.MAX_DAPL_RECURSION_DEPTH)


            self._push_scope()
            self.function_frame_indices.append(len(self.scope_stack) - 1)
            self.current_function_stack.append(func_def)
            pushed_scope = True
            local_scope = self._get_current_scope()
            for i, (param_name, param_type_str) in enumerate(func_def.param_names_types):
                arg_val = actual_arg_values[i]
                coerced_arg_val, error = self._coerce_value_to_type(arg_val, param_type_str, param_name, call_line, call_column)
                if error:
                    raise ArgumentTypeException(func_name, param_name, param_type_str,
                                                self._get_value_type_str(arg_val), call_line, i)
                local_scope[param_name] = [param_type_str, call_line, coerced_arg_val]

            for line_ctx in func_def.body_ctx_list:
                self.visit(line_ctx)

        except FunctionReturnException as e:
            returned_value = e.value
            fret_exception = e
        finally:
            if pushed_scope:
                
                self._pop_scope()
                if self.function_frame_indices:
                    self.function_frame_indices.pop()
                if self.current_function_stack:
                    self.current_function_stack.pop()
            self._in_function_call_depth -= 1

        if func_def.return_type_str == 'void':
            if fret_exception and returned_value is not None:
                raise VoidFunctionReturnsValueException(func_name,
                                                        fret_exception.line if fret_exception and fret_exception.line else call_line)
            return None
        else:
            if not fret_exception:
                raise MissingReturnValueException(func_name, func_def.return_type_str, func_def.definition_line)

            final_returned_value, error = self._coerce_value_to_type(returned_value, func_def.return_type_str,
                                                                     f"return value of {func_name}",
                                                                     fret_exception.line if fret_exception and fret_exception.line else call_line, call_column)
            if error:
                raise ReturnTypeMismatchException(func_name, func_def.return_type_str,
                                                  self._get_value_type_str(returned_value),
                                                  fret_exception.line if fret_exception and fret_exception.line else call_line)
            return final_returned_value

    def visitFunctionCall(self, ctx: DAPLParser.FunctionCallContext):
        func_name = ctx.NAME().getText()
        call_line = ctx.start.line
        call_column = (ctx.start.column + ctx.stop.column) // 2

        if func_name in self.library_functions:
            if func_name == "startsWith":
                return None

            if func_name == "length":
                return None

        if func_name not in self.functions:
            raise FunctionNotFoundException(func_name, call_line)

        func_def: FunctionDefinition = self.functions[func_name]
        actual_arg_values = []
        if ctx.argList():
            for val_ctx in ctx.argList().value():
                actual_arg_values.append(self.visit(val_ctx))

        expected_arg_count = len(func_def.param_names_types)
        if len(actual_arg_values) != expected_arg_count:
            raise ArgumentCountException(func_name, expected_arg_count, len(actual_arg_values), call_line)

        self._in_function_call_depth += 1
        returned_value = None
        fret_exception = None
        pushed_scope = False

        try:
            if self._in_function_call_depth > self.MAX_DAPL_RECURSION_DEPTH:
                raise MaxRecursionDepthExceededError(func_name, call_line, self.MAX_DAPL_RECURSION_DEPTH)


            self._push_scope()
            self.function_frame_indices.append(len(self.scope_stack) - 1)
            self.current_function_stack.append(func_def)
            pushed_scope = True
            local_scope = self._get_current_scope()
            for i, (param_name, param_type_str) in enumerate(func_def.param_names_types):
                arg_val = actual_arg_values[i]
                coerced_arg_val, error = self._coerce_value_to_type(arg_val, param_type_str, param_name, call_line, call_column)
                if error:
                    raise ArgumentTypeException(func_name, param_name, param_type_str,
                                                self._get_value_type_str(arg_val), call_line, i)
                local_scope[param_name] = [param_type_str, call_line, coerced_arg_val]

            for line_ctx in func_def.body_ctx_list:
                self.visit(line_ctx)

        except FunctionReturnException as e:
            returned_value = e.value
            fret_exception = e
        finally:
            if pushed_scope:
                
                self._pop_scope()
                if self.function_frame_indices:
                    self.function_frame_indices.pop()
                if self.current_function_stack:
                    self.current_function_stack.pop()
            self._in_function_call_depth -= 1

        if func_def.return_type_str == 'void':
            if fret_exception and returned_value is not None:
                raise VoidFunctionReturnsValueException(func_name,
                                                        fret_exception.line if fret_exception and fret_exception.line else call_line)
        else:
            if not fret_exception:
                raise MissingReturnValueException(func_name, func_def.return_type_str, func_def.definition_line)

            _, type_error = self._coerce_value_to_type(returned_value, func_def.return_type_str,
                                                       f"return value of {func_name}",
                                                       fret_exception.line if fret_exception and fret_exception.line else call_line, call_column)
            if type_error:
                raise ReturnTypeMismatchException(func_name, func_def.return_type_str,
                                                  self._get_value_type_str(returned_value),
                                                  fret_exception.line if fret_exception and fret_exception.line else call_line)
        return None

    def visitReturnStatement(self, ctx: DAPLParser.ReturnStatementContext):  #
        if self._in_function_call_depth == 0:
            raise ReturnOutsideFunctionException(ctx.start.line)

        return_value = None
        if ctx.value():
            return_value = self.visit(ctx.value())

        raise FunctionReturnException(return_value)

    def visitTableDec(self, ctx:DAPLParser.EmptyTableDecContext):
        name = ctx.NAME().getText()
        self.current_table = name
        self.visit(ctx.table())

    def visitEmptyTableDec(self, ctx:DAPLParser.EmptyTableDecContext):
        pass

    def visitRead_csv(self, ctx:DAPLParser.Read_csvContext):
        name = ctx.NAME().getText()
        self.current_table = name
        file_name = ctx.TEXT().getText().replace("'", "").replace('"', "")
        current_key = self.tables_to_heap[name]

        file_path = f"{Path(__file__).resolve().parent.parent.parent}/{file_name}"
        print(file_path)

        try:
            with open(file_path, "r") as csvfile:
                header = csvfile.readline()[:-1].split(",")
                for row in csvfile.readlines():
                    values = row.replace("\n", "").split(",")
                    values = ["null" if el == "" else el for el in values]
                    self.heap[current_key].append(values)
        except:
            raise FileExistsError(f"File in line {ctx.start.line} does not exist")
        n_rows = max([len(row) for row in self.heap[current_key]])
        types = []
        for row in self.heap[current_key]:
            if len(row) != n_rows:
                for i in range(n_rows - len(row)):
                    row.append("null")

        for row in range(n_rows):
            column = [el[row] for el in self.heap[current_key]]
            types.append(self.classify_list(column))

        final_header = {name.replace("\n", "") : type_ for name, type_ in zip(header, types)}
        self.tables[name] = final_header

    def visitTable(self, ctx:DAPLParser.TableContext):
        rows = []

        for child in ctx.getChildren():
            if isinstance(child, DAPLParser.RowContext):
                row = self.visitRow(child)

                if len(row) != len(list(self.tables[self.current_table].keys())):
                    raise WrongShapeException(ctx.start.line, ctx.stop.column)

                rows.append(row)

        self.heap[self.tables_to_heap[self.current_table]] = rows

    def visitRow(self, ctx:DAPLParser.RowContext):
        values = []
        counter = 0

        for child in ctx.getChildren():
            if isinstance(child, DAPLParser.ValueContext):
                name = ""
                line = ctx.start.line
                column = (child.start.column + child.stop.column) // 2

                try:
                    type = list(self.tables[self.current_table].values())[counter]
                except:
                    raise WrongShapeException(ctx.start.line, (ctx.start.column + ctx.stop.column)//2)
                value = self.visit(ctx.value(counter))
                self.checkType(name, value, type, line, column)
                values.append(value)
                counter += 1
        return values

    def visitTableAction(self, ctx:DAPLParser.TableActionContext):
        name = ctx.NAME().getText()
        self.current_table = name

        for child in ctx.getChildren():
            if isinstance(child, DAPLParser.TableOperationContext):
                self.visit(child)
            elif isinstance(child, DAPLParser.TableOperationContext):
                self.visit(child)

        for child in ctx.getChildren():
            if isinstance(child, DAPLParser.TerminalTableOperationContext):
                self.visit(child)

    def visitApplyOp(self, ctx:DAPLParser.ApplyOpContext):
        n_column = int(ctx.INT().getText())
        name = ctx.lambdaExpr().NAME().getText()
        type_ = self.tables[self.current_table][list(self.tables[self.current_table].keys())[n_column]]
        line = ctx.lambdaExpr().value().start.line
        column = (ctx.lambdaExpr().value().stop.column + ctx.lambdaExpr().value().stop.column)//2
        self._push_scope()
        self.scope_stack[-1].update({name : [type_, None, None]})
        heap_key = self.tables_to_heap[self.current_table]

        for c, e in enumerate(self.heap[heap_key]):
            self._perform_assignment(name, e[n_column], 0, line, column)
            e[n_column] = self.visit(ctx.lambdaExpr().value())

        self._pop_scope()

    def visitFillterOp(self, ctx:DAPLParser.FillterOpContext):
        n_column = int(ctx.INT().getText())
        name = ctx.lambdaExpr().NAME().getText()
        type_ = self.tables[self.current_table][list(self.tables[self.current_table].keys())[n_column]]
        line = ctx.lambdaExpr().value().start.line
        column = (ctx.lambdaExpr().value().stop.column + ctx.lambdaExpr().value().stop.column)//2
        self._push_scope()
        self.scope_stack[-1].update({name : [type_, None, None]})
        heap_key = self.tables_to_heap[self.current_table]
        columns_to_remove = []

        for c, e in enumerate(self.heap[heap_key]):
            self._perform_assignment(name, e[n_column], 0, line, column)
            bool_expr = self.visit(ctx.lambdaExpr().value())

            if bool_expr == "true":
                bool_expr = True
            elif bool_expr == "false":
                bool_expr = False
            else:
                pass

            if not bool_expr:
                columns_to_remove.append(c)

        for c, row in enumerate(columns_to_remove):
            self.heap[heap_key].pop(row-c)

        self._pop_scope()

    def visitDropOp(self, ctx:DAPLParser.DropOpContext):
        name = self.current_table
        n_column = int(ctx.INT().getText())

        try:
            self.tables[name].pop(list(self.tables[name].keys())[n_column])
        except:
            id_token = ctx.INT().getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnNumber(line, column)

        heap_key = self.tables_to_heap[self.current_table]

        for row in self.heap[heap_key]:
            row.pop(n_column)

    def visitJoinOp(self, ctx:DAPLParser.JoinOpContext):
        name1 = self.current_table
        name2 = ctx.NAME().getText()
        n1 = int(ctx.INT(0).getText())
        n2 = int(ctx.INT(1).getText())

        flag = False

        if list(self.tables[name1].keys())[n1] == list(self.tables[name2].keys())[n2]:
            flag = True

        heap_key1 = self.tables_to_heap[name1]
        heap_key2 = self.tables_to_heap[name2]

        try:
            col1 = [row[n1] for row in self.heap[heap_key1]]
        except:
            id_token = ctx.INT(0).getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnNumber(line, column)

        try:
            col2 = [row[n2] for row in self.heap[heap_key2]]
        except:
            id_token = ctx.INT(1).getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnNumber(line, column)

        match_dict = {i : [] for i in range(len(col1))}
        for c1, i in enumerate(col1):
            for c2, j in enumerate(col2):
                if i == j:
                    match_dict[c1].append(c2)

        new_table =[]
        for i in match_dict.keys():
            for j in match_dict[i]:
                if flag:
                    row = self.heap[heap_key1][i] + self.heap[heap_key2][j][:n2] + self.heap[heap_key2][j][n2+1:]
                else:
                    row = self.heap[heap_key1][i] + self.heap[heap_key2][j]
                new_table.append(row)

        self.tables[name1] = self.tables[name1] | self.tables[name2]

        self.heap[heap_key1] = new_table

    def visitJoinOp2(self, ctx:DAPLParser.JoinOp2Context):
        name1 = self.current_table
        name2 = ctx.NAME(0).getText()

        try:
            n1 = list(self.tables[name1].keys()).index(ctx.NAME(1).getText())
        except:
            id_token = ctx.NAME(1).getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnName(line, column)

        try:
            n2 = list(self.tables[name2].keys()).index(ctx.NAME(2).getText())
        except:
            id_token = ctx.NAME(2).getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnName(line, column)
        flag = False

        if list(self.tables[name1].keys())[n1] == list(self.tables[name2].keys())[n2]:
            flag = True

        heap_key1 = self.tables_to_heap[name1]
        heap_key2 = self.tables_to_heap[name2]

        col1  = [row[n1] for row in self.heap[heap_key1]]
        col2 = [row[n2] for row in self.heap[heap_key2]]

        match_dict = {i : [] for i in range(len(col1))}
        for c1, i in enumerate(col1):
            for c2, j in enumerate(col2):
                if i == j:
                    match_dict[c1].append(c2)

        new_table =[]
        for i in match_dict.keys():
            for j in match_dict[i]:
                if flag:
                    row = self.heap[heap_key1][i] + self.heap[heap_key2][j][:n2] + self.heap[heap_key2][j][n2+1:]
                else:
                    row = self.heap[heap_key1][i] + self.heap[heap_key2][j]
                new_table.append(row)

        self.heap[heap_key1] = new_table
        self.tables[name1] = self.tables[name1] | self.tables[name2]

    def visitGroupOp(self, ctx:DAPLParser.GroupOpContext):
        operation = self.visit(ctx.agregation())
        n1 = int(ctx.INT(0).getText())
        n2 = int(ctx.INT(1).getText())

        if n1 == n2:
            id_token = ctx.INT(1).getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnNumber(line, column)

        heap_key = self.tables_to_heap[self.current_table]

        try:
            agregation_dict1 = {}
            for c in [self.heap[heap_key][i][n1] for i in range(len(self.heap[heap_key]))]:
                if c not in agregation_dict1.keys():
                    agregation_dict1.update({c: []})
        except:
            id_token = ctx.INT(0).getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnNumber(line, column)

        try:
            for c1, c2 in zip([self.heap[heap_key][i][n1] for i in range(len(self.heap[heap_key]))], [self.heap[heap_key][j][n2] for j in range(len(self.heap[heap_key]))]):
                agregation_dict1[c1].append(c2)
        except:
            id_token = ctx.INT(1).getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnNumber(line, column)

        agregation_dict2 = {}
        types = self.tables[self.current_table]
        type_ = list(types.values())[n2]

        for k, v in agregation_dict1.items():
            if operation == "max":
                agregation_dict2[k] = self.max(v, type_, ctx.start.line)
            if operation == "count":
                agregation_dict2[k] = len(v)
            if operation == "min":
                agregation_dict2[k] = self.min(v, type_, ctx.start.line)
            if operation == "sum":
                agregation_dict2[k] = self.sum(v, type_, ctx.start.line)
            if operation == "average":
                agregation_dict2[k] = self.average(v, type_, ctx.start.line)

        new_table = [[k, v] for k, v in agregation_dict2.items()]
        name1 = list(self.tables[self.current_table].keys())[n1]
        name2 = list(self.tables[self.current_table].keys())[n2]

        self.tables[self.current_table] = {k : v for k, v in zip(self.tables[self.current_table].keys(), self.tables[self.current_table].values()) if k == name1 or k == name2}

        self.heap[heap_key] = new_table

        current_key = self.tables_to_heap[self.current_table]
        n_rows = max([len(row) for row in self.heap[current_key]])
        types = []
        header = self.tables[self.current_table].keys()

        for row in self.heap[current_key]:
            if len(row) != n_rows:
                for i in range(n_rows - len(row)):
                    row.append("null")

        for row in range(n_rows):
            column = [el[row] for el in self.heap[current_key]]
            types.append(self.classify_list(column))

        final_header = {name.replace("\n", "") : type_ for name, type_ in zip(header, types)}
        self.tables[self.current_table] = final_header

    def visitAddRow(self, ctx:DAPLParser.AddRowContext):
        name = self.current_table
        row = self.visitRow(ctx)
        size = len(self.tables[name].keys())

        if len(row) < size:
            for i in range(size - len(row)):
                row.append('null')
        elif len(row) > size:
            raise WrongRowSizeException(ctx.start.line, (ctx.start.column + ctx.stop.column)//2)

        self.heap[self.tables_to_heap[name]].append(row)

    def visitAgregation(self, ctx:DAPLParser.AgregationContext):
        return ctx.getText()

    def visitShowOp(self, ctx:DAPLParser.ShowOpContext):
        name = self.current_table

        if name in self.global_variables.keys():
            pass
        elif name in self.constants.keys():
            pass
        elif name in self.tables.keys():
            content = " " * 4

            for type, colname in self.tables[name].items():
                content += f"| {colname} : {type}"
            content += "\n"
            key = self.tables_to_heap[name]

            for c, row in enumerate(self.heap[key]):
                content += f"{c} : "
                for col in row:
                    content += f"| {col} "
                content += "\n"

            print(content)

    def visitColumnList(self, ctx:DAPLParser.ColumnListContext):
        for child in ctx.children:
            if isinstance(child, DAPLParser.ColumnContext):
                self.visit(child)

    def visitColumn(self, ctx:DAPLParser.ColumnContext):
        name = self.current_table
        type_ = ctx.type_().getText()
        colname = ctx.NAME().getText()

        if colname in self.tables[name].keys():
            id_token = ctx.NAME().getSymbol()
            line = id_token.line
            column = id_token.column

            raise WrongColumnName(line, column)

        self.tables[name].update({colname: type_})

        heap_key = self.tables_to_heap[name]
        for row in self.heap[heap_key]:
            row.append("null")

    def emptyHeap(self):
        self.heap.clear()

    def average(self, values: list, type_, line):
        if values.__contains__("null"):
            return "null"
        else:
            if type_ == "int":
                return sum([int(v) for v in values]) / len(values)
            elif type_ == "double":
                return sum([float(v) for v in values]) / len(values)
            else:
                raise InvalidOperationException(line)

    def max(self, values: list, type_, line):
        if values.__contains__("null"):
            return "null"
        else:
            if type_ == "int":
                return max([int(v) for v in values])
            elif type_ == "double":
                return max([float(v) for v in values])
            else:
                raise InvalidOperationException(line)

    def min(self, values: list, type_, line):
        if values.__contains__("null"):
            return "null"
        else:
            if type_ == "int":
                return min([int(v) for v in values])
            elif type_ == "double":
                return min([float(v) for v in values])
            else:
                raise InvalidOperationException(line)

    def sum(self, values: list, type_, line):
        if values.__contains__("null"):
            return "null"
        else:
            if type_ == "int":
                return sum([int(v) for v in values])
            elif type_ == "double":
                return sum([float(v) for v in values])
            else:
                raise InvalidOperationException(line)

    def classify_list(self, lst: list):
        def infer_type(item):
            if item == "null":
                return "null"

            if isinstance(item, bool):
                return "bool"
            elif isinstance(item, int):
                return "int"
            elif isinstance(item, float):
                return "double"
            elif isinstance(item, str):
                val = item.strip().lower()
                if val in ("true", "false"):
                    return "bool"
                try:
                    int(val)
                    return "int"
                except ValueError:
                    try:
                        float(val)
                        return "double"
                    except ValueError:
                        return "string"
            else:
                return "unknown"

        types = set(infer_type(item) for item in lst)
        types.discard("null")

        if len(types) == 1:
            return f"{types.pop()}"
        else:
            return f"auto"

    def checkType(self, name: str, value: str, type: str, line: int, column: int):
        if value != "null":
            actual_type = self._get_value_type_str(value)
            match type:
                case "int":
                    if isinstance(value, str):
                        raise WrongTypeException(name, type, line, column, actual_type)
                    try:
                        int(value)
                    except ValueError:
                        raise WrongTypeException(name, type, line, column, actual_type)
                case "double":
                    if isinstance(value, str):
                        raise WrongTypeException(name, type, line, column, actual_type)
                    try:
                        float(value)
                    except ValueError:
                        raise WrongTypeException(name, type, line, column, actual_type)
                case "string":
                    if isinstance(value, bool) or isinstance(value, int) or isinstance(value, float):
                        raise WrongTypeException(name, type, line, column, actual_type)
                case "bool":
                    try:
                        bool(value)
                    except:
                        raise WrongTypeException(name, type, line, column, actual_type)

