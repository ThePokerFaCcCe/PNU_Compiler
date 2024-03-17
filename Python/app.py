from compiler import Compiler


def main():
    compiler = Compiler("C:/Users/Matin/Codes/Compiler/Example/simple_app.x")

    words = compiler.__split_words()
    print(words.__next__())

    # for word in compiler.read_word():
    #     print(word)


if __name__ == "__main__":
    main()
