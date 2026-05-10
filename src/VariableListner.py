from antlr4.tree.Tree import TerminalNodeImpl
from DAPLListener import DAPLListener
from DAPLParser import DAPLParser
from errors import DoubleDeclarationError, WrongShapeException, WrongTypeException, UknownLibraryException
from errors import UknownNameException

class FunctionDefinition:
    def __init__(self, name, params_ctx, return_type_repr, body_ctx_list, definition_line, lexical_scope_depth=0):
        self.name = name
        self.params_ctx = params_ctx
        self.body_ctx_list = body_ctx_list
        self.definition_line = definition_line
        self.lexical_scope_depth = lexical_scope_depth
        self.param_names_types = []
        if self.params_ctx:
            seen_param_names = set()
            for p_ctx in self.params_ctx.param():
                param_name = p_ctx.NAME().getText()
                param_type = p_ctx.type_().getText()

                if param_name in seen_param_names:
                    param_line = p_ctx.start.line
                    param_column = p_ctx.NAME().getSymbol().column
                    raise DoubleDeclarationError(param_name, definition_line, param_line, param_column)
                
                seen_param_names.add(param_name)
                self.param_names_types.append((param_name, param_type))
        self.return_type_str = 'void'
        if isinstance(return_type_repr, DAPLParser.TypeContext):
            self.return_type_str = return_type_repr.getText()
        elif isinstance(return_type_repr, str) and return_type_repr == 'void':
            self.return_type_str = 'void'

class VariableListner(DAPLListener):

    def __init__(self, heap: dict = None):
        self.variables = {}  # name: [type_str, line_num, value_placeholder_or_None]
        self.constants = {}  # name: [type_str, line_num, value_placeholder_or_None]
        self.tables = {}  # name: {colName: type_str, ...} (schema)
        self.tables_to_heap = {}  # name: heap_key_str
        self.heap = heap if heap is not None else {}  # heap_key_str: list_of_rows
        self.heap_number = 0
        self.skip = False
        self.functions = {}  # name: FunctionDefinition
        self.current_table = None
        self.function_declaration_depth = 0
        self.library_functions = {"str": ["length", "startsWith"]}
        self.library_functions_used = []

    def _get_node_column(self, node_with_symbol):
        if hasattr(node_with_symbol, 'getSymbol') and node_with_symbol.getSymbol() is not None:
            return node_with_symbol.getSymbol().column
        elif isinstance(node_with_symbol, TerminalNodeImpl) and node_with_symbol.symbol is not None:
            return node_with_symbol.symbol.column
        return 0

    def enterIm1(self, ctx:DAPLParser.ImContext):
        lib = ctx.NAME().getText()

        if lib not in self.library_functions.keys():
            raise UknownLibraryException(lib, ctx.start.line, self._get_node_column(ctx.NAME))

        if lib == "str":

            for func_name in self.library_functions[lib]:
                self.function_declaration_depth += 1

                line = ctx.start.line
                column = ctx.start.column

                if func_name in self.variables:
                    raise DoubleDeclarationError(func_name, self.variables[func_name][1], line, column)
                if func_name in self.constants:
                    raise DoubleDeclarationError(func_name, self.constants[func_name][1], line, column)
                if func_name in self.functions:
                    raise DoubleDeclarationError(func_name, self.functions[func_name].definition_line, line, column)

                func_def = FunctionDefinition(func_name, None, "bool", None, line)
                self.functions[func_name] = func_def

                self.library_functions_used.append(func_name)
                self.function_declaration_depth -=1

    def enterIm2(self, ctx:DAPLParser.Im2Context):
        lib = ctx.NAME(0).getText()
        func_name = ctx.NAME(1).getText()

        if lib not in self.library_functions.keys():
            raise UknownNameException(lib, ctx.start.line, self._get_node_column(ctx.NAME(0).getSymbol()))

        if func_name not in self.library_functions[lib]:
            raise UknownNameException(lib, ctx.start.line, self._get_node_column(ctx.NAME(1).getSymbol()))

        line = ctx.start.line
        column = ctx.start.column

        if func_name in self.variables:
            raise DoubleDeclarationError(func_name, self.variables[func_name][1], line, column)
        if func_name in self.constants:
            raise DoubleDeclarationError(func_name, self.constants[func_name][1], line, column)
        if func_name in self.functions:
            raise DoubleDeclarationError(func_name, self.functions[func_name].definition_line, line, column)

        func_def = FunctionDefinition(func_name, None, "bool", None, line)
        self.functions[func_name] = func_def

        self.library_functions_used.append(func_name)

    def enterVarDecInitValue(self, ctx: DAPLParser.VarDecInitValueContext):
        if self.function_declaration_depth > 0:
            return

        name = ctx.NAME().getText()
        type_ = ctx.type_().getText()
        line = ctx.start.line
        column = self._get_node_column(ctx.NAME())

        if name in self.variables:
            raise DoubleDeclarationError(name, self.variables[name][1], line, column)
        if name in self.constants:
            raise DoubleDeclarationError(name, self.constants[name][1], line, column)
        # if name in self.functions:
        #     raise DoubleDeclarationError(name, self.functions[name].definition_line, line, column)
        self.variables[name] = [type_, line, None]

    def enterVarDecDefaultValue(self, ctx: DAPLParser.VarDecDefaultValueContext):
        if self.function_declaration_depth > 0:
            return

        name = ctx.NAME().getText()
        type_ = ctx.type_().getText()
        line = ctx.start.line
        column = self._get_node_column(ctx.NAME())

        if name in self.variables:
            raise DoubleDeclarationError(name, self.variables[name][1], line, column)
        if name in self.constants:
            raise DoubleDeclarationError(name, self.constants[name][1], line, column)
        # if name in self.functions:
        #     raise DoubleDeclarationError(name, self.functions[name].definition_line, line, column)
        self.variables[name] = [type_, line, None]

    def enterConstDec(self, ctx: DAPLParser.ConstDecContext):
        name = ctx.NAME().getText()
        type_ = ctx.type_().getText()
        line = ctx.start.line
        column = self._get_node_column(ctx.NAME())

        if name in self.variables:
            raise DoubleDeclarationError(name, self.variables[name][1], line, column)
        if name in self.constants:
            raise DoubleDeclarationError(name, self.constants[name][1], line, column)
        # if name in self.functions:
        #     raise DoubleDeclarationError(name, self.functions[name].definition_line, line, column)
        self.constants[name] = [type_, line, None]

    def enterFuncDec(self, ctx: DAPLParser.FuncDecContext):
        self.function_declaration_depth += 1

        func_name = ctx.NAME().getText()
        line = ctx.start.line
        column = self._get_node_column(ctx.NAME())

        # if func_name in self.variables:
        #     raise DoubleDeclarationError(func_name, self.variables[func_name][1], line, column)
        # if func_name in self.constants:
        #     raise DoubleDeclarationError(func_name, self.constants[func_name][1], line, column)
        if func_name in self.functions:
            raise DoubleDeclarationError(func_name, self.functions[func_name].definition_line, line, column)

        params_ctx = ctx.paramList()
        body_ctx_list = ctx.line()
        return_type_repr = None
        children = list(ctx.getChildren())
        try:
            colon_index = -1
            for i, child_node in enumerate(children):
                if isinstance(child_node, TerminalNodeImpl) and child_node.symbol.text == ':':
                    colon_index = i
                    break
            if colon_index != -1 and colon_index + 1 < len(children):
                type_spec_node = children[colon_index + 1]
                if isinstance(type_spec_node, DAPLParser.TypeContext):
                    return_type_repr = type_spec_node
                elif isinstance(type_spec_node, TerminalNodeImpl) and type_spec_node.symbol.text == 'void':
                    return_type_repr = 'void'
        except Exception:
            pass
        func_def = FunctionDefinition(func_name, params_ctx, return_type_repr, body_ctx_list, line, self.function_declaration_depth + 1)
        self.functions[func_name] = func_def

    def exitFuncDec(self, ctx: DAPLParser.FuncDecContext):
        self.function_declaration_depth -= 1

    def enterScope(self, ctx:DAPLParser.ScopeContext):
        self.function_declaration_depth += 1

    def exitScope(self, ctx:DAPLParser.ScopeContext):
        self.function_declaration_depth -= 1

    def enterTableDec(self, ctx:DAPLParser.TableDecContext):
        name = ctx.NAME().getText()
        self.current_table = name
        self.tables.update({name : {}})
        self.tables_to_heap.update({name : f"h{self.heap_number}"})

        self.enterColumnList(ctx.columnList())

    def exitTableDec(self, ctx:DAPLParser.TableDecContext):
        self.heap_number += 1

    def enterEmptyTableDec(self, ctx:DAPLParser.TableDecContext):
        name = ctx.NAME().getText()
        self.current_table = name
        self.tables.update({name : {}})
        self.heap.update({f"h{self.heap_number}" : []})
        self.tables_to_heap.update({name : f"h{self.heap_number}"})
        self.heap_number+=1

    def enterRead_csv(self, ctx:DAPLParser.Read_csvContext):
        name = ctx.NAME().getText()
        self.current_table = name
        self.tables.update({name : {}})
        self.heap.update({f"h{self.heap_number}" : []})
        self.tables_to_heap.update({name : f"h{self.heap_number}"})
        self.heap_number+=1

    def enterTableAction(self, ctx:DAPLParser.ColumnListContext):
        self.skip = True

    def exitTableAction(self, ctx:DAPLParser.ColumnListContext):
        self.skip = False

    def enterColumn(self, ctx:DAPLParser.ColumnContext):
        if not self.skip:
            current_key = list(self.tables.keys())[-1]
            self.tables[current_key].update({ctx.NAME().getText() : ctx.type_().getText()})

    def enterTable(self, ctx:DAPLParser.TableContext):
        rows = []

        for child in ctx.getChildren():
            if isinstance(child, DAPLParser.RowContext):
                row = self.visitRow(child)
                current_key = list(self.tables.keys())[-1]

                if len(row) != len(list(self.tables[current_key].keys())):
                    raise WrongShapeException(ctx.start.line, ctx.stop.column)

                rows.append(row)
        self.heap[f"h{self.heap_number}"] = rows

        return rows

    def visitRow(self, ctx:DAPLParser.RowContext):
        values = []

        for child in ctx.getChildren():
            if isinstance(child, DAPLParser.ValueContext):
                values.append(child.getText())

        return values

    def getVariables(self):
        return self.variables

    def getConsants(self):
        return self.constants

    def getTables(self):
        return self.tables

    def getHeap(self):
        return self.heap

    def getTablesToHeap(self):
        return self.tables_to_heap

    def getFunctions(self):
        return self.functions

    def getLibraryFunctions(self):
        return self.library_functions_used