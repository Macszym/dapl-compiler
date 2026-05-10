from program import Program

if __name__ == "__main__":
    filename = "code"

    with open(filename, encoding='utf-8') as f:
        source_lines = f.readlines()

    program = Program(filename, source_lines)
    program.execute()