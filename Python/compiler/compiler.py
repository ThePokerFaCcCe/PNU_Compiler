from enum import Enum
from io import TextIOWrapper
import os
import re
from typing import Any, Iterator

REGEX_VARIABLE_NAME = "^[a-zA-Z_][a-zA-Z0-9_]*$"
REGEX_VALUE_STRING = '^".*"$'


class WordTypeEnum(Enum):
    RESERVED_WORD = 100
    OPERAND = 101
    VALUE_TYPE = 102
    COMMENT = 103
    VARIABLE_NAME = 104

    VALUE = 200

    OPERATOR_ASSIGNMENT_EQUALS = 300
    OPERATOR_ARITHMETIC_ADDITION = 320
    OPERATOR_ARITHMETIC_SUBSTRACTION = 321


class WordDetail:
    word_type: WordTypeEnum
    detail: Any | None
    word: str

    def __init__(
        self, word_type: WordTypeEnum, word: str, word_detail: Any | None = None
    ) -> None:
        self.word_type = word_type
        self.detail = word_detail
        self.word = word


class ReservedWordTypeEnum(Enum):
    VALUE_TYPE = WordTypeEnum.VALUE_TYPE


class ReservedWordDetail:
    reserved_type: ReservedWordTypeEnum
    word_in_cpp: str | None

    def __init__(self, reserved_type: ReservedWordTypeEnum, word_in_cpp: str) -> None:
        self.reserved_type = reserved_type
        self.word_in_cpp = word_in_cpp


RESERVED_WORDS = {
    "int": WordDetail(
        word_type=WordTypeEnum.RESERVED_WORD,
        word="int",
        word_detail=ReservedWordDetail(
            reserved_type=ReservedWordTypeEnum.VALUE_TYPE, word_in_cpp="int"
        ),
    ),
}

OPERATORS = {
    "=": WordDetail(word_type=WordTypeEnum.OPERATOR_ASSIGNMENT_EQUALS, word="="),
    "+": WordDetail(word_type=WordTypeEnum.OPERATOR_ARITHMETIC_ADDITION, word="+"),
    "-": WordDetail(word_type=WordTypeEnum.OPERATOR_ARITHMETIC_SUBSTRACTION, word="-"),
}

COMMENT_WORD = "//"


class LineActionTypeEnum(Enum):
    DECLARE_VARIABLE = 1
    SET_VARIABLE = 2
    DECLARE_AND_SET_VARIABLE = 3


class LineActionDetail:
    line_action_type: LineActionTypeEnum
    line_word_details: list[WordDetail]

    def __init__(
        self, line_action_type: LineActionTypeEnum, line_word_details: list[WordDetail]
    ) -> None:
        self.line_action_type = line_action_type
        self.line_word_details = line_word_details


LINE_ACTION_EXPRESSIONS = {
    f"{WordTypeEnum.OPERAND}{WordTypeEnum.OPERATOR_ASSIGNMENT_EQUALS}{WordTypeEnum.VALUE}": LineActionTypeEnum.SET_VARIABLE
}


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

    def __lex_word(self, word: str) -> WordDetail:
        if word == COMMENT_WORD:
            return WordDetail(word_type=WordTypeEnum.COMMENT, word=COMMENT_WORD)

        reserved_word_detail = RESERVED_WORDS.get(word)
        if reserved_word_detail != None:
            return reserved_word_detail

        operator_word_detail = OPERATORS.get(word)
        if operator_word_detail != None:
            return operator_word_detail

        is_variable_name = re.match(REGEX_VARIABLE_NAME, word)
        if is_variable_name:
            return WordDetail(word_type=WordTypeEnum.VARIABLE_NAME, word=word)

        is_string_value = re.match(REGEX_VALUE_STRING, word)

        raise SyntaxError(f"'{word}' is not a valid word")

    def __lex_line(self, line: str) -> list[WordDetail]:
        words = self.__split_words(line)

        word_detail_list: list[WordDetail] = []
        for word in words:
            word_detail = self.__lex_word(word)
            word_detail_list.append(word_detail)

        return word_detail_list
        # if word_detail.word_type == WordTypeEnum.RESERVED_WORD:
        #     reserved_word_detail: ReservedWordDetail = word_detail.detail
        #     if (
        #         reserved_word_detail.reserved_type
        #         == ReservedWordTypeEnum.VALUE_TYPE
        #     ):
        #         pass

    def __parse_line(self, line: str) -> LineActionDetail:
        word_detail_list = self.__lex_line(line)

        line_expression = "".join(
            [word_detail.word_type for word_detail in word_detail_list]
        )

        line_action_type = LINE_ACTION_EXPRESSIONS.get(line_expression)
        if line_action_type:
            return LineActionDetail(
                line_action_type=line_action_type, line_word_details=word_detail_list
            )

        raise SyntaxError(f"Syntax Error Near {line}")

    def __parse(self):
        lines = self.__read_lines()
        compiled_text = ""
        for line in lines:
            line_detail = self.__parse_line(line)
            if line_detail.line_action_type == LineActionTypeEnum.SET_VARIABLE:
                variable_name = line_detail.line_word_details[0]
                variable_value = line_detail.line_word_details[2]
                compiled_text += f"int {variable_name} = {variable_value}"

        return compiled_text

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
