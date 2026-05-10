from antlr4 import *
from DAPLLexer import DAPLLexer
from DAPLParser import DAPLParser
from VariableListner import VariableListner
from FirstVisitor import FirstVisitor
from errors import *
from errors import SyntaxError as CustomSyntaxError
from ErrorListener import SyntaxErrorListener as CustomErrorListener


class Program:
    def __init__(self, path: str, source_lines: list):
        self.path = path
        self.source_lines = source_lines

    def execute(self):
        try:
            with open(self.path, "r", encoding='utf-8') as file:
                input_text = file.read()
        except FileNotFoundError:
            print(f"Error: Source file '{self.path}' not found.")
            return 1
        except Exception as e:
            print(f"Error reading file '{self.path}': {e}")
            return 1

        input_stream = InputStream(input_text)
        lexer = DAPLLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = DAPLParser(tokens)

        parser.removeErrorListeners()
        error_listener = CustomErrorListener(input_lines=self.source_lines)
        parser.addErrorListener(error_listener)

        tree = parser.start()

        if error_listener.has_errors:
            print("Parsing failed due to syntax errors. Execution halted.")
            return 1

        listener = VariableListner()

        '''
        Pass 1: Definitions (Variables, Constants, Functions, Table Schemas)
        '''
        try:
            walker = ParseTreeWalker()
            walker.walk(listener, tree)
        except DoubleDeclarationError as e:
            print(
                f"Error: Double declaration of '{e.varName}'. First at line {e.line1}, then at line {e.line2}, column {e.column}.")
            e.printError(self.source_lines)  # Use printError for detailed output
            return 1
        # Catch other specific listener-phase errors if any
        except Exception as e:
            print(f"Error during definition pass: {e}")
            import traceback
            traceback.print_exc()
            return 1

        '''
        Pass 2: Execution
        '''
        visitor = FirstVisitor(
            variables=listener.getVariables(),
            constants=listener.getConsants(),
            tables=listener.getTables(),
            tables_to_heap=listener.getTablesToHeap(),
            heap=listener.getHeap(),
            functions=listener.getFunctions(),
            source_lines=self.source_lines,
            library_functions=listener.getLibraryFunctions()
        )
        try:
            visitor.visit(tree)
        except CustomSyntaxError as e:
            print(e.message)
        except UknownNameException as e:
            print(e)
        except WrongTypeException as e:
            print(e)
        except ZeroDivisionError:
            print("Error: Division by zero.")
        except ZeroDivisionException as e:
            print(e)
        except InvalidOperationException as e:
            print(e)
        except ConstantOperationExcpetion as e:
            print(e)
            e.printError(self.source_lines)
        except FunctionNotFoundException as e:
            print(e)
        except ArgumentCountException as e:
            print(e)
        except ArgumentTypeException as e:
            print(e)
        except ReturnOutsideFunctionException as e:
            print(e)
        except MissingReturnValueException as e:
            print(e)
        except VoidFunctionReturnsValueException as e:
            print(e)
        except ReturnTypeMismatchException as e:
            print(e)
        except WrongColumnName as e:
            print(e)
        except WrongColumnNumber as e:
            print(e)
        except WrongShapeException as e:
            print(e)
        except NotImplementedError as e:
            print(f"Execution Error: Feature not fully implemented: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"An unexpected runtime error occurred: {e}")
            import traceback
            traceback.print_exc()
            return 1
        return 0


if __name__ == "__main__":
    # filename = "code" # Original
    import sys

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "code.dapl"  # Default to .dapl extension
        # Create a dummy code.dapl for testing if it doesn't exist
        try:
            with open(filename, "x") as f:  # Create if not exists
                f.write("// Default empty DAPL file for testing\n")
                f.write("out(\"Hello from default code.dapl!\");\n")
            print(f"Created dummy file: {filename}")
        except FileExistsError:
            pass

    source_lines = []
    try:
        with open(filename, encoding='utf-8') as f:
            source_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Test file '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading test file '{filename}': {e}")
        sys.exit(1)

    program = Program(filename, source_lines)
    exit_code = program.execute()
    if exit_code == 0:
        print("\nExecution finished successfully.")
    else:
        print(f"\nExecution failed with code {exit_code}.")