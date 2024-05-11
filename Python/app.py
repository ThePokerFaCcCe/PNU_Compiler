import sys
from compiler import Compiler, Interpreter


def invalid_args_error():
    print(
        "Invalid args.",
        "Compiler example: py app.py compile 'path/to/input' 'path/to/output'",
        "Interpreter example: py app.py run 'path/to/input'",
    )


def main():
    args = sys.argv[1:]
    if not args:
        return invalid_args_error()

    action = args[0]

    if action == "compile":
        if len(args) != 3:
            return invalid_args_error()

        compiler = Compiler(args[1], args[2])

        compiler.start()

    elif action == "run":
        if len(args) != 2:
            return invalid_args_error()

        interpreter = Interpreter(args[1])
        interpreter.start()

    else:
        print("Invalid action.valid actions are: `run`,`compile`")
        pass


if __name__ == "__main__":
    main()
