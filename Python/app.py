from compiler import Compiler


def main():
    compiler = Compiler()
    compiler.compile_file(
        "C:/Users/Matin/Codes/Compiler/Example/1-declare_variables.x",
        "C:/Users/Matin/Codes/Compiler/Example/1-declare_variables.cpp",
    )

    # for word in compiler.read_word():
    #     print(word)


if __name__ == "__main__":
    main()
