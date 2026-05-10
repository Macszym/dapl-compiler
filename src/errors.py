class DoubleDeclarationError(Exception):
    def __init__(self, varName, line1, line2, column):
        self.varName = varName
        self.line1 = line1
        self.line2 = line2
        self.column = column

    def printError(self, source_lines: list[str]) -> None:
        print(f"[DoubleDeclarationError] Double declaration of '{self.varName}'")
        print(f"First declared at line {self.line1}")
        print(f"Second declaration: line {self.line2}, column {self.column}")
        print(f"{self.line2}: {source_lines[self.line2 - 1].rstrip()}")
        print(" " * (self.column + 2) + "^")


class UknownNameException(Exception):
    def __init__(self, varName, line, column):
        self.varName = varName
        self.line = line
        self.column = column

    def printError(self, source_lines: list[str]) -> None:
        print(
            f"[UnknownNameException] Use of undeclared name '{self.varName}' at line {self.line}, column {self.column}")
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")
        print(" " * (self.column + 3) + "^")

class UknownLibraryException(Exception):
    def __init__(self, libName, line, column):
        self.libName = libName
        self.line = line
        self.column = column
        message = (
            f"[UknownLibraryException] Uknown library named {libName}: "
        )
        super().__init__(message)

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")
        print(" " * (self.column + 1) + "^")


class WrongTypeException(Exception):
    def __init__(self, varName, expectedType, line, column, gotType=None):
        self.varName = varName
        self.line = line
        self.column = column
        self.expectedType = expectedType
        self.gotType = gotType
        name_info = f"'{varName}'" if varName else "expression"
        got_str = gotType if gotType else "unknown"
        message = (
            f"[WrongTypeException] Wrong type for {name_info}: "
            f"expected '{expectedType}', but got '{got_str}'"
        )
        super().__init__(message)

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")
        print(" " * (self.column + 1) + "^")

class ImpossibleCastException(Exception):
    def __init__(self, line, message: str = "Impossible cast"):
        self.line = line
        super().__init__(f"[ImpossibleCastException] {message}")
    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")
        print("^")

class InvalidOperationException(Exception):
    def __init__(self, line: int, message: str = "Invalid operation"):
        self.line = line
        super().__init__(f"[InvalidOperationException] {message}")

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")
        print("^")
class ZeroDivisionException(Exception):
    def __init__(self, line: int):
        self.line = line
        message = "[ZeroDivisionException] Division by zero"
        super().__init__(message)

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")


class SyntaxError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class WrongLambdaException(Exception):
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
    def printError(self):
        pass

class ConstantOperationExcpetion(Exception):
    def __init__(self, name, line, column):
        self.name = name
        self.line = line
        self.column = column
    def printError(self, source_lines: list[str]):
        print(f"Opearion on a const value named {self.name}")
        print(f"{self.line} : {source_lines[self.line-1]}")
        print(" " * (self.column + 3), "^")

class WrongShapeException(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
    def printError(self,  source_lines: list[str]):
        print("Input table has a wrong shape")
        print(f"{self.line} : {source_lines[self.line-1]}")
        print(" " * (self.column - 4), "^")

class WrongColumnName(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
    def printError(self,  source_lines: list[str]):
        print("Wrong column name")
        print(f"{self.line} : {source_lines[self.line-1]}")
        print(" " * (self.column + 3), "^")

class WrongColumnNumber(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
    def printError(self,  source_lines: list[str]):
        print("Wrong column number")
        print(f"{self.line} : {source_lines[self.line-1]}")
        print(" " * (self.column + 3), "^")
        print("Index out of bonds")

class WrongColumnNumber2(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
    def printError(self,  source_lines: list[str]):
        print("Wrong column number")
        print(f"{self.line} : {source_lines[self.line-1]}")
        print(" " * (self.column + 3), "^")

class WrongRowSizeException(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
    def printError(self,  source_lines: list[str]):
        print("Row is too big")
        print(f"{self.line} : {source_lines[self.line-1]}")
        print(" " * (self.column + 3), "^")

class FunctionReturnException(Exception):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line
        super().__init__("Function return (internal control flow)")


class FunctionNotFoundException(Exception):
    def __init__(self, func_name: str, line: int):
        self.func_name = func_name
        self.line = line
        super().__init__(f"[FunctionNotFoundException] Function '{func_name}' not found")

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")


class ArgumentCountException(Exception):
    def __init__(self, func_name: str, expected: int, got: int, line: int):
        self.func_name = func_name
        self.expected = expected
        self.got = got
        self.line = line
        super().__init__(
            f"[ArgumentCountException] Function '{func_name}' expected {expected} arguments, but got {got}"
        )

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")


class ArgumentTypeException(Exception):
    def __init__(
        self,
        func_name: str,
        param_name: str,
        expected_type: str,
        got_type: str,
        line: int,
        arg_index: int
    ):
        self.func_name = func_name
        self.param_name = param_name
        self.expected_type = expected_type
        self.got_type = got_type
        self.line = line
        self.arg_index = arg_index
        super().__init__(
            f"[ArgumentTypeException] Function '{func_name}' argument {arg_index+1} ('{param_name}'): "
            f"expected type {expected_type}, but got {got_type}"
        )

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")


class ReturnOutsideFunctionException(Exception):
    def __init__(self, line: int):
        self.line = line
        super().__init__("[ReturnOutsideFunctionException] 'return' statement outside of a function")

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")



class MissingReturnValueException(Exception):
    def __init__(self, func_name: str, expected_type: str, line: int):
        self.func_name = func_name
        self.expected_type = expected_type
        self.line = line
        super().__init__(
            f"[MissingReturnValueException] Non-void function '{func_name}' must return a value of type '{expected_type}'"
        )

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")



class VoidFunctionReturnsValueException(Exception):
    def __init__(self, func_name: str, line: int):
        self.func_name = func_name
        self.line = line
        super().__init__(f"[VoidFunctionReturnsValueException] Void function '{func_name}' cannot return a value")

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")


class ReturnTypeMismatchException(Exception):
    def __init__(self, func_name: str, expected_type: str, got_type: str, line: int):
        self.func_name = func_name
        self.expected_type = expected_type
        self.got_type = got_type
        self.line = line
        super().__init__(
            f"[ReturnTypeMismatchException] Function '{func_name}' expected to return '{expected_type}', but returned '{got_type}'"
        )

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")


class MaxRecursionDepthExceededError(Exception):
    def __init__(self, func_name: str, line: int, max_depth: int):
        self.func_name = func_name
        self.line = line
        self.max_depth = max_depth
        super().__init__(
            f"[MaxRecursionDepthExceededError] Max recursion depth ({max_depth}) exceeded during call to function '{func_name}'"
        )

    def printError(self, source_lines: list[str]) -> None:
        print(self.args[0])
        print(f"{self.line}: {source_lines[self.line - 1].rstrip()}")

