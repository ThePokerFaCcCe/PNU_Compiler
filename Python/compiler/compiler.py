from enum import Enum
from io import TextIOWrapper
import os
from typing import Iterator


class ReservedWordTypeEnum(Enum):
    VALUE_TYPE = 1


class ReservedWordData:
    reserved_type: ReservedWordTypeEnum
    word_in_cpp: str | None

    def __init__(self, reserved_type: ReservedWordTypeEnum, word_in_cpp: str) -> None:
        self.reserved_type = reserved_type
        self.word_in_cpp = word_in_cpp


RESERVED_WORDS = {
    "int": ReservedWordData(
        reserved_type=ReservedWordTypeEnum.VALUE_TYPE, word_in_cpp="int"
    ),
}

OPERATORS = {}

BASE_CPP_CODE = """
#include <iostream>
using namespace std;

int main()
{
    {0}
    
    return 0;
}
"""


class Compiler:
    __input_file: TextIOWrapper

    def __read_lines(self) -> Iterator[str]:
        line_text = self.__input_file.readline()
        while len(line_text) > 0:
            yield line_text
            line_text = self.__input_file.readline()

    def __split_words(self, text: str) -> Iterator[str]:
        words: list[str] = text.split(" ")
        for word in words:
            if len(word) > 0:
                yield word

    def __parse(self) -> str:
        lines = self.__read_lines()
        compiled_text = ""
        for line in lines:
            words = self.__split_words(line)
            word: str = words.__next__()

            reserved_word = RESERVED_WORDS.get(word)
            if reserved_word:
                if reserved_word.reserved_type == ReservedWordTypeEnum.VALUE_TYPE:
                    pass

    def compile_file(self, input_x_path: str, output_cpp_path: str):
        # TODO - check file types & exists
        self.__input_file = open(input_x_path, "r", encoding="utf-8")

        try:
            compiled_code = self.__parse()
            cpp_code = BASE_CPP_CODE.format(compiled_code)

            with open(output_cpp_path, "w", encoding="utf-8") as output_file:
                output_file.write(cpp_code)

        except Exception as ex:
            self.__input_file.close()
            raise ex
