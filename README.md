# DAPL — Data Analysis Programming Language

Interpreter for **DAPL** (Data Analysis Programming Language), a small statically-typed language designed for tabular-data manipulation. Built as a course project at AGH for **Teoria kompilacji i kompilatory** (Compiler Theory & Compilers), June 2025.

## Authors

Co-authored with **Jan Rolka**, **Mateusz Sobiech**, and **Maciej Szymański**.

## Language at a glance

DAPL combines a familiar imperative core (functions, `if`/`elif`/`else`, `while`, `for`, scoped variables) with first-class support for `Table` and `List`. Types: `int`, `double`, `string`, `bool`, plus `auto` for inferred locals; the `^` operator reaches into an enclosing scope.

A quick taste — joining two tables:

```dapl
Table <int:empid, string:name, int:deptid> Employees = [
    [1, "Ala",     10],
    [2, "Bartek",  20],
    [3, "Celina",  10],
    [4, "Damian",  30]
];
Table <int:deptid, string:deptname> Departments = [
    [10, "Kadry"],
    [20, "IT"],
    [30, "Sprzedaż"],
    [40, "Marketing"]
];
Employees.join(Departments, deptid, deptid).show();
```

Supported table operations: filtering, grouping, aggregations, lambda expressions, joins.

## Architecture

Implemented in Python with **ANTLR4** for lexing and parsing. The interpreter walks the parse tree using two visitor passes:

- `FirstVisitor` — declaration collection (functions, type signatures)
- `VariableListner` — execution

The compiler pipeline lives under `src/`:

```
src/
├── DAPL.g4                # ANTLR grammar
├── DAPLLexer.py           # generated lexer
├── DAPLParser.py          # generated parser
├── DAPLListener.py        # generated listener
├── DAPLVisitor.py         # generated visitor base
├── FirstVisitor.py        # declarations pass
├── VariableListner.py     # execution pass
├── ErrorListener.py       # parse-error reporting
├── errors.py              # runtime errors
├── main.py                # CLI entrypoint
├── program.py             # program object
└── examples/              # sample DAPL programs (numbered)
```

## Setup & usage

```bash
python3 -m venv env
source env/bin/activate          # Linux/macOS — Windows: env\Scripts\activate
pip install -r requirements.txt  # antlr4-python3-runtime
```

Run a DAPL program:

```bash
cd src
python main.py examples/employees
```

## Documentation

Two reports ship with the source, both in Polish:

- `RAPORT_IMPLEMENTACJI.md` — implementation report (architecture, design decisions, type system)
- `DOKUMENTACJA_UZYTKOWNIKA.md` — user manual (syntax, types, examples)

PDF copies (`DAPL-raport_techniczny.pdf`, `DAPL-dokumentacja-uzytkownika.pdf`) are also included.

## A note

Course project — the language is intentionally narrow (no module system, limited I/O beyond CSV import) but the parser and interpreter scaffolding are straightforward to extend.
